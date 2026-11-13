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

The human inspection/discussion of saved service behavior is not yet confirmed.
Keep #48 open until it is merged to dev and acceptance evidence is complete;
contract agreement alone does not establish real-artifact parity or deployment.
