# FleetPulse issue backlog

The master plan supplies 26 phase gates and 234 numbered tasks: 78 each for Abdullah, Shaheer, and Taha. Issue links below are actual GitHub records. Issues track work; they do not mark it implemented. See `planning/backlog.json` for exact source requirements and `planning/issue-map.json` for stable IDs.

## Phase index

| Phase | Parent | Prerequisite gates | Shared outcome |
| --- | --- | --- | --- |
| P01 | [#6](https://github.com/Artfever/AI_PROJECT/issues/6) | none | Everyone can run the same app and tests |
| P02 | [#7](https://github.com/Artfever/AI_PROJECT/issues/7) | P01 [#6](https://github.com/Artfever/AI_PROJECT/issues/6) | Real FD001 files load, validate and display |
| P03 | [#8](https://github.com/Artfever/AI_PROJECT/issues/8) | P02 [#7](https://github.com/Artfever/AI_PROJECT/issues/7) | Correct training RUL and engine exploration |
| P04 | [#9](https://github.com/Artfever/AI_PROJECT/issues/9) | P03 [#8](https://github.com/Artfever/AI_PROJECT/issues/8) | Leakage-safe split and useful validation evaluator |
| P05 | [#10](https://github.com/Artfever/AI_PROJECT/issues/10) | P04 [#9](https://github.com/Artfever/AI_PROJECT/issues/9) | Tested past-only rolling feature extractor |
| P06 | [#11](https://github.com/Artfever/AI_PROJECT/issues/11) | P05 [#10](https://github.com/Artfever/AI_PROJECT/issues/10) | Reproducible feature tables, constant baseline and Decision Tree |
| P07 | [#12](https://github.com/Artfever/AI_PROJECT/issues/12) | P06 [#11](https://github.com/Artfever/AI_PROJECT/issues/11) | First deployed real prediction |
| P08 | [#13](https://github.com/Artfever/AI_PROJECT/issues/13) | P07 [#12](https://github.com/Artfever/AI_PROJECT/issues/12) | Random Forest candidate |
| P09 | [#14](https://github.com/Artfever/AI_PROJECT/issues/14) | P07 [#12](https://github.com/Artfever/AI_PROJECT/issues/12) | XGBoost candidate |
| P10 | [#15](https://github.com/Artfever/AI_PROJECT/issues/15) | P07 [#12](https://github.com/Artfever/AI_PROJECT/issues/12) | MLP candidate |
| P11 | [#20](https://github.com/Artfever/AI_PROJECT/issues/20) | P08 [#13](https://github.com/Artfever/AI_PROJECT/issues/13), P09 [#14](https://github.com/Artfever/AI_PROJECT/issues/14), P10 [#15](https://github.com/Artfever/AI_PROJECT/issues/15) | Controlled comparison and selected configuration |
| P12 | [#22](https://github.com/Artfever/AI_PROJECT/issues/22) | P11 [#20](https://github.com/Artfever/AI_PROJECT/issues/20) | All final models refitted and frozen |
| P13 | [#23](https://github.com/Artfever/AI_PROJECT/issues/23) | P12 [#22](https://github.com/Artfever/AI_PROJECT/issues/22) | Official test evaluation evidence |
| P14 | [#16](https://github.com/Artfever/AI_PROJECT/issues/16) | P07 [#12](https://github.com/Artfever/AI_PROJECT/issues/12) | Validated CSV upload and prediction |
| P15 | [#17](https://github.com/Artfever/AI_PROJECT/issues/17) | P07 [#12](https://github.com/Artfever/AI_PROJECT/issues/12) | Correct fleet-wide prediction table |
| P16 | [#18](https://github.com/Artfever/AI_PROJECT/issues/18) | P07 [#12](https://github.com/Artfever/AI_PROJECT/issues/12) | Past-only historical prediction replay |
| P17 | [#24](https://github.com/Artfever/AI_PROJECT/issues/24) | P12 [#22](https://github.com/Artfever/AI_PROJECT/issues/22), P16 [#18](https://github.com/Artfever/AI_PROJECT/issues/18) | SHAP and model disagreement |
| P18 | [#19](https://github.com/Artfever/AI_PROJECT/issues/19) | P07 [#12](https://github.com/Artfever/AI_PROJECT/issues/12) | Defined simulation and working EDD scheduler |
| P19 | [#21](https://github.com/Artfever/AI_PROJECT/issues/21) | P18 [#19](https://github.com/Artfever/AI_PROJECT/issues/19) | Valid, repeatable GA scheduler |
| P20 | [#25](https://github.com/Artfever/AI_PROJECT/issues/25) | P12 [#22](https://github.com/Artfever/AI_PROJECT/issues/22), P15 [#17](https://github.com/Artfever/AI_PROJECT/issues/17), P19 [#21](https://github.com/Artfever/AI_PROJECT/issues/21) | Real predictions drive both planners |
| P21 | [#26](https://github.com/Artfever/AI_PROJECT/issues/26) | P14 [#16](https://github.com/Artfever/AI_PROJECT/issues/16), P16 [#18](https://github.com/Artfever/AI_PROJECT/issues/18), P17 [#24](https://github.com/Artfever/AI_PROJECT/issues/24), P20 [#25](https://github.com/Artfever/AI_PROJECT/issues/25) | Complete connected product experience |
| P22 | [#27](https://github.com/Artfever/AI_PROJECT/issues/27) | P13 [#23](https://github.com/Artfever/AI_PROJECT/issues/23), P17 [#24](https://github.com/Artfever/AI_PROJECT/issues/24), P20 [#25](https://github.com/Artfever/AI_PROJECT/issues/25) | Error, robustness and scheduling studies |
| P23 | [#28](https://github.com/Artfever/AI_PROJECT/issues/28) | P13 [#23](https://github.com/Artfever/AI_PROJECT/issues/23), P21 [#26](https://github.com/Artfever/AI_PROJECT/issues/26) | Full public release and remote smoke checks |
| P24 | [#29](https://github.com/Artfever/AI_PROJECT/issues/29) | P22 [#27](https://github.com/Artfever/AI_PROJECT/issues/27), P23 [#28](https://github.com/Artfever/AI_PROJECT/issues/28) | Clean-install and claim audit; feature freeze |
| P25 | [#30](https://github.com/Artfever/AI_PROJECT/issues/30) | P24 [#29](https://github.com/Artfever/AI_PROJECT/issues/29) | Finished report, slides and rehearsed defense |
| P26 | [#31](https://github.com/Artfever/AI_PROJECT/issues/31) | P25 [#30](https://github.com/Artfever/AI_PROJECT/issues/30) | Extracted submission package verified |

## Phase tasks

### P01: Shared setup that actually runs — [#6](https://github.com/Artfever/AI_PROJECT/issues/6)

Gate: on each member's environment, `python -m pytest -q` and `streamlit run app/Home.py` work. Record commands and results, not just screenshots.

- **Abdullah:** P01-A1 [#32](https://github.com/Artfever/AI_PROJECT/issues/32) — Make one shared project folder and repository; P01-A2 [#108](https://github.com/Artfever/AI_PROJECT/issues/108) — Make Python imports and file locations work on every laptop; P01-A3 [#185](https://github.com/Artfever/AI_PROJECT/issues/185) — Add a small setup test and write the real setup commands
- **Shaheer:** P01-S1 [#186](https://github.com/Artfever/AI_PROJECT/issues/186) — Try the setup as a new user would; P01-S2 [#238](https://github.com/Artfever/AI_PROJECT/issues/238) — Make a tiny made-up engine history for tests; P01-S3 [#264](https://github.com/Artfever/AI_PROJECT/issues/264) — Make GitHub run tests when code changes
- **Taha:** P01-T1 [#33](https://github.com/Artfever/AI_PROJECT/issues/33) — Make Home and the five main app pages; P01-T2 [#109](https://github.com/Artfever/AI_PROJECT/issues/109) — Make navigation and useful empty screens; P01-T3 [#187](https://github.com/Artfever/AI_PROJECT/issues/187) — Click every page and write the intended user journey

### P02: Read and validate real FD001 data — [#7](https://github.com/Artfever/AI_PROJECT/issues/7)

Gate: demonstrate one actual engine; malformed-column and duplicate fixtures fail clearly; report matches loaded data. Raw files remain unchanged.

- **Abdullah:** P02-A1 [#34](https://github.com/Artfever/AI_PROJECT/issues/34) — Get the three original NASA files and record where they came from; P02-A2 [#110](https://github.com/Artfever/AI_PROJECT/issues/110) — Read the sensor files and the separate answer file correctly; P02-A3 [#188](https://github.com/Artfever/AI_PROJECT/issues/188) — Show a useful error if a file is missing or damaged
- **Shaheer:** P02-S1 [#35](https://github.com/Artfever/AI_PROJECT/issues/35) — Check readings, engine IDs, cycle numbers and duplicate rows; P02-S2 [#111](https://github.com/Artfever/AI_PROJECT/issues/111) — Count the actual records and inspect sensors that barely change; P02-S3 [#189](https://github.com/Artfever/AI_PROJECT/issues/189) — Save the quality findings and simple dataset notes
- **Taha:** P02-T1 [#36](https://github.com/Artfever/AI_PROJECT/issues/36) — Show the actual loaded dataset in the app; P02-T2 [#112](https://github.com/Artfever/AI_PROJECT/issues/112) — Let a user choose one engine and see its records; P02-T3 [#190](https://github.com/Artfever/AI_PROJECT/issues/190) — Explain missing data and how demo data is packaged

### P03: Correct RUL labels and a useful engine explorer — [#8](https://github.com/Artfever/AI_PROJECT/issues/8)

Gate: changing engine never mixes records; label tests pass; one member explains the formula using real records. Export a figure for later reporting.

- **Abdullah:** P03-A1 [#37](https://github.com/Artfever/AI_PROJECT/issues/37) — Calculate remaining cycles for each training row; P03-A2 [#113](https://github.com/Artfever/AI_PROJECT/issues/113) — Keep the answer columns away from prediction inputs; P03-A3 [#191](https://github.com/Artfever/AI_PROJECT/issues/191) — Test the calculation on a tiny example and actual engines
- **Shaheer:** P03-S1 [#38](https://github.com/Artfever/AI_PROJECT/issues/38) — Work out a tiny RUL example by hand; P03-S2 [#114](https://github.com/Artfever/AI_PROJECT/issues/114) — Check Abdullah’s answers independently; P03-S3 [#192](https://github.com/Artfever/AI_PROJECT/issues/192) — Draw real sensor histories and describe only what you can observe
- **Taha:** P03-T1 [#39](https://github.com/Artfever/AI_PROJECT/issues/39) — Add engine and sensor choices to the charts; P03-T2 [#115](https://github.com/Artfever/AI_PROJECT/issues/115) — Separate sensors whose number ranges are very different; P03-T3 [#193](https://github.com/Artfever/AI_PROJECT/issues/193) — Show known training RUL only in a clearly labeled analysis area

### P04: Safe development split and meaningful validation — [#9](https://github.com/Artfever/AI_PROJECT/issues/9)

Gate: no fitting/validation engine overlap; prefixes contain no future rows; metric tests pass; official test labels unused. Numeric unit IDs in train/test may repeat: identity must include dataset partition.

- **Abdullah:** P04-A1 [#40](https://github.com/Artfever/AI_PROJECT/issues/40) — Put whole engines into fitting and validation groups; P04-A2 [#116](https://github.com/Artfever/AI_PROJECT/issues/116) — Save exactly which engines and history stopping points were chosen; P04-A3 [#194](https://github.com/Artfever/AI_PROJECT/issues/194) — Prove the groups do not share engines and cutoffs are before failure
- **Shaheer:** P04-S1 [#41](https://github.com/Artfever/AI_PROJECT/issues/41) — Score predictions made from short visible histories; P04-S2 [#117](https://github.com/Artfever/AI_PROJECT/issues/117) — Implement the two error measures and verify them by hand; P04-S3 [#239](https://github.com/Artfever/AI_PROJECT/issues/239) — Record the evaluation rules before model comparisons
- **Taha:** P04-T1 [#42](https://github.com/Artfever/AI_PROJECT/issues/42) — Show the groups, stopping points and target ranges; P04-T2 [#118](https://github.com/Artfever/AI_PROJECT/issues/118) — Run a tiny test of the evaluator with a simple constant predictor; P04-T3 [#240](https://github.com/Artfever/AI_PROJECT/issues/240) — Explain visible history versus hidden future information

### P05: One reliable past-only feature extractor — [#10](https://github.com/Artfever/AI_PROJECT/issues/10)

Gate: fixed field names/order; finite features for minimum supported history; future-data test passes; no target/identity field in model feature list.

- **Abdullah:** P05-A1 [#43](https://github.com/Artfever/AI_PROJECT/issues/43) — Agree on exactly which feature names appear and in what order; P05-A2 [#119](https://github.com/Artfever/AI_PROJECT/issues/119) — Write checks for means, slopes and short histories; P05-A3 [#195](https://github.com/Artfever/AI_PROJECT/issues/195) — Prove that changing later readings does not change earlier features
- **Shaheer:** P05-S1 [#120](https://github.com/Artfever/AI_PROJECT/issues/120) — Turn recent readings into a few useful numbers; P05-S2 [#196](https://github.com/Artfever/AI_PROJECT/issues/196) — Handle histories shorter than 30 cycles, including one reading; P05-S3 [#241](https://github.com/Artfever/AI_PROJECT/issues/241) — Give every result a stable name and position
- **Taha:** P05-T1 [#44](https://github.com/Artfever/AI_PROJECT/issues/44) — Show the actual input history and calculated feature table; P05-T2 [#121](https://github.com/Artfever/AI_PROJECT/issues/121) — Let the team inspect the feature order and selected cycle; P05-T3 [#265](https://github.com/Artfever/AI_PROJECT/issues/265) — Write and independently check one small feature example

### P06: Model-ready tables, constant baseline and first Decision Tree — [#11](https://github.com/Artfever/AI_PROJECT/issues/11)

Gate: one documented command rebuilds tables and trains the tree; metrics match per-engine predictions; fresh-process reload predictions match original outputs. Plot predicted versus actual validation RUL.

- **Abdullah:** P06-A1 [#45](https://github.com/Artfever/AI_PROJECT/issues/45) — Build one training-feature row for every eligible fitting cycle; P06-A2 [#122](https://github.com/Artfever/AI_PROJECT/issues/122) — Build validation rows only at the saved stopping points; P06-A3 [#197](https://github.com/Artfever/AI_PROJECT/issues/197) — Save the exact feature names, order and matching labels
- **Shaheer:** P06-S1 [#46](https://github.com/Artfever/AI_PROJECT/issues/46) — Make a baseline that always predicts one fitting-data statistic; P06-S2 [#123](https://github.com/Artfever/AI_PROJECT/issues/123) — Score it on the saved validation examples; P06-S3 [#242](https://github.com/Artfever/AI_PROJECT/issues/242) — Define one common results-file format for all models
- **Taha:** P06-T1 [#47](https://github.com/Artfever/AI_PROJECT/issues/47) — Train your first Decision Tree using the common table; P06-T2 [#124](https://github.com/Artfever/AI_PROJECT/issues/124) — Save the model, settings and actual predictions; P06-T3 [#243](https://github.com/Artfever/AI_PROJECT/issues/243) — Compare it with the constant baseline in the app

### P07: First real deployed prediction — [#12](https://github.com/Artfever/AI_PROJECT/issues/12)

Gate: public app runs a saved trained model on a selected history; outputs match local inference; no true RUL enters prediction. If deployment fails, record the blocker and fix it before polishing the UI.

- **Abdullah:** P07-A1 [#48](https://github.com/Artfever/AI_PROJECT/issues/48) — Make one service that validates history and runs a saved model; P07-A2 [#125](https://github.com/Artfever/AI_PROJECT/issues/125) — Return raw estimate, displayed cycles and useful model information; P07-A3 [#198](https://github.com/Artfever/AI_PROJECT/issues/198) — Reject bad features or missing model files clearly
- **Shaheer:** P07-S1 [#49](https://github.com/Artfever/AI_PROJECT/issues/49) — Compare the service against offline saved predictions; P07-S2 [#126](https://github.com/Artfever/AI_PROJECT/issues/126) — Check short histories and wrong model names; P07-S3 [#244](https://github.com/Artfever/AI_PROJECT/issues/244) — Write the first honest model card from measured results
- **Taha:** P07-T1 [#50](https://github.com/Artfever/AI_PROJECT/issues/50) — Let a user select an engine and ask the saved model for a prediction; P07-T2 [#127](https://github.com/Artfever/AI_PROJECT/issues/127) — Package demo data and load models efficiently; P07-T3 [#245](https://github.com/Artfever/AI_PROJECT/issues/245) — Deploy the first app and compare three remote predictions

### P08: Random Forest candidate — [#13](https://github.com/Artfever/AI_PROJECT/issues/13)

Gate: actual held-out validation results, reload parity and real forest inference in the app. A stronger score than the tree is a result to measure, not a completion requirement.

- **Abdullah:** P08-A1 [#51](https://github.com/Artfever/AI_PROJECT/issues/51) — Train a modest Random Forest using the same data rules; P08-A2 [#128](https://github.com/Artfever/AI_PROJECT/issues/128) — Save measured errors, settings and predictions; P08-A3 [#199](https://github.com/Artfever/AI_PROJECT/issues/199) — Register the saved forest with the shared service
- **Shaheer:** P08-S1 [#52](https://github.com/Artfever/AI_PROJECT/issues/52) — Audit the forest’s validation engines and errors; P08-S2 [#129](https://github.com/Artfever/AI_PROJECT/issues/129) — Inspect examples it predicts poorly; P08-S3 [#246](https://github.com/Artfever/AI_PROJECT/issues/246) — Check that its model and feature versions agree
- **Taha:** P08-T1 [#53](https://github.com/Artfever/AI_PROJECT/issues/53) — Add the trained forest to the model selector; P08-T2 [#130](https://github.com/Artfever/AI_PROJECT/issues/130) — Keep the selected engine and history when switching models; P08-T3 [#247](https://github.com/Artfever/AI_PROJECT/issues/247) — Show actual forest scores in the comparison

### P09: XGBoost candidate — [#14](https://github.com/Artfever/AI_PROJECT/issues/14)

Gate: saved boosted model, traceable metrics, service prediction and parity test. No assumption that XGBoost must win.

- **Abdullah:** P09-A1 [#54](https://github.com/Artfever/AI_PROJECT/issues/54) — Review the boosted model’s feature and target handling; P09-A2 [#131](https://github.com/Artfever/AI_PROJECT/issues/131) — Check loading and fair runtime measurement; P09-A3 [#248](https://github.com/Artfever/AI_PROJECT/issues/248) — Record the software versions required to reload it
- **Shaheer:** P09-S1 [#55](https://github.com/Artfever/AI_PROJECT/issues/55) — Independently calculate boosted-model errors; P09-S2 [#132](https://github.com/Artfever/AI_PROJECT/issues/132) — Write an honest comparison with earlier models; P09-S3 [#249](https://github.com/Artfever/AI_PROJECT/issues/249) — Check invalid readings are rejected before prediction
- **Taha:** P09-T1 [#56](https://github.com/Artfever/AI_PROJECT/issues/56) — Implement the first XGBoost training script; P09-T2 [#133](https://github.com/Artfever/AI_PROJECT/issues/133) — Run one bounded training experiment and save actual results; P09-T3 [#200](https://github.com/Artfever/AI_PROJECT/issues/200) — Save and register the candidate for prediction

### P10: PyTorch MLP candidate — [#15](https://github.com/Artfever/AI_PROJECT/issues/15)

Gate: neural network trains, loss is finite, best checkpoint and scaler exist, service inference matches offline inference. Backpropagation and the scaler's role can be explained by all three.

- **Abdullah:** P10-A1 [#57](https://github.com/Artfever/AI_PROJECT/issues/57) — Load neural weights, architecture and scaler as one bundle; P10-A2 [#134](https://github.com/Artfever/AI_PROJECT/issues/134) — Test shape, order, CPU use and finite output; P10-A3 [#250](https://github.com/Artfever/AI_PROJECT/issues/250) — Check scaler numbers were learned from fitting engines only
- **Shaheer:** P10-S1 [#58](https://github.com/Artfever/AI_PROJECT/issues/58) — Build a small neural regressor and training loop; P10-S2 [#135](https://github.com/Artfever/AI_PROJECT/issues/135) — Scale fitting inputs correctly and stop using validation results; P10-S3 [#201](https://github.com/Artfever/AI_PROJECT/issues/201) — Save best weights, architecture, scaler, curves and best epoch
- **Taha:** P10-T1 [#59](https://github.com/Artfever/AI_PROJECT/issues/59) — Add the trained MLP to the selector and results; P10-T2 [#136](https://github.com/Artfever/AI_PROJECT/issues/136) — Show its real learning curves with clear labels; P10-T3 [#251](https://github.com/Artfever/AI_PROJECT/issues/251) — Ensure opening the app never starts model training

### P11: Controlled model selection and small experiments — [#20](https://github.com/Artfever/AI_PROJECT/issues/20)

Gate: selected window/features/hyperparameters, justified production choice and frozen MLP refit epoch rule. Official test labels remain unused.

- **Abdullah:** P11-A1 [#60](https://github.com/Artfever/AI_PROJECT/issues/60) — Run a few predeclared forest and boosting settings; P11-A2 [#137](https://github.com/Artfever/AI_PROJECT/issues/137) — Try a small, controlled feature comparison; P11-A3 [#202](https://github.com/Artfever/AI_PROJECT/issues/202) — Save good and bad experiments with timing
- **Shaheer:** P11-S1 [#61](https://github.com/Artfever/AI_PROJECT/issues/61) — Compare 10-,20- and 30-cycle windows on one model; P11-S2 [#138](https://github.com/Artfever/AI_PROJECT/issues/138) — Try a few neural settings and record best epochs; P11-S3 [#203](https://github.com/Artfever/AI_PROJECT/issues/203) — Summarize whether added complexity actually helps
- **Taha:** P11-T1 [#62](https://github.com/Artfever/AI_PROJECT/issues/62) — Check model scores describe the same validation problem; P11-T2 [#139](https://github.com/Artfever/AI_PROJECT/issues/139) — Save the final selection decision and comparison view; P11-T3 [#252](https://github.com/Artfever/AI_PROJECT/issues/252) — Help the team choose and explain the production model

### P12: Refit and freeze all final artifacts — [#22](https://github.com/Artfever/AI_PROJECT/issues/22)

Gate: all four final bundles load, schema tests pass and parity checks succeed. No official test scores have influenced these decisions.

- **Abdullah:** P12-A1 [#63](https://github.com/Artfever/AI_PROJECT/issues/63) — Retrain all final tree models and the constant baseline on original training engines; P12-A2 [#140](https://github.com/Artfever/AI_PROJECT/issues/140) — Refit any required preprocessing correctly; P12-A3 [#204](https://github.com/Artfever/AI_PROJECT/issues/204) — Save fixed versioned bundles and file checksums
- **Shaheer:** P12-S1 [#64](https://github.com/Artfever/AI_PROJECT/issues/64) — Fit a fresh scaler using all original training-engine features; P12-S2 [#141](https://github.com/Artfever/AI_PROJECT/issues/141) — Retrain the MLP using its already chosen epoch budget; P12-S3 [#205](https://github.com/Artfever/AI_PROJECT/issues/205) — Save final weights/scaler separately from development models
- **Taha:** P12-T1 [#65](https://github.com/Artfever/AI_PROJECT/issues/65) — Clearly separate development and final models in the registry; P12-T2 [#142](https://github.com/Artfever/AI_PROJECT/issues/142) — Test each final model in a new process; P12-T3 [#253](https://github.com/Artfever/AI_PROJECT/issues/253) — Update cache versions and the model inventory

### P13: Official held-out test evaluation — [#23](https://github.com/Artfever/AI_PROJECT/issues/23)

Gate: correct official pairing, complete metric provenance and reproducible frozen evaluation. Re-running unchanged models for auditing is allowed; retuning against these test results is not part of this plan.

- **Abdullah:** P13-A1 [#66](https://github.com/Artfever/AI_PROJECT/issues/66) — Audit official engine-to-label pairing; P13-A2 [#143](https://github.com/Artfever/AI_PROJECT/issues/143) — Recalculate final scores independently from saved predictions; P13-A3 [#206](https://github.com/Artfever/AI_PROJECT/issues/206) — Check evaluated bundles match frozen final files
- **Shaheer:** P13-S1 [#67](https://github.com/Artfever/AI_PROJECT/issues/67) — Predict once per official test engine at its last observed cycle; P13-S2 [#144](https://github.com/Artfever/AI_PROJECT/issues/144) — Pair predictions with the separate official RUL answers; P13-S3 [#207](https://github.com/Artfever/AI_PROJECT/issues/207) — Save all final predictions, scores and error figures
- **Taha:** P13-T1 [#68](https://github.com/Artfever/AI_PROJECT/issues/68) — Separate development validation from official test results; P13-T2 [#145](https://github.com/Artfever/AI_PROJECT/issues/145) — Show units, sample counts and model versions; P13-T3 [#254](https://github.com/Artfever/AI_PROJECT/issues/254) — Export real result tables without filling gaps with invented numbers

### P14: Safe CSV upload — [#16](https://github.com/Artfever/AI_PROJECT/issues/16)

Gate: clean uploaded CSV produces matching output; each malformed fixture returns a specific useful error without a public traceback.

- **Abdullah:** P14-A1 [#69](https://github.com/Artfever/AI_PROJECT/issues/69) — Validate every required CSV field and value; P14-A2 [#146](https://github.com/Artfever/AI_PROJECT/issues/146) — Reject guessed columns, target columns and unsorted cycles; P14-A3 [#208](https://github.com/Artfever/AI_PROJECT/issues/208) — Reject incomplete/mixed histories unless a single engine is explicitly selected
- **Shaheer:** P14-S1 [#70](https://github.com/Artfever/AI_PROJECT/issues/70) — Make good and bad upload examples; P14-S2 [#147](https://github.com/Artfever/AI_PROJECT/issues/147) — Prove bad histories never reach a model; P14-S3 [#209](https://github.com/Artfever/AI_PROJECT/issues/209) — Check supported short histories keep the same feature layout
- **Taha:** P14-T1 [#71](https://github.com/Artfever/AI_PROJECT/issues/71) — Give users a correct example CSV; P14-T2 [#148](https://github.com/Artfever/AI_PROJECT/issues/148) — Build upload, preview and clear errors; P14-T3 [#255](https://github.com/Artfever/AI_PROJECT/issues/255) — Send valid uploads through the common predictor

### P15: Fleet predictions with correct identity mapping — [#17](https://github.com/Artfever/AI_PROJECT/issues/17)

Gate: batch/single parity and ID tests pass; sorting/filtering do not change predictions or lose engine identity.

- **Abdullah:** P15-A1 [#72](https://github.com/Artfever/AI_PROJECT/issues/72) — Predict several engine histories together; P15-A2 [#149](https://github.com/Artfever/AI_PROJECT/issues/149) — Return IDs, cycles, estimates, versions and per-engine errors; P15-A3 [#210](https://github.com/Artfever/AI_PROJECT/issues/210) — Keep each result attached to the right engine after filtering
- **Shaheer:** P15-S1 [#73](https://github.com/Artfever/AI_PROJECT/issues/73) — Compare batch predictions with single-engine calls; P15-S2 [#150](https://github.com/Artfever/AI_PROJECT/issues/150) — Test bad engines, ties and duplicate identities; P15-S3 [#211](https://github.com/Artfever/AI_PROJECT/issues/211) — Explain planning priority without claiming a confirmed fault
- **Taha:** P15-T1 [#74](https://github.com/Artfever/AI_PROJECT/issues/74) — Display actual fleet predictions and model details; P15-T2 [#151](https://github.com/Artfever/AI_PROJECT/issues/151) — Add sorting, thresholds and engine selection; P15-T3 [#256](https://github.com/Artfever/AI_PROJECT/issues/256) — Remember selected engines for the planner

### P16: Historical prediction replay — [#18](https://github.com/Artfever/AI_PROJECT/issues/18)

Gate: future-row mutation test passes; slider and chart agree on cutoff; replay is labeled correctly and runs at bounded cost.

- **Abdullah:** P16-A1 [#75](https://github.com/Artfever/AI_PROJECT/issues/75) — Predict repeatedly at selected earlier cycles; P16-A2 [#152](https://github.com/Artfever/AI_PROJECT/issues/152) — Cut history separately for every replay point; P16-A3 [#212](https://github.com/Artfever/AI_PROJECT/issues/212) — Cache using history, model and feature versions
- **Shaheer:** P16-S1 [#76](https://github.com/Artfever/AI_PROJECT/issues/76) — Change future readings in tests and compare earlier outputs; P16-S2 [#153](https://github.com/Artfever/AI_PROJECT/issues/153) — Check each replay point independently; P16-S3 [#213](https://github.com/Artfever/AI_PROJECT/issues/213) — Label training examples honestly after final refitting
- **Taha:** P16-T1 [#77](https://github.com/Artfever/AI_PROJECT/issues/77) — Connect cycle slider, sensor history and prediction; P16-T2 [#154](https://github.com/Artfever/AI_PROJECT/issues/154) — Show earlier predictions as a timeline; P16-T3 [#257](https://github.com/Artfever/AI_PROJECT/issues/257) — Display model version and whether the engine was seen in fitting

### P17: SHAP explanations and model disagreement — [#24](https://github.com/Artfever/AI_PROJECT/issues/24)

Gate: exact prediction/explanation version match; correct feature names; model table uses the same input prefix; missing explanations fail gracefully.

- **Abdullah:** P17-A1 [#78](https://github.com/Artfever/AI_PROJECT/issues/78) — Compare final models on the same history; P17-A2 [#155](https://github.com/Artfever/AI_PROJECT/issues/155) — Return estimates and a clearly defined spread; P17-A3 [#214](https://github.com/Artfever/AI_PROJECT/issues/214) — Check prediction and explanation versions agree
- **Shaheer:** P17-S1 [#79](https://github.com/Artfever/AI_PROJECT/issues/79) — Explain a frozen supported tree prediction using its actual feature row; P17-S2 [#156](https://github.com/Artfever/AI_PROJECT/issues/156) — Choose a documented training-data reference sample; P17-S3 [#215](https://github.com/Artfever/AI_PROJECT/issues/215) — Return named contributions and test the numerical explanation
- **Taha:** P17-T1 [#80](https://github.com/Artfever/AI_PROJECT/issues/80) — Show features pushing an estimate up or down; P17-T2 [#157](https://github.com/Artfever/AI_PROJECT/issues/157) — Show model comparison and spread without fake confidence; P17-T3 [#258](https://github.com/Artfever/AI_PROJECT/issues/258) — Explain limits in simple language

### P18: Define the simulation and implement EDD — [#19](https://github.com/Artfever/AI_PROJECT/issues/19)

Gate: see the Appendix B worked example; no overlapping jobs on one team; all jobs scheduled once; penalty matches hand calculation. Early completion is allowed and not penalized in this initial objective.

- **Abdullah:** P18-A1 [#81](https://github.com/Artfever/AI_PROJECT/issues/81) — Convert an engine ordering into team/time assignments; P18-A2 [#158](https://github.com/Artfever/AI_PROJECT/issues/158) — Make EDD order and use the same decoder; P18-A3 [#216](https://github.com/Artfever/AI_PROJECT/issues/216) — Return timing, lateness and overflow with hard-rule checks
- **Shaheer:** P18-S1 [#82](https://github.com/Artfever/AI_PROJECT/issues/82) — Define each synthetic job’s duration and priority; P18-S2 [#159](https://github.com/Artfever/AI_PROJECT/issues/159) — Define completion deadlines and late work; P18-S3 [#217](https://github.com/Artfever/AI_PROJECT/issues/217) — Write one shared score and hard feasibility rules
- **Taha:** P18-T1 [#83](https://github.com/Artfever/AI_PROJECT/issues/83) — Build a small form for a simulated maintenance scenario; P18-T2 [#160](https://github.com/Artfever/AI_PROJECT/issues/160) — Show the baseline table and timeline; P18-T3 [#218](https://github.com/Artfever/AI_PROJECT/issues/218) — Save the scenario and its expected hand-checked output

### P19: Genetic Algorithm with valid permutations — [#21](https://github.com/Artfever/AI_PROJECT/issues/21)

Gate: valid schedules, repeatable seeded output and exact-reference checks. With EDD seeded and elitism, returned best score must not exceed that seeded EDD score under the same objective; equality is entirely acceptable. This is a design invariant, not evidence that GA improves every scenario.

- **Abdullah:** P19-A1 [#84](https://github.com/Artfever/AI_PROJECT/issues/84) — Test that GA operations keep every engine exactly once; P19-A2 [#161](https://github.com/Artfever/AI_PROJECT/issues/161) — Test repeatability, capacity and best-score tracking; P19-A3 [#259](https://github.com/Artfever/AI_PROJECT/issues/259) — Check tiny cases against all possible engine orders
- **Shaheer:** P19-S1 [#85](https://github.com/Artfever/AI_PROJECT/issues/85) — Start with engine-ID orderings including EDD; P19-S2 [#162](https://github.com/Artfever/AI_PROJECT/issues/162) — Add selection, safe crossover, swap mutation and elitism; P19-S3 [#219](https://github.com/Artfever/AI_PROJECT/issues/219) — Run a bounded seeded search using the shared decoder and score
- **Taha:** P19-T1 [#86](https://github.com/Artfever/AI_PROJECT/issues/86) — Add algorithm and bounded GA controls; P19-T2 [#163](https://github.com/Artfever/AI_PROJECT/issues/163) — Show best-so-far score and method summary; P19-T3 [#220](https://github.com/Artfever/AI_PROJECT/issues/220) — Handle tiny and invalid scenarios cleanly

### P20: Real model predictions drive both schedulers — [#25](https://github.com/Artfever/AI_PROJECT/issues/25)

Gate: user selects real engine histories, predicts, selects a fleet and compares two valid schedules. Changing a buffer/capacity does not silently change model predictions.

- **Abdullah:** P20-A1 [#87](https://github.com/Artfever/AI_PROJECT/issues/87) — Send one fleet-prediction snapshot into both schedulers; P20-A2 [#164](https://github.com/Artfever/AI_PROJECT/issues/164) — Use consistent nonnegative RUL without early rounding; P20-A3 [#221](https://github.com/Artfever/AI_PROJECT/issues/221) — Return schedules and the same summary measures
- **Shaheer:** P20-S1 [#88](https://github.com/Artfever/AI_PROJECT/issues/88) — Check predictions reach planning correctly; P20-S2 [#165](https://github.com/Artfever/AI_PROJECT/issues/165) — Test urgent engines, capacity pressure and varied jobs; P20-S3 [#222](https://github.com/Artfever/AI_PROJECT/issues/222) — Save paired comparisons with model and scenario provenance
- **Taha:** P20-T1 [#89](https://github.com/Artfever/AI_PROJECT/issues/89) — Bring selected fleet engines into the planner; P20-T2 [#166](https://github.com/Artfever/AI_PROJECT/issues/166) — Show both schedules and comparable numbers; P20-T3 [#260](https://github.com/Artfever/AI_PROJECT/issues/260) — Separate model estimates from user assumptions and show late/overflow work

### P21: Complete connected application — [#26](https://github.com/Artfever/AI_PROJECT/issues/26)

Gate: repeatable end-to-end demonstration without manual data substitution, mixed engine state, fabricated results or missing principal screens.

- **Abdullah:** P21-A1 [#90](https://github.com/Artfever/AI_PROJECT/issues/90) — Audit state and cache keys; P21-A2 [#167](https://github.com/Artfever/AI_PROJECT/issues/167) — Remove duplicated prediction/feature code from pages; P21-A3 [#223](https://github.com/Artfever/AI_PROJECT/issues/223) — Check built-in and uploaded journeys end to end
- **Shaheer:** P21-S1 [#91](https://github.com/Artfever/AI_PROJECT/issues/91) — Check scientific labels on every screen; P21-S2 [#168](https://github.com/Artfever/AI_PROJECT/issues/168) — Remove unsupported percentages, diagnoses and savings claims; P21-S3 [#224](https://github.com/Artfever/AI_PROJECT/issues/224) — Trace displayed values back to real outputs
- **Taha:** P21-T1 [#92](https://github.com/Artfever/AI_PROJECT/issues/92) — Connect all six screens into one journey; P21-T2 [#169](https://github.com/Artfever/AI_PROJECT/issues/169) — Preserve the intended engine/model/cycle between screens; P21-T3 [#225](https://github.com/Artfever/AI_PROJECT/issues/225) — Fix readable forms, charts and missing-result states

### P22: Quantitative evidence beyond a single average — [#27](https://github.com/Artfever/AI_PROJECT/issues/27)

Gate: essential model error plots and paired scheduler comparisons exist with provenance. No metric-confidence interval is presented as an individual prediction interval.

- **Abdullah:** P22-A1 [#93](https://github.com/Artfever/AI_PROJECT/issues/93) — Run fixed fleet scenarios with different sizes and team counts; P22-A2 [#170](https://github.com/Artfever/AI_PROJECT/issues/170) — Compare both schedulers across declared seeds; P22-A3 [#226](https://github.com/Artfever/AI_PROJECT/issues/226) — Measure speed and improve only proven bottlenecks
- **Shaheer:** P22-S1 [#94](https://github.com/Artfever/AI_PROJECT/issues/94) — Plot errors and summarize them by true RUL range; P22-S2 [#171](https://github.com/Artfever/AI_PROJECT/issues/171) — Estimate validation error variability by resampling whole engines; P22-S3 [#227](https://github.com/Artfever/AI_PROJECT/issues/227) — Test small artificial sensor changes on genuine development holdouts
- **Taha:** P22-T1 [#95](https://github.com/Artfever/AI_PROJECT/issues/95) — Display saved model and scheduling studies; P22-T2 [#172](https://github.com/Artfever/AI_PROJECT/issues/172) — Separate saved experiments from the current live scenario; P22-T3 [#228](https://github.com/Artfever/AI_PROJECT/issues/228) — Export clearly labeled figures and real result paragraphs

### P23: Full public release and remote checks — [#28](https://github.com/Artfever/AI_PROJECT/issues/28)

Gate: public full flow and local/remote parity pass, including malformed input. A temporary screen recording does not substitute for the required working app/live demo.

- **Abdullah:** P23-A1 [#96](https://github.com/Artfever/AI_PROJECT/issues/96) — Check deployment includes every needed file; P23-A2 [#173](https://github.com/Artfever/AI_PROJECT/issues/173) — Check memory/load behavior and input limits; P23-A3 [#261](https://github.com/Artfever/AI_PROJECT/issues/261) — Compare remote predictions and schedules with local references
- **Shaheer:** P23-S1 [#97](https://github.com/Artfever/AI_PROJECT/issues/97) — Check remote metrics point to the intended files; P23-S2 [#174](https://github.com/Artfever/AI_PROJECT/issues/174) — Exercise explanations and disagreement; P23-S3 [#262](https://github.com/Artfever/AI_PROJECT/issues/262) — Test remote upload failures and record evidence
- **Taha:** P23-T1 [#98](https://github.com/Artfever/AI_PROJECT/issues/98) — Deploy the full release with final bundles; P23-T2 [#175](https://github.com/Artfever/AI_PROJECT/issues/175) — Test cold startup and the complete user flow; P23-T3 [#229](https://github.com/Artfever/AI_PROJECT/issues/229) — Record actual URL, version and fixes

### P24: Independent reproduction and feature freeze — [#29](https://github.com/Artfever/AI_PROJECT/issues/29)

Gate: clean install, public flow, mandatory tests and metric audit pass. No unresolved blocker. Cosmetic improvements are deferred.

- **Abdullah:** P24-A1 [#99](https://github.com/Artfever/AI_PROJECT/issues/99) — Install from the README in a fresh folder; P24-A2 [#176](https://github.com/Artfever/AI_PROJECT/issues/176) — Reproduce a declared development experiment; P24-A3 [#230](https://github.com/Artfever/AI_PROJECT/issues/230) — Check final file hashes and make a release candidate
- **Shaheer:** P24-S1 [#100](https://github.com/Artfever/AI_PROJECT/issues/100) — Trace every reported result to its actual model and split; P24-S2 [#177](https://github.com/Artfever/AI_PROJECT/issues/177) — Recheck frozen evaluation without retuning; P24-S3 [#231](https://github.com/Artfever/AI_PROJECT/issues/231) — Audit claims, references and shared understanding
- **Taha:** P24-T1 [#101](https://github.com/Artfever/AI_PROJECT/issues/101) — Run full and uploaded demos independently; P24-T2 [#178](https://github.com/Artfever/AI_PROJECT/issues/178) — Capture real screenshots and note known issues; P24-T3 [#232](https://github.com/Artfever/AI_PROJECT/issues/232) — Freeze features and own the remaining product checklist

### P25: Complete report, slides and shared defense — [#30](https://github.com/Artfever/AI_PROJECT/issues/30)

Gate: report includes every mandatory section; slides contain actual qualitative/quantitative evidence; each member can explain and run the whole project, not only their own packet.

- **Abdullah:** P25-A1 [#102](https://github.com/Artfever/AI_PROJECT/issues/102) — Finish data, features and architecture chapters; P25-A2 [#179](https://github.com/Artfever/AI_PROJECT/issues/179) — Create diagrams and verify real reproduction commands; P25-A3 [#233](https://github.com/Artfever/AI_PROJECT/issues/233) — Prepare slides and teach the data/service design
- **Shaheer:** P25-S1 [#103](https://github.com/Artfever/AI_PROJECT/issues/103) — Finish model, evaluation and scheduling chapters; P25-S2 [#180](https://github.com/Artfever/AI_PROJECT/issues/180) — Caption actual evidence and explain limitations; P25-S3 [#234](https://github.com/Artfever/AI_PROJECT/issues/234) — Prepare AI slides and answer technical questions
- **Taha:** P25-T1 [#104](https://github.com/Artfever/AI_PROJECT/issues/104) — Assemble problem, application, report and slides; P25-T2 [#181](https://github.com/Artfever/AI_PROJECT/issues/181) — Check headings, references and export layouts; P25-T3 [#235](https://github.com/Artfever/AI_PROJECT/issues/235) — Write clicks for a repeatable live demo and rehearse together

### P26: Verify the submitted package — [#31](https://github.com/Artfever/AI_PROJECT/issues/31)

Gate: all three review and sign off the exact archive; extracted code and deployed app work; group is ready for submission by 6 December and live demonstration 7-9 December. Preparing this plan does not submit anything.

- **Abdullah:** P26-A1 [#105](https://github.com/Artfever/AI_PROJECT/issues/105) — Collect runnable source, models, scripts and tests; P26-A2 [#182](https://github.com/Artfever/AI_PROJECT/issues/182) — Exclude caches, secrets and machine-specific paths; P26-A3 [#236](https://github.com/Artfever/AI_PROJECT/issues/236) — Extract the actual final ZIP and run its instructions
- **Shaheer:** P26-S1 [#106](https://github.com/Artfever/AI_PROJECT/issues/106) — Check the complete AI evidence inventory; P26-S2 [#183](https://github.com/Artfever/AI_PROJECT/issues/183) — Compare versions and claims across report, slides and app; P26-S3 [#237](https://github.com/Artfever/AI_PROJECT/issues/237) — Sign off only the evidence you actually verified
- **Taha:** P26-T1 [#107](https://github.com/Artfever/AI_PROJECT/issues/107) — Include final report, slides, URL and demo procedure; P26-T2 [#184](https://github.com/Artfever/AI_PROJECT/issues/184) — Open final exports and test the app once more; P26-T3 [#263](https://github.com/Artfever/AI_PROJECT/issues/263) — Assemble one final ZIP and identify the human submitter

## Per-person index

### Abdullah (78 tasks)

| Phase | Three assigned tasks |
| --- | --- |
| P01 | P01-A1 [#32](https://github.com/Artfever/AI_PROJECT/issues/32), P01-A2 [#108](https://github.com/Artfever/AI_PROJECT/issues/108), P01-A3 [#185](https://github.com/Artfever/AI_PROJECT/issues/185) |
| P02 | P02-A1 [#34](https://github.com/Artfever/AI_PROJECT/issues/34), P02-A2 [#110](https://github.com/Artfever/AI_PROJECT/issues/110), P02-A3 [#188](https://github.com/Artfever/AI_PROJECT/issues/188) |
| P03 | P03-A1 [#37](https://github.com/Artfever/AI_PROJECT/issues/37), P03-A2 [#113](https://github.com/Artfever/AI_PROJECT/issues/113), P03-A3 [#191](https://github.com/Artfever/AI_PROJECT/issues/191) |
| P04 | P04-A1 [#40](https://github.com/Artfever/AI_PROJECT/issues/40), P04-A2 [#116](https://github.com/Artfever/AI_PROJECT/issues/116), P04-A3 [#194](https://github.com/Artfever/AI_PROJECT/issues/194) |
| P05 | P05-A1 [#43](https://github.com/Artfever/AI_PROJECT/issues/43), P05-A2 [#119](https://github.com/Artfever/AI_PROJECT/issues/119), P05-A3 [#195](https://github.com/Artfever/AI_PROJECT/issues/195) |
| P06 | P06-A1 [#45](https://github.com/Artfever/AI_PROJECT/issues/45), P06-A2 [#122](https://github.com/Artfever/AI_PROJECT/issues/122), P06-A3 [#197](https://github.com/Artfever/AI_PROJECT/issues/197) |
| P07 | P07-A1 [#48](https://github.com/Artfever/AI_PROJECT/issues/48), P07-A2 [#125](https://github.com/Artfever/AI_PROJECT/issues/125), P07-A3 [#198](https://github.com/Artfever/AI_PROJECT/issues/198) |
| P08 | P08-A1 [#51](https://github.com/Artfever/AI_PROJECT/issues/51), P08-A2 [#128](https://github.com/Artfever/AI_PROJECT/issues/128), P08-A3 [#199](https://github.com/Artfever/AI_PROJECT/issues/199) |
| P09 | P09-A1 [#54](https://github.com/Artfever/AI_PROJECT/issues/54), P09-A2 [#131](https://github.com/Artfever/AI_PROJECT/issues/131), P09-A3 [#248](https://github.com/Artfever/AI_PROJECT/issues/248) |
| P10 | P10-A1 [#57](https://github.com/Artfever/AI_PROJECT/issues/57), P10-A2 [#134](https://github.com/Artfever/AI_PROJECT/issues/134), P10-A3 [#250](https://github.com/Artfever/AI_PROJECT/issues/250) |
| P11 | P11-A1 [#60](https://github.com/Artfever/AI_PROJECT/issues/60), P11-A2 [#137](https://github.com/Artfever/AI_PROJECT/issues/137), P11-A3 [#202](https://github.com/Artfever/AI_PROJECT/issues/202) |
| P12 | P12-A1 [#63](https://github.com/Artfever/AI_PROJECT/issues/63), P12-A2 [#140](https://github.com/Artfever/AI_PROJECT/issues/140), P12-A3 [#204](https://github.com/Artfever/AI_PROJECT/issues/204) |
| P13 | P13-A1 [#66](https://github.com/Artfever/AI_PROJECT/issues/66), P13-A2 [#143](https://github.com/Artfever/AI_PROJECT/issues/143), P13-A3 [#206](https://github.com/Artfever/AI_PROJECT/issues/206) |
| P14 | P14-A1 [#69](https://github.com/Artfever/AI_PROJECT/issues/69), P14-A2 [#146](https://github.com/Artfever/AI_PROJECT/issues/146), P14-A3 [#208](https://github.com/Artfever/AI_PROJECT/issues/208) |
| P15 | P15-A1 [#72](https://github.com/Artfever/AI_PROJECT/issues/72), P15-A2 [#149](https://github.com/Artfever/AI_PROJECT/issues/149), P15-A3 [#210](https://github.com/Artfever/AI_PROJECT/issues/210) |
| P16 | P16-A1 [#75](https://github.com/Artfever/AI_PROJECT/issues/75), P16-A2 [#152](https://github.com/Artfever/AI_PROJECT/issues/152), P16-A3 [#212](https://github.com/Artfever/AI_PROJECT/issues/212) |
| P17 | P17-A1 [#78](https://github.com/Artfever/AI_PROJECT/issues/78), P17-A2 [#155](https://github.com/Artfever/AI_PROJECT/issues/155), P17-A3 [#214](https://github.com/Artfever/AI_PROJECT/issues/214) |
| P18 | P18-A1 [#81](https://github.com/Artfever/AI_PROJECT/issues/81), P18-A2 [#158](https://github.com/Artfever/AI_PROJECT/issues/158), P18-A3 [#216](https://github.com/Artfever/AI_PROJECT/issues/216) |
| P19 | P19-A1 [#84](https://github.com/Artfever/AI_PROJECT/issues/84), P19-A2 [#161](https://github.com/Artfever/AI_PROJECT/issues/161), P19-A3 [#259](https://github.com/Artfever/AI_PROJECT/issues/259) |
| P20 | P20-A1 [#87](https://github.com/Artfever/AI_PROJECT/issues/87), P20-A2 [#164](https://github.com/Artfever/AI_PROJECT/issues/164), P20-A3 [#221](https://github.com/Artfever/AI_PROJECT/issues/221) |
| P21 | P21-A1 [#90](https://github.com/Artfever/AI_PROJECT/issues/90), P21-A2 [#167](https://github.com/Artfever/AI_PROJECT/issues/167), P21-A3 [#223](https://github.com/Artfever/AI_PROJECT/issues/223) |
| P22 | P22-A1 [#93](https://github.com/Artfever/AI_PROJECT/issues/93), P22-A2 [#170](https://github.com/Artfever/AI_PROJECT/issues/170), P22-A3 [#226](https://github.com/Artfever/AI_PROJECT/issues/226) |
| P23 | P23-A1 [#96](https://github.com/Artfever/AI_PROJECT/issues/96), P23-A2 [#173](https://github.com/Artfever/AI_PROJECT/issues/173), P23-A3 [#261](https://github.com/Artfever/AI_PROJECT/issues/261) |
| P24 | P24-A1 [#99](https://github.com/Artfever/AI_PROJECT/issues/99), P24-A2 [#176](https://github.com/Artfever/AI_PROJECT/issues/176), P24-A3 [#230](https://github.com/Artfever/AI_PROJECT/issues/230) |
| P25 | P25-A1 [#102](https://github.com/Artfever/AI_PROJECT/issues/102), P25-A2 [#179](https://github.com/Artfever/AI_PROJECT/issues/179), P25-A3 [#233](https://github.com/Artfever/AI_PROJECT/issues/233) |
| P26 | P26-A1 [#105](https://github.com/Artfever/AI_PROJECT/issues/105), P26-A2 [#182](https://github.com/Artfever/AI_PROJECT/issues/182), P26-A3 [#236](https://github.com/Artfever/AI_PROJECT/issues/236) |

### Shaheer (78 tasks)

| Phase | Three assigned tasks |
| --- | --- |
| P01 | P01-S1 [#186](https://github.com/Artfever/AI_PROJECT/issues/186), P01-S2 [#238](https://github.com/Artfever/AI_PROJECT/issues/238), P01-S3 [#264](https://github.com/Artfever/AI_PROJECT/issues/264) |
| P02 | P02-S1 [#35](https://github.com/Artfever/AI_PROJECT/issues/35), P02-S2 [#111](https://github.com/Artfever/AI_PROJECT/issues/111), P02-S3 [#189](https://github.com/Artfever/AI_PROJECT/issues/189) |
| P03 | P03-S1 [#38](https://github.com/Artfever/AI_PROJECT/issues/38), P03-S2 [#114](https://github.com/Artfever/AI_PROJECT/issues/114), P03-S3 [#192](https://github.com/Artfever/AI_PROJECT/issues/192) |
| P04 | P04-S1 [#41](https://github.com/Artfever/AI_PROJECT/issues/41), P04-S2 [#117](https://github.com/Artfever/AI_PROJECT/issues/117), P04-S3 [#239](https://github.com/Artfever/AI_PROJECT/issues/239) |
| P05 | P05-S1 [#120](https://github.com/Artfever/AI_PROJECT/issues/120), P05-S2 [#196](https://github.com/Artfever/AI_PROJECT/issues/196), P05-S3 [#241](https://github.com/Artfever/AI_PROJECT/issues/241) |
| P06 | P06-S1 [#46](https://github.com/Artfever/AI_PROJECT/issues/46), P06-S2 [#123](https://github.com/Artfever/AI_PROJECT/issues/123), P06-S3 [#242](https://github.com/Artfever/AI_PROJECT/issues/242) |
| P07 | P07-S1 [#49](https://github.com/Artfever/AI_PROJECT/issues/49), P07-S2 [#126](https://github.com/Artfever/AI_PROJECT/issues/126), P07-S3 [#244](https://github.com/Artfever/AI_PROJECT/issues/244) |
| P08 | P08-S1 [#52](https://github.com/Artfever/AI_PROJECT/issues/52), P08-S2 [#129](https://github.com/Artfever/AI_PROJECT/issues/129), P08-S3 [#246](https://github.com/Artfever/AI_PROJECT/issues/246) |
| P09 | P09-S1 [#55](https://github.com/Artfever/AI_PROJECT/issues/55), P09-S2 [#132](https://github.com/Artfever/AI_PROJECT/issues/132), P09-S3 [#249](https://github.com/Artfever/AI_PROJECT/issues/249) |
| P10 | P10-S1 [#58](https://github.com/Artfever/AI_PROJECT/issues/58), P10-S2 [#135](https://github.com/Artfever/AI_PROJECT/issues/135), P10-S3 [#201](https://github.com/Artfever/AI_PROJECT/issues/201) |
| P11 | P11-S1 [#61](https://github.com/Artfever/AI_PROJECT/issues/61), P11-S2 [#138](https://github.com/Artfever/AI_PROJECT/issues/138), P11-S3 [#203](https://github.com/Artfever/AI_PROJECT/issues/203) |
| P12 | P12-S1 [#64](https://github.com/Artfever/AI_PROJECT/issues/64), P12-S2 [#141](https://github.com/Artfever/AI_PROJECT/issues/141), P12-S3 [#205](https://github.com/Artfever/AI_PROJECT/issues/205) |
| P13 | P13-S1 [#67](https://github.com/Artfever/AI_PROJECT/issues/67), P13-S2 [#144](https://github.com/Artfever/AI_PROJECT/issues/144), P13-S3 [#207](https://github.com/Artfever/AI_PROJECT/issues/207) |
| P14 | P14-S1 [#70](https://github.com/Artfever/AI_PROJECT/issues/70), P14-S2 [#147](https://github.com/Artfever/AI_PROJECT/issues/147), P14-S3 [#209](https://github.com/Artfever/AI_PROJECT/issues/209) |
| P15 | P15-S1 [#73](https://github.com/Artfever/AI_PROJECT/issues/73), P15-S2 [#150](https://github.com/Artfever/AI_PROJECT/issues/150), P15-S3 [#211](https://github.com/Artfever/AI_PROJECT/issues/211) |
| P16 | P16-S1 [#76](https://github.com/Artfever/AI_PROJECT/issues/76), P16-S2 [#153](https://github.com/Artfever/AI_PROJECT/issues/153), P16-S3 [#213](https://github.com/Artfever/AI_PROJECT/issues/213) |
| P17 | P17-S1 [#79](https://github.com/Artfever/AI_PROJECT/issues/79), P17-S2 [#156](https://github.com/Artfever/AI_PROJECT/issues/156), P17-S3 [#215](https://github.com/Artfever/AI_PROJECT/issues/215) |
| P18 | P18-S1 [#82](https://github.com/Artfever/AI_PROJECT/issues/82), P18-S2 [#159](https://github.com/Artfever/AI_PROJECT/issues/159), P18-S3 [#217](https://github.com/Artfever/AI_PROJECT/issues/217) |
| P19 | P19-S1 [#85](https://github.com/Artfever/AI_PROJECT/issues/85), P19-S2 [#162](https://github.com/Artfever/AI_PROJECT/issues/162), P19-S3 [#219](https://github.com/Artfever/AI_PROJECT/issues/219) |
| P20 | P20-S1 [#88](https://github.com/Artfever/AI_PROJECT/issues/88), P20-S2 [#165](https://github.com/Artfever/AI_PROJECT/issues/165), P20-S3 [#222](https://github.com/Artfever/AI_PROJECT/issues/222) |
| P21 | P21-S1 [#91](https://github.com/Artfever/AI_PROJECT/issues/91), P21-S2 [#168](https://github.com/Artfever/AI_PROJECT/issues/168), P21-S3 [#224](https://github.com/Artfever/AI_PROJECT/issues/224) |
| P22 | P22-S1 [#94](https://github.com/Artfever/AI_PROJECT/issues/94), P22-S2 [#171](https://github.com/Artfever/AI_PROJECT/issues/171), P22-S3 [#227](https://github.com/Artfever/AI_PROJECT/issues/227) |
| P23 | P23-S1 [#97](https://github.com/Artfever/AI_PROJECT/issues/97), P23-S2 [#174](https://github.com/Artfever/AI_PROJECT/issues/174), P23-S3 [#262](https://github.com/Artfever/AI_PROJECT/issues/262) |
| P24 | P24-S1 [#100](https://github.com/Artfever/AI_PROJECT/issues/100), P24-S2 [#177](https://github.com/Artfever/AI_PROJECT/issues/177), P24-S3 [#231](https://github.com/Artfever/AI_PROJECT/issues/231) |
| P25 | P25-S1 [#103](https://github.com/Artfever/AI_PROJECT/issues/103), P25-S2 [#180](https://github.com/Artfever/AI_PROJECT/issues/180), P25-S3 [#234](https://github.com/Artfever/AI_PROJECT/issues/234) |
| P26 | P26-S1 [#106](https://github.com/Artfever/AI_PROJECT/issues/106), P26-S2 [#183](https://github.com/Artfever/AI_PROJECT/issues/183), P26-S3 [#237](https://github.com/Artfever/AI_PROJECT/issues/237) |

### Taha (78 tasks)

| Phase | Three assigned tasks |
| --- | --- |
| P01 | P01-T1 [#33](https://github.com/Artfever/AI_PROJECT/issues/33), P01-T2 [#109](https://github.com/Artfever/AI_PROJECT/issues/109), P01-T3 [#187](https://github.com/Artfever/AI_PROJECT/issues/187) |
| P02 | P02-T1 [#36](https://github.com/Artfever/AI_PROJECT/issues/36), P02-T2 [#112](https://github.com/Artfever/AI_PROJECT/issues/112), P02-T3 [#190](https://github.com/Artfever/AI_PROJECT/issues/190) |
| P03 | P03-T1 [#39](https://github.com/Artfever/AI_PROJECT/issues/39), P03-T2 [#115](https://github.com/Artfever/AI_PROJECT/issues/115), P03-T3 [#193](https://github.com/Artfever/AI_PROJECT/issues/193) |
| P04 | P04-T1 [#42](https://github.com/Artfever/AI_PROJECT/issues/42), P04-T2 [#118](https://github.com/Artfever/AI_PROJECT/issues/118), P04-T3 [#240](https://github.com/Artfever/AI_PROJECT/issues/240) |
| P05 | P05-T1 [#44](https://github.com/Artfever/AI_PROJECT/issues/44), P05-T2 [#121](https://github.com/Artfever/AI_PROJECT/issues/121), P05-T3 [#265](https://github.com/Artfever/AI_PROJECT/issues/265) |
| P06 | P06-T1 [#47](https://github.com/Artfever/AI_PROJECT/issues/47), P06-T2 [#124](https://github.com/Artfever/AI_PROJECT/issues/124), P06-T3 [#243](https://github.com/Artfever/AI_PROJECT/issues/243) |
| P07 | P07-T1 [#50](https://github.com/Artfever/AI_PROJECT/issues/50), P07-T2 [#127](https://github.com/Artfever/AI_PROJECT/issues/127), P07-T3 [#245](https://github.com/Artfever/AI_PROJECT/issues/245) |
| P08 | P08-T1 [#53](https://github.com/Artfever/AI_PROJECT/issues/53), P08-T2 [#130](https://github.com/Artfever/AI_PROJECT/issues/130), P08-T3 [#247](https://github.com/Artfever/AI_PROJECT/issues/247) |
| P09 | P09-T1 [#56](https://github.com/Artfever/AI_PROJECT/issues/56), P09-T2 [#133](https://github.com/Artfever/AI_PROJECT/issues/133), P09-T3 [#200](https://github.com/Artfever/AI_PROJECT/issues/200) |
| P10 | P10-T1 [#59](https://github.com/Artfever/AI_PROJECT/issues/59), P10-T2 [#136](https://github.com/Artfever/AI_PROJECT/issues/136), P10-T3 [#251](https://github.com/Artfever/AI_PROJECT/issues/251) |
| P11 | P11-T1 [#62](https://github.com/Artfever/AI_PROJECT/issues/62), P11-T2 [#139](https://github.com/Artfever/AI_PROJECT/issues/139), P11-T3 [#252](https://github.com/Artfever/AI_PROJECT/issues/252) |
| P12 | P12-T1 [#65](https://github.com/Artfever/AI_PROJECT/issues/65), P12-T2 [#142](https://github.com/Artfever/AI_PROJECT/issues/142), P12-T3 [#253](https://github.com/Artfever/AI_PROJECT/issues/253) |
| P13 | P13-T1 [#68](https://github.com/Artfever/AI_PROJECT/issues/68), P13-T2 [#145](https://github.com/Artfever/AI_PROJECT/issues/145), P13-T3 [#254](https://github.com/Artfever/AI_PROJECT/issues/254) |
| P14 | P14-T1 [#71](https://github.com/Artfever/AI_PROJECT/issues/71), P14-T2 [#148](https://github.com/Artfever/AI_PROJECT/issues/148), P14-T3 [#255](https://github.com/Artfever/AI_PROJECT/issues/255) |
| P15 | P15-T1 [#74](https://github.com/Artfever/AI_PROJECT/issues/74), P15-T2 [#151](https://github.com/Artfever/AI_PROJECT/issues/151), P15-T3 [#256](https://github.com/Artfever/AI_PROJECT/issues/256) |
| P16 | P16-T1 [#77](https://github.com/Artfever/AI_PROJECT/issues/77), P16-T2 [#154](https://github.com/Artfever/AI_PROJECT/issues/154), P16-T3 [#257](https://github.com/Artfever/AI_PROJECT/issues/257) |
| P17 | P17-T1 [#80](https://github.com/Artfever/AI_PROJECT/issues/80), P17-T2 [#157](https://github.com/Artfever/AI_PROJECT/issues/157), P17-T3 [#258](https://github.com/Artfever/AI_PROJECT/issues/258) |
| P18 | P18-T1 [#83](https://github.com/Artfever/AI_PROJECT/issues/83), P18-T2 [#160](https://github.com/Artfever/AI_PROJECT/issues/160), P18-T3 [#218](https://github.com/Artfever/AI_PROJECT/issues/218) |
| P19 | P19-T1 [#86](https://github.com/Artfever/AI_PROJECT/issues/86), P19-T2 [#163](https://github.com/Artfever/AI_PROJECT/issues/163), P19-T3 [#220](https://github.com/Artfever/AI_PROJECT/issues/220) |
| P20 | P20-T1 [#89](https://github.com/Artfever/AI_PROJECT/issues/89), P20-T2 [#166](https://github.com/Artfever/AI_PROJECT/issues/166), P20-T3 [#260](https://github.com/Artfever/AI_PROJECT/issues/260) |
| P21 | P21-T1 [#92](https://github.com/Artfever/AI_PROJECT/issues/92), P21-T2 [#169](https://github.com/Artfever/AI_PROJECT/issues/169), P21-T3 [#225](https://github.com/Artfever/AI_PROJECT/issues/225) |
| P22 | P22-T1 [#95](https://github.com/Artfever/AI_PROJECT/issues/95), P22-T2 [#172](https://github.com/Artfever/AI_PROJECT/issues/172), P22-T3 [#228](https://github.com/Artfever/AI_PROJECT/issues/228) |
| P23 | P23-T1 [#98](https://github.com/Artfever/AI_PROJECT/issues/98), P23-T2 [#175](https://github.com/Artfever/AI_PROJECT/issues/175), P23-T3 [#229](https://github.com/Artfever/AI_PROJECT/issues/229) |
| P24 | P24-T1 [#101](https://github.com/Artfever/AI_PROJECT/issues/101), P24-T2 [#178](https://github.com/Artfever/AI_PROJECT/issues/178), P24-T3 [#232](https://github.com/Artfever/AI_PROJECT/issues/232) |
| P25 | P25-T1 [#104](https://github.com/Artfever/AI_PROJECT/issues/104), P25-T2 [#181](https://github.com/Artfever/AI_PROJECT/issues/181), P25-T3 [#235](https://github.com/Artfever/AI_PROJECT/issues/235) |
| P26 | P26-T1 [#107](https://github.com/Artfever/AI_PROJECT/issues/107), P26-T2 [#184](https://github.com/Artfever/AI_PROJECT/issues/184), P26-T3 [#263](https://github.com/Artfever/AI_PROJECT/issues/263) |

## Initial readiness from open hard blockers

- Abdullah: P01-A1 [#32](https://github.com/Artfever/AI_PROJECT/issues/32) has no issue blocker. Repository evidence is partial; check its acceptance items before closing. P01-A2 and A3 wait for the preceding Abdullah task.
- Taha: P01-T1 [#33](https://github.com/Artfever/AI_PROJECT/issues/33) has no issue blocker. The Home shell exists, but the five pages remain unverified. P01-T2 and T3 wait for their preceding Taha task.
- Shaheer: no P01 task is free of a hard blocker yet. P01-S1 [#186](https://github.com/Artfever/AI_PROJECT/issues/186) waits for P01-A2 [#108](https://github.com/Artfever/AI_PROJECT/issues/108); S2 waits for S1, and S3 waits for S2. Existing CI and install evidence is partial, not task closure.

All P02 and later phase gates wait for their listed predecessor gates. Parallel model packets P08/P09/P10 become technically available only after P07; owner availability is a separate constraint. Readiness changes as reviewed outputs and gates close.
