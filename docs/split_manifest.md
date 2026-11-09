# Development split manifest, schema v1

P04-A2 / [#116](https://github.com/Artfever/FleetpulseAI/issues/116).
The reviewed [whole-engine splitter](development_split.md) supplies memberships;
`artifacts/split_manifest.json` saves their exact dataset-qualified IDs and one
validation-prefix cutoff per held-out training engine.

Regenerate from the original local training file, after the editable install:

```powershell
python scripts/generate_split_manifest.py
```

The generator reads **only** `data/raw/train_FD001.txt`. It checks the reviewed
source SHA-256 before loading and again before saving. It uses split seed `42`,
validation fraction `0.2`, cutoff seed `42`, and minimum history `1` observed row.
These are declared development settings for review, not results selected by
trying models or examining official test answers. Agree the seed and cutoff rule
with Shaheer before comparing models. No model comparison is part of this task.

The cutoff proposal samples uniformly over an engine's **observed nonterminal
cycles** having at least the minimum row count. It does not invent missing cycles
or require a 30-cycle history; P05's available-prefix feature contract supports
short histories. A separate local cutoff RNG visits validation engines in sorted
ID order, independently of the split RNG. If any assigned validation engine has
no eligible cutoff, generation fails; it does not resample assignments, drop the
engine, or include failure. The serialized file contains no timestamp and uses
sorted JSON keys and LF newlines for repeatable bytes with identical inputs.

| Key | Meaning |
| --- | --- |
| `schema_version` | `1`, the version of this persisted contract |
| `source` | Qualified partition `FD001/train`, relative source path, SHA-256, row and engine counts |
| `split` | Split seed, fraction, and algorithm identifier |
| `cutoff_policy` | Cutoff seed, algorithm, minimum observed rows, terminal exclusion and sampling rule |
| `fitting_engines` | Array of `{dataset_partition, unit_id}` identities |
| `validation_prefixes` | Array of qualified identities with cutoff/scoring metadata below |

Each validation entry records `cutoff_cycle`, `prefix_row_count`, the first/last
eligible observed cutoff (`eligible_cutoff_range`), `eligible_cutoff_count`,
`full_lifetime`, and `target_rul = full_lifetime - cutoff_cycle`. Bounds alone do
not imply all intermediate cycles were observed when histories contain gaps.
`prefix_row_count` counts records, not the numeric cutoff. The manifest stores
80 fitting IDs and 20 validation identities; those numeric IDs belong to training
data, not the identically numbered official test engines.

Consumers must verify source identity, select each engine from the training
partition, and pass **only rows at or before its cutoff** to feature generation
and prediction. `full_lifetime` and `target_rul` are scoring/analysis metadata,
never model features. The manifest does not contain clipped prefix sensor data;
it does not implement or attest to a predictor/evaluator. Shaheer's evaluator and
Taha's audit page integrate this reviewed contract under their own tasks.

Only this small manifest is excepted from artifact ignore rules; raw data and
trained artifacts stay ignored. Existing output is deterministically replaced by
the command; review any diff before accepting it. P04-A3 will independently audit
no overlap, cutoff eligibility, and source/manifest agreement. The shared P04 gate
also needs evaluator/metric and human checks; saving this file does not close it.
