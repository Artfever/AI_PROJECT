"""Validate normalized NASA C-MAPSS FD001 engine-history records.

The input contract is an iterable of mappings with the normalized FD001 columns
``unit_id``, ``cycle``, ``setting_1`` through ``setting_3``, and ``sensor_1``
through ``sensor_21``. Values must already be parsed as numbers. Validation
reports findings without modifying, sorting, or dropping any input record.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from numbers import Integral, Real
from typing import Literal

IDENTITY_COLUMNS = ("unit_id", "cycle")
SETTING_COLUMNS = tuple(f"setting_{number}" for number in range(1, 4))
SENSOR_COLUMNS = tuple(f"sensor_{number}" for number in range(1, 22))
READING_COLUMNS = (*SETTING_COLUMNS, *SENSOR_COLUMNS)
FD001_COLUMNS = frozenset((*IDENTITY_COLUMNS, *READING_COLUMNS))


@dataclass(frozen=True)
class QualityFinding:
    """One row-level validation result; row numbers are 1-based."""

    code: str
    severity: Literal["error", "warning"]
    row_number: int | None
    field: str | None
    message: str


@dataclass(frozen=True)
class QualityReport:
    """Validation results for an input history, preserving its row count."""

    rows_checked: int
    findings: tuple[QualityFinding, ...]

    @property
    def errors(self) -> tuple[QualityFinding, ...]:
        return tuple(item for item in self.findings if item.severity == "error")

    @property
    def warnings(self) -> tuple[QualityFinding, ...]:
        return tuple(item for item in self.findings if item.severity == "warning")

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _positive_integer(value: object) -> int | None:
    if isinstance(value, bool) or not isinstance(value, Real):
        return None
    if isinstance(value, Integral):
        return int(value) if value > 0 else None
    try:
        numeric_value = float(value)
    except OverflowError:
        return None
    if not math.isfinite(numeric_value) or numeric_value <= 0:
        return None
    if not numeric_value.is_integer():
        return None
    return int(numeric_value)


def _is_finite_number(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, Real):
        return False
    if isinstance(value, Integral):
        return True
    try:
        return math.isfinite(float(value))
    except OverflowError:
        return False


def validate_engine_history(
    records: Iterable[Mapping[str, object]],
) -> QualityReport:
    """Check FD001 columns, finite readings, identities, duplicates, and cycles.

    Cycle gaps are warnings because their cause needs review and records must
    not be discarded automatically. Malformed values, duplicate engine-cycle
    pairs, and non-increasing cycles are errors.
    """

    findings: list[QualityFinding] = []
    rows_checked = 0
    seen_pairs: set[tuple[int, int]] = set()
    last_cycle_by_unit: dict[int, int] = {}

    def add(
        code: str,
        severity: Literal["error", "warning"],
        row_number: int | None,
        field: str | None,
        message: str,
    ) -> None:
        findings.append(QualityFinding(code, severity, row_number, field, message))

    for row_number, record in enumerate(records, start=1):
        rows_checked += 1
        if not isinstance(record, Mapping):
            add(
                "invalid_record",
                "error",
                row_number,
                None,
                "Record must be a mapping of normalized column names to values.",
            )
            continue

        columns = frozenset(record)
        missing_columns = FD001_COLUMNS - columns
        extra_columns = columns - FD001_COLUMNS
        if missing_columns or extra_columns:
            details = []
            if missing_columns:
                details.append(f"missing {', '.join(sorted(missing_columns))}")
            if extra_columns:
                details.append(f"unexpected {', '.join(sorted(map(str, extra_columns)))}")
            add(
                "invalid_columns",
                "error",
                row_number,
                None,
                "Record columns do not match normalized FD001 schema: "
                + "; ".join(details)
                + ".",
            )

        unit_id = _positive_integer(record.get("unit_id"))
        cycle = _positive_integer(record.get("cycle"))
        if unit_id is None:
            add(
                "invalid_identifier",
                "error",
                row_number,
                "unit_id",
                "Engine ID must be a positive finite integer.",
            )
        if cycle is None:
            add(
                "invalid_cycle",
                "error",
                row_number,
                "cycle",
                "Cycle must be a positive finite integer.",
            )

        for field in READING_COLUMNS:
            value = record.get(field)
            if isinstance(value, bool) or not isinstance(value, Real):
                add(
                    "invalid_reading",
                    "error",
                    row_number,
                    field,
                    "Reading must be a numeric value.",
                )
            elif not _is_finite_number(value):
                add(
                    "non_finite_reading",
                    "error",
                    row_number,
                    field,
                    "Reading must be finite.",
                )

        if unit_id is None or cycle is None:
            continue

        pair = (unit_id, cycle)
        if pair in seen_pairs:
            add(
                "duplicate_engine_cycle",
                "error",
                row_number,
                None,
                f"Engine {unit_id} has more than one record for cycle {cycle}.",
            )
        seen_pairs.add(pair)

        previous_cycle = last_cycle_by_unit.get(unit_id)
        if previous_cycle is None:
            if cycle > 1:
                add(
                    "cycle_gap",
                    "warning",
                    row_number,
                    "cycle",
                    f"Engine {unit_id} starts at cycle {cycle}; cycles 1-{cycle - 1} were not observed.",
                )
        elif cycle <= previous_cycle:
            add(
                "cycle_order",
                "error",
                row_number,
                "cycle",
                f"Engine {unit_id} cycle {cycle} is not greater than its previous cycle {previous_cycle}.",
            )
        elif cycle > previous_cycle + 1:
            add(
                "cycle_gap",
                "warning",
                row_number,
                "cycle",
                f"Engine {unit_id} has an observed cycle gap from {previous_cycle} to {cycle}.",
            )

        last_cycle_by_unit[unit_id] = cycle

    if rows_checked == 0:
        add("empty_history", "error", None, None, "History contains no records.")

    return QualityReport(rows_checked=rows_checked, findings=tuple(findings))
