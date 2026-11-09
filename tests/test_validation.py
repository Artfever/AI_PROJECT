"""Development prefix evaluation using deliberately synthetic histories."""

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.evaluation import ValidationPrediction, evaluate_validation_prefix


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
        dataset_partition="train",
        unit_id=17,
        cutoff_cycle=4,
        predictor=predictor,
    )

    assert [row["cycle"] for row in received[0]] == [1, 2, 3, 4]
    assert all("full_lifetime" not in row for row in received[0])
    assert result == ValidationPrediction("train", 17, 4, 3.5, 2)
    assert result.engine_key == ("train", 17)
    assert history == original


def test_predictor_mutation_cannot_change_the_source_history():
    history = [_row(2, cycle) for cycle in range(1, 5)]
    original = [row.copy() for row in history]

    def mutating_predictor(prefix):
        prefix[0]["sensor_1"] = -1
        return 1

    evaluate_validation_prefix(
        history,
        dataset_partition="train",
        unit_id=2,
        cutoff_cycle=2,
        predictor=mutating_predictor,
    )

    assert history == original


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"dataset_partition": "test"}, "train partition"),
        ({"cutoff_cycle": 4}, "before the engine's terminal cycle"),
        ({"cutoff_cycle": 3}, "observed cycle"),
        ({"unit_id": 99}, "requested unit_id"),
    ],
)
def test_invalid_partition_or_prefix_metadata_is_rejected(kwargs, message):
    cycles = (1, 2, 4) if kwargs.get("cutoff_cycle") == 3 else range(1, 5)
    history = [_row(2, cycle) for cycle in cycles]
    args = {
        "dataset_partition": "train",
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
            dataset_partition="train",
            unit_id=2,
            cutoff_cycle=2,
            predictor=lambda prefix: prediction,
        )
