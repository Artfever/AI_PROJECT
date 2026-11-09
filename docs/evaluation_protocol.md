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

## Concrete visible-prefix example

The saved manifest selects **FD001/train engine 4**, a simulated validation
engine, at cycle 164. Its complete training history has observed cycles 1?189.
The predictor receives only cycles 1?164: 164 sensor-history rows from this
engine. Cycles 165?189 are the hidden future and must not be supplied to the
predictor or used to create its input features. The scoring path can use the
known final cycle 189 to calculate the target: `189 - 164 = 25` cycles.

| Information | Available to predictor? | Purpose |
| --- | --- | --- |
| Engine 4 sensor records through cycle 164 | Yes | Observed prefix input |
| Engine 4 sensor records from cycles 165?189 | No | Future trajectory, hidden from prediction |
| Final cycle 189 and target RUL 25 | No | Scoring and analysis only |

This example describes a held-out engine from the original **training**
partition; it is not an official-test engine or a model prediction. Numeric
engine IDs can repeat across partitions, so keep `FD001/train` with the ID.
The row counts above were checked against the local source and saved manifest;
other engines or gapped histories need their actual observed row counts rather
than assuming a cutoff cycle equals a row count.

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
- `.venv\Scripts\python.exe scripts/smoke_validation.py` — passed on Python
  3.12.10. This deterministic evaluator inference smoke uses two artificial
  histories and a fixed 3-cycle callback (split/cutoff seed: not applicable;
  fitted model/artifact version: not applicable). It observed prefixes
  `[1, 2, 3, 4]` and `[1, 2, 3]`, targets `[2, 5]`, predictions `[3, 3]`, MAE
  `1.5`, and RMSE `1.5811388300841898` cycles. This verifies prefix wiring and
  metric arithmetic only; it is not a trained-model inference result. PR
  [#315](https://github.com/Artfever/FleetpulseAI/pull/315) records Taha's
  confirmation that he inspected the saved output and discussed the constant
  callback and its limitations with a teammate.
- Model training, model comparison, inference, and model reload: **NOT RUN**;
  no trained model artifact exists. The synthetic evaluator smoke above is the
  relevant available execution evidence; no trained-model metric or behavior
  is claimed.

The split, metric, label-boundary, and synthetic evaluator checks are technical
evidence. Abdullah approved the protocol PR #316. The shared P04 gate is tracked
separately and remains open until all nine task outcomes and its shared
acceptance checks are verified.
