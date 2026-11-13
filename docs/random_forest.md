# P08 Random Forest candidate

P08-A1 / #51. P07 gate #12 is closed and its promotion is merged; no phase
dependency exception is needed. Task PRs target dev under current repository
policy. This candidate uses the same FD001 fitting/validation tables and
past-only feature contract as P06, not a new split or feature implementation.

```python
from fleetpulse.models.train_forest import train_random_forest

result = train_random_forest(fitting_dataset, validation_dataset)
```

The trainer accepts the existing provenance-checked FeatureDataset objects.
Only fitting.X/fitting.y enter fit. Validation X is predicted once per saved
engine/cutoff; labels enter the common metric functions only afterward. Shared
schema/provenance/disjoint-engine checks were extracted unchanged from the
Decision Tree trainer into models/training_validation.py and are used by both.
No shared feature files or data-selection policy changed.

Abdullah agreed the initial configuration and run budget:100 estimators, max_depth12, min_samples_leaf5,
max_features1.0, bootstrapTrue, seed42, n_jobs1. One candidate run, no search,
with a five-minute subprocess timeout. The single real fit completed within
that budget; no parameter search or second real fit was performed.

The forest averages many bounded trees instead of using a single tree. It may
improve development-validation error, but improvement is measured rather than
required. Predictions are uncapped operating cycles; primary MAE/RMSE use raw
values. The official test partition and answers remain unused. This is a
development candidate, not a final model or a maintenance safety guarantee.

## Trainer verification

Python3.12.16 / scikit-learn1.9.1 / pytest8.4.2 / Ruff0.17.4:

- Initial Ruff check flagged import sorting while extracting the shared helper;
  corrected imports and final `.venv/Scripts/python.exe -m ruff check .` PASS.
- `.venv/Scripts/python.exe -m pytest -q tests/test_train_forest.py tests/test_train_tree.py`:
  **15passed in42.78s**. Includes9new forest cases: direct fit-input capture,
  seed reproducibility, fixed validation identities/labels, overlap/source/schema/
  role rejection before fitting and invalid parameter rejection.
- `.venv/Scripts/python.exe -m pytest -q`: **285passed in75.37s**.
- `git diff --check`: PASS before commit.
- Real local table inspection with pinned original source hash, canonical saved
  manifest hash and FeatureConfig:16,738 fitting rows/80engines;20 validation
  rows/20engines;96features each. No raw/official-test answer file was used for
  model selection. Synthetic trainer tests use eight small trees, not the real
  candidate or a parameter search.

Local Streamlit smoke NOT RUN:no app changes. Candidate persistence is A2 and
shared-service loading A3. App model selection/comparison UI and independent
evaluation support belong to Taha and Shaheer. No deployment or final-model
claim follows from this trainer implementation.

## Actual initial candidate (A1)

Python stdin loaded the existing tables with expected original source hash,
semantic manifest hash and FeatureConfig, checked the fitting engine set and
exact saved validation keys/labels, then called train_random_forest(fitting,
validation). The child process had timeout300seconds. Input byte hashes were
checked unchanged afterward. It observed:

- model_version=random-forest-rul-v1; sklearn1.9.1; seed42.
- 16,738 fitting rows/80engines/96features;20validation engines.
- Fit+batch-prediction runtime **163.1630856999982seconds**.
- **MAE18.833479230754712cycles; RMSE25.24302308237894cycles**.
- Engine4/cutoff164:34.04320452065351 vs target25cycles.
- Engine5/cutoff58:159.8769392222517 vs target211cycles.
- Engine12/cutoff7:160.9491664455265 vs target163cycles.

These are actual same-protocol development results; no official-test results
or final model selection are claimed. A1's ignored reports/P08_A1_run.json
retains full configuration/input hashes and all20raw predictions. Ignored
reports/P08_A1_candidate.joblib retains the fitted result as a trusted local
checkpoint (SHA256 be7578beecfc0b3f658dcbe0df006fbe9fc2638f522d1fee6d320e68fecfdf7c),
so A2 can persist this same candidate without another fit. This temporary
checkpoint is not the production candidate bundle or a committed artifact.
Human output discussion has been requested; no inspection is invented.
