"""Behavioral checks for normalized FD001 history validation."""

import csv
import math
from pathlib import Path

from fleetpulse.data.quality import READING_COLUMNS, validate_engine_history

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_engine_history.csv"


def _row(unit_id: object, cycle: object) -> dict[str, object]:
    return {
        "unit_id": unit_id,
        "cycle": cycle,
        **{field: float(index) for index, field in enumerate(READING_COLUMNS, start=1)},
    }


def _fixture_rows() -> list[dict[str, object]]:
    with FIXTURE.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    return [
        {
            field: int(value) if field in {"unit_id", "cycle"} else float(value)
            for field, value in row.items()
        }
        for row in rows
    ]


def test_synthetic_fd001_shaped_history_passes_without_mutation():
    rows = _fixture_rows()
    original_rows = [row.copy() for row in rows]

    report = validate_engine_history(rows)

    assert report.rows_checked == 3
    assert report.is_valid
    assert report.findings == ()
    assert rows == original_rows


def test_integrity_report_flags_schema_values_duplicates_and_cycle_sequence():
    rows = [
        _row(1, 1),
        _row(1, 3),
        _row(1, 2),
        _row(0, 2),
        _row(1, 1),
        _row(2, 1),
    ]
    rows[1]["sensor_1"] = math.inf
    rows[5].pop("sensor_21")
    original_rows = [row.copy() for row in rows]

    report = validate_engine_history(rows)
    codes = {finding.code for finding in report.findings}
    warning_rows = {finding.row_number for finding in report.warnings}

    assert report.rows_checked == 6
    assert not report.is_valid
    assert {
        "invalid_columns",
        "invalid_identifier",
        "invalid_reading",
        "non_finite_reading",
        "duplicate_engine_cycle",
        "cycle_order",
        "cycle_gap",
    } <= codes
    assert warning_rows == {2}
    assert rows == original_rows


def test_empty_history_is_invalid():
    report = validate_engine_history([])

    assert report.rows_checked == 0
    assert not report.is_valid
    assert [finding.code for finding in report.errors] == ["empty_history"]
