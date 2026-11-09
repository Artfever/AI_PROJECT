"""Keep the artificial history usable without confusing it with FD001 data."""

import csv
import math
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_engine_history.csv"
FIELDS = [
    "unit_id",
    "cycle",
    *(f"setting_{number}" for number in range(1, 4)),
    *(f"sensor_{number}" for number in range(1, 22)),
]


def test_synthetic_history_has_one_complete_ordered_engine():
    with FIXTURE.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        assert reader.fieldnames == FIELDS
        rows = list(reader)

    assert len(rows) == 3
    assert {row["unit_id"] for row in rows} == {"900001"}
    assert [int(row["cycle"]) for row in rows] == [1, 2, 3]
    assert all(None not in row and all(row.values()) for row in rows)
    assert all(
        math.isfinite(float(row[field]))
        for row in rows
        for field in FIELDS[2:]
    )
    assert [float(row["sensor_1"]) for row in rows] == [10101, 10102, 10103]
    assert [float(row["sensor_21"]) for row in rows] == [12101, 12102, 12103]
