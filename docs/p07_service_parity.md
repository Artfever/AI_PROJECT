# P07-S1 saved-service parity

## Verified result

`python scripts/compare_service_parity.py` replayed the saved P06 inference
service against all 20 fixed validation prefixes in
`artifacts/development/decision_tree_validation.json`. Each service call read
only the raw `FD001/train` prefix ending at the saved engine/cutoff; the
comparison never loaded official test answers. Before scoring, the command
verified that the local training source matched the source hash recorded by
the saved P06 model and oracle.

All 20 raw service predictions exactly matched their saved P06 values. Maximum
absolute difference was 0.0 cycles. The script requires exactly 20 unique
partition/engine/cycle identities and exits nonzero if any prediction differs
or the report's counts do not match its rows. The report with each engine, cutoff,
prediction, and label is written to the ignored local file
`reports/p07_service_parity.json`; it is reproducible and is not committed.

| Item | Observed value |
| --- | --- |
| Partition / unit | `FD001/train` / engine prefix |
| Model | `decision-tree-rul` / `decision-tree-rul-v1` |
| scikit-learn | 1.9.1 |
| Seed and parameters | 42; `max_depth=8`, `min_samples_leaf=5` |
| Model SHA-256 | `2a693e6ecc09de5d9549e287a6798fdb339c7e945c700231444f0c5bcd425018` |
| Training source SHA-256 | `963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8` |
| P06 oracle document SHA-256 | `fd0382e90385109ca8b67ffd6aa536383c63e8f363838c5a5a5553120d8c12f6` |
| Prefixes / exact matches | 20 / 20 |
| Maximum absolute difference | 0.0 cycles |

This verifies local saved-service parity on the fixed development-validation
set. It does not establish generalization, official-test performance, a final
model, or remote deployment parity. P07-T3 remote comparisons remain separate.

## Reproduction

With the original local FD001 training file and P06 development artifacts
present:

```powershell
.venv/Scripts/python.exe scripts/compare_service_parity.py
```

The script checks the source and saved-oracle hashes, selects exactly the
saved engine/cutoff prefixes, invokes the public `predict_rul` service, and
writes the ignored JSON report. It fails on missing cycles, mismatched source
provenance, changed oracle content, duplicate or missing identities, or any
nonzero prediction difference. A failed comparison still leaves the report
available for diagnosis and returns a nonzero process status.
