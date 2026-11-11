"""Past-only numeric features from one dataset-qualified engine history."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from numbers import Integral, Real

from fleetpulse.features.config import FeatureConfig

HistoryRow = Mapping[str, object]


@dataclass(frozen=True)
class EngineFeatureVector:
    """Ordered features plus the identity and cutoff metadata used to create them."""

    dataset_partition: str
    unit_id: int
    selected_cycle: int
    observed_row_count: int
    window_row_count: int
    config: FeatureConfig
    values: tuple[float, ...]

    @property
    def engine_key(self) -> tuple[str, int]:
        """Return an engine identity that is unique across dataset partitions."""
        return self.dataset_partition, self.unit_id

    def as_dict(self) -> dict[str, float]:
        """Return feature values keyed in the configuration's authoritative order."""
        return dict(zip(self.config.output_schema, self.values, strict=True))


def engineer_features(
    history: Iterable[HistoryRow],
    *,
    dataset_partition: str,
    unit_id: int,
    selected_cycle: int | None = None,
    config: FeatureConfig | None = None,
) -> EngineFeatureVector:
    """Calculate latest, mean, population std, and actual-cycle slope per channel.

    The input must contain records for one engine. If ``selected_cycle`` is
    omitted, the greatest observed cycle is selected. Rows after an explicit
    cutoff are ignored for feature values and visible-row metadata. The window
    is the inclusive cycle interval ``[selected_cycle - window_cycles + 1,
    selected_cycle]``; gaps are not filled or used to reach farther back.
    """
    if not isinstance(dataset_partition, str) or not dataset_partition.strip():
        raise ValueError("dataset_partition must be a nonempty string.")
    requested_unit = _positive_integer(unit_id, "unit_id")
    feature_config = config if config is not None else FeatureConfig()
    if not isinstance(feature_config, FeatureConfig):
        raise TypeError("config must be a FeatureConfig.")

    rows = tuple(history)
    if not rows:
        raise ValueError("At least one engine-history row is required.")

    cycles: set[int] = set()
    rows_by_cycle: dict[int, HistoryRow] = {}
    for row_number, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            raise TypeError(f"History row {row_number} must be a mapping.")
        row_unit = _positive_integer(row.get("unit_id"), f"row {row_number} unit_id")
        if row_unit != requested_unit:
            raise ValueError("History must contain only the requested unit_id.")
        cycle = _positive_integer(row.get("cycle"), f"row {row_number} cycle")
        if cycle in cycles:
            raise ValueError(f"Duplicate cycle {cycle} for engine {requested_unit}.")
        cycles.add(cycle)
        rows_by_cycle[cycle] = row

    cutoff = max(cycles) if selected_cycle is None else _positive_integer(
        selected_cycle, "selected_cycle"
    )
    if cutoff not in cycles:
        raise ValueError("selected_cycle must identify an observed cycle in the history.")

    visible_cycles = sorted(cycle for cycle in cycles if cycle <= cutoff)
    first_window_cycle = cutoff - feature_config.window_cycles + 1
    window_cycles = [
        cycle for cycle in visible_cycles if cycle >= first_window_cycle
    ]
    values: list[float] = []
    try:
        x_mean = math.fsum(window_cycles) / len(window_cycles)
        x_deltas = [cycle - x_mean for cycle in window_cycles]
        x_variance_sum = math.fsum(delta * delta for delta in x_deltas)
    except (OverflowError, ValueError) as error:
        raise ValueError("Could not calculate finite features for the cycle window.") from error
    if not math.isfinite(x_mean) or not math.isfinite(x_variance_sum):
        raise ValueError("Could not calculate finite features for the cycle window.")

    for channel in feature_config.channels:
        readings = [
            _finite_reading(rows_by_cycle[cycle].get(channel), channel, cycle)
            for cycle in window_cycles
        ]
        try:
            mean = math.fsum(readings) / len(readings)
            deviations = [reading - mean for reading in readings]
            if not math.isfinite(mean) or not all(map(math.isfinite, deviations)):
                raise ValueError("non-finite centered readings")
            population_std = math.sqrt(
                math.fsum(delta * delta for delta in deviations) / len(readings)
            )
            slope = (
                math.fsum(
                    x_delta * y_delta
                    for x_delta, y_delta in zip(x_deltas, deviations, strict=True)
                )
                / x_variance_sum
                if x_variance_sum
                else 0.0
            )
        except (OverflowError, ValueError) as error:
            raise ValueError(f"Could not calculate finite features for {channel}.") from error
        latest = readings[-1]
        channel_features = (latest, mean, population_std, slope)
        if not all(math.isfinite(value) for value in channel_features):
            raise ValueError(f"Could not calculate finite features for {channel}.")
        values.extend(channel_features)

    return EngineFeatureVector(
        dataset_partition=dataset_partition,
        unit_id=requested_unit,
        selected_cycle=cutoff,
        observed_row_count=len(visible_cycles),
        window_row_count=len(window_cycles),
        config=feature_config,
        values=tuple(values),
    )


def _positive_integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        raise ValueError(f"{name} must be a positive integer.")
    return int(value)


def _finite_reading(value: object, channel: str, cycle: int) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{channel} at cycle {cycle} must be numeric.")
    try:
        reading = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f"{channel} at cycle {cycle} must be finite.") from error
    if not math.isfinite(reading):
        raise ValueError(f"{channel} at cycle {cycle} must be finite.")
    return reading
