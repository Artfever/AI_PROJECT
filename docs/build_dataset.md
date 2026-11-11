# P06 dataset builder

Schema v1 is the trainer contract accepted by both trainers, as confirmed by Abdullah. Import `build_fitting_dataset` from
`fleetpulse.features.build_dataset`. Supply the complete original training
records, saved P04 manifest and independently calculated original-file SHA-256;
the builder audits the manifest against those histories before extracting.
No official test source or answer file is opened by the builder.

```python
dataset = build_fitting_dataset(
    records, manifest=manifest, source_sha256=actual_source_sha256,
    config=FeatureConfig(),
)
X, y = dataset.X, dataset.y
names, row_keys = dataset.feature_names, dataset.row_keys
```

`FeatureDataset.rows` is an immutable tuple of `LabeledFeatureRow` objects,
each holding one `EngineFeatureVector` and a separately held `true_rul` label.
`X`, `y` and `row_keys` are projections from those same rows. `X` contains only
ordered numeric feature values, while `row_keys` are
`(dataset_partition, unit_id, selected_cycle)`. Other metadata remains in each
vector. Neither IDs nor cycle/lifetime/target is appended to model inputs.
`feature_names` is the exact `FeatureConfig.output_schema`; defaults give 96
columns using `past-only-v1`, 24 channels and a 30-cycle interval.

## Fitting eligibility and labels (A1 / #45)

The extractor supports one observation, so **every observed fitting-engine
cycle is eligible**, including the first cycle and the terminal zero-RUL row.
Only engines listed in `manifest.fitting_engines` are emitted. Rows are ordered
by engine ID then observed cycle. Gaps generate no invented rows. Complete
training trajectories must start at cycle 1; their provenance and completeness
are caller responsibilities and cannot be inferred from sensor readings.

For every row the extractor receives only that fitting engine's observed prefix
through the selected cycle. Labels are computed separately by the reviewed
`calculate_training_rul` using full training trajectories: final cycle minus
selected cycle. No clipping, target capping, learned filtering or model training
occurs here. This is an in-memory producer; validation construction and persisted
reproducibility are subsequent A2/A3 tasks.

Synthetic check: fitting engine 2 has cycles 1..4 and sensor readings 2,4,6,8.
At cycle 2, `X=(4,3,1,2)` for latest/mean/population std/actual-cycle slope, while
the separate label is `4-2=2` cycles. All four labels are `[3,2,1,0]`. These are
artificial values in unspecified reading units; slope is per cycle.

### Execution on 11 November 2026

Python 3.12.16 / pytest 8.4.2 / Ruff 0.17.4:

- `.venv/Scripts/python.exe -m ruff check .`: PASS.
- `.venv/Scripts/python.exe -m pytest -q tests/test_fitting_dataset.py`:
  **4 passed in 0.29s**. Checks fitting membership, keys/labels, one-row and
  two-row arithmetic, direct prefix-only callback inspection, raw-only columns,
  unchanged inputs, interleaved-engine alignment and fail-before-extraction
  on source/hash errors.
- `.venv/Scripts/python.exe -m pytest -q`: **180 passed in 15.15s**.
- `git diff --check`: PASS before commit.
- Direct original-train execution with the saved audited manifest:
  **16,738 rows, 96 features, 80 engines**, uncapped labels 0..361, 80 zeros.
  First key `('FD001/train',1,1)` has target 191 and first-channel values
  `(-0.0007,-0.0007,0,0)`. Observed build time 21.07s on this machine;
  this is an execution observation, not a performance guarantee.

Original raw training source SHA-256 is
`963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8`.
No raw/model artifacts were added. Streamlit startup **NOT RUN**: no app changes;
app tests passed in the full suite. Model training/inference **NOT RUN**: builder
only. Abdullah confirmed agreement with both trainers on schema v1 and independently
checked the A1 row/target separation example. This records supplied human
evidence; no teammate message or GitHub approval is claimed.

## Saved-cutoff validation (A2 / #122)

`build_validation_dataset(records, manifest=manifest, source_sha256=hash, config=config)`
returns the same FeatureDataset interface with role validation. It audits the
saved manifest first, emits one row per saved validation engine in numeric ID
order, and calls the extractor only with that engine's rows through its saved
cutoff. No resampling, additional cutoffs, terminal validation rows or fitting
engines are introduced. Labels are the independently audited saved full-lifetime
minus cutoff targets, not the truncated prefix's apparent lifetime. IDs and
cutoffs remain vector metadata and row_keys, separate from X.

Artificial check: validation engine1 has full lifetime3 and saved cutoff1.
Only reading2 at cycle1 enters X=(2,2,0,0), while y=2cycles. Cycles2/3 never
reach the extractor. Synthetic readings have unspecified units; slope is percycle.

Executed on Python3.12.16:

- `.venv/Scripts/python.exe -m ruff check .`: PASS.
- `.venv/Scripts/python.exe -m pytest -q tests/test_validation_dataset.py`:
  **5 passed in0.38s** (prefix/identity/target separation, fitting-versus-validation
  schema and disjoint membership, corrupted cutoff/label/count rejection before extraction).
- `.venv/Scripts/python.exe -m pytest -q`: **185 passed in14.32s**.
- Direct original training-source build: **20 rows x96 features/20engines**,
  positive labels1..211; first key(FD001/train,4,164), target25, observed164,
  window30. No official answers read or dataset artifacts written.
- `git diff --check`: PASS before commit.

Streamlit startup NOT RUN:no app changes; full app tests pass. Model training/
inference NOT RUN:no model. A2 small-example inspection is pending confirmation;
A1 acceptance and both-trainer schema agreement are already supplied. Saved
reproducibility and alignment checks remain A3; shared phase11 stays open.
