"""Reproducible whole-engine development split of original training histories."""

import math
import random
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from numbers import Real

from fleetpulse.data.quality import validate_engine_history

TRAIN_PARTITION = "FD001/train"


@dataclass(frozen=True, order=True)
class EngineIdentity:
    """Engine ID qualified by dataset and partition, rather than ID alone."""

    dataset_partition: str
    unit_id: int


@dataclass(frozen=True)
class EngineSplit:
    """Assignments only; no target values, prefix cutoffs or copied sensor rows."""

    fitting_engines: tuple[EngineIdentity, ...]
    validation_engines: tuple[EngineIdentity, ...]
    seed: int
    validation_fraction: float
    algorithm: str = "python-random-sample-v1"


def split_training_engines(
    records: Iterable[Mapping[str, object]],
    *,
    dataset_partition: str,
    seed: int = 42,
    validation_fraction: float = 0.2,
) -> EngineSplit:
    """Assign entire original-training engines, independently of row counts.

    The caller must supply complete original FD001 training trajectories and
    explicitly declare ``FD001/train``. Provenance cannot be inferred from
    sensor values. Official test histories/answers are not development inputs.
    Sorted unique IDs precede local seeded sampling; output groups are sorted.
    Validation size is ceil(n_engines * fraction), capped to leave one fitting
    engine. At least two engines and a finite fraction strictly in (0, 1) are
    required. No input rows are modified or dropped.
    """
    if dataset_partition != TRAIN_PARTITION:
        raise ValueError("Development splitting requires original FD001/train histories.")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer.")
    if (
        isinstance(validation_fraction, bool)
        or not isinstance(validation_fraction, Real)
        or not math.isfinite(validation_fraction)
        or not 0 < validation_fraction < 1
    ):
        raise ValueError("validation_fraction must be finite and strictly between 0 and 1.")
    rows = tuple(records)
    quality = validate_engine_history(rows)
    if not quality.is_valid:
        codes = ", ".join(sorted({finding.code for finding in quality.errors}))
        raise ValueError(f"Cannot split invalid training history: {codes}.")
    engines = sorted({int(row["unit_id"]) for row in rows})
    if len(engines) < 2:
        raise ValueError("At least two complete training engines are required for a split.")
    count = min(len(engines) - 1, math.ceil(len(engines) * validation_fraction))
    validation_ids = set(random.Random(seed).sample(engines, count))
    return EngineSplit(
        fitting_engines=tuple(
            EngineIdentity(TRAIN_PARTITION, engine) for engine in engines if engine not in validation_ids
        ),
        validation_engines=tuple(
            EngineIdentity(TRAIN_PARTITION, engine) for engine in engines if engine in validation_ids
        ),
        seed=seed,
        validation_fraction=float(validation_fraction),
    )
