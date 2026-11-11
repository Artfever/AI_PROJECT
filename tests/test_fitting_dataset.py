"""Fitting tables must use whole fitting engines and prefix-only predictor input."""

import copy
from unittest.mock import patch

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split_manifest import build_split_manifest
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import build_fitting_dataset
from fleetpulse.features.engineering import engineer_features


@pytest.fixture
def source_and_manifest():
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
    assert manifest["fitting_engines"] == [{"dataset_partition": "FD001/train", "unit_id": 2}]
    return rows, manifest


def test_every_fitting_cycle_has_aligned_uncapped_label_and_only_prefix_inputs(source_and_manifest):
    rows, manifest = source_and_manifest
    original = copy.deepcopy(rows)
    calls = []

    def observed(history, **kwargs):
        calls.append(copy.deepcopy(history))
        assert {row["unit_id"] for row in history} == {2}
        assert max(row["cycle"] for row in history) == kwargs["selected_cycle"]
        assert all(set(row) == {"unit_id", "cycle", *READING_COLUMNS} for row in history)
        return engineer_features(history, **kwargs)

    with patch("fleetpulse.features.build_dataset.engineer_features", side_effect=observed):
        data = build_fitting_dataset(
            iter(rows),
            manifest=manifest,
            source_sha256="a" * 64,
            config=FeatureConfig(channels=("sensor_1",)),
        )
    assert data.role == "fitting"
    assert data.row_keys == tuple(("FD001/train", 2, cycle) for cycle in (1, 2, 3, 4))
    assert data.y == (3, 2, 1, 0)
    assert data.X[0] == (2, 2, 0, 0)
    assert data.X[1] == (4, 3, 1, 2)
    assert [len(call) for call in calls] == [1, 2, 3, 4]
    assert len(data.feature_names) == 4
    assert rows == original


def test_interleaved_engine_input_preserves_key_target_alignment(source_and_manifest):
    rows, manifest = source_and_manifest
    interleaved = sorted(rows, key=lambda row: (row["cycle"], -row["unit_id"]))
    first = build_fitting_dataset(rows, manifest=manifest, source_sha256="a" * 64)
    assert build_fitting_dataset(interleaved, manifest=manifest, source_sha256="a" * 64) == first


def test_source_hash_mismatch_fails_before_extracting(source_and_manifest):
    rows, manifest = source_and_manifest
    with patch("fleetpulse.features.build_dataset.engineer_features") as extract:
        with pytest.raises(ValueError, match="SHA-256 mismatch"):
            build_fitting_dataset(rows, manifest=manifest, source_sha256="b" * 64)
        extract.assert_not_called()


def test_invalid_training_row_is_not_silently_dropped(source_and_manifest):
    rows, manifest = source_and_manifest
    rows[0]["sensor_1"] = float("nan")
    with pytest.raises(ValueError, match="source history is invalid"):
        build_fitting_dataset(rows, manifest=manifest, source_sha256="a" * 64)
