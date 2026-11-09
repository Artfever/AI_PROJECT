"""Hand-checked validation metrics over one row per engine."""

from math import sqrt

import pytest

from fleetpulse.evaluation import ValidationPrediction, calculate_validation_metrics


def _prediction(unit_id: int, true_rul: int, predicted_rul: float) -> ValidationPrediction:
    return ValidationPrediction(
        dataset_partition="FD001/train",
        unit_id=unit_id,
        cutoff_cycle=10,
        prediction=predicted_rul,
        true_rul=true_rul,
    )


def test_metrics_match_the_hand_calculation_and_keep_one_row_per_engine():
    result = calculate_validation_metrics(
        [_prediction(4, true_rul=10, predicted_rul=12), _prediction(5, true_rul=20, predicted_rul=16)]
    )

    assert result.engine_count == 2
    assert result.mae == pytest.approx(3.0)
    assert result.rmse == pytest.approx(sqrt(10))
    assert [row.engine_key for row in result.per_engine] == [
        ("FD001/train", 4),
        ("FD001/train", 5),
    ]
    assert [row.absolute_error for row in result.per_engine] == [2, 4]
    assert [row.squared_error for row in result.per_engine] == [4, 16]


def test_metrics_reject_empty_or_repeated_engine_predictions():
    with pytest.raises(ValueError, match="At least one"):
        calculate_validation_metrics([])

    duplicate = _prediction(4, true_rul=10, predicted_rul=12)
    with pytest.raises(ValueError, match="Duplicate validation prediction"):
        calculate_validation_metrics([duplicate, duplicate])


@pytest.mark.parametrize("bad_prediction", [True, float("nan"), float("inf")])
def test_metrics_reject_invalid_predictions(bad_prediction):
    with pytest.raises((TypeError, ValueError), match="prediction"):
        calculate_validation_metrics([_prediction(4, true_rul=10, predicted_rul=bad_prediction)])
