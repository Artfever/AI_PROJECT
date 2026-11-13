# Raw prediction service (P07-A1 / #48)

Abdullah confirmed on **13 November 2026** that both Shaheer and Taha accept
this input and return contract. This records supplied team agreement, not a
GitHub approval or an automated message to either teammate.

```python
from fleetpulse.services import predict_rul

result = predict_rul(
    observed_history,
    dataset_partition="FD001/train",
    unit_id=4,
    manifest_path="artifacts/development/decision_tree_validation.json",
)
raw_prediction_for_comparison = result.raw_rul_cycles
```

The path is an example of the **existing P06 producer's** output, not a claim
that the ignored bundle is installed in every clone. No default artifact path,
training fallback, new registry or model selection is introduced.

## Exact contract

`predict_rul(history, *, dataset_partition, unit_id, manifest_path)` returns a
frozen `RawRULPrediction` with exactly one field:

- `raw_rul_cycles: float`: the estimator's finite, **unclipped** output in
  operating cycles. `dataclasses.asdict(result)` produces that single JSON field.

Input is an iterable of mappings for **one engine's observed prefix**, in
increasing cycle order. Each row must have exactly the existing 26 normalized
columns: `unit_id`, `cycle`, settings 1..3 and sensors 1..21. No RUL, final
lifetime, validation target, label or other extra columns are accepted.
Identifiers/cycles must be positive integer-valued numbers; validated identity
values are normalized on copies, leaving caller data unchanged. The requested
unit ID is a positive integer, and partition is a nonempty string used as
identity metadata, not a model feature.

The final observed cycle is the cutoff. **The caller must truncate hidden
future rows before calling.** For a P04 saved-cutoff comparison, Shaheer should
supply only rows at/before that cutoff. The service cannot infer what a caller
was allowed to observe from complete future histories. Gaps and short histories
use the reviewed feature rules; they are not silently imputed or extended.

The service reads the saved `feature_config` and exact ordered `feature_names`;
it never substitutes the default channels/window. Supported feature version is
the current `past-only-v1`. Default P06 bundles contain 24 channels/96 features,
but a valid saved subset/order/window is honored exactly.

## Artifact and error requirements

Use a trusted P06 Decision Tree bundle produced by `save_decision_tree_artifact`:

- Hashed JSON envelope, artifact schema `decision-tree-validation-v1`.
- Model name `decision-tree-rul`, version `decision-tree-rul-v1`.
- Runtime scikit-learn must exactly match the saved version (currently 1.9.1).
- Sibling `decision_tree_model.joblib`, matching its recorded SHA-256.
- Saved config/version and ordered names must match each other; the loaded
  fitted `DecisionTreeRegressor` must have matching feature count, one output,
  and parameters matching the manifest.

Only the manifest and estimator are read. Scoring targets/predictions may exist
in the P06 manifest, but are not accessed as inference inputs; no validation
table, metric file or official answer file is required. The envelope checksum
covers manifest content. Joblib deserializes the same model bytes whose hash
was checked; its inputs must be trusted project artifacts.

`PredictionInputError(ValueError)` reports invalid raw schema/values, mixed
engines, duplicate/non-increasing cycles or inability to create finite features.
`PredictionArtifactError(ValueError)` reports unavailable/unreadable files,
corrupt hashes, unsupported/inconsistent schema/runtime or failed estimator
loading/prediction. Missing-file errors include the supplied manifest path.
The service never attempts training to recover a missing artifact.

## Executed evidence (13 November 2026)

The existing declared dependencies were installed with
`.venv/Scripts/python.exe -m pip install -e '.[dev]'` successfully. Python
3.12.16, scikit-learn 1.9.1, joblib 1.6.0, pytest 8.4.2 and Ruff 0.17.4:

- `.venv/Scripts/python.exe -m ruff check .`: **PASS**.
- `.venv/Scripts/python.exe -m pytest -q tests/test_predictor.py`:
  **14 passed in 35.23s** (first cold import of the newly installed dependency).
- `.venv/Scripts/python.exe -m pytest -q`: **248 passed in 27.04s**.
- `git diff --check`: **PASS** before commit.

Tests create small, temporary **synthetic** saved trees using the actual P06
artifact producer. They verify the saved reordered channel list and two-cycle
window, immutable inputs, exact one-field return, short/gapped histories,
raw-schema/engine/target rejection, missing/corrupt/incompatible artifacts, no
dependency on evaluation labels, and preservation of an artificial negative
prediction. This is component verification, not #49's real offline/service audit
or #198's downstream compatibility test packet.

An actual Python stdin invocation of that temporary fixture observed:

```text
Synthetic saved-tree service output: {'raw_rul_cycles': 5.5}
artifact=decision-tree-validation-v1; model=decision-tree-rul-v1; seed=42
feature version=past-only-v1; channels=(sensor_2,sensor_1); window=2; fields=8
```

The synthetic negative-output test observed `-2.5` unchanged. These are artificial
test outputs, not FD001 predictions, validation metrics or maintenance advice.

Recursive inspection of local `artifacts/development/` found only the two
previous feature tables and `.gitkeep`; **real P06 inference/reload NOT RUN**:
the saved model/manifest are absent. Abdullah instructed use of synthetic
fixtures in that case. The real model was not retrained, regenerated, fetched
or fabricated. No raw data or temporary test artifact is committed.

**Streamlit smoke NOT RUN locally:** no app changes. #125's display clipping,
model/version/context/warnings fields and #198's separate task remain untouched.
Shaheer's #49/#126/#244 parity/model-card/deployment work is not implemented.

## Handoff to next consumers

Shaheer can import `predict_rul`, pass each real saved-cutoff prefix and the
existing P06 manifest, and compare **`raw_rul_cycles`** to the matching saved
offline prediction. He needs the trusted real bundle locally; its absence here
is not evidence of parity. No display clipping should be applied to evaluation
values. Taha can use the same raw service through the later presentation layer.

Abdullah subsequently confirmed the A1 output was inspected/discussed with a
teammate; #48 is now closed after merge and supplied acceptance. This does not
establish real-artifact parity or deployment; the real bundle is absent here.

## Separate presentation/context contract (P07-A2 / #125)

Abdullah confirmed on13November2026 that Shaheer and Taha agree these fields.
`predict_rul` keeps its original one-field RawRULPrediction return. New
`predict_rul_with_context` takes exactly the same keyword arguments and returns
an immutable RULPrediction with:

| Field | Meaning |
| --- | --- |
| raw_rul_cycles | Finite model output, unchanged even if negative; use for evaluation. |
| displayed_rul_cycles | max(0.0,raw_rul_cycles), a separate display policy in cycles. |
| model_name | Name from the validated saved manifest, currently decision-tree-rul. |
| model_version | Validated saved model version, currently decision-tree-rul-v1. |
| observed_cycle | Final observed cycle actually passed to feature extraction. |
| input_window_rows | Number of observations actually used inside the saved cycle interval. |
| warnings | Immutable tuple of stable warning codes described below. |

Both APIs share a single internal validated inference operation; each call
loads once and constructs one feature vector. The raw API does not clip its
output or add presentation fields. Context is derived from that same verified
artifact/input, avoiding an independent metadata read or a second prediction.
Caller history remains unchanged; labels/targets remain forbidden inputs.

Warning codes are returned in this deterministic order when applicable:

- cycle_gaps: the existing raw-history validator reports missing cycles,
  including an observed history starting after cycle1. No rows are filled in.
- short_window: actual input_window_rows is less than the saved window_cycles;
  this can result from a short prefix or gaps. It uses available observations.
- display_clipped_at_zero: raw output was negative; displayed value is0.0,
  while raw output remains untouched.

Warnings describe these input/display conditions, not model uncertainty or a
maintenance safety assessment. Lack of warnings does not guarantee accuracy.
Configured cycle span and actual row count can differ: observed cycles1,3,6
with a saved2-cycle window use only cycle6, so observed_cycle=6 and
input_window_rows=1. No metadata/label is added to the numeric feature vector.

### Actual A2 verification

- `.venv/Scripts/python.exe -m ruff check .` initially reported RUF022 for
  __all__ ordering. `.venv/Scripts/python.exe -m ruff check src/fleetpulse/services/__init__.py --fix`
  fixed that single issue; final full Ruff check PASS.
- `.venv/Scripts/python.exe -m pytest -q tests/test_predictor.py`:
  **17passed in7.15s**, including all14 prior raw-service cases. New checks cover
  context schema/model/window correspondence, unchanged raw API, short/gapped
  observed counts and raw-negative/display-zero separation.
- `.venv/Scripts/python.exe -m pytest -q`: **251passed in46.97s**.
- `git diff --check`: PASS before commit.

Actual temporary synthetic saved-tree outputs:

```json
{"raw_rul_cycles":5.5,"displayed_rul_cycles":5.5,"model_name":"decision-tree-rul","model_version":"decision-tree-rul-v1","observed_cycle":3,"input_window_rows":2,"warnings":[]}
{"raw_rul_cycles":-2.5,"displayed_rul_cycles":0.0,"model_name":"decision-tree-rul","model_version":"decision-tree-rul-v1","observed_cycle":1,"input_window_rows":1,"warnings":["short_window","display_clipped_at_zero"]}
```

These used the same temporary toy artifact producer as A1, seed42, saved
past-only-v1/custom sensor2,sensor1 order/window2. They are observed synthetic
outputs, not FD001 results or metrics. Real P06 inference/reload NOT RUN: real
bundle still absent; no real model retrained. Local Streamlit smoke NOT RUN:
no app changes. No #49 parity, model-card, deployment or #198 compatibility
packet implemented. Shaheer keeps using predict_rul/raw_rul_cycles for parity;
Taha can consume the new context function for presentation. Abdullah confirmed independent inspection/discussion of A2 output with a
teammate; #125 is closed after its implementation merged to dev.

## Compatibility and raw-record verification (P07-A3 / #198)

The current P06 artifact is a plain DecisionTreeRegressor using unscaled saved
features. There is no supported scaler file or preprocessing stage to recreate
or pair with the model. Tests explicitly substitute a fitted StandardScaler
and a scaler/tree Pipeline into the model slot, with valid updated byte/content
hashes. Both fail the supported-model type check. This verifies rejection of
unexpected preprocessing, not support for loading a scaler. No preprocessing
or training fallback was added.

The twelve additional cases in tests/test_predictor.py exercise:

| Case | Observed behavior |
| --- | --- |
| Missing model binary | PredictionArtifactError names both manifest and unavailable model paths. |
| Scaler or preprocessing Pipeline in model slot | Saved model is not a DecisionTreeRegressor. |
| Estimator width differs from saved config | Saved estimator dimensions do not match the feature schema. |
| Unfitted tree | Clear compatible-model loading error; no prediction returned. |
| Unsupported artifact/model/runtime version | Specific compatibility error. |
| Estimator parameters differ from manifest | Parameter mismatch error. |
| Edited config with stale manifest checksum | Manifest content hash mismatch. |
| Invalid serialization with updated byte checksum | Compatible-model loading error. |
| Saved raw/display record | Reloaded raw stays-2.5; separately labelled display stays0.0. |

Prior cases continue to cover a missing manifest, changed model-byte hash,
wrong feature names/order/version, invalid raw input and label exclusion.
No new public interface or return-shape decision was required. Model failures
never produce a guessed or fallback RUL value.

A new Windows-path test initially failed because the unavailable model path
appeared only inside an escaped OSError representation. The small runtime fix
now explicitly prints the failed file path and underlying reason. Existing
callers still receive PredictionArtifactError with the original exception cause.
The other compatibility guards already existed and were verified directly.

### Executed checks (13 November 2026)

- `.venv/Scripts/python.exe -m ruff check .` initially reported I001 import
  ordering. `.venv/Scripts/python.exe -m ruff check tests/test_predictor.py --fix`
  corrected that issue; final full Ruff PASS.
- Initial focused runs:1failed/28passed, the missing-model Windows path assertion.
  Initial full run:1failed/262passed in25.46s. The explicit-path fix resolved it.
- Final `.venv/Scripts/python.exe -m pytest -q tests/test_predictor.py`:
  **29passed in8.61s**.
- Final `.venv/Scripts/python.exe -m pytest -q`: **263passed in34.71s**.
- `git diff --check`: PASS before commit.

An actual temporary-fixture execution saved
`reports/P07_A3_synthetic_checks.json` (ignored), with provenance, seed42,
artifact/model/feature versions, sklearn1.9.1, observed error messages and:

```json
{
  "evaluation_prediction": {"raw_rul_cycles": -2.5},
  "display_only": {
    "displayed_rul_cycles": 0.0,
    "policy": "max(0, raw_rul_cycles)"
  }
}
```

This is synthetic compatibility evidence, not FD001 predictions or metrics.
The observed errors included "Saved model is not a DecisionTreeRegressor."
and "Saved estimator dimensions do not match the feature schema." The missing
binary message explicitly named decision_tree_model.joblib. Temporary artifacts
were deleted; no raw/model/test artifact was committed.

Abdullah confirmed the saved outputs and limitations were inspected/discussed
with a teammate; the teammate was not specified. Both return-field agreements
remain as recorded above. No GitHub approval or automated teammate message is
claimed. Real P06 inference/reload and #49 parity NOT RUN here: the real bundle
is absent and was not retrained. Local Streamlit smoke NOT RUN:no app changes;
full app tests pass. P07 model-card/deployment/parity remain other owners' work.
