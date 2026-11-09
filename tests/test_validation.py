"""Development prefix evaluation using deliberately synthetic histories."""

import hashlib

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.evaluation import (
    ValidationPrediction,
    evaluate_validation_manifest,
    evaluate_validation_prefix,
)


def _row(unit_id: int, cycle: int) -> dict[str, int | float]:
    return {"unit_id": unit_id, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 0.5)}


def test_prediction_sees_only_the_prefix_and_label_uses_full_train_lifetime():
    history = [_row(17, cycle) for cycle in range(1, 7)]
    original = [row.copy() for row in history]
    received = []

    def predictor(prefix):
        received.append(prefix)
        return 3.5

    result = evaluate_validation_prefix(
        history,
        dataset_partition="FD001/train",
        unit_id=17,
        cutoff_cycle=4,
        predictor=predictor,
    )

    assert [row["cycle"] for row in received[0]] == [1, 2, 3, 4]
    assert all("full_lifetime" not in row for row in received[0])
    assert result == ValidationPrediction("FD001/train", 17, 4, 3.5, 2)
    assert result.engine_key == ("FD001/train", 17)
    assert history == original


def test_predictor_mutation_cannot_change_the_source_history():
    history = [_row(2, cycle) for cycle in range(1, 5)]
    original = [row.copy() for row in history]

    def mutating_predictor(prefix):
        prefix[0]["sensor_1"] = -1
        return 1

    evaluate_validation_prefix(
        history,
        dataset_partition="FD001/train",
        unit_id=2,
        cutoff_cycle=2,
        predictor=mutating_predictor,
    )

    assert history == original


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"dataset_partition": "FD001/test"}, "FD001/train"),
        ({"cutoff_cycle": 4}, "before the engine's terminal cycle"),
        ({"cutoff_cycle": 3}, "observed cycle"),
        ({"unit_id": 99}, "requested unit_id"),
    ],
)
def test_invalid_partition_or_prefix_metadata_is_rejected(kwargs, message):
    cycles = (1, 2, 4) if kwargs.get("cutoff_cycle") == 3 else range(1, 5)
    history = [_row(2, cycle) for cycle in cycles]
    args = {
        "dataset_partition": "FD001/train",
        "unit_id": 2,
        "cutoff_cycle": 2,
        "predictor": lambda prefix: 1,
    }
    args.update(kwargs)

    with pytest.raises(ValueError, match=message):
        evaluate_validation_prefix(history, **args)


@pytest.mark.parametrize("prediction", [True, float("nan"), float("inf"), "2"])
def test_non_numeric_or_non_finite_predictions_are_rejected(prediction):
    history = [_row(2, cycle) for cycle in range(1, 5)]

    with pytest.raises((TypeError, ValueError), match="numeric RUL estimate"):
        evaluate_validation_prefix(
            history,
            dataset_partition="FD001/train",
            unit_id=2,
            cutoff_cycle=2,
            predictor=lambda prefix: prediction,
        )


def test_manifest_evaluator_uses_only_manifest_prefix_and_scores_label():
    history = [_row(1, cycle) for cycle in range(1, 5)] + [
        _row(2, cycle) for cycle in range(1, 6)
    ]
    source_sha256 = hashlib.sha256(b"synthetic FD001 training source").hexdigest()
    manifest = {
        "schema_version": 1,
        "source": {
            "dataset_partition": "FD001/train",
            "path": "synthetic/train_FD001.txt",
            "sha256": source_sha256,
            "row_count": len(history),
            "engine_count": 2,
        },
        "fitting_engines": [{"dataset_partition": "FD001/train", "unit_id": 1}],
        "validation_prefixes": [
            {
                "dataset_partition": "FD001/train",
                "unit_id": 2,
                "cutoff_cycle": 3,
                "prefix_row_count": 3,
                "full_lifetime": 5,
                "target_rul": 2,
            }
        ],
    }
    received = []

    predictions = evaluate_validation_manifest(
        history,
        manifest=manifest,
        source_sha256=source_sha256,
        predictor=lambda prefix: received.append(prefix) or 2.5,
    )

    assert len(predictions) == 1
    assert predictions[0] == ValidationPrediction("FD001/train", 2, 3, 2.5, 2)
    assert [row["cycle"] for row in received[0]] == [1, 2, 3]
    assert {row["unit_id"] for row in received[0]} == {2}


def test_manifest_source_mismatch_is_rejected_before_prediction():
    history = [_row(1, cycle) for cycle in range(1, 3)] + [
        _row(2, cycle) for cycle in range(1, 4)
    ]
    manifest = {
        "schema_version": 1,
        "source": {
            "dataset_partition": "FD001/train",
            "sha256": "a" * 64,
            "row_count": 5,
            "engine_count": 2,
        },
        "fitting_engines": [{"dataset_partition": "FD001/train", "unit_id": 1}],
        "validation_prefixes": [
            {
                "dataset_partition": "FD001/train",
                "unit_id": 2,
                "cutoff_cycle": 2,
                "prefix_row_count": 2,
                "full_lifetime": 3,
                "target_rul": 1,
            }
        ],
    }
    called = False

    def predictor(prefix):
        nonlocal called
        called = True
        return 1

    with pytest.raises(ValueError, match="SHA-256"):
        evaluate_validation_manifest(
            history,
            manifest=manifest,
            source_sha256="b" * 64,
            predictor=predictor,
        )

    assert not called
