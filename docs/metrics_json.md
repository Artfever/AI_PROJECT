# Common validation metrics record

P06-S3 defines `metrics-v1`, a strict JSON record for comparing RUL models on
the same saved validation partition. The record is model-neutral: each model
supplies its name/version and JSON parameters while using the same evaluation
fields. The Python builder and validator are exported from
`fleetpulse.evaluation` as `build_metrics_record`, `validate_metrics_record`,
and `save_metrics_record`.

## Fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Contract version; currently `metrics-v1`. |
| `model.name`, `model.version` | Stable model identifier and the implementation/artifact version used. |
| `evaluation.partition` | Dataset-qualified partition, such as `FD001/train`. |
| `evaluation.sample_unit`, `sample_count` | Unit scored and positive number of units, e.g. `engine` and 20. |
| `evaluation.feature_config` | Complete JSON feature configuration used by the model. |
| `evaluation.random_seed` | Nonnegative integer if randomness was seeded; `null` if no random seed applies. |
| `evaluation.parameters` | Model parameters needed to interpret or reproduce the result. |
| `evaluation.metrics.mae_cycles`, `rmse_cycles` | Finite, nonnegative validation errors in RUL cycles. |
| `evaluation.runtime_seconds` | Measured wall time for model fit, prediction, and metric calculation; data loading and JSON writing are excluded. |
| `evaluation.input_hashes` | Nonempty mapping of input names to lowercase SHA-256 digests. |

The contract rejects missing or extra fields, invalid values, non-finite JSON
numbers, and malformed input hashes. JSON keys are sorted on write and the file
ends with LF. Runtime is an observation and may vary between runs; it must not
be used as a deterministic model parameter.

## Observed constant-baseline record

`python scripts/score_constant_baseline.py` now writes the full per-engine
artifact to the ignored local
`artifacts/development/constant_rul_validation.json` and a separate
`artifacts/development/metrics.json` using this common format. The latter is
reloaded and validated before the script succeeds. Its baseline record uses
model `constant-rul-baseline`, version `constant-rul-v1`, partition
`FD001/train`, sample unit `engine`, 20 samples, feature config `past-only-v1`
with a 30-cycle window, seed `null`, mean parameter `109.609989246027` cycles,
MAE `65.728002150795` cycles and RMSE `74.258986754232` cycles. Runtime is
measured on each local scoring run; one observed run took `0.010332900`
seconds for fit, prediction, and scoring. Both generated files are ignored; this
tracked document defines their interface and reports the observed validation
results without publishing local NASA-derived artifacts.

The complete local records also carry SHA-256 hashes for the training source,
saved split manifest, fitting table, and validation table. The validation
metrics are development evidence, not official-test results or individual
maintenance predictions.
