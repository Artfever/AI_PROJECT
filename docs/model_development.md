# P06 model development and validation

Run the complete development workflow from the repository root:

```powershell
python scripts/run_p06_validation.py
```

This rebuilds the ignored fitting and validation feature tables from the original
FD001 training histories and tracked split manifest, scores the mean constant
baseline, fits the bounded Decision Tree, saves both result sets, reloads the
tree in a fresh Python process, and verifies that per-engine outputs and summary
metrics agree. It requires the locally supplied `data/raw/train_FD001.txt` whose
hash is pinned in `docs/fd001_provenance.md`. It does not open official test
histories or answer files. Generated feature tables, model binaries, and result
JSON files stay under ignored `artifacts/development/` and are not committed.

The Model Laboratory checks input hashes, the saved model version and feature
schema, validation engine identities/cutoffs, and metric consistency before
showing a comparison. It plots predicted versus actual RUL for each held-out
development engine. The current validation set contains 20 engines from the
FD001 training histories; these measurements are development evidence, not
official-test performance or individual maintenance guarantees.
