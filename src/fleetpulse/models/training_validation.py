"""Shared fitting/validation boundary checks for development model trainers."""

from fleetpulse.features.build_dataset import FeatureDataset


def validate_training_datasets(fitting: FeatureDataset, validation: FeatureDataset) -> None:
    """Preserve the P06 trainer's schema/provenance/engine separation rules."""
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


def validate_integer_parameter(value: int, name: str, *, allow_zero: bool = False) -> None:
    minimum = 0 if allow_zero else 1
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        comparison = "nonnegative" if allow_zero else "positive"
        raise ValueError(f"{name} must be a {comparison} integer.")
