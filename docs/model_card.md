# Model card: FleetPulse FD001 development Decision Tree

**Status:** Development candidate; not approved for real maintenance decisions  
**Model:** `decision-tree-rul` / `decision-tree-rul-v1`  
**Last checked:** 13 November 2026

## Summary

This bounded scikit-learn Decision Tree estimates remaining useful life (RUL)
in operating cycles from a single engine's observed sensor history. It is a
course-project model trained and evaluated on the simulated NASA C-MAPSS FD001
training partition. Its results are development evidence, not official-test
performance or evidence that the estimate is safe for maintenance decisions.

## Intended use and limits

The model is intended for reproducible development experiments and the
FleetPulse demonstration. It can show how a saved RUL model consumes an
observed history and returns a cycle estimate. Do not use it to schedule,
defer, or authorize real maintenance; it is not validated or certified for
safety-critical use.

## Data and target

- **Source:** NASA C-MAPSS FD001 `train` histories, identified by source SHA-256
  `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8`.
- **Split:** The saved engine-level manifest assigns 80 engines to fitting and
  20 distinct engines to development validation. Split/feature provenance is
  recorded by manifest SHA-256
  `6fd1d32f7570f70f5a9513d900fbb9d26b182359aced425e2276700c84f08d92`.
- **Target:** Uncapped cycles from the observed cutoff to the engine's final
  cycle in the complete training trajectory. Future rows and the target are
  scoring data only; neither is passed to prediction.
- **Official test data:** Test histories and answer files were not used for
  these results. No official-test score is available in this card.

## Model and inputs

- **Estimator:** `sklearn.tree.DecisionTreeRegressor`.
- **Parameters:** `max_depth=8`, `min_samples_leaf=5`, `random_state=42`.
- **Training:** 16,738 fitting feature rows from 80 fitting engines.
- **Runtime:** scikit-learn 1.9.1.
- **Features:** `past-only-v1`; 24 settings/sensor channels summarized over the
  saved inclusive 30-cycle window as latest value, mean, standard deviation,
  and cycle-based slope (96 ordered features total).
- **Prediction input:** One engine's validated rows through the stated cutoff.
  The service rejects target/lifetime columns, checks the saved artifact and
  feature schema, and uses only available rows for short histories; it does
  not pad or impute missing history. Context output can flag `short_window`.

The saved model SHA-256 is
`2a693e6ecc09de5d9549e287a6798fdb339c7e945c700231444f0c5bcd425018`.

## Development validation results

Scores are calculated once per held-out engine at its saved nonterminal
training-history cutoff. Lower error is better.

| Predictor | MAE (cycles) | RMSE (cycles) | Validation engines |
| --- | ---: | ---: | ---: |
| Decision Tree (`decision-tree-rul-v1`) | 22.49426974577135 | 29.449573581432592 | 20 |
| Mean constant baseline (`constant-rul-v1`) | 65.728002150795 | 74.258986754232 | 20 |

Both predictors were scored on the same saved FD001/train development
validation examples. These results show the Decision Tree performed better
than this constant baseline on this split; they do not estimate performance on
future engines, another C-MAPSS subset, or real equipment. Model development
used this validation set, so it is not an untouched final test set.

The service replay also reproduced all 20 saved P06 Decision Tree predictions
exactly (maximum raw difference 0.0 cycles). That checks implementation and
artifact parity against the saved outputs; it is not a separate accuracy or
generalization result.

## Known limitations and risks

- Evaluation uses only 20 engine-level prefixes from one simulated subset.
  Results may not transfer to other subsets, operating conditions, or real
  machinery.
- A bounded tree can still make large errors. On these validation examples,
  engine 29 at cycle 27 had the largest absolute error: 66.7297 cycles (true
  RUL 136; prediction 202.7297). This illustrates that aggregate metrics do
  not describe every engine.
- The model provides no calibrated uncertainty interval or confidence score.
- Sensor summaries discard sequence detail outside the configured window.
  Short or gapped histories can contain less information and are surfaced with
  warnings by the contextual service; warnings do not measure prediction
  reliability.
- RUL is an estimate in cycles, not a date or maintenance recommendation.
  Display clipping of negative estimates is a presentation rule and must not
  replace raw predictions in evaluation.
- Remote predictions have not been compared with the local references for the
  deployed application. The owner supplied
  <https://fleetpulseai.streamlit.app/> as its URL; an anonymous HTTP check on
  13 November 2026 redirected to Streamlit's `/-/login` route, so public access
  and remote parity were not verified. See P07-T3 [issue #245](https://github.com/Artfever/FleetpulseAI/issues/245).

## Reproduction and provenance

With the original local FD001 training file and tracked split manifest
available, rebuild and verify the P06 development artifacts with:

```powershell
python scripts/run_p06_validation.py
```

Then replay the saved inference service against the fixed validation oracle:

```powershell
python scripts/compare_service_parity.py
```

The latter command checks source/model/oracle provenance and requires 20 unique
engine/cutoff identities with exact raw prediction matches. Generated model,
feature, prediction, and parity-report files remain ignored local artifacts;
this repository tracks the model card and reproducible code, not the trained
binary or NASA-derived output tables.
