"""Ensure deployment packaging stays within the approved training prefixes."""

import pytest

from scripts.package_p07_training_subset import PREFIX_CUTOFFS, select_prefix_lines


def _line(engine: int, cycle: int) -> str:
    return " ".join(map(str, (engine, cycle, *([0] * 24))))


def test_selection_keeps_only_approved_engine_prefixes_and_cutoffs():
    source = [
        *(_line(engine, cycle) for engine, cutoff in PREFIX_CUTOFFS.items() for cycle in range(1, cutoff + 2)),
        _line(1, 1),
    ]

    selected = select_prefix_lines(source)

    assert len(selected) == 229
    assert {int(line.split()[0]) for line in selected} == {4, 5, 12}
    assert {
        engine: [int(line.split()[1]) for line in selected if int(line.split()[0]) == engine]
        for engine in PREFIX_CUTOFFS
    } == {engine: list(range(1, cutoff + 1)) for engine, cutoff in PREFIX_CUTOFFS.items()}


def test_selection_rejects_missing_cycle_in_an_approved_prefix():
    source = [
        *(_line(engine, cycle) for engine, cutoff in PREFIX_CUTOFFS.items() for cycle in range(1, cutoff + 1) if (engine, cycle) != (5, 12)),
    ]

    with pytest.raises(ValueError, match="consecutive cycles"):
        select_prefix_lines(source)


def test_selection_rejects_malformed_source_rows():
    source = [
        *(_line(engine, cycle) for engine, cutoff in PREFIX_CUTOFFS.items() for cycle in range(1, cutoff + 1)),
        "4 165 malformed",
    ]

    with pytest.raises(ValueError, match="expected 26"):
        select_prefix_lines(source)
