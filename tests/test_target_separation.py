"""Guard the raw-history boundary against ground-truth leakage."""

from types import MappingProxyType

import pytest

from fleetpulse.data.loader import HISTORY_COLUMNS
from fleetpulse.data.quality import READING_COLUMNS, validate_engine_history
from fleetpulse.data.targets import calculate_training_rul


def _row(cycle):
    # Deliberately synthetic readings and engine identity, not NASA data.
    return {"unit_id": 900001, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 0.5)}


def test_target_generation_accepts_read_only_raw_rows_and_keeps_schema_separate():
    raw = [MappingProxyType(_row(cycle)) for cycle in (3, 8, 12)]

    labels = calculate_training_rul(raw)

    assert labels == [9, 4, 0]
    assert len(labels) == len(raw)
    assert all(tuple(row) == HISTORY_COLUMNS for row in raw)
    assert validate_engine_history(raw).is_valid


@pytest.mark.parametrize("field", ["rul", "true_rul", "target", "last_cycle", "final_lifetime"])
def test_raw_history_rejects_answer_or_lifetime_columns(field):
    contaminated = _row(3)
    contaminated[field] = 12

    report = validate_engine_history([contaminated])

    assert any(finding.code == "invalid_columns" for finding in report.errors)
    with pytest.raises(ValueError, match="invalid_columns"):
        calculate_training_rul([contaminated])
    # Do not silently discard answer columns and pretend the input is raw.
    assert contaminated[field] == 12
