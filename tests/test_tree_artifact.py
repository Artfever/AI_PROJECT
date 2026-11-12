"""Saved Decision Tree model, provenance, and predictions must agree."""

import json
from dataclasses import replace

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split_manifest import build_split_manifest
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import build_fitting_dataset, build_validation_dataset
from fleetpulse.models.train_tree import train_decision_tree
from fleetpulse.models.tree_artifact import (
    MANIFEST_FILENAME,
    MODEL_FILENAME,
    save_decision_tree_artifact,
    verify_decision_tree_artifact,
)


@pytest.fixture
def trained_tree(tmp_path):
    rows = [
        {"unit_id": unit, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, cycle + unit)}
        for unit, lifetime in ((1, 5), (2, 7), (3, 9), (4, 11))
        for cycle in range(1, lifetime + 1)
    ]
    manifest = build_split_manifest(
        rows,
        dataset_partition="FD001/train",
        source_path="synthetic/train.txt",
        source_sha256="a" * 64,
        validation_fraction=0.5,
    )
    options = {
        "manifest": manifest,
        "source_sha256": "a" * 64,
        "config": FeatureConfig(channels=("sensor_1",)),
    }
    fitting = build_fitting_dataset(rows, **options)
    validation = build_validation_dataset(rows, **options)
    result = train_decision_tree(fitting, validation)
    paths = save_decision_tree_artifact(
        result,
        fitting,
        validation,
        tmp_path,
        fitting_dataset_sha256="b" * 64,
        validation_dataset_sha256="c" * 64,
    )
    return tmp_path, validation, result, paths


def test_artifact_reload_reproduces_predictions_metrics_and_provenance(trained_tree):
    output_dir, validation, result, paths = trained_tree

    replay = verify_decision_tree_artifact(paths["manifest_path"], validation)

    assert paths["model_path"].name == MODEL_FILENAME
    assert paths["manifest_path"].name == MANIFEST_FILENAME
    assert replay == {
        "prediction_count": len(validation.rows),
        "mae_cycles": result.metrics.mae,
        "rmse_cycles": result.metrics.rmse,
    }
    manifest = json.loads(paths["manifest_path"].read_text(encoding="utf-8"))["payload"]
    assert manifest["training"]["fitting_dataset_sha256"] == "b" * 64
    assert manifest["training"]["validation_dataset_sha256"] == "c" * 64
    assert len(manifest["evaluation"]["predictions"]) == len(validation.rows)
    assert (output_dir / "decision_tree_metrics.json").exists()


def test_artifact_rejects_model_file_tampering(trained_tree):
    _, validation, _, paths = trained_tree
    paths["model_path"].write_bytes(paths["model_path"].read_bytes() + b"tamper")

    with pytest.raises(ValueError, match="model file hash"):
        verify_decision_tree_artifact(paths["manifest_path"], validation)


def test_artifact_rejects_validation_provenance_mismatch(trained_tree):
    _, validation, _, paths = trained_tree

    with pytest.raises(ValueError, match="Validation dataset does not match"):
        verify_decision_tree_artifact(
            paths["manifest_path"], replace(validation, split_manifest_sha256="d" * 64)
        )


def test_artifact_rejects_manifest_content_tampering(trained_tree):
    _, validation, _, paths = trained_tree
    document = json.loads(paths["manifest_path"].read_text(encoding="utf-8"))
    document["payload"]["evaluation"]["predictions"][0]["true_rul_cycles"] += 1
    paths["manifest_path"].write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match="manifest content hash"):
        verify_decision_tree_artifact(paths["manifest_path"], validation)
