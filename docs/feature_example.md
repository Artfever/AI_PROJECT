# Feature example: one visible training prefix

This example uses the local **simulated NASA FD001 training** file described in
[FD001 provenance](fd001_provenance.md). It is a feature calculation, not a
model prediction. In Engine Explorer, choose training engine **4**, open the
development feature preview and select cycle **3**. The visible prefix has three
observed rows; no later cycles are needed or passed into the feature function.

For `sensor_2`, the source readings are:

| Operating cycle | sensor_2 reading |
| ---: | ---: |
| 1 | 642.60 |
| 2 | 642.45 |
| 3 | 642.16 |

The default `past-only-v1` configuration uses a 30-cycle window, so all three
available readings are included. The independent hand calculations are:

- Mean: `(642.60 + 642.45 + 642.16) / 3 = 642.403333...`.
- Least-squares slope: the cycle mean is 2, so the centered products are
  `(-1 × -0.196666...) + (0 × 0.046666...) + (1 × -0.243333...) = -0.44`.
  The centered cycle-square sum is `1 + 0 + 1 = 2`; slope is `-0.44 / 2 = -0.22`.

The extractor returned `sensor_2_mean = 642.4033333333333` and
`sensor_2_slope = -0.22000000000002728`, matching the hand values within a
`1e-10` absolute tolerance; the tiny difference is floating-point rounding. It
returned 96 features overall and reported three visible and three window rows.
The mean retains the sensor's source units and the slope is in those units per
operating cycle; this example does not assert a physical unit not established by
the source documentation.

Dataset partition, engine ID and selected cycle identify the example; they are
metadata, not model feature columns. True RUL, final lifetime and future
readings are excluded from the input. This check used the training file only and
did not read official test answers. The complete feature schema and window
rules are in [the feature contract](feature_contract.md).
