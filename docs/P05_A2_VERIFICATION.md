# P05-A2 independent numeric verification

Abdullah, 11 November 2026; #119. Checks consume the actual extractor merged
by Shaheer's PR #321 (`79e23b6` on dev), not a replacement implementation.
The agreed `past-only-v1` config and P04 predecessor are available; #43 and
#9 are closed. Shaheer's #120/#196/#241 are closed. P05 gate #10 is separate.

`tests/test_feature_numerics_independent.py` adds 18 independent synthetic
acceptance cases. Expected numbers are hand-derived constants rather than
results from another numerical implementation:

- Gapped cycles `[2,5,9]`, readings `[2,8,5]`: latest 5, mean 5, population
  variance 6, standard deviation `sqrt(6)`. Centered cross-product sum is 9;
  centered cycle-square sum is `74/3`, so slope is `27/74` per cycle. This
  catches using row positions for slope and sample standard deviation.
- A simultaneous constant channel gives latest/mean 7 and zero std/slope;
  custom channel order matches the authoritative schema. Read-only input maps
  ensure the implementation does not write into source rows.
- Decreasing readings `[6,4,2]` at cycles `[1,2,3]` give latest 2, mean 4,
  std `sqrt(8/3)` and slope -2; a negative constant channel remains constant.
- One observation covers every default reading channel and yields 96 finite
  values, with zero standard deviation/slope for each channel.
- A short cycle window `[7,9]` on observed cycles `[2,5,9]` uses only cycle 9;
  visible row count is 3 and window row count is 1.
- Missing values, booleans, strings, NaN and both infinities in requested
  channels fail instead of being imputed; invalid first and last window rows
  are tested separately. Empty input and a missing selected channel also fail.

## Observed execution

Python 3.12.16, pytest 8.4.2, Ruff 0.17.4:

- `.venv/Scripts/python.exe -m ruff check .`: PASS.
- `.venv/Scripts/python.exe -m pytest -q tests/test_feature_numerics_independent.py`:
  **18 passed in 0.43s**.
- `.venv/Scripts/python.exe -m pytest -q`: **168 passed in 12.75s**.
- `git diff --check`: PASS before commit.

A Python stdin call to `engineer_features` with the gapped example printed:

```text
sensor_2: latest=7.0, mean=7.0, std=0.0, slope=0.0
sensor_1: latest=5.0, mean=5.0, std=2.449489742783178,
          slope=0.36486486486486486
metadata: ('synthetic/P05-A2', 17), selected cycle=9,
          observed rows=3, window rows=3
```

These are artificial readings and arithmetic checks, not NASA measurements or
model metrics. Reading units are unspecified synthetic units; slope is per
cycle. No raw FD001 data, official answer file, feature table or model artifact
is read or written by these new tests. Local Streamlit startup: **NOT RUN**,
no app changes; existing app checks pass in the full suite. Model
training/inference: **NOT RUN**, no model exists.

Abdullah confirmed on 11 November 2026 that Shaheer or Taha checked and
accepted these presented results against the requirement. The particular
teammate was not specified; this is supplied confirmation, not a GitHub review.
The test PR can merge to dev once five required checks and conversations pass,
without an approving review. Close #119 only after successful dev merge; #195 follows its completion. No teammate message was sent by the agent.
