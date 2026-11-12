"""The Model Laboratory compares two verified outputs on identical engines."""

import hashlib
import json
from dataclasses import asdict

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split_manifest import build_split_manifest
from fleetpulse.evaluation import build_metrics_record, save_metrics_record, score_constant_baseline
from fleetpulse.evaluation.model_comparison import load_model_comparison
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import build_fitting_dataset, build_validation_dataset
from fleetpulse.models.train_tree import train_decision_tree
from fleetpulse.models.tree_artifact import save_decision_tree_artifact


@pytest.fixture
def verified_outputs(tmp_path):
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
    fitting_sha, validation_sha = "b" * 64, "c" * 64

    baseline_result = score_constant_baseline(fitting, validation)
    baseline_predictions = [
        {
            "dataset_partition": row.dataset_partition,
            "unit_id": row.unit_id,
            "cutoff_cycle": row.cutoff_cycle,
            "prediction_cycles": row.prediction,
            "true_rul_cycles": row.true_rul,
            "absolute_error_cycles": row.absolute_error,
            "squared_error_cycles": row.squared_error,
        }
        for row in baseline_result.metrics.per_engine
    ]
    baseline_payload = {
        "artifact_version": "constant-rul-validation-v1",
        "baseline": baseline_result.baseline.to_artifact(),
        "evaluation": {
            "dataset_partition": "FD001/train",
            "sample_unit": "engine",
            "sample_count": len(validation.rows),
            "feature_config": asdict(fitting.config),
            "random_seed": None,
            "source_sha256": fitting.source_sha256,
            "split_manifest_sha256": fitting.split_manifest_sha256,
            "fitting_dataset_sha256": fitting_sha,
            "validation_dataset_sha256": validation_sha,
            "mae_cycles": baseline_result.metrics.mae,
            "rmse_cycles": baseline_result.metrics.rmse,
            "predictions": baseline_predictions,
        },
    }
    baseline_path = tmp_path / "constant_rul_validation.json"
    _save_hashed(baseline_payload, baseline_path)
    save_metrics_record(
        build_metrics_record(
            model_name="constant-rul-baseline",
            model_version=baseline_result.baseline.artifact_version,
            partition="FD001/train",
            sample_unit="engine",
            sample_count=len(validation.rows),
            feature_config=asdict(fitting.config),
            random_seed=None,
            parameters=baseline_result.baseline.to_artifact(),
            mae_cycles=baseline_result.metrics.mae,
            rmse_cycles=baseline_result.metrics.rmse,
            runtime_seconds=0.01,
            input_hashes={"fitting_dataset_sha256": fitting_sha,
                          "validation_dataset_sha256": validation_sha},
        ),
        tmp_path / "metrics.json",
    )
    tree_result = train_decision_tree(fitting, validation)
    save_decision_tree_artifact(
        tree_result,
        fitting,
        validation,
        tmp_path,
        fitting_dataset_sha256=fitting_sha,
        validation_dataset_sha256=validation_sha,
    )
    return tmp_path, fitting, validation, fitting_sha, validation_sha


def test_comparison_aligns_per_engine_outputs_and_reports_both_metrics(verified_outputs):
    directory, fitting, validation, fitting_sha, validation_sha = verified_outputs

    comparison = load_model_comparison(
        directory,
        fitting,
        validation,
        fitting_dataset_sha256=fitting_sha,
        validation_dataset_sha256=validation_sha,
    )

    assert comparison.validation_engine_count == len(validation.rows)
    assert len(comparison.predictions) == 2 * len(validation.rows)
    assert comparison.baseline_metrics.engine_count == len(validation.rows)
    assert comparison.tree_metrics.engine_count == len(validation.rows)
    assert {row["Model"] for row in comparison.predictions} == {
        "Constant mean baseline",
        "Decision Tree",
    }
    baseline = [row for row in comparison.predictions if row["Model"] == comparison.baseline_name]
    tree = [row for row in comparison.predictions if row["Model"] == comparison.tree_name]
    assert [row["Engine"] for row in baseline] == [row["Engine"] for row in tree]
    assert [row["Actual RUL (cycles)"] for row in baseline] == [
        row["Actual RUL (cycles)"] for row in tree
    ]
    assert {row["Predicted RUL (cycles)"] for row in baseline} == {
        comparison.baseline_prediction
    }


def test_comparison_rejects_altered_baseline_engine_prediction(verified_outputs):
    directory, fitting, validation, fitting_sha, validation_sha = verified_outputs
    path = directory / "constant_rul_validation.json"
    payload = json.loads(path.read_text(encoding="utf-8"))["payload"]
    payload["evaluation"]["predictions"][0]["prediction_cycles"] += 1
    _save_hashed(payload, path)

    with pytest.raises(ValueError, match="baseline per-engine output differs"):
        load_model_comparison(
            directory,
            fitting,
            validation,
            fitting_dataset_sha256=fitting_sha,
            validation_dataset_sha256=validation_sha,
        )


def _save_hashed(payload, path):
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    path.write_text(
        json.dumps({"payload": payload, "sha256": digest}, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
