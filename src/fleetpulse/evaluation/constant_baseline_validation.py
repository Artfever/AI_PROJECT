"""Score the selected constant baseline on saved validation feature rows."""

from dataclasses import dataclass
from typing import Literal

from fleetpulse.evaluation.metrics import ValidationMetrics, calculate_validation_metrics
from fleetpulse.evaluation.validation import ValidationPrediction
from fleetpulse.features.build_dataset import FeatureDataset
from fleetpulse.models.constant_baseline import ConstantRULBaseline


@dataclass(frozen=True)
class ConstantBaselineValidationResult:
    """The fitting-only model and its one-prediction-per-engine validation scores."""

    baseline: ConstantRULBaseline
    metrics: ValidationMetrics


def score_constant_baseline(
    fitting_dataset: FeatureDataset,
    validation_dataset: FeatureDataset,
    *,
    statistic: Literal["mean", "median"] = "mean",
) -> ConstantBaselineValidationResult:
    """Fit from fitting labels, then score the saved validation rows by engine.

    Validation feature values are checked for compatible provenance but are not
    passed to the constant predictor. Validation labels are used only by the
    metric calculator after predictions have been created.
    """
    if fitting_dataset.role != "fitting":
        raise ValueError("The first dataset must have role='fitting'.")
    if validation_dataset.role != "validation":
        raise ValueError("The second dataset must have role='validation'.")
    if not fitting_dataset.rows or not validation_dataset.rows:
        raise ValueError("Fitting and validation datasets must both contain rows.")
    if fitting_dataset.config != validation_dataset.config:
        raise ValueError("Fitting and validation feature configs must match.")
    if (
        fitting_dataset.source_sha256 != validation_dataset.source_sha256
        or fitting_dataset.split_manifest_sha256 != validation_dataset.split_manifest_sha256
    ):
        raise ValueError("Fitting and validation datasets must share source and split provenance.")

    fitting_engines = {row.vector.engine_key for row in fitting_dataset.rows}
    validation_engines = {row.vector.engine_key for row in validation_dataset.rows}
    if fitting_engines & validation_engines:
        raise ValueError("Fitting and validation datasets must contain disjoint engines.")
    if len(validation_engines) != len(validation_dataset.rows):
        raise ValueError("Validation dataset must contain exactly one row per engine.")

    baseline = ConstantRULBaseline.fit(fitting_dataset.y, statistic=statistic)
    predictions = baseline.predict(sample_count=len(validation_dataset.rows))
    scored_rows = tuple(
        ValidationPrediction(
            dataset_partition=row.vector.dataset_partition,
            unit_id=row.vector.unit_id,
            cutoff_cycle=row.vector.selected_cycle,
            prediction=prediction,
            true_rul=row.true_rul,
        )
        for row, prediction in zip(validation_dataset.rows, predictions, strict=True)
    )
    metrics = calculate_validation_metrics(scored_rows)
    return ConstantBaselineValidationResult(baseline=baseline, metrics=metrics)
