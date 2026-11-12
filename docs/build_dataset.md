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
inference NOT RUN:no model. Abdullah supplied A2 small-example inspection and acceptance, in addition to
A1 acceptance and both-trainer schema agreement. Saved
reproducibility and alignment checks remain A3; shared phase11 stays open.

## Reproducible storage (A3 / #197)

Rebuild both ignored tables from the repository root:

```powershell
.venv/Scripts/python.exe scripts/build_feature_datasets.py
```

Inputs are original `data/raw/train_FD001.txt` and tracked
`artifacts/split_manifest.json`; the script pins the original training-file SHA,
checks source and manifest bytes remain unchanged during construction, builds
both tables, saves them, reloads with expected input hashes/config, and checks
exact dataset equality. It never opens the official test source or answer file.
Outputs are ignored `artifacts/development/fitting_features.json` and
`artifacts/development/validation_features.json`. Do not add generated feature
tables or raw data to Git. This command builds datasets, not models.

`FeatureDataset` now carries the builder's immutable `source_sha256` and
`split_manifest_sha256`. The first is the actual source-file byte hash; the
second hashes canonical semantic manifest JSON (sorted keys, compact separators,
UTF-8, no NaN), so whitespace changes do not alter semantic identity. The existing
P04 manifest **file** hash is a different value and must not be substituted.

`save_feature_dataset(dataset, path)` returns the canonical payload SHA-256.
`load_feature_dataset(path, expected_source_sha256=..., expected_manifest_sha256=...,
expected_config=...)` exposes the original FeatureDataset after checking stored
content and caller-pinned provenance. Use `manifest_digest(manifest)` for the
expected semantic manifest hash and the same FeatureConfig used for building.
The loader itself performs no feature extraction or model fitting.

Saved JSON contains:

- Envelope `sha256` and `payload` with dataset schema version1 and role.
- Exact `feature_names`, full versioned `feature_config`, and source-file,
  semantic-manifest and canonical-config hashes.
- A canonical list of complete rows. Each row has its explicit qualified
  `key`, separate identity/count `metadata`, numeric `features`, and `true_rul`.
  This keeps the label attached to its vector while allowing separate X/y/key
  projections. Feature values never contain the metadata or label.

Reload rejects content drift, incorrect feature order/version/config hash,
invalid widths/numeric labels/counts, noncanonical or duplicate row keys, and
row-key/metadata mismatches. Shuffling metadata fails even after recomputing
content hash; shuffling labels without updating the hash fails the content
check. These hashes detect drift, not a deliberately regenerated false dataset:
original source, audited manifest and the producer remain scientific authorities.
No learned filtering exists; future learned preprocessing must still fit only
fitting engines.

### Actual A3 checks (11 November 2026)

Python3.12.16 / pytest8.4.2 / Ruff0.17.4:

- `.venv/Scripts/python.exe -m ruff check .`: PASS.
- `.venv/Scripts/python.exe -m pytest -q tests/test_dataset_io.py tests/test_fitting_dataset.py tests/test_validation_dataset.py`:
  **24 passed in1.22s**, including15 persistence cases. Synthetic expectations
  cover deterministic bytes, both roles, a fresh Python process/path with spaces,
  exact X/y/keys, metadata/label shuffles and caller-pinned provenance mismatch.
- `.venv/Scripts/python.exe -m pytest -q`: **200 passed in15.48s**.
- `git diff --check`: PASS before commit.
- First real rebuild/save/reload succeeded: **16,738x96 fitting**, **20x96
  validation**. Canonical payload hashes:
  fitting `6e2a0f0c28b0fbcb3afdc2b81d8f0c3aa02920617df758053d4d33f43bbb712c`;
  validation `f843a342a3f8799a22a1d386936e9f4c2ab57b6f7cb30cc21885a2b989fcdff7`.

No model training, prediction metrics or artifact reload are claimed. Local
Streamlit startup NOT RUN:no app changes; app tests pass in the full suite.
Teammate inspection of the storage output is requested and pending confirmation;
no teammate message or approving review is fabricated. P06 shared gate11 needs
separate actual trainers, validation predictions/metrics and reload evidence.

Two complete original-source rebuilds produced **byte-identical** saved files:

| Local generated file | Bytes | File SHA-256 |
| --- | ---: | --- |
| fitting_features.json | 23,754,754 | c87fb2f2039fe515cb7c5566cd0b7b87f43aa64bc56a7ff31e59e5d7a95be665 |
| validation_features.json | 30,852 | b241a6ec5a72cade8925ed40802e2d118871f71eee1622beec18f6dc8b869487 |

Both use canonical feature-config hash
`19dd0331ee3e0c3a90217446a4481507b7da94fe1424b1c251c4605a6b168dfe`
and semantic manifest hash
`6fd1d32f7570f70f5a9513d900fbb9d26b182359aced425e2276700c84f08d92`.
Byte hashes above identify the envelope files, and differ from payload hashes.
The second verification used Python stdin to capture file byte hashes, execute
`runpy.run_path('scripts/build_feature_datasets.py', run_name='__main__')`, and
assert both post-rebuild byte hashes equaled their captured values. Generated
files remain ignored; only this evidence is tracked.
