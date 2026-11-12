"""Deterministic constant RUL baseline fitted from fitting labels only."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from numbers import Real
from statistics import fmean, median
from typing import Literal

BaselineStatistic = Literal["mean", "median"]
ARTIFACT_VERSION = "constant-rul-v1"
TARGET_NAME = "rul_cycles"


@dataclass(frozen=True)
class ConstantRULBaseline:
    """A fixed RUL prediction derived from one declared fitting-label statistic.

    Features and validation labels are not accepted by ``fit``. The caller is
    responsible for supplying only labels from the fitting partition selected
    by the saved split manifest.
    """

    statistic: BaselineStatistic
    value_cycles: float
    fitting_label_count: int
    artifact_version: str = ARTIFACT_VERSION
    target_name: str = TARGET_NAME
    random_seed: None = None

    def __post_init__(self) -> None:
        if self.statistic not in ("mean", "median"):
            raise ValueError("statistic must be 'mean' or 'median'.")
        if not math.isfinite(self.value_cycles) or self.value_cycles < 0:
            raise ValueError("value_cycles must be a finite, nonnegative RUL value.")
        if (
            isinstance(self.fitting_label_count, bool)
            or not isinstance(self.fitting_label_count, int)
            or self.fitting_label_count < 1
        ):
            raise ValueError("fitting_label_count must be a positive integer.")
        if self.artifact_version != ARTIFACT_VERSION:
            raise ValueError(f"Only artifact version {ARTIFACT_VERSION!r} is supported.")
        if self.target_name != TARGET_NAME:
            raise ValueError(f"target_name must be {TARGET_NAME!r}.")
        if self.random_seed is not None:
            raise ValueError("The constant baseline is deterministic and has no random seed.")

    @classmethod
    def fit(
        cls,
        fitting_rul_cycles: Iterable[Real],
        *,
        statistic: BaselineStatistic,
    ) -> ConstantRULBaseline:
        """Fit the explicitly selected statistic using only supplied fitting labels."""
        if statistic not in ("mean", "median"):
            raise ValueError("statistic must be 'mean' or 'median'.")
        labels = tuple(_nonnegative_label(label, index) for index, label in enumerate(
            fitting_rul_cycles, start=1
        ))
        if not labels:
            raise ValueError("At least one fitting RUL label is required.")

        value = fmean(labels) if statistic == "mean" else median(labels)
        if not math.isfinite(value):
            raise ValueError("The fitted RUL statistic must be finite.")
        return cls(
            statistic=statistic,
            value_cycles=value,
            fitting_label_count=len(labels),
        )

    def predict(self, *, sample_count: int) -> tuple[float, ...]:
        """Return one constant prediction per requested feature row.

        The method accepts only a row count, so feature values and scoring
        labels cannot influence this baseline's predictions.
        """
        if isinstance(sample_count, bool) or not isinstance(sample_count, int):
            raise TypeError("sample_count must be a nonnegative integer.")
        if sample_count < 0:
            raise ValueError("sample_count must be a nonnegative integer.")
        return (self.value_cycles,) * sample_count

    def to_artifact(self) -> dict[str, str | int | float | None]:
        """Return the complete deterministic model state in a JSON-ready mapping."""
        return {
            "artifact_version": self.artifact_version,
            "statistic": self.statistic,
            "value_cycles": self.value_cycles,
            "target_name": self.target_name,
            "fitting_label_count": self.fitting_label_count,
            "random_seed": self.random_seed,
        }

    @classmethod
    def from_artifact(cls, artifact: Mapping[str, object]) -> ConstantRULBaseline:
        """Restore a baseline artifact and validate its versioned schema."""
        expected_fields = {
            "artifact_version",
            "statistic",
            "value_cycles",
            "target_name",
            "fitting_label_count",
            "random_seed",
        }
        if set(artifact) != expected_fields:
            raise ValueError("Baseline artifact fields do not match the supported schema.")

        return cls(
            statistic=artifact["statistic"],  # type: ignore[arg-type]
            value_cycles=_nonnegative_label(artifact["value_cycles"], 0),
            fitting_label_count=artifact["fitting_label_count"],  # type: ignore[arg-type]
            artifact_version=artifact["artifact_version"],  # type: ignore[arg-type]
            target_name=artifact["target_name"],  # type: ignore[arg-type]
            random_seed=artifact["random_seed"],  # type: ignore[arg-type]
        )


def _nonnegative_label(value: object, index: int) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"Fitting RUL label {index} must be numeric.")
    try:
        label = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f"Fitting RUL label {index} must be finite.") from error
    if not math.isfinite(label):
        raise ValueError(f"Fitting RUL label {index} must be finite.")
    if label < 0:
        raise ValueError(f"Fitting RUL label {index} must be nonnegative.")
    return label
