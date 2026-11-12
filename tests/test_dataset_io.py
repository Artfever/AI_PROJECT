"""Persisted feature order, input provenance and target/metadata correspondence."""

import hashlib
import json
import subprocess
import sys

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split_manifest import build_split_manifest
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import (
    build_fitting_dataset,
    build_validation_dataset,
    manifest_digest,
)
from fleetpulse.features.dataset_io import load_feature_dataset, save_feature_dataset


@pytest.fixture
def datasets():
    rows = [
        {"unit_id": unit, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 2 * cycle)}
        for unit, last in ((1, 3), (2, 4))
        for cycle in range(1, last + 1)
    ]
    manifest = build_split_manifest(
        rows,
        dataset_partition="FD001/train",
        source_path="synthetic/train.txt",
        source_sha256="a" * 64,
        validation_fraction=0.5,
    )
    kwargs = {
        "manifest": manifest,
        "source_sha256": "a" * 64,
        "config": FeatureConfig(channels=("sensor_2", "sensor_1")),
    }
    return build_fitting_dataset(rows, **kwargs), build_validation_dataset(rows, **kwargs), manifest


def _rewrite(path, document, *, rehash=False):
    if rehash:
        content = json.dumps(
            document["payload"], sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        document["sha256"] = hashlib.sha256(content.encode()).hexdigest()
    path.write_text(json.dumps(document), encoding="utf-8")


@pytest.mark.parametrize("index", [0, 1])
def test_deterministic_round_trip_preserves_exact_X_y_keys_schema_and_input_hashes(
    datasets, tmp_path, index
):
    dataset = datasets[index]
    path = tmp_path / "table.json"
    first_hash = save_feature_dataset(dataset, path)
    original = path.read_bytes()
    assert save_feature_dataset(dataset, path) == first_hash
    assert path.read_bytes() == original
    restored = load_feature_dataset(
        path,
        expected_source_sha256="a" * 64,
        expected_manifest_sha256=manifest_digest(datasets[2]),
        expected_config=dataset.config,
    )
    assert restored == dataset
    assert restored.X == dataset.X and restored.y == dataset.y
    assert restored.row_keys == dataset.row_keys
    assert restored.feature_names[:4] == (
        "sensor_2_latest",
        "sensor_2_mean",
        "sensor_2_std",
        "sensor_2_slope",
    )
    assert dataset.source_sha256 == "a" * 64
    assert dataset.split_manifest_sha256 == manifest_digest(datasets[2])


def test_fresh_process_reload_preserves_labels_and_keys(datasets, tmp_path):
    path = tmp_path / "table with spaces.json"
    save_feature_dataset(datasets[0], path)
    code = (
        "import json,sys; from fleetpulse.features.dataset_io import load_feature_dataset; "
        "d=load_feature_dataset(sys.argv[1]); print(json.dumps({'keys':d.row_keys,'y':d.y,'X':d.X}))"
    )
    result = json.loads(subprocess.check_output([sys.executable, "-c", code, str(path)], text=True))
    assert result["keys"] == [list(key) for key in datasets[0].row_keys]
    assert result["y"] == list(datasets[0].y)
    assert result["X"] == [list(row) for row in datasets[0].X]


def test_shuffled_metadata_fails_row_binding_even_with_recomputed_content_hash(datasets, tmp_path):
    path = tmp_path / "table.json"
    save_feature_dataset(datasets[0], path)
    document = json.loads(path.read_text())
    first, second = document["payload"]["rows"][:2]
    first["metadata"], second["metadata"] = second["metadata"], first["metadata"]
    _rewrite(path, document, rehash=True)
    with pytest.raises(ValueError, match="row key and metadata alignment mismatch"):
        load_feature_dataset(path)


def test_shuffled_labels_are_rejected_as_content_drift(datasets, tmp_path):
    path = tmp_path / "table.json"
    save_feature_dataset(datasets[0], path)
    document = json.loads(path.read_text())
    first, second = document["payload"]["rows"][:2]
    first["true_rul"], second["true_rul"] = second["true_rul"], first["true_rul"]
    _rewrite(path, document)
    with pytest.raises(ValueError, match="content hash mismatch"):
        load_feature_dataset(path)


@pytest.mark.parametrize(
    "corruption",
    ["feature_order", "version", "row_order", "duplicate", "label", "width", "config_hash"],
)
def test_malformed_contract_is_rejected_even_after_rehash(datasets, tmp_path, corruption):
    path = tmp_path / "table.json"
    save_feature_dataset(datasets[0], path)
    document = json.loads(path.read_text())
    payload = document["payload"]
    if corruption == "feature_order":
        payload["feature_names"].reverse()
    elif corruption == "version":
        payload["schema_version"] = 99
    elif corruption == "row_order":
        payload["rows"].reverse()
    elif corruption == "duplicate":
        payload["rows"][1] = payload["rows"][0]
    elif corruption == "label":
        payload["rows"][0]["true_rul"] = True
    elif corruption == "width":
        payload["rows"][0]["features"].pop()
    else:
        payload["input_hashes"]["feature_config_sha256"] = "b" * 64
    _rewrite(path, document, rehash=True)
    with pytest.raises(ValueError, match="Invalid feature dataset"):
        load_feature_dataset(path)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"expected_source_sha256": "b" * 64},
        {"expected_manifest_sha256": "b" * 64},
        {"expected_config": FeatureConfig(channels=("sensor_1",))},
    ],
)
def test_caller_pinned_inputs_reject_otherwise_valid_table(datasets, tmp_path, kwargs):
    path = tmp_path / "table.json"
    save_feature_dataset(datasets[0], path)
    with pytest.raises(ValueError, match="differs from expected"):
        load_feature_dataset(path, **kwargs)
