"""Read original-format FD001 histories and separate RUL answer files.

History records are normalized to the column names used by the quality module.
Test answers are available only through the separate, explicit RUL reader; they
are never joined to histories or loaded by the history reader.
"""

from pathlib import Path

from fleetpulse.data.quality import IDENTITY_COLUMNS, READING_COLUMNS

HISTORY_COLUMNS = (*IDENTITY_COLUMNS, *READING_COLUMNS)


def load_engine_history(path: str | Path) -> list[dict[str, int | float]]:
    """Read whitespace-separated records in their original order.

    Each nonempty line must have the two integer identity fields followed by
    three settings and 21 sensor values. The input file is never modified.
    """
    records: list[dict[str, int | float]] = []
    with Path(path).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            values = line.split()
            if not values:
                continue
            if len(values) != len(HISTORY_COLUMNS):
                raise ValueError(
                    f"{path}: line {line_number} has {len(values)} fields; "
                    f"expected {len(HISTORY_COLUMNS)}."
                )
            try:
                numeric_values = [int(value) for value in values[:2]] + [
                    float(value) for value in values[2:]
                ]
            except ValueError as error:
                raise ValueError(f"{path}: line {line_number} contains invalid numbers.") from error
            records.append(dict(zip(HISTORY_COLUMNS, numeric_values, strict=True)))
    return records


def load_rul_values(path: str | Path) -> list[int]:
    """Read a one-column answer file separately, preserving its row order."""
    values: list[int] = []
    with Path(path).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            fields = line.split()
            if not fields:
                continue
            if len(fields) != 1:
                raise ValueError(f"{path}: line {line_number} must contain exactly one RUL value.")
            try:
                values.append(int(fields[0]))
            except ValueError as error:
                raise ValueError(f"{path}: line {line_number} contains an invalid RUL value.") from error
    return values
