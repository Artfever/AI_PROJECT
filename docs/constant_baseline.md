# Constant RUL baseline (P06-S1)

`ConstantRULBaseline` is a deterministic reference predictor. It fits one
explicitly selected statistic from fitting RUL labels and repeats that value
for each requested prediction row. Its `fit` method accepts labels only; it
does not accept validation labels or features. The caller must supply only the
fitting labels selected by the saved P04 split manifest. Feature-table
construction remains Abdullah's P06-A1 task.

```python
from fleetpulse.models import ConstantRULBaseline

baseline = ConstantRULBaseline.fit(
    fitting_rul_cycles,
    statistic=selected_statistic,  # "mean" or "median"; no implicit default
)
predictions = baseline.predict(sample_count=len(validation_feature_rows))
artifact = baseline.to_artifact()
reloaded = ConstantRULBaseline.from_artifact(artifact)
```

The required `statistic` argument prevents a comparison from silently choosing
or changing its baseline. The repository owner and team still need to decide
whether the pre-comparison choice is mean or median. Until they do, no model
comparison is run and P06-S1 remains open. The implementation supports both
choices but does not claim a team decision.

The JSON-ready artifact records `constant-rul-v1`, statistic, RUL value in
cycles, target name, fitting-label count, and `random_seed: null`. The predictor
has no random choices. Its constant value is a model parameter, not a measured
validation result. No true RUL, final lifetime, feature values, or validation
labels enter the fit. The actual FD001 fitting run waits for Abdullah's
P06-A1 fitting table; current automated checks use synthetic labels only.
