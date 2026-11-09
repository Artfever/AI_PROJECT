# Training RUL labels

`fleetpulse.data.targets.calculate_training_rul(records)` accepts normalized
records from **complete run-to-failure training engines** and returns a list of
integer RUL labels aligned to the input rows. For engine `i` at cycle `t`:

```text
RUL(i, t) = maximum observed training cycle for engine i - t
```

Units are operating cycles. Labels are uncapped, nonnegative, and zero at every
engine's terminal row. Engine groups may be interleaved; each uses its own last
cycle. Per-engine cycles must increase and identities must pass the existing
quality validator. Gaps produce the existing warnings, not invented records or
adjusted labels. Empty or invalid histories raise `ValueError`.

```python
from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.targets import calculate_training_rul

training_rows = load_engine_history(PROJECT_ROOT / "data/raw/train_FD001.txt")
training_rul = calculate_training_rul(training_rows)
assert len(training_rul) == len(training_rows)
```

The function does not modify, sort, or add fields to sensor rows. It reads no
files and produces no model predictions. The label vector uses the same row
order as the supplied records; do not filter or reorder one without the other.
Dataset-partition provenance and completeness must be established by the caller.
The function cannot discover whether a supplied trajectory actually reaches
failure. A single row is valid only if it is the complete supplied engine
trajectory; it then has a zero label.

Do not call this on truncated test histories or prediction prefixes: their last
observed cycle is not the failure cycle. Do not combine train and test records
whose numeric engine IDs can overlap. The official answer file is unrelated to
this training-label calculation and is never opened. Final lifetime and RUL
must not become model features. P03-A3 owns the broader tiny/real-engine verification,
and P03-S2 the independent
audit. This implementation does not claim those tasks complete.

## Raw histories and answer metadata

The raw-history contract remains exactly the 26 `HISTORY_COLUMNS` in
`fleetpulse.data.loader`. `validate_engine_history` rejects any extra fields,
including `rul`, `true_rul`, `target`, `last_cycle`, and `final_lifetime`.
`calculate_training_rul` uses that validation and returns only a separate label
vector. It also accepts read-only row mappings: it has no need to append target
or lifetime fields to the input. Internal per-engine final cycles remain local
to label calculation and are not returned as sensor columns.

Keep the original raw records and the labels as separate objects. To display
ground truth, construct a separate, clearly labeled analysis view. Do not feed
that augmented view back through the raw-history path. Unknown fields are
rejected, rather than silently dropped. The two identity fields (`unit_id`,
`cycle`) remain raw record metadata; these 26 columns are not a model feature
list. Feature selection/order belongs to P05, and prediction services to P07.

This boundary helps catch accidental label leakage; it does not detect a
target deliberately disguised as a sensor value or prove that a caller supplied
complete training trajectories. Future feature/service consumers must enforce
their own declared input contracts. Run
`python -m pytest -q tests/test_target_separation.py` for the focused P03-A2
read-only-input and contaminated-schema checks.

The [synthetic hand calculation](rul_hand_calculation.md) gives labels 9, 4, 0
at cycles 3, 8, 12 for an engine ending at 12. The tests also interleave a second
engine with a different lifetime to catch accidentally using a global maximum.
Run `python -m pytest -q tests/test_training_targets.py` after the editable install.
