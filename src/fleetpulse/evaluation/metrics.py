"""Cycle-based error summaries for one primary validation prediction per engine."""

from collections.abc import Iterable
from dataclasses import dataclass
from math import fsum, isfinite, sqrt
from numbers import Integral, Real

from fleetpulse.evaluation.validation import ValidationPrediction


@dataclass(frozen=True)
class ValidationErrorRow:
    """One engine's contribution to the primary validation metrics."""

    dataset_partition: str
    unit_id: int
    cutoff_cycle: int
    true_rul: int
    prediction: float
    absolute_error: float
    squared_error: float

    @property
    def engine_key(self) -> tuple[str, int]:
        """Return the dataset-qualified identity for this metric row."""
        return self.dataset_partition, self.unit_id


@dataclass(frozen=True)
class ValidationMetrics:
    """Aggregate MAE/RMSE and the per-engine rows used to calculate them."""

    engine_count: int
    mae: float
    rmse: float
    per_engine: tuple[ValidationErrorRow, ...]


def calculate_validation_metrics(
    predictions: Iterable[ValidationPrediction],
) -> ValidationMetrics:
    """Calculate cycle-based MAE and RMSE from one prediction per engine.

    Raises ``ValueError`` for empty input, repeated engine identities, invalid
    RUL metadata, or arithmetic overflow. Predictions may be negative; the
    metrics score the supplied estimate without clipping it.
    """
    values = tuple(predictions)
    if not values:
        raise ValueError("At least one validation prediction is required.")

    seen_engines: set[tuple[str, int]] = set()
    rows: list[ValidationErrorRow] = []
    for prediction in values:
        if not isinstance(prediction, ValidationPrediction):
            raise TypeError("Every item must be a ValidationPrediction.")
        if not isinstance(prediction.dataset_partition, str) or not prediction.dataset_partition:
            raise ValueError("dataset_partition must be a nonempty string.")
        unit_id = _positive_integer(prediction.unit_id, "unit_id")
        cutoff_cycle = _positive_integer(prediction.cutoff_cycle, "cutoff_cycle")
        true_rul = _positive_integer(prediction.true_rul, "true_rul")
        if isinstance(prediction.prediction, bool) or not isinstance(prediction.prediction, Real):
            raise TypeError("prediction must be a numeric RUL estimate.")
        predicted_rul = float(prediction.prediction)
        if not isfinite(predicted_rul):
            raise ValueError("prediction must be finite.")

        engine_key = (prediction.dataset_partition, unit_id)
        if engine_key in seen_engines:
            raise ValueError(f"Duplicate validation prediction for engine {engine_key}.")
        seen_engines.add(engine_key)

        error = predicted_rul - true_rul
        absolute_error = abs(error)
        squared_error = error * error
        if not isfinite(absolute_error) or not isfinite(squared_error):
            raise ValueError("Prediction error is too large to calculate finite metrics.")
        rows.append(
            ValidationErrorRow(
                dataset_partition=prediction.dataset_partition,
                unit_id=unit_id,
                cutoff_cycle=cutoff_cycle,
                true_rul=true_rul,
                prediction=predicted_rul,
                absolute_error=absolute_error,
                squared_error=squared_error,
            )
        )

    count = len(rows)
    mae = fsum(row.absolute_error for row in rows) / count
    rmse = sqrt(fsum(row.squared_error for row in rows) / count)
    if not isfinite(mae) or not isfinite(rmse):
        raise ValueError("Could not calculate finite validation metrics.")
    return ValidationMetrics(engine_count=count, mae=mae, rmse=rmse, per_engine=tuple(rows))


def _positive_integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        raise ValueError(f"{name} must be a positive integer.")
    return int(value)
