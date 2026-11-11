# P04 shared gate verification

Verified by Abdullah on 11 November 2026 against main `52a0c32` for
[phase #9](https://github.com/Artfever/FleetpulseAI/issues/9).
This document submits the combined evidence for peer review. The phase remains
open until this evidence is accepted; P05-A1 #43 must wait for that closure.

All nine native child issues are closed: #40, #116, #194, #41, #117,
#239, #42, #118 and #240. Native predecessor P03 #8 is closed. Child closure
alone is not the evidence for the shared gate.

| Shared requirement | Observed evidence |
| --- | --- |
| No fitting/validation engine overlap | Original training-source audit verifies 80 fitting and 20 validation identities, disjoint and exhaustive. |
| Prefixes contain no future rows | Prefix tests and synthetic smoke pass; an additional real-manifest callback check verifies every one of the 20 saved prefixes, exact row count, single engine, maximum cycle equal to cutoff, and only the 26 raw history columns. Fitting engines never reach the callback. |
| Metric tests pass | Full suite includes independent hand-calculation checks for MAE 3 and RMSE sqrt(10), duplicate rejection, and the synthetic evaluator smoke. |
| Official test labels unused | Gate commands read original training histories and the saved manifest only. Source scan found no `RUL_FD001` or `load_rul_values` references in `scripts` or `src/fleetpulse/evaluation`. This establishes the checked execution path, not a claim about every person's historical access. |

## Commands and results

Executed with the existing Python 3.12.16 environment:

- `.venv/Scripts/python.exe -m ruff check .`: PASS.
- `.venv/Scripts/python.exe -m pytest -q`: **119 passed in 23.62s**.
- `.venv/Scripts/python.exe scripts/verify_split_manifest.py`: PASS; 80/20
  engines, no overlap, observed nonterminal cutoffs meeting the minimum,
  split/cutoff seeds 42/42. Manifest SHA-256:
  `47eeae52d9099035f1db2780f2e11e8ec7718eec807aa248d11141dd67072c78`.
- `.venv/Scripts/python.exe scripts/verify_training_targets.py`: PASS; 20,631
  labels across 100 engines, one terminal zero per engine, range 0..361 cycles.
- `.venv/Scripts/python.exe scripts/smoke_validation.py`: PASS; artificial
  histories expose cycles `[1,2,3,4]` and `[1,2,3]`, targets 2/5, fixed callback
  predictions 3/3, illustrative MAE 1.5 and RMSE 1.5811388300841898 cycles.
- `rg -n 'RUL_FD001|load_rul_values' scripts src/fleetpulse/evaluation`:
  no matches (expected exit 1).
- `git diff --check`: PASS after writing this record.

The additional real-manifest check was executed through PowerShell's here-string
piped into `.venv/Scripts/python.exe -`. Reproduce with this Python body:

```python
import hashlib
import json
from pathlib import Path
from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.quality import FD001_COLUMNS
from fleetpulse.evaluation import evaluate_validation_manifest

source = Path('data/raw/train_FD001.txt')
manifest = json.loads(Path('artifacts/split_manifest.json').read_text(encoding='utf-8'))
expected = {p['unit_id']: p for p in manifest['validation_prefixes']}
seen = set()

def predictor(prefix):
    unit = prefix[0]['unit_id']
    entry = expected[unit]
    assert unit not in seen
    assert len(prefix) == entry['prefix_row_count']
    assert all(set(row) == FD001_COLUMNS and row['unit_id'] == unit
               and row['cycle'] <= entry['cutoff_cycle'] for row in prefix)
    assert max(row['cycle'] for row in prefix) == entry['cutoff_cycle']
    seen.add(unit)
    return 3.0

results = evaluate_validation_manifest(
    load_engine_history(source), manifest=manifest,
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), predictor=predictor,
)
assert seen == set(expected) and len(results) == 20
assert all(r.true_rul == expected[r.unit_id]['target_rul'] for r in results)
```

Result: PASS for all 20 real validation callbacks and scoring targets. The fixed
callback has no trained parameters; no model-performance score is reported.

## Review and next step

Reviewed upstream outputs include the manifest/audit PRs #311/#313, evaluator
#312, metrics #314, audit UI #308, smoke #315 and protocol/examples #316/#317/#318.
The latest protocol completion #318 is merged with Abdullah's approval and all
five CI checks successful. See the [evaluation protocol](evaluation_protocol.md)
and [smoke explanation](evaluator_smoke.md) for boundaries and units.

Local Streamlit startup: **NOT RUN**, documentation-only gate work; the full
suite includes app checks. Training, model inference/reload and official-test
evaluation: **NOT RUN**, no trained artifact exists. No raw data or model artifact
was changed or added. This gate does not certify future feature code or a model.

One current-revision approval from Shaheer or Taha, required CI and resolved
conversations are still required for this gate PR. Peer review should explicitly
accept this combined evidence. Once #9 is closed, pull main and inspect P05-A1
#43. Its feature contract needs agreement with Shaheer on population standard
deviation, actual-cycle slope and the one-row rule before dependent code.
