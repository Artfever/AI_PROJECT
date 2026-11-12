"""Versioned storage and independent verification for the P06 Decision Tree."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from math import isclose
from pathlib import Path
from typing import Any

import joblib
import sklearn
from sklearn.tree import DecisionTreeRegressor

from fleetpulse.evaluation import (
    ValidationPrediction,
    build_metrics_record,
    calculate_validation_metrics,
    save_metrics_record,
    validate_metrics_record,
)
from fleetpulse.features.build_dataset import FeatureDataset
from fleetpulse.models.train_tree import MODEL_VERSION, DecisionTreeValidationResult

TREE_ARTIFACT_SCHEMA = "decision-tree-validation-v1"
MODEL_FILENAME = "decision_tree_model.joblib"
MANIFEST_FILENAME = "decision_tree_validation.json"
METRICS_FILENAME = "decision_tree_metrics.json"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_decision_tree_artifact(
    result: DecisionTreeValidationResult,
    fitting: FeatureDataset,
    validation: FeatureDataset,
    output_dir: str | Path,
    *,
    fitting_dataset_sha256: str,
    validation_dataset_sha256: str,
) -> dict[str, Any]:
    """Save model, provenance, per-engine predictions, and common metrics JSON."""
    if result.feature_names != fitting.feature_names:
        raise ValueError("Model feature order differs from the fitting feature table.")
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    model_path = destination / MODEL_FILENAME
    temporary_model = destination / f"{MODEL_FILENAME}.tmp"
    joblib.dump(result.model, temporary_model)
    temporary_model.replace(model_path)
    model_sha256 = sha256_file(model_path)

    rows = [
        {
            "dataset_partition": row.dataset_partition,
            "unit_id": row.unit_id,
            "cutoff_cycle": row.cutoff_cycle,
            "prediction_cycles": row.prediction,
            "true_rul_cycles": row.true_rul,
            "absolute_error_cycles": metric.absolute_error,
            "squared_error_cycles": metric.squared_error,
        }
        for row, metric in zip(result.predictions, result.metrics.per_engine, strict=True)
    ]
    payload = {
        "schema_version": TREE_ARTIFACT_SCHEMA,
        "model": {
            "name": "decision-tree-rul",
            "version": MODEL_VERSION,
            "scikit_learn_version": sklearn.__version__,
            "filename": MODEL_FILENAME,
            "sha256": model_sha256,
        },
        "training": {
            "fitting_row_count": len(fitting.rows),
            "fitting_engine_count": len({row.vector.engine_key for row in fitting.rows}),
            "feature_names": list(fitting.feature_names),
            "feature_config": asdict(fitting.config),
            "random_seed": result.random_seed,
            "parameters": {
                "max_depth": result.max_depth,
                "min_samples_leaf": result.min_samples_leaf,
            },
            "source_sha256": fitting.source_sha256,
            "split_manifest_sha256": fitting.split_manifest_sha256,
            "fitting_dataset_sha256": fitting_dataset_sha256,
            "validation_dataset_sha256": validation_dataset_sha256,
        },
        "evaluation": {
            "partition": "FD001/train",
            "sample_unit": "engine",
            "sample_count": result.metrics.engine_count,
            "mae_cycles": result.metrics.mae,
            "rmse_cycles": result.metrics.rmse,
            "predictions": rows,
        },
    }
    manifest_path = destination / MANIFEST_FILENAME
    _write_hashed_json(payload, manifest_path)

    metrics = build_metrics_record(
        model_name="decision-tree-rul",
        model_version=MODEL_VERSION,
        partition="FD001/train",
        sample_unit="engine",
        sample_count=result.metrics.engine_count,
        feature_config=asdict(fitting.config),
        random_seed=result.random_seed,
        parameters={
            "max_depth": result.max_depth,
            "min_samples_leaf": result.min_samples_leaf,
            "fitting_row_count": len(fitting.rows),
            "fitting_engine_count": len({row.vector.engine_key for row in fitting.rows}),
        },
        mae_cycles=result.metrics.mae,
        rmse_cycles=result.metrics.rmse,
        runtime_seconds=result.runtime_seconds,
        input_hashes={
            "training_source_sha256": fitting.source_sha256,
            "split_manifest_sha256": fitting.split_manifest_sha256,
            "fitting_dataset_sha256": fitting_dataset_sha256,
            "validation_dataset_sha256": validation_dataset_sha256,
        },
    )
    metrics_path = destination / METRICS_FILENAME
    save_metrics_record(metrics, metrics_path)
    return {
        "model_path": model_path,
        "manifest_path": manifest_path,
        "metrics_path": metrics_path,
        "model_sha256": model_sha256,
        "metrics": metrics,
    }


def verify_decision_tree_artifact(
    manifest_path: str | Path,
    validation: FeatureDataset,
) -> dict[str, Any]:
    """Verify hashes/provenance, reload the model, and reproduce every score."""
    document = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    payload = document["payload"]
    if document["sha256"] != hashlib.sha256(_canonical(payload)).hexdigest():
        raise ValueError("Tree manifest content hash mismatch.")
    if payload.get("schema_version") != TREE_ARTIFACT_SCHEMA:
        raise ValueError("Unsupported Decision Tree artifact schema.")
    model_info = payload["model"]
    if model_info.get("version") != MODEL_VERSION:
        raise ValueError("Unsupported Decision Tree model version.")
    if model_info.get("scikit_learn_version") != sklearn.__version__:
        raise ValueError("Saved scikit-learn version does not match the current runtime.")
    model_path = Path(manifest_path).parent / model_info["filename"]
    if sha256_file(model_path) != model_info["sha256"]:
        raise ValueError("Saved model file hash mismatch.")
    training = payload["training"]
    if (
        validation.role != "validation"
        or validation.source_sha256 != training["source_sha256"]
        or validation.split_manifest_sha256 != training["split_manifest_sha256"]
        or list(validation.feature_names) != training["feature_names"]
        or json.loads(_canonical(asdict(validation.config))) != training["feature_config"]
    ):
        raise ValueError("Validation dataset does not match the saved model provenance/schema.")

    model = joblib.load(model_path)
    if not isinstance(model, DecisionTreeRegressor):
        raise TypeError("Saved model is not a DecisionTreeRegressor.")
    if model.n_features_in_ != len(training["feature_names"]):
        raise ValueError("Saved model feature count does not match its manifest.")
    predicted = model.predict(validation.X)
    saved_rows = payload["evaluation"]["predictions"]
    if len(saved_rows) != len(validation.rows):
        raise ValueError("Saved prediction count does not match validation rows.")
    replayed: list[ValidationPrediction] = []
    for row, actual_prediction, saved in zip(validation.rows, predicted, saved_rows, strict=True):
        expected_identity = {
            "dataset_partition": row.vector.dataset_partition,
            "unit_id": row.vector.unit_id,
            "cutoff_cycle": row.vector.selected_cycle,
            "true_rul_cycles": row.true_rul,
        }
        if any(saved.get(key) != value for key, value in expected_identity.items()):
            raise ValueError("Saved prediction row identity/label differs from the validation table.")
        if float(actual_prediction) != saved["prediction_cycles"]:
            raise ValueError("Fresh-process model prediction differs from the saved output.")
        replayed.append(
            ValidationPrediction(
                dataset_partition=row.vector.dataset_partition,
                unit_id=row.vector.unit_id,
                cutoff_cycle=row.vector.selected_cycle,
                prediction=float(actual_prediction),
                true_rul=row.true_rul,
            )
        )
    metrics = calculate_validation_metrics(replayed)
    evaluation = payload["evaluation"]
    for metric_row, saved in zip(metrics.per_engine, saved_rows, strict=True):
        if (
            saved["absolute_error_cycles"] != metric_row.absolute_error
            or saved["squared_error_cycles"] != metric_row.squared_error
        ):
            raise ValueError("Saved per-engine errors do not match predictions and labels.")
    if not isclose(metrics.mae, evaluation["mae_cycles"], rel_tol=0, abs_tol=1e-12):
        raise ValueError("Saved MAE does not match the per-engine predictions.")
    if not isclose(metrics.rmse, evaluation["rmse_cycles"], rel_tol=0, abs_tol=1e-12):
        raise ValueError("Saved RMSE does not match the per-engine predictions.")
    metrics_path = Path(manifest_path).parent / METRICS_FILENAME
    saved_metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    validate_metrics_record(saved_metrics)
    if (
        saved_metrics["evaluation"]["metrics"]["mae_cycles"] != metrics.mae
        or saved_metrics["evaluation"]["metrics"]["rmse_cycles"] != metrics.rmse
        or saved_metrics["evaluation"]["sample_count"] != metrics.engine_count
    ):
        raise ValueError("Common metrics record does not match the saved predictions.")
    return {"prediction_count": len(saved_rows), "mae_cycles": metrics.mae, "rmse_cycles": metrics.rmse}


def _write_hashed_json(payload: dict[str, Any], path: Path) -> None:
    digest = hashlib.sha256(_canonical(payload)).hexdigest()
    path.write_text(
        json.dumps({"payload": payload, "sha256": digest}, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
