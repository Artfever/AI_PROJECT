# Independent training-target check

This check addresses P03-S2: independently verify training RUL labels and catch
mixing an engine's lifetime with another engine's rows. Abdullah's implementation
is `fleetpulse.data.targets.calculate_training_rul(records)`; it returns one
integer label per input row and does not modify the sensor records.

## Hand check

For the synthetic engine ending at cycle 12, the independent arithmetic is
`12 - 3 = 9`, `12 - 8 = 4`, and `12 - 12 = 0`. The existing synthetic
two-engine test interleaves engine 10 (ending at 12) and engine 20 (ending at 5)
and expects `[9, 4, 4, 0, 0]` in input-row order. Engine 20's cycle-1 label is 4;
using engine 10's lifetime would incorrectly yield 11. The test also checks that
the input rows remain unchanged.

## Real training-history comparison

Run locally after placing the original training file at
`data/raw/train_FD001.txt`:

```powershell
python scripts/verify_training_targets.py
```

The verifier loads only the training history. It compares each returned label to
the independently generated per-engine final-cycle values in
`artifacts/data_quality.json`, whose report generator uses the data summary
path rather than the target function. It also checks the raw-file SHA-256 against
that report, input immutability, integer/nonnegative labels, and one terminal
zero per engine. It does not read `RUL_FD001.txt` or add a target column to raw
sensor rows.

Verified on Python 3.12.10 against the locally hashed NASA FD001 training file:

- 20,631 labels across 100 engines matched the independent per-engine report.
- There was one terminal zero per engine; labels ranged from 0 to 361 cycles.
- Engine 1: cycles 1–192, first RUL 191, terminal RUL 0.
- Engine 2: cycles 1–287, first RUL 286, terminal RUL 0.
- Engine 100: cycles 1–200, first RUL 199, terminal RUL 0.
- Input rows were unchanged. No test-answer values were read.

The focused synthetic contract test remains in `tests/test_training_targets.py`;
it passes independently of the ignored local data. This audit verifies target
labels only; it does not train or score a model, use test labels, or establish
prediction performance.
