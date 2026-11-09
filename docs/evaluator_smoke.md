# Synthetic validation evaluator smoke run

Run `python scripts/smoke_validation.py` from the repository root. To save the
output locally in PowerShell:

```powershell
python scripts/smoke_validation.py | Set-Content -Encoding utf8 artifacts/development/P04_T2_synthetic_smoke.json
```

The file is ignored by Git. This example constructs two **artificial** complete
histories; it does not read NASA data or the official test answers. The evaluator
requires the partition string `FD001/train`, but the records here are explicitly
synthetic and do not represent that dataset. A deliberately fixed callback always
returns 3 cycles. It has no fitted parameters and is not a trained model or a
performance benchmark.

For the synthetic engines, the visible cutoffs are 4 and 3; their terminal
cycles are 6 and 8, giving known labels of 2 and 5 cycles respectively. The
absolute errors are therefore 1 and 2 cycles. Their illustrative mean absolute
error is 1.5 cycles; their root mean square error is `sqrt((1 + 4) / 2)`,
approximately 1.581 cycles. The output records which cycles the callback saw;
only the prefix through each cutoff is supplied to it. These small examples
verify wiring and arithmetic, not generalization or model performance.
