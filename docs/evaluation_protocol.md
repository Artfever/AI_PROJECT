# FD001 development evaluation protocol

P04-S3 / [#239](https://github.com/Artfever/FleetpulseAI/issues/239). This
protocol is fixed before any model comparison. It applies to simulated NASA
C-MAPSS FD001 development data only; it does not define an official test result.

## Data and split

- Use original `FD001/train` histories only for fitting and development
  validation. Keep every engine trajectory in exactly one group.
- Use the reviewed schema-v1 `artifacts/split_manifest.json` as the fixed
  assignment and cutoff source. It records 80 fitting engines and 20 validation
  engines, with split and cutoff seeds `42`. Do not resample or choose another
  seed after looking at scores. These recorded settings remain subject to
  teammate review; do not start model comparisons until that review is complete.
- Each validation cutoff must be an observed, nonterminal cycle. The predictor
  receives only that engine's observed rows through the cutoff. Later rows,
  full lifetime, and target RUL are scoring metadata and must not enter features,
  preprocessing, or predictor inputs.
- The validation target is `full_lifetime - cutoff_cycle`, measured in
  operating cycles. Dataset-qualified engine identity is
  `(dataset_partition, unit_id)`; a numeric unit ID alone is insufficient.
- The manifest used for the recorded check has SHA-256
  `47eeae52d9099035f1db2780f2e11e8ec7718eec807aa248d11141dd67072c78`.
  Verify it against the original local training file before relying on its
  assignments.

## Primary validation measures

Produce exactly one prediction for each validation engine and calculate the
primary metrics over those 20 engine-level predictions:

- `MAE = mean(abs(prediction - true_rul))`
- `RMSE = sqrt(mean((prediction - true_rul) ** 2))`

Both metrics are in cycles. Do not clip a prediction before scoring. Reject
duplicate engine predictions and preserve the per-engine error rows used to
calculate the aggregate values. The implementation is
`fleetpulse.evaluation.calculate_validation_metrics`.

Hand check: for true RUL `[10, 20]` and predictions `[12, 16]`, absolute errors
are `[2, 4]`; MAE is `(2 + 4) / 2 = 3` cycles, and RMSE is
`sqrt((2**2 + 4**2) / 2) = sqrt(10)` cycles.

## Target and test-label safeguards

- Before comparing models, verify that target labels are not all zero. A zero
  is expected at the terminal row of each complete training engine; the check
  must therefore report the full distribution and confirm positive labels also
  exist, rather than treating every zero as an error.
- For validation, targets are computed from the training engine's full lifetime
  and saved cutoff. They must be positive because cutoffs precede terminal
  cycles.
- Never load `RUL_FD001.txt` or use official test labels in development scripts,
  model choice, tuning, or this validation protocol. The separate official
  test answer file is reserved for the later held-out evaluation phase.
- Do not report a model score until a real model, its configuration, artifact
  version, and predictions exist and can be reproduced. A constant predictor
  used for an interface smoke test is not a trained model result.

## Verification record (2026-11-09)

- `.venv\Scripts\python.exe scripts/verify_training_targets.py` — verified
  20,631 training labels across 100 engines; one terminal zero per engine;
  range 0–361 cycles. Thus 20,531 labels are positive; the distribution is not
  all zero.
- `.venv\Scripts\python.exe scripts/verify_split_manifest.py` — verified 80
  fitting / 20 validation engines, no overlap, observed nonterminal cutoffs,
  seeds 42/42, and the manifest hash above.
- Direct manifest target summary command:

  ```powershell
  .venv\Scripts\python.exe -c "import json; from pathlib import Path; m=json.loads(Path('artifacts/split_manifest.json').read_text(encoding='utf-8')); t=[p['target_rul'] for p in m['validation_prefixes']]; print(f'validation_targets={len(t)} min={min(t)} max={max(t)} zeros={sum(v == 0 for v in t)} distinct={len(set(t))}')"
  ```

  Result: 20 targets, range 1–211 cycles, 0 zeros, 19 distinct values.
- A source scan of `scripts`, `src/fleetpulse/evaluation`, and tests found no
  official answer-file path or answer-loader use in development scripts or the
  evaluator. Loader unit tests mention the separate reader only to test its
  parsing behavior with synthetic values.
- Model training, model comparison, inference, and model reload: **NOT RUN**;
  no trained model artifact exists. No model metric or behavior is claimed.

The split, metric, and label-boundary checks are technical evidence. Teammate
review of this protocol and the separate shared P04 gate are still required.
