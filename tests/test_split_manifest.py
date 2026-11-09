"""Synthetic checks for stable, dataset-qualified validation cutoff metadata."""

import json
import random

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split import TRAIN_PARTITION
from fleetpulse.data.split_manifest import build_split_manifest


def _rows():
    # Deliberately gapped observations; no cycle may be invented for a cutoff.
    return [
        {"unit_id": engine, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 0.5)}
        for engine in range(1, 11)
        for cycle in (1, 4, 8, 12)
    ]


def _build(rows, **kwargs):
    return build_split_manifest(
        rows, dataset_partition=TRAIN_PARTITION, source_path="synthetic.txt",
        source_sha256="a" * 64, **kwargs,
    )


def test_serialized_manifest_is_stable_and_preserves_inputs_and_rng():
    rows = _rows()
    before = [row.copy() for row in rows]
    state = random.getstate()
    first = _build(iter(rows), minimum_history_rows=2)
    reordered = [row for engine in reversed(range(1, 11)) for row in rows if row["unit_id"] == engine]
    assert json.dumps(first, sort_keys=True) == json.dumps(_build(reordered, minimum_history_rows=2), sort_keys=True)
    assert rows == before
    assert random.getstate() == state
    fitting = {entry["unit_id"] for entry in first["fitting_engines"]}
    validation = {entry["unit_id"] for entry in first["validation_prefixes"]}
    assert len(fitting) == 8 and len(validation) == 2
    assert not fitting & validation and fitting | validation == set(range(1, 11))
    for prefix in first["validation_prefixes"]:
        assert prefix["dataset_partition"] == "FD001/train"
        assert prefix["cutoff_cycle"] in (4, 8)
        assert prefix["eligible_cutoff_range"] == {"first": 4, "last": 8}
        assert prefix["eligible_cutoff_count"] == 2
        assert prefix["prefix_row_count"] in (2, 3)
        assert prefix["target_rul"] == 12 - prefix["cutoff_cycle"] > 0


def test_cutoff_seed_changes_cutoffs_without_changing_engine_assignment():
    first, second = _build(_rows(), cutoff_seed=1), _build(_rows(), cutoff_seed=2)
    assert first["fitting_engines"] == second["fitting_engines"]
    assert [p["unit_id"] for p in first["validation_prefixes"]] == [p["unit_id"] for p in second["validation_prefixes"]]
    assert first["validation_prefixes"] != second["validation_prefixes"]


def test_ineligible_engine_fails_instead_of_using_failure_cycle_or_resampling():
    with pytest.raises(ValueError, match="no nonterminal cutoff"):
        _build(_rows(), minimum_history_rows=4)


@pytest.mark.parametrize("minimum", [0, -1])
def test_invalid_minimum_history_rejected(minimum):
    with pytest.raises(ValueError, match="at least 1"):
        _build(_rows(), minimum_history_rows=minimum)
