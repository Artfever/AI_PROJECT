# Constant RUL baseline (P06-S1)

`ConstantRULBaseline` is a deterministic reference predictor. It fits one
declared statistic from fitting RUL labels and repeats that value for each
requested prediction row. Its `fit` method accepts labels only; it does not
accept validation labels or features. The caller must supply only the fitting
labels selected by the saved P04 split manifest.

```python
from fleetpulse.models import ConstantRULBaseline

baseline = ConstantRULBaseline.fit(
    fitting_rul_cycles,
    statistic="mean",
)
predictions = baseline.predict(sample_count=len(validation_feature_rows))
artifact = baseline.to_artifact()
reloaded = ConstantRULBaseline.from_artifact(artifact)
```

## Chosen statistic: mean

Shaheer, the repository owner, initially chose the arithmetic mean before
model comparison. The mean minimizes the sum of squared deviations from the
fitting labels, so a constant prediction set to that mean is directly aligned
with squared-error loss and RMSE. It also uses the magnitude of every fitting
label rather than only the middle ranked value.

The median was not selected because it minimizes absolute-error loss (and is
the natural constant choice when MAE is the sole objective), not squared-error
loss. It is more resistant to unusually large or small fitting labels. Had we
chosen the median, every prediction would instead equal the fitting-label
median: that could favor MAE and reduce sensitivity to extreme labels, while
potentially increasing RMSE when large errors occur in the tails. The mean
has the corresponding tradeoff: it is aligned with RMSE but can be pulled by
extreme fitting labels. This decision is fixed before validation scoring; no
validation result was used to choose it, and the median was not evaluated on
validation data.

The required `statistic` argument prevents a caller from silently changing
the declared choice. The implementation retains median support for explicit
comparison, but the selected baseline remains `mean`.

## Owner-directed validation comparison

After selecting mean, the owner requested a direct mean/median score check and
asked to switch only if median scored better. Both constants were fit on the
same 16,738 labels from the manifest's 80 fitting engines. Each was scored on
the same 20 saved FD001 validation prefixes with
`evaluate_validation_manifest` and `calculate_validation_metrics`:

| Fitting statistic | Constant prediction (cycles) | MAE (cycles) | RMSE (cycles) |
| --- | ---: | ---: | ---: |
| Mean | 109.609989246027 | 65.728002150795 | 74.258986754232 |
| Median | 104.0 | 67.35 | 74.518789576858 |

Mean had lower MAE by 1.621997849205 cycles and lower RMSE by
0.259802822626 cycles. Median therefore did not score better on either
reported metric, so the selected statistic remains mean. The scores use the
saved schema-v1 manifest and its fixed 80/20 engine split and cutoffs; training
source SHA-256 is
`963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8`, and
semantic manifest SHA-256 is
`6fd1d32f7570f70f5a9513d900fbb9d26b182359aced425e2276700c84f08d92`.

Because this comparison used development-validation labels to make the
conditional choice, these scores are selection evidence, not an untouched
final estimate of generalization. The official FD001 test histories and RUL
answers were not read. P06-S2's saved per-engine output and teammate inspection
are recorded on [issue #123](https://github.com/Artfever/FleetpulseAI/issues/123).
The common downstream metrics record is specified in [`metrics_json.md`](metrics_json.md).

The JSON-ready artifact records `constant-rul-v1`, statistic, RUL value in
cycles, target name, fitting-label count, and `random_seed: null`. The predictor
has no random choices. Its constant value is a model parameter, not a measured
validation result. No true RUL, final lifetime, feature values, or validation
labels enter the fit. The real FD001 fitting-data execution, artifact reload,
and owner-requested validation comparison are recorded in `handoff_Shaheer.md`.
The validation comparison is not a substitute for completing P06-S2.

## P06-S2: saved per-engine validation output

`python scripts/score_constant_baseline.py` loads the hash-checked fitting and
validation feature tables generated from the saved P04 manifest. It verifies
their source, manifest and feature configuration; fits mean from fitting labels
only; predicts once per saved validation engine; and calculates MAE/RMSE from
the held-out validation targets. Validation features are not passed to this
constant predictor. The script writes the complete, full-precision output to
the ignored local file `artifacts/development/constant_rul_validation.json` and
reloads it to check row uniqueness and consistency of the stored metrics.

Observed run: artifact `constant-rul-validation-v1`, 16,738 fitting labels,
20 `FD001/train` validation engines, mean prediction 109.609989246027 cycles,
MAE 65.728002150795 cycles and RMSE 74.258986754232 cycles. The saved artifact
SHA-256 was
`c1a91a96338be50f0b91f45546c63722570e4db44fd7011fde71dbfdbc6027f8`; it also
records the source, split-manifest, fitting-table and validation-table hashes,
and every per-engine prediction, target and error. This development artifact
is ignored by Git; the tracked per-engine summary below makes the results
reviewable, and the script recreates the full-precision artifact locally.

| Unit | Cutoff | True RUL | Predicted RUL | Absolute error |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 164 | 25 | 109.610 | 84.610 |
| 5 | 58 | 211 | 109.610 | 101.390 |
| 12 | 7 | 163 | 109.610 | 53.390 |
| 14 | 71 | 109 | 109.610 | 0.610 |
| 15 | 63 | 144 | 109.610 | 34.390 |
| 18 | 58 | 137 | 109.610 | 27.390 |
| 28 | 36 | 129 | 109.610 | 19.390 |
| 29 | 27 | 136 | 109.610 | 26.390 |
| 30 | 174 | 20 | 109.610 | 89.610 |
| 32 | 190 | 1 | 109.610 | 108.610 |
| 36 | 140 | 18 | 109.610 | 91.610 |
| 55 | 23 | 170 | 109.610 | 60.390 |
| 65 | 152 | 1 | 109.610 | 108.610 |
| 70 | 109 | 28 | 109.610 | 81.610 |
| 72 | 9 | 204 | 109.610 | 94.390 |
| 76 | 8 | 202 | 109.610 | 92.390 |
| 78 | 24 | 207 | 109.610 | 97.390 |
| 82 | 56 | 158 | 109.610 | 48.390 |
| 87 | 60 | 118 | 109.610 | 8.390 |
| 95 | 259 | 24 | 109.610 | 85.610 |

Each row is one engine-level prediction at the P04-saved cutoff. The target is
derived from that engine's complete training lifetime for scoring only; no
later history or target is supplied to the predictor. These 20 development
validation results are not official test results. The constant ignores sensor
readings and individual engine condition, so this artifact is a benchmark, not
an individual maintenance prediction.
