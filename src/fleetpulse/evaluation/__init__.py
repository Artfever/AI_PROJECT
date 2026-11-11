"""Leakage-safe model evaluation utilities."""

from fleetpulse.evaluation.constant_baseline_validation import (
    ConstantBaselineValidationResult,
    score_constant_baseline,
)
from fleetpulse.evaluation.metrics import (
    ValidationErrorRow,
    ValidationMetrics,
    calculate_validation_metrics,
)
from fleetpulse.evaluation.metrics_artifact import (
    METRICS_SCHEMA_VERSION,
    build_metrics_record,
    save_metrics_record,
    validate_metrics_record,
)
from fleetpulse.evaluation.validation import (
    ValidationPrediction,
    evaluate_validation_manifest,
    evaluate_validation_prefix,
)

__all__ = [
    "METRICS_SCHEMA_VERSION",
    "ConstantBaselineValidationResult",
    "ValidationErrorRow",
    "ValidationMetrics",
    "ValidationPrediction",
    "build_metrics_record",
    "calculate_validation_metrics",
    "evaluate_validation_manifest",
    "evaluate_validation_prefix",
    "save_metrics_record",
    "score_constant_baseline",
    "validate_metrics_record",
]
