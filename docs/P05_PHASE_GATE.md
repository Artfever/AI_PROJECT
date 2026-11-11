# P05 shared gate evidence

Phase 5 develops a past-only feature extractor and preview; it does not train a
model. All nine owned tasks (#43, #119, #195, #120, #196, #241, #44, #121,
#265) were closed after their work merged to `dev`.

## Focused checks

On Python 3.12.16, from the repository root:

```powershell
.venv/Scripts/python.exe -m pytest -q tests/test_feature_config.py tests/test_feature_engineering.py tests/test_feature_numerics_independent.py tests/test_feature_future_invariance.py tests/test_feature_preview.py
```

Result: **57 passed** with the ignored local training source available. The
future-invariance test includes actual saved FD001 training validation cutoffs;
its synthetic cases remain identified as synthetic. The full suite passed 176
tests during the last task's local check; the task PR's five GitHub checks also
passed. These checks do not represent model performance.

A separate read-only check ran the actual extractor on the simulated FD001/train
engine 4. A one-row prefix returned 96 finite values. At selected cycle 164,
the output names matched `FeatureConfig.output_schema` in order, and replacing
all later reading channels in memory with `1e9` did not change any feature
value. The channel configuration excluded unit ID, cycle, RUL and lifetime
metadata. The input partition remained `FD001/train`; no test answer file was
opened. The default contract is `past-only-v1`, 24 reading channels and a
30-cycle window; names and version are documented in [feature_contract.md](feature_contract.md).

The UI preview and its input prefix were checked by Taha. The example in
[feature_example.md](feature_example.md) compares a source-derived mean and
slope independently with the extractor. Taha explained the example's provenance
and units after receiving an explanation; that assistance is recorded in the
handoff. No trained model, model score, or official-test result is claimed.
