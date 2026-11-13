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
from fleetpulse.models.training_validation import (
    validate_integer_parameter,
    validate_training_datasets,
)

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
    validate_training_datasets(fitting, validation)
    validate_integer_parameter(random_seed, "random_seed", allow_zero=True)
    validate_integer_parameter(max_depth, "max_depth")
    validate_integer_parameter(min_samples_leaf, "min_samples_leaf")

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
