"""Check engine-specific training labels using explicitly synthetic histories."""

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.targets import calculate_training_rul


def _row(engine, cycle):
    return {"unit_id": engine, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 0.5)}


def test_interleaved_engines_use_their_own_lifetime_without_mutating_rows():
    # Synthetic complete lifetimes: engine 10 ends at 12, engine 20 at 5.
    rows = [_row(10, 3), _row(20, 1), _row(10, 8), _row(20, 5), _row(10, 12)]
    before = [row.copy() for row in rows]

    assert calculate_training_rul(iter(rows)) == [9, 4, 4, 0, 0]
    assert rows == before


def test_labels_remain_uncapped_cycles_and_include_single_row_engine():
    assert calculate_training_rul([_row(1, 1), _row(1, 202), _row(2, 8)]) == [201, 0, 0]


@pytest.mark.parametrize(
    "rows, message",
    [
        ([], "at least one"),
        ([_row(1, 1), _row(1, 1)], "duplicate_engine_cycle"),
        ([_row(1, 2), _row(1, 1)], "cycle_order"),
        ([_row(1, 0)], "invalid_cycle"),
    ],
)
def test_invalid_histories_do_not_produce_labels(rows, message):
    with pytest.raises(ValueError, match=message):
        calculate_training_rul(rows)
