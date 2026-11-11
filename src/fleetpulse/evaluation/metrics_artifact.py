"""Versioned common JSON record for one model's validation metrics."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

METRICS_SCHEMA_VERSION = "metrics-v1"
_HASH_PATTERN = re.compile(r"[a-f0-9]{64}")


def build_metrics_record(
    *,
    model_name: str,
    model_version: str,
    partition: str,
    sample_unit: str,
    sample_count: int,
    feature_config: Mapping[str, Any],
    random_seed: int | None,
    parameters: Mapping[str, Any],
    mae_cycles: float,
    rmse_cycles: float,
    runtime_seconds: float,
    input_hashes: Mapping[str, str],
) -> dict[str, Any]:
    """Build a JSON-ready, model-neutral RUL validation record."""
    record = {
        "schema_version": METRICS_SCHEMA_VERSION,
        "model": {"name": model_name, "version": model_version},
        "evaluation": {
            "partition": partition,
            "sample_unit": sample_unit,
            "sample_count": sample_count,
            "feature_config": dict(feature_config),
            "random_seed": random_seed,
            "parameters": dict(parameters),
            "metrics": {"mae_cycles": mae_cycles, "rmse_cycles": rmse_cycles},
            "runtime_seconds": runtime_seconds,
            "input_hashes": dict(input_hashes),
        },
    }
    try:
        json_ready = json.loads(json.dumps(record, sort_keys=True, allow_nan=False))
    except (TypeError, ValueError) as error:
        raise ValueError("Invalid metrics record: values must be finite JSON data.") from error
    validate_metrics_record(json_ready)
    return json_ready


def validate_metrics_record(record: Mapping[str, Any]) -> None:
    """Reject unsupported, incomplete, or non-JSON metrics records."""
    _require(set(record) == {"schema_version", "model", "evaluation"}, "unexpected top-level fields")
    _require(record["schema_version"] == METRICS_SCHEMA_VERSION, "unsupported schema version")

    model = record["model"]
    _require(isinstance(model, Mapping), "model must be an object")
    _require(set(model) == {"name", "version"}, "model needs name and version")
    _nonempty_string(model["name"], "model.name")
    _nonempty_string(model["version"], "model.version")

    evaluation = record["evaluation"]
    _require(isinstance(evaluation, Mapping), "evaluation must be an object")
    expected_fields = {
        "partition",
        "sample_unit",
        "sample_count",
        "feature_config",
        "random_seed",
        "parameters",
        "metrics",
        "runtime_seconds",
        "input_hashes",
    }
    _require(set(evaluation) == expected_fields, "evaluation fields do not match metrics-v1")
    _nonempty_string(evaluation["partition"], "evaluation.partition")
    _nonempty_string(evaluation["sample_unit"], "evaluation.sample_unit")
    _require(type(evaluation["sample_count"]) is int and evaluation["sample_count"] > 0,
             "sample_count must be a positive integer")
    _require(isinstance(evaluation["feature_config"], Mapping), "feature_config must be an object")
    _json_object(evaluation["feature_config"], "feature_config")
    seed = evaluation["random_seed"]
    _require(seed is None or (type(seed) is int and seed >= 0), "random_seed must be null or nonnegative")
    _require(isinstance(evaluation["parameters"], Mapping), "parameters must be an object")
    _json_object(evaluation["parameters"], "parameters")

    metrics = evaluation["metrics"]
    _require(isinstance(metrics, Mapping), "metrics must be an object")
    _require(set(metrics) == {"mae_cycles", "rmse_cycles"}, "metrics-v1 requires MAE and RMSE in cycles")
    _finite_nonnegative(metrics["mae_cycles"], "mae_cycles")
    _finite_nonnegative(metrics["rmse_cycles"], "rmse_cycles")
    _finite_nonnegative(evaluation["runtime_seconds"], "runtime_seconds")

    hashes = evaluation["input_hashes"]
    _require(isinstance(hashes, Mapping) and bool(hashes), "input_hashes must be a nonempty object")
    _require(
        all(isinstance(key, str) and key and isinstance(value, str) and _HASH_PATTERN.fullmatch(value)
            for key, value in hashes.items()),
        "input_hashes values must be lowercase SHA-256 hex digests",
    )
    _json_object(record, "record")


def save_metrics_record(record: Mapping[str, Any], path: str | Path) -> None:
    """Validate and write a deterministic UTF-8 JSON record with a trailing LF."""
    validate_metrics_record(record)
    Path(path).write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _json_object(value: Mapping[str, Any], name: str) -> None:
    try:
        json.dumps(value, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must contain only finite JSON values") from error


def _nonempty_string(value: Any, name: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{name} must be a nonempty string")


def _finite_nonnegative(value: Any, name: str) -> None:
    _require(
        type(value) in (int, float) and math.isfinite(value) and value >= 0,
        f"{name} must be a finite nonnegative number",
    )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"Invalid metrics record: {message}.")
