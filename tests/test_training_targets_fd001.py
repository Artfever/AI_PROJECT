"""Local integration checks against the original FD001 training file only."""

import hashlib

import pytest

from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.targets import calculate_training_rul

TRAIN_SHA256 = "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8"


@pytest.fixture(scope="module")
def fd001_training_labels():
    path = PROJECT_ROOT / "data" / "raw" / "train_FD001.txt"
    if not path.is_file():
        pytest.skip("Local FD001 train file absent; follow docs/fd001_provenance.md.")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == TRAIN_SHA256
    rows = load_engine_history(path)
    labels = calculate_training_rul(rows)
    assert len(labels) == len(rows)
    pairs_by_engine = {}
    for row, label in zip(rows, labels, strict=True):
        pairs_by_engine.setdefault(row["unit_id"], []).append((row["cycle"], label))
    yield pairs_by_engine
    assert hashlib.sha256(path.read_bytes()).hexdigest() == TRAIN_SHA256


@pytest.mark.parametrize("engine, final_cycle", [(1, 192), (2, 287), (100, 200)])
def test_real_training_engine_labels_match_audited_lifetime(
    fd001_training_labels, engine, final_cycle
):
    # Independent lifetimes recorded by the reviewed FD001 quality audit.
    pairs = fd001_training_labels[engine]
    assert pairs[0] == (1, final_cycle - 1)
    assert pairs[-1] == (final_cycle, 0)
    assert sum(label == 0 for _, label in pairs) == 1
    assert all(type(label) is int and label == final_cycle - cycle for cycle, label in pairs)
