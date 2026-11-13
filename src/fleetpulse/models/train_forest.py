"""One bounded, fixed-seed Random Forest under the existing FD001 protocol."""

from dataclasses import dataclass
from time import perf_counter

from sklearn.ensemble import RandomForestRegressor

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

MODEL_VERSION = "random-forest-rul-v1"
DEFAULT_RANDOM_SEED = 42
DEFAULT_N_ESTIMATORS = 100
DEFAULT_MAX_DEPTH = 12
DEFAULT_MIN_SAMPLES_LEAF = 5


@dataclass(frozen=True)
class RandomForestValidationResult:
    model: RandomForestRegressor
    metrics: ValidationMetrics
    predictions: tuple[ValidationPrediction, ...]
    feature_names: tuple[str, ...]
    random_seed: int
    parameters: dict[str, object]
    runtime_seconds: float


def train_random_forest(
    fitting: FeatureDataset,
    validation: FeatureDataset,
    *,
    random_seed: int = DEFAULT_RANDOM_SEED,
    n_estimators: int = DEFAULT_N_ESTIMATORS,
    max_depth: int = DEFAULT_MAX_DEPTH,
    min_samples_leaf: int = DEFAULT_MIN_SAMPLES_LEAF,
) -> RandomForestValidationResult:
    """Fit fitting X/y only; predict once per unchanged saved validation prefix.

    No feature extraction, split/cutoff selection, preprocessing or search is
    performed here. One CPU worker and fixed max_features/bootstrapping policy
    bound the initial candidate. Runtime covers fit plus batch prediction.
    """
    validate_training_datasets(fitting, validation)
    validate_integer_parameter(random_seed, "random_seed", allow_zero=True)
    for name, value in (
        ("n_estimators", n_estimators),
        ("max_depth", max_depth),
        ("min_samples_leaf", min_samples_leaf),
    ):
        validate_integer_parameter(value, name)
    parameters = {
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "min_samples_leaf": min_samples_leaf,
        "max_features": 1.0,
        "bootstrap": True,
        "n_jobs": 1,
    }
    model = RandomForestRegressor(random_state=random_seed, **parameters)
    started = perf_counter()
    model.fit(fitting.X, fitting.y)
    values = model.predict(validation.X)
    runtime = perf_counter() - started
    predictions = tuple(
        ValidationPrediction(
            row.vector.dataset_partition,
            row.vector.unit_id,
            row.vector.selected_cycle,
            float(value),
            row.true_rul,
        )
        for row, value in zip(validation.rows, values, strict=True)
    )
    return RandomForestValidationResult(
        model,
        calculate_validation_metrics(predictions),
        predictions,
        fitting.feature_names,
        random_seed,
        parameters,
        runtime,
    )
