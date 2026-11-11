# P05 feature contract, past-only-v1

P05-A1 / #43 defines this contract. P05-S1 / #120 implements numerical
extraction through `from fleetpulse.features import engineer_features` and
`EngineFeatureVector`. No feature table, trained model, or model score is
supplied by this work.

## Channels and exact order

`FeatureConfig()` declares `setting_1`, `setting_2`, `setting_3`, then `sensor_1`
through `sensor_21` in numeric order. All 24 raw reading channels are retained;
no data-derived selection or constant-channel filtering is performed. A caller
may explicitly select an ordered, nonempty tuple of these names. Duplicate,
unknown, identity, cycle, target, lifetime and metadata channels are rejected.

For each channel the output statistics are, in order, `latest`, `mean`, `std`,
`slope`. `config.output_schema` is the authoritative tuple of flattened names,
channel first, statistic second. The default contains 96 columns, beginning
with `setting_1_latest`, `setting_1_mean`, `setting_1_std`, `setting_1_slope`,
and ending with the four `sensor_21` fields. Custom channel order is preserved;
never alphabetically sort a model's vector independently of its configuration.

```python
from fleetpulse.features import FeatureConfig

config = FeatureConfig(channels=("sensor_1",), window_cycles=30)
assert config.output_schema == (
    "sensor_1_latest", "sensor_1_mean", "sensor_1_std", "sensor_1_slope",
)
```

`engineer_features(history, dataset_partition=..., unit_id=...,
selected_cycle=..., config=...)` returns an `EngineFeatureVector`. Its
`values` tuple follows `config.output_schema`; `as_dict()` returns the same
values keyed by those names. `engine_key`, `selected_cycle`, `observed_row_count`,
`window_row_count`, and `config` carry the identity and extraction metadata.
`observed_row_count` counts rows at or before the selected cycle, while
`window_row_count` counts the observed rows inside the feature window. If the
cutoff is omitted, the greatest observed cycle is selected.

```python
result = engineer_features(
    history,
    dataset_partition="FD001/train",
    unit_id=4,
    selected_cycle=164,
    config=config,
)
```

## Window and numerical rules for the next consumer

The default `window_cycles=30` means the inclusive cycle interval
`[selected_cycle - 29, selected_cycle]`. Consume only observed rows of the
selected engine inside that interval. For a cutoff of 40, cycle 10 is excluded,
cycle 11 is included, and cycle 41 is future information and excluded. Gaps
are not filled and are not counted as observations; a 30-cycle window is not
a request to reach farther backwards to collect 30 rows. With contiguous
FD001 histories these interpretations give the same rows.

- Use all available observations in the window for short histories; require
  at least one observation at the selected cycle. Reject empty histories,
  missing requested readings and nonfinite values; do not silently impute.
- `latest` is the value at the selected cycle, `mean` is the arithmetic mean,
  and `std` is population standard deviation (`ddof=0`).
- `slope` is least-squares slope of the reading against actual cycle numbers.
  One observation has standard deviation and slope zero.
- Latest, mean and standard deviation retain the channel's source units;
  slope is source units per operating cycle. Sensor units must come from
  source documentation rather than being guessed from the numbers.
- Dataset-qualified engine identity, selected cycle, observed/window row counts,
  and configuration/version accompany an output as metadata. They are not
  additional model feature columns. True RUL and full lifetime are scoring-only.

Abdullah confirmed on 11 November 2026 that he and Shaheer agreed to the
30-cycle past-only window, population standard deviation, actual-cycle slope
and zero one-row standard deviation/slope. PR #320 merged the versioned
configuration and documented interval semantics; issue #43 records acceptance
of that contract. This records the supplied confirmation; no teammate message
was sent by the agent.

## Versioning and evidence boundary

The frozen config has `version="past-only-v1"`; positive integer windows and
immutable unique channel tuples are validated. Persist version, channels,
window and ordered schema with any future feature table/model. A changed
mathematical rule or naming convention requires a new version and retraining;
even within a version, different channels/windows are different configurations.
Any future learned filtering must be fitted only on fitting engines and reused
unchanged for validation. There is no learned filter here.

Observed synthetic numerical check in `tests/test_feature_engineering.py`:
values 2, 4, 6 at cycles 1, 2, 3 produce latest 6, mean 4, population standard
deviation `sqrt(8/3)`, and slope 2. The inclusive-window check uses cycles 11,
20, and 40 for a cutoff of 40, excluding cycle 10 and future cycle 41; the
actual-cycle slope is 2. These are synthetic contract checks, not measured
FD001 results. P05-A2 #119 supplies independent feature checks; P05-S2 #196
owns further short-history checks; A3 #195 owns future-data invariance. The
P05 shared gate remains open.
