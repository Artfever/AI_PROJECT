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

Shaheer, the repository owner, chose the arithmetic mean before any model
comparison. The primary validation measures are MAE and RMSE, with RMSE a
primary error measure in the evaluation protocol. The mean minimizes the sum
of squared deviations from the fitting labels, so a constant prediction set
to that mean is directly aligned with squared-error loss and RMSE. It also
uses the magnitude of every fitting label rather than only the middle ranked
value.

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
future use, but this baseline and its recorded artifact use `mean`.

The JSON-ready artifact records `constant-rul-v1`, statistic, RUL value in
cycles, target name, fitting-label count, and `random_seed: null`. The predictor
has no random choices. Its constant value is a model parameter, not a measured
validation result. No true RUL, final lifetime, feature values, or validation
labels enter the fit. The real FD001 fitting-data execution and artifact
reload are recorded in `handoff_Shaheer.md`; validation scoring belongs to
P06-S2 and has not been performed here.
