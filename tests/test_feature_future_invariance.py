"""Selected-cycle feature vectors must not depend on hidden future readings."""

import copy
import hashlib
import json

import pytest

from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.features import FeatureConfig, engineer_features

TRAIN_SHA256 = "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8"


def _row(cycle):
    return {
        "unit_id": 17,
        "cycle": cycle,
        **{channel: 2 * cycle + index for index, channel in enumerate(READING_COLUMNS)},
    }


def _features(history, cutoff, *, unit=17, partition="synthetic/P05-A3"):
    return engineer_features(
        history,
        dataset_partition=partition,
        unit_id=unit,
        selected_cycle=cutoff,
        config=FeatureConfig(),
    )


def _replace_future_and_append(history, cutoff):
    changed = copy.deepcopy(history)
    for row in changed:
        if row["cycle"] > cutoff:
            row.update(dict.fromkeys(READING_COLUMNS, (-1) ** row["cycle"] * 1e200))
    last = max(row["cycle"] for row in changed)
    for cycle in range(last + 1, last + 6):
        changed.append(
            {
                "unit_id": changed[0]["unit_id"],
                "cycle": cycle,
                **dict.fromkeys(READING_COLUMNS, (-1) ** cycle * 1e200),
            }
        )
    return changed


@pytest.mark.parametrize("cutoff", [1, 3, 30, 40])
def test_all_features_and_visible_metadata_survive_future_replacement_and_append(cutoff):
    full = [_row(cycle) for cycle in range(1, 51)]
    original = copy.deepcopy(full)
    prefix = [row for row in full if row["cycle"] <= cutoff]
    changed_future = _replace_future_and_append(full, cutoff)
    changed_snapshot = copy.deepcopy(changed_future)

    reference = _features(prefix, cutoff)
    assert _features(full, cutoff) == reference
    assert _features(changed_future, cutoff) == reference
    assert reference.selected_cycle == cutoff
    assert reference.observed_row_count == cutoff
    assert reference.window_row_count == min(cutoff, 30)
    assert len(reference.values) == 96
    assert tuple(reference.as_dict()) == reference.config.output_schema
    assert full == original
    assert changed_future == changed_snapshot


def test_visible_change_is_detected_as_a_control_for_the_invariance_check():
    full = [_row(cycle) for cycle in range(1, 51)]
    reference = _features(full, 3)
    changed = copy.deepcopy(full)
    changed[2]["sensor_1"] += 100
    altered = _features(changed, 3)
    assert altered.values != reference.values
    assert altered.as_dict()["sensor_1_latest"] == reference.as_dict()["sensor_1_latest"] + 100
    assert altered.config == reference.config


def test_partition_identity_is_metadata_and_not_a_feature_channel():
    history = [_row(cycle) for cycle in (1, 2, 3)]
    first = _features(history, 3, partition="synthetic/train")
    second = _features(history, 3, partition="synthetic/test")
    assert first.engine_key != second.engine_key
    assert first.values == second.values
    assert first.config.output_schema == second.config.output_schema


def test_saved_real_validation_cutoffs_ignore_all_hidden_future_readings():
    source = PROJECT_ROOT / "data/raw/train_FD001.txt"
    if not source.is_file():
        pytest.skip("Original ignored FD001 training file is not installed.")
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    assert before == TRAIN_SHA256, "Requires the reviewed original FD001 training source."
    manifest = json.loads(
        (PROJECT_ROOT / "artifacts/split_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["source"]["sha256"] == before
    by_unit = {}
    for row in load_engine_history(source):
        by_unit.setdefault(row["unit_id"], []).append(row)

    assert len(manifest["validation_prefixes"]) == 20
    for entry in manifest["validation_prefixes"]:
        unit, cutoff = entry["unit_id"], entry["cutoff_cycle"]
        history = by_unit[unit]
        prefix = [row for row in history if row["cycle"] <= cutoff]
        reference = _features(prefix, cutoff, unit=unit, partition="FD001/train")
        assert reference.observed_row_count == entry["prefix_row_count"]
        assert reference.engine_key == ("FD001/train", unit)
        assert len(reference.values) == 96
        assert _features(history, cutoff, unit=unit, partition="FD001/train") == reference
        altered = _replace_future_and_append(history, cutoff)
        assert _features(altered, cutoff, unit=unit, partition="FD001/train") == reference
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
