"""Contract checks for common model-validation metrics JSON."""

import json

import pytest

from fleetpulse.evaluation import (
    METRICS_SCHEMA_VERSION,
    build_metrics_record,
    save_metrics_record,
    validate_metrics_record,
)


def make_record():
    return build_metrics_record(
        model_name="example-rul-model",
        model_version="model-v2",
        partition="FD001/train",
        sample_unit="engine",
        sample_count=20,
        feature_config={"version": "past-only-v1", "window_cycles": 30},
        random_seed=None,
        parameters={"regularization": 0.25},
        mae_cycles=4.5,
        rmse_cycles=6.0,
        runtime_seconds=0.125,
        input_hashes={"validation": "a" * 64},
    )


def test_metrics_record_is_model_neutral_and_round_trips(tmp_path):
    record = make_record()
    path = tmp_path / "metrics.json"

    save_metrics_record(record, path)

    loaded = json.loads(path.read_text(encoding="utf-8"))
    validate_metrics_record(loaded)
    assert loaded == record
    assert loaded["schema_version"] == METRICS_SCHEMA_VERSION
    assert loaded["model"] == {"name": "example-rul-model", "version": "model-v2"}
    assert loaded["evaluation"]["sample_unit"] == "engine"


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda row: row.update(schema_version="metrics-v2"), "unsupported schema"),
        (lambda row: row["evaluation"].update(sample_count=True), "positive integer"),
        (lambda row: row["evaluation"].update(runtime_seconds=float("nan")), "runtime_seconds"),
        (lambda row: row["evaluation"]["input_hashes"].update(validation="bad"), "SHA-256"),
    ],
)
def test_metrics_record_rejects_invalid_version_or_measurements(change, message):
    record = make_record()
    change(record)

    with pytest.raises(ValueError, match=message):
        validate_metrics_record(record)
