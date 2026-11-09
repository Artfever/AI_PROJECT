"""Read original-format FD001 histories and separate RUL answer files.

History records are normalized to the column names used by the quality module.
Test answers are available only through the separate, explicit RUL reader; they
are never joined to histories or loaded by the history reader.
"""

from collections.abc import Iterator
from pathlib import Path

from fleetpulse.data.quality import IDENTITY_COLUMNS, READING_COLUMNS

HISTORY_COLUMNS = (*IDENTITY_COLUMNS, *READING_COLUMNS)


class FD001LoadError(ValueError):
    """An FD001 source file cannot be read or does not match its format."""


def _file_lines(path: str | Path) -> Iterator[tuple[int, str]]:
    """Keep file-access/encoding diagnostics consistent across both readers."""
    try:
        with Path(path).open(encoding="utf-8") as source:
            yield from enumerate(source, start=1)
    except OSError as error:
        raise FD001LoadError(
            f"Cannot read FD001 file {path}: {error.strerror or str(error)}. "
            "Check the path and read permissions; obtain missing originals using "
            "docs/fd001_provenance.md."
        ) from error
    except UnicodeError as error:
        raise FD001LoadError(
            f"Cannot decode FD001 file {path} as UTF-8 text. "
            "Verify it is an extracted original text file, not a ZIP or damaged download."
        ) from error


def load_engine_history(path: str | Path) -> list[dict[str, int | float]]:
    """Read whitespace-separated records in their original order.

    Each nonempty line must have the two integer identity fields followed by
    three settings and 21 sensor values. The input file is never modified.
    """
    records: list[dict[str, int | float]] = []
    for line_number, line in _file_lines(path):
        values = line.split()
        if not values:
            continue
        if len(values) != len(HISTORY_COLUMNS):
            raise FD001LoadError(
                f"{path}: line {line_number} has {len(values)} fields; "
                f"expected {len(HISTORY_COLUMNS)}."
            )
        try:
            numeric_values = [int(value) for value in values[:2]] + [
                float(value) for value in values[2:]
            ]
        except ValueError as error:
            raise FD001LoadError(
                f"{path}: line {line_number} contains invalid numbers."
            ) from error
        records.append(dict(zip(HISTORY_COLUMNS, numeric_values, strict=True)))
    if not records:
        raise FD001LoadError(f"{path}: no sensor records found; expected nonempty 26-column history.")
    return records


def load_rul_values(path: str | Path, *, expected_engine_count: int | None = None) -> list[int]:
    """Read separate answers; optionally check one answer per distinct test engine.

    The caller supplies the count from test histories, not the sensor row count.
    This checks cardinality only; it does not establish engine/answer alignment.
    """
    if expected_engine_count is not None and (
        isinstance(expected_engine_count, bool)
        or not isinstance(expected_engine_count, int)
        or expected_engine_count < 1
    ):
        raise ValueError("expected_engine_count must be a positive integer.")
    values: list[int] = []
    for line_number, line in _file_lines(path):
        fields = line.split()
        if not fields:
            continue
        if len(fields) != 1:
            raise FD001LoadError(
                f"{path}: line {line_number} must contain exactly one RUL value."
            )
        try:
            values.append(int(fields[0]))
        except ValueError as error:
            raise FD001LoadError(
                f"{path}: line {line_number} contains an invalid RUL value."
            ) from error
    if not values:
        raise FD001LoadError(f"{path}: no RUL answers found; expected a nonempty one-column file.")
    if expected_engine_count is not None and len(values) != expected_engine_count:
        raise FD001LoadError(
            f"{path}: found {len(values)} RUL answers; expected {expected_engine_count} "
            "(one per distinct test engine). Check that the FD001 files belong together."
        )
    return values
