"""Engine-level separation and determinism with deliberately synthetic histories."""

import random

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split import TRAIN_PARTITION, split_training_engines


def _engine(engine, length):
    return [
        {"unit_id": engine, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 0.5)}
        for cycle in range(1, length + 1)
    ]


def test_complete_engines_are_disjoint_exhaustive_and_independent_of_input_order():
    groups = [_engine(engine, engine) for engine in range(1, 11)]
    rows = [row for group in groups for row in group]
    before = [row.copy() for row in rows]
    global_state = random.getstate()

    split = split_training_engines(iter(rows), dataset_partition=TRAIN_PARTITION)
    reordered = [row for group in reversed(groups) for row in group]

    assert split == split_training_engines(reordered, dataset_partition=TRAIN_PARTITION)
    fitting = {identity.unit_id for identity in split.fitting_engines}
    validation = {identity.unit_id for identity in split.validation_engines}
    assert len(fitting) == 8
    assert len(validation) == 2
    assert not fitting & validation
    assert fitting | validation == set(range(1, 11))
    assert all(
        identity.dataset_partition == "FD001/train"
        for identity in split.fitting_engines + split.validation_engines
    )
    # Every row follows its engine, despite unequal trajectory lengths.
    for group in groups:
        assert all(row["unit_id"] in fitting for row in group) or all(
            row["unit_id"] in validation for row in group
        )
    assert rows == before
    assert random.getstate() == global_state


def test_fixed_seed_and_fraction_are_recorded_and_seed_changes_membership():
    rows = [_engine(engine, 1)[0] for engine in range(1, 101)]
    split = split_training_engines(rows, dataset_partition=TRAIN_PARTITION, seed=42)
    assert len(split.fitting_engines) == 80
    assert len(split.validation_engines) == 20
    assert split.seed == 42
    assert split.validation_fraction == 0.2
    assert split != split_training_engines(rows, dataset_partition=TRAIN_PARTITION, seed=43)


def test_small_cohort_rounding_keeps_both_groups_nonempty():
    rows = _engine(1, 2) + _engine(2, 3)
    split = split_training_engines(rows, dataset_partition=TRAIN_PARTITION, validation_fraction=0.99)
    assert len(split.fitting_engines) == len(split.validation_engines) == 1


@pytest.mark.parametrize("rows, message", [([], "empty_history"), (_engine(1, 2), "At least two")])
def test_insufficient_engines_rejected(rows, message):
    with pytest.raises(ValueError, match=message):
        split_training_engines(rows, dataset_partition=TRAIN_PARTITION)


@pytest.mark.parametrize("fraction", [0, 1, -0.2, float("nan"), float("inf"), True])
def test_invalid_fraction_rejected(fraction):
    with pytest.raises(ValueError, match="validation_fraction"):
        split_training_engines([], dataset_partition=TRAIN_PARTITION, validation_fraction=fraction)


def test_official_test_partition_and_malformed_histories_rejected():
    with pytest.raises(ValueError, match="original FD001/train"):
        split_training_engines(_engine(1, 2), dataset_partition="FD001/test")
    with pytest.raises(ValueError, match="duplicate_engine_cycle"):
        split_training_engines(_engine(1, 1) * 2, dataset_partition=TRAIN_PARTITION)
    with pytest.raises(TypeError, match="seed"):
        split_training_engines([], dataset_partition=TRAIN_PARTITION, seed=True)
