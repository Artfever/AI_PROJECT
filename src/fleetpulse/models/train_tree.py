"""Reproducible Decision Tree training and development validation."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from sklearn.tree import DecisionTreeRegressor

from fleetpulse.evaluation import (
    ValidationMetrics,
    ValidationPrediction,
    calculate_validation_metrics,
)
from fleetpulse.features.build_dataset import FeatureDataset

MODEL_VERSION = "decision-tree-rul-v1"
DEFAULT_RANDOM_SEED = 42
DEFAULT_MAX_DEPTH = 8
DEFAULT_MIN_SAMPLES_LEAF = 5


@dataclass(frozen=True)
class DecisionTreeValidationResult:
    """Fitted estimator and predictions scored once per held-out engine."""

    model: DecisionTreeRegressor
    metrics: ValidationMetrics
    predictions: tuple[ValidationPrediction, ...]
    feature_names: tuple[str, ...]
    random_seed: int
    max_depth: int
    min_samples_leaf: int
    runtime_seconds: float


def train_decision_tree(
    fitting: FeatureDataset,
    validation: FeatureDataset,
    *,
    random_seed: int = DEFAULT_RANDOM_SEED,
    max_depth: int = DEFAULT_MAX_DEPTH,
    min_samples_leaf: int = DEFAULT_MIN_SAMPLES_LEAF,
) -> DecisionTreeValidationResult:
    """Fit only fitting rows and score the saved validation row for each engine.

    This entry point accepts the common, hash-checked feature-table objects.
    It rejects mismatched provenance and engine overlap before passing numeric
    features to scikit-learn. Validation labels are read only after prediction.
    """
    _validate_datasets(fitting, validation)
    _positive_int(random_seed, "random_seed", allow_zero=True)
    _positive_int(max_depth, "max_depth")
    _positive_int(min_samples_leaf, "min_samples_leaf")

    model = DecisionTreeRegressor(
        random_state=random_seed,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
    )
    started = perf_counter()
    model.fit(fitting.X, fitting.y)
    predicted = model.predict(validation.X)
    runtime_seconds = perf_counter() - started

    predictions = tuple(
        ValidationPrediction(
            dataset_partition=row.vector.dataset_partition,
            unit_id=row.vector.unit_id,
            cutoff_cycle=row.vector.selected_cycle,
            prediction=float(value),
            true_rul=row.true_rul,
        )
        for row, value in zip(validation.rows, predicted, strict=True)
    )
    metrics = calculate_validation_metrics(predictions)
    return DecisionTreeValidationResult(
        model=model,
        metrics=metrics,
        predictions=predictions,
        feature_names=fitting.feature_names,
        random_seed=random_seed,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        runtime_seconds=runtime_seconds,
    )


def _validate_datasets(fitting: FeatureDataset, validation: FeatureDataset) -> None:
    if not isinstance(fitting, FeatureDataset) or not isinstance(validation, FeatureDataset):
        raise TypeError("fitting and validation must be FeatureDataset objects.")
    if fitting.role != "fitting":
        raise ValueError("The training dataset role must be 'fitting'.")
    if validation.role != "validation":
        raise ValueError("The scoring dataset role must be 'validation'.")
    if not fitting.rows or not validation.rows:
        raise ValueError("Fitting and validation datasets must both contain rows.")
    if fitting.config != validation.config or fitting.feature_names != validation.feature_names:
        raise ValueError("Fitting and validation feature schemas must match exactly.")
    if (
        fitting.source_sha256 != validation.source_sha256
        or fitting.split_manifest_sha256 != validation.split_manifest_sha256
    ):
        raise ValueError("Fitting and validation tables must share source and split provenance.")
    fitting_engines = {row.vector.engine_key for row in fitting.rows}
    validation_engines = {row.vector.engine_key for row in validation.rows}
    if fitting_engines & validation_engines:
        raise ValueError("Fitting and validation engine groups must be disjoint.")
    if len(validation_engines) != len(validation.rows):
        raise ValueError("Validation must contain exactly one row per engine.")


def _positive_int(value: int, name: str, *, allow_zero: bool = False) -> None:
    minimum = 0 if allow_zero else 1
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        comparison = "nonnegative" if allow_zero else "positive"
        raise ValueError(f"{name} must be a {comparison} integer.")
