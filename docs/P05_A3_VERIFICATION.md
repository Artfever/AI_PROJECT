# P05-A3 future-reading invariance

Abdullah, 11 November 2026; #195. Uses the actual `engineer_features` on dev
and config `past-only-v1`. A2 PR #323 merged as `9ec5172`; #119 and P04 #9
are closed. No feature implementation or teammate subsystem changed here.

`tests/test_feature_future_invariance.py` compares the complete
`EngineFeatureVector` (all 96 values, schema/config, dataset-qualified identity,
selected cycle and visible/window counts) under three inputs at the same cutoff:

1. Only the observed prefix.
2. The complete history, including hidden future rows.
3. The complete history with every later reading replaced by alternating
   `+1e200`/`-1e200`, plus five additional extreme future rows.

The magnitude is deliberately large enough to expose accidental future-window
use through extreme or overflowing statistics. The original source rows remain
unchanged. Explicit selected cycles are essential: without a cutoff, selecting
the last observed cycle is intentionally a different prediction request.

## Synthetic evidence

Four cutoffs (1, 3, 30, 40) cover one-row, short, full and rolling windows over
50 artificial rows and all 24 channels. Channel values are `2*cycle + index`.
At cutoff 3, `setting_1` has observed values `[2,4,6]`, in arbitrary synthetic
reading units; its slope is per cycle. Direct execution printed:

```text
setting_1 before: (6.0, 4.0, 1.632993161855452, 2.0)
setting_1 after:  (6.0, 4.0, 1.632993161855452, 2.0)
all96 features and visible metadata identical: True
```

A control changes a visible `sensor_1` reading and verifies the vector changes,
with latest increased by 100. Another case verifies partition identity changes
metadata while leaving the numerical vector and schema unchanged. No identity
or target becomes a model feature.

## Real-source evidence

The real-data test uses only original local `data/raw/train_FD001.txt`, checks
its reviewed SHA-256 before parsing and after execution, and matches the saved
manifest's source hash. For each of the **20** saved validation entries, the
prefix-only, full-history and altered/appended-future results are identical,
with the actual prefix count and qualified `FD001/train` identity. This executes
the real extractor at saved cutoffs; it does not calculate model predictions,
performance metrics or official-test results. Alterations are in memory only.

If the ignored raw file is absent, that single real-data test skips explicitly;
the six synthetic tests still execute. A present file with the wrong hash fails.
No raw contents are committed and no official test answers are opened.

## Commands and limits

Python 3.12.16, pytest 8.4.2, Ruff 0.17.4:

- `.venv/Scripts/python.exe -m ruff check .`: PASS.
- `.venv/Scripts/python.exe -m pytest -q tests/test_feature_future_invariance.py`:
  **7 passed in 0.71s**, including all 20 real cutoff checks.
- `.venv/Scripts/python.exe -m pytest -q`: **175 passed in 13.12s**.
- `git diff --check`: PASS before commit.

Inspection of `src/fleetpulse/features/config.py` and `engineering.py` found
declared channels and deterministic per-window calculations, with no learned
column filter, estimator fit, scaler fit or data-derived channel selection.
Thus fitting learned filters on fitting engines only is **NOT APPLICABLE** to
this implementation. Any future learned filtering must fit on fitting engines
only and preserve its frozen schema for validation; these tests do not certify
an absent future preprocessing pipeline.

Local Streamlit startup: **NOT RUN**, no app change; full suite includes app
tests. Model training/inference: **NOT RUN**, no model exists. Abdullah confirmed on 11 November 2026: "I checked and accept this example",
including its synthetic provenance and the reported future-invariance result.
This is supplied human acceptance, not an agent-invented observation.
The task PR targets dev without an approval requirement; all five CI checks
and resolved conversations still apply. P05's UI tasks and shared phase gate
remain separate, and no phase promotion to main is claimed.
