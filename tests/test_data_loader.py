"""Loader behavior using deliberately artificial, test-only data."""

import csv
from pathlib import Path

import pytest

from fleetpulse.data.loader import (
    HISTORY_COLUMNS,
    FD001LoadError,
    load_engine_history,
    load_rul_values,
)
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


@pytest.mark.parametrize(
    "line", ["1 2 3", "1 2 " + " ".join(["bad"] * 24), " ".join(["1"] * 27)]
)
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


@pytest.mark.parametrize("reader", [load_engine_history, load_rul_values])
def test_missing_file_explains_path_and_recovery(tmp_path, reader):
    path = tmp_path / "missing.txt"
    with pytest.raises(FD001LoadError) as caught:
        reader(path)
    assert str(path) in str(caught.value)
    assert "docs/fd001_provenance.md" in str(caught.value)
    assert isinstance(caught.value.__cause__, FileNotFoundError)


@pytest.mark.parametrize("reader", [load_engine_history, load_rul_values])
def test_permission_error_is_actionable(tmp_path, monkeypatch, reader):
    def denied(*args, **kwargs):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(Path, "open", denied)
    with pytest.raises(FD001LoadError, match="read permissions") as caught:
        reader(tmp_path / "unreadable.txt")
    assert isinstance(caught.value.__cause__, PermissionError)


@pytest.mark.parametrize("reader", [load_engine_history, load_rul_values])
@pytest.mark.parametrize("payload, message", [(b"\xff\xfe", "decode"), (b" \n\t", "no ")])
def test_damaged_encoding_and_empty_file_fail(tmp_path, reader, payload, message):
    path = tmp_path / "damaged.txt"
    path.write_bytes(payload)
    with pytest.raises(FD001LoadError, match=message):
        reader(path)
    assert path.read_bytes() == payload


def test_train_test_separation_and_answer_count_uses_engines_not_rows(tmp_path):
    def history(name, pairs):
        path = tmp_path / name
        path.write_text(
            "\n".join(f"{unit} {cycle} " + " ".join(["0.5"] * 24) for unit, cycle in pairs),
            encoding="utf-8",
        )
        return load_engine_history(path)

    train = history("train.txt", [(1, 1), (1, 2), (1, 3)])
    test = history("test.txt", [(1, 1), (1, 2), (2, 1)])
    assert len(train) == len(test) == 3
    assert {row["unit_id"] for row in train} == {1}
    test_engines = len({row["unit_id"] for row in test})
    assert test_engines == 2
    answers = tmp_path / "synthetic_rul.txt"
    answers.write_text("8\n3\n", encoding="utf-8")
    assert load_rul_values(answers, expected_engine_count=test_engines) == [8, 3]
    for expected in [1, 3]:
        with pytest.raises(FD001LoadError, match=f"found 2 RUL answers; expected {expected}"):
            load_rul_values(answers, expected_engine_count=expected)
    assert all("rul" not in row for row in train + test)


@pytest.mark.parametrize("count", [0, -1, True, 1.5])
def test_invalid_expected_count_rejected_before_reading(tmp_path, count):
    with pytest.raises(ValueError, match="positive integer"):
        load_rul_values(tmp_path / "not-opened.txt", expected_engine_count=count)
