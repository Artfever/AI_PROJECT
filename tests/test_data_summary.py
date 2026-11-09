"""Behavioral checks for FD001 counts, cycle ranges, and sensor variance."""

import csv
import math
from pathlib import Path

import pytest

from fleetpulse.data.quality import SENSOR_COLUMNS
from fleetpulse.data.summary import EngineCoverage, summarize_engine_history

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_engine_history.csv"


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


def test_summary_matches_hand_calculated_synthetic_counts_and_variance():
    rows = _fixture_rows()

    summary = summarize_engine_history(rows)

    assert summary.row_count == 3
    assert summary.engine_count == 1
    assert summary.engines == (EngineCoverage(900001, 3, 1, 3),)
    assert set(summary.sensor_population_variance) == set(SENSOR_COLUMNS)
    assert all(
        math.isclose(variance, 2 / 3)
        for variance in summary.sensor_population_variance.values()
    )
    assert summary.constant_sensors == ()
    assert summary.quality.is_valid


def test_summary_keeps_engine_ranges_separate_and_exposes_cycle_gap_warnings():
    rows = _fixture_rows()
    rows[0]["unit_id"] = 900002
    rows[1]["unit_id"] = 900001
    rows[1]["cycle"] = 1
    rows[2]["unit_id"] = 900002
    rows[2]["cycle"] = 3
    for row in rows:
        for field in SENSOR_COLUMNS:
            row[field] = 7.0

    summary = summarize_engine_history(rows)

    assert summary.engine_count == 2
    assert summary.engines == (
        EngineCoverage(900001, 1, 1, 1),
        EngineCoverage(900002, 2, 1, 3),
    )
    assert summary.constant_sensors == SENSOR_COLUMNS
    assert all(variance == 0.0 for variance in summary.sensor_population_variance.values())
    assert [finding.code for finding in summary.quality.warnings] == ["cycle_gap"]


def test_summary_rejects_invalid_duplicate_records_instead_of_dropping_them():
    rows = _fixture_rows()
    rows.append(rows[0].copy())

    with pytest.raises(ValueError, match="duplicate_engine_cycle"):
        summarize_engine_history(rows)
