"""Summarize normalized FD001 histories without hiding quality warnings."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from fleetpulse.data.quality import (
    SENSOR_COLUMNS,
    QualityReport,
    validate_engine_history,
)


@dataclass(frozen=True)
class EngineCoverage:
    """Observed row count and cycle range for one engine."""

    engine_id: int
    row_count: int
    first_cycle: int
    last_cycle: int


@dataclass(frozen=True)
class DatasetSummary:
    """Counts and population variances derived from supplied records only."""

    row_count: int
    engine_count: int
    engines: tuple[EngineCoverage, ...]
    sensor_population_variance: dict[str, float]
    constant_sensors: tuple[str, ...]
    quality: QualityReport


def summarize_engine_history(
    records: Iterable[Mapping[str, object]],
) -> DatasetSummary:
    """Count records/engines, cycle ranges, and per-sensor population variance.

    The input is validated before summarizing. Invalid rows are never skipped;
    instead a ``ValueError`` lists the finding codes to keep the source visible
    for review. Cycle-gap warnings remain attached to the returned summary.
    Variance uses population variance (ddof=0). Constant sensors are reported
    only for exactly zero variance; this function sets no "barely changes"
    threshold.
    """

    rows = tuple(records)
    quality = validate_engine_history(rows)
    if not quality.is_valid:
        codes = ", ".join(sorted({finding.code for finding in quality.errors}))
        raise ValueError(f"Cannot summarize invalid engine history: {codes}.")

    counts = {field: 0 for field in SENSOR_COLUMNS}
    means = {field: 0.0 for field in SENSOR_COLUMNS}
    sums_of_squares = {field: 0.0 for field in SENSOR_COLUMNS}
    coverage: dict[int, list[int]] = {}

    for row in rows:
        engine_id = int(row["unit_id"])
        cycle = int(row["cycle"])
        engine = coverage.setdefault(engine_id, [0, cycle, cycle])
        engine[0] += 1
        engine[1] = min(engine[1], cycle)
        engine[2] = max(engine[2], cycle)

        for field in SENSOR_COLUMNS:
            try:
                value = float(row[field])
            except OverflowError as error:
                raise ValueError(
                    f"Cannot represent {field} values as finite numbers."
                ) from error
            count = counts[field] + 1
            delta = value - means[field]
            mean = means[field] + delta / count
            sums_of_squares[field] += delta * (value - mean)
            means[field] = mean
            counts[field] = count

    sensor_variance = {
        field: sums_of_squares[field] / counts[field]
        for field in SENSOR_COLUMNS
    }
    if any(not math.isfinite(value) for value in sensor_variance.values()):
        raise ValueError("Cannot represent one or more sensor variances as finite numbers.")

    engines = tuple(
        EngineCoverage(
            engine_id=engine_id,
            row_count=values[0],
            first_cycle=values[1],
            last_cycle=values[2],
        )
        for engine_id, values in sorted(coverage.items())
    )
    constant_sensors = tuple(
        field for field, variance in sensor_variance.items() if variance == 0.0
    )
    return DatasetSummary(
        row_count=len(rows),
        engine_count=len(engines),
        engines=engines,
        sensor_population_variance=sensor_variance,
        constant_sensors=constant_sensors,
        quality=quality,
    )
