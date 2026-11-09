# Whole-engine development split

P04-A1 / [#40](https://github.com/Artfever/FleetpulseAI/issues/40).

`fleetpulse.data.split.split_training_engines` assigns **complete original
training engines** to fitting and validation groups. It never splits rows of
one engine across groups, samples rows, or balances groups using RUL/sensors.

```python
from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.split import TRAIN_PARTITION, split_training_engines

rows = load_engine_history(PROJECT_ROOT / "data/raw/train_FD001.txt")
split = split_training_engines(rows, dataset_partition=TRAIN_PARTITION, seed=42)
```

The return value is a frozen `EngineSplit` containing sorted tuples of
`EngineIdentity(dataset_partition, unit_id)` for `fitting_engines` and
`validation_engines`, plus the seed, requested validation fraction, and algorithm
identifier `python-random-sample-v1`. `FD001/train` qualifies every ID, so it must
not be confused with the same numeric ID in `FD001/test`. The caller must
establish source provenance and complete trajectories; declaring a partition
cannot detect test data deliberately mislabeled as training data.

Unique IDs are sorted before a local `random.Random(seed).sample` call. Thus
engine-group input order and unequal trajectory lengths do not affect
membership, and the global random generator is untouched. Validation size is
`ceil(number_of_engines * validation_fraction)`, capped to leave at least one
fitting engine. At least two engines are required; both groups are nonempty.
Defaults are seed `42` and validation fraction `0.2`. For small cohorts, rounding
can depart from 80/20; the real 100-engine training set splits exactly 80/20.
The raw normalized schema is validated first; invalid histories raise
`ValueError`, and a noninteger seed raises `TypeError`.

Local verification on 9 November 2026 produced 80 fitting engines (16,738 rows)
and 20 validation engines (3,893 rows). Validation IDs were:

```text
4, 5, 12, 14, 15, 18, 28, 29, 30, 32, 36, 55, 65, 70, 72, 76, 78, 82, 87, 95
```

These observed assignments are a proposed development configuration for peer
review, not model results. Agree the seed and cutoff policy with Shaheer before
comparing models. Neither the official test histories nor their answers enter
this choice. Do not retry seeds based on validation/model scores.

This API returns identities only. Consumers associate **every** raw row with
its engine's assigned group; never reshuffle rows independently. It does not
yet persist a manifest, select prefix cutoffs, create features, fit preprocessing
or models, or evaluate predictions. P04-A2 will save exact assignments, source
provenance, configuration and cutoff policy; P04-A3 verifies that contract.
For reproducibility, persist the exact groups rather than relying only on a
future Python version's sampling implementation. Taha's audit page and Shaheer's
prefix evaluator consume those later reviewed artifacts, not fabricated counts.

Run `python -m pytest -q tests/test_engine_split.py` for synthetic engine-level
separation, rounding, invalid input, determinism and global-RNG isolation tests.
