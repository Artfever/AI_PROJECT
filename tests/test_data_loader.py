"""Loader behavior using deliberately artificial, test-only data."""

import csv
from pathlib import Path

import pytest

from fleetpulse.data.loader import HISTORY_COLUMNS, load_engine_history, load_rul_values
from fleetpulse.data.quality import validate_engine_history

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_engine_history.csv"


def test_whitespace_histories_preserve_fields_values_and_order(tmp_path):
    with FIXTURE.open(newline="", encoding="utf-8") as source:
        synthetic = list(csv.DictReader(source))
    path = tmp_path / "synthetic_history.txt"
    path.write_text(
        "\n".join("  \t".join(row[column] for column in HISTORY_COLUMNS) for row in synthetic)
        + "\n",
        encoding="utf-8",
    )
    original = path.read_bytes()

    records = load_engine_history(path)

    assert len(records) == 3
    assert list(records[0]) == list(HISTORY_COLUMNS)
    assert [record["cycle"] for record in records] == [1, 2, 3]
    assert records[0]["unit_id"] == 900001
    assert records[0]["sensor_1"] == 10101.0
    assert validate_engine_history(records).is_valid
    assert path.read_bytes() == original


def test_rul_file_is_parsed_separately_and_in_order(tmp_path):
    path = tmp_path / "synthetic_answers.txt"
    path.write_text("  12\n0  \n7\n", encoding="utf-8")

    assert load_rul_values(path) == [12, 0, 7]


@pytest.mark.parametrize("line", ["1 2 3", "1 2 " + " ".join(["bad"] * 24)])
def test_malformed_history_fails_with_line_number(tmp_path, line):
    path = tmp_path / "bad_history.txt"
    path.write_text(line + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="line 1"):
        load_engine_history(path)


@pytest.mark.parametrize("line", ["1 2", "not-a-number"])
def test_malformed_rul_fails_with_line_number(tmp_path, line):
    path = tmp_path / "bad_answers.txt"
    path.write_text(line + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="line 1"):
        load_rul_values(path)
