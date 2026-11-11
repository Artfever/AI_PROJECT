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
answers were not read. The full P06-S2 deliverable, including a saved
per-engine prediction artifact and its human review, remains separate.

The JSON-ready artifact records `constant-rul-v1`, statistic, RUL value in
cycles, target name, fitting-label count, and `random_seed: null`. The predictor
has no random choices. Its constant value is a model parameter, not a measured
validation result. No true RUL, final lifetime, feature values, or validation
labels enter the fit. The real FD001 fitting-data execution, artifact reload,
and owner-requested validation comparison are recorded in `handoff_Shaheer.md`.
The validation comparison is not a substitute for completing P06-S2.
