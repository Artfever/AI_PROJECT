"""Build auditable engine assignments and observed validation-prefix cutoffs."""

import random
import re
from collections.abc import Iterable, Mapping
from dataclasses import asdict

from fleetpulse.data.split import split_training_engines


def build_split_manifest(
    records: Iterable[Mapping[str, object]],
    *,
    dataset_partition: str,
    source_path: str,
    source_sha256: str,
    split_seed: int = 42,
    cutoff_seed: int = 42,
    validation_fraction: float = 0.2,
    minimum_history_rows: int = 1,
) -> dict[str, object]:
    """Choose one observed cutoff before failure for each held-out engine.

    Full lifetimes and RUL are scoring metadata, never prediction inputs. The
    caller supplies verified original-training provenance; no file is read here.
    If a selected engine has no eligible cutoff, fail rather than changing its
    assignment, dropping it, or admitting its terminal cycle.
    """
    if isinstance(cutoff_seed, bool) or not isinstance(cutoff_seed, int):
        raise TypeError("cutoff_seed must be an integer.")
    if isinstance(minimum_history_rows, bool) or not isinstance(minimum_history_rows, int):
        raise TypeError("minimum_history_rows must be an integer.")
    if minimum_history_rows < 1:
        raise ValueError("minimum_history_rows must be at least 1.")
    if re.fullmatch(r"[a-f0-9]{64}", source_sha256) is None:
        raise ValueError("source_sha256 must be a lowercase SHA-256 hex digest.")

    rows = tuple(records)
    split = split_training_engines(
        rows, dataset_partition=dataset_partition, seed=split_seed,
        validation_fraction=validation_fraction,
    )
    cycles_by_engine: dict[int, list[int]] = {}
    for row in rows:
        cycles_by_engine.setdefault(int(row["unit_id"]), []).append(int(row["cycle"]))
    generator = random.Random(cutoff_seed)
    prefixes = []
    for identity in split.validation_engines:
        cycles = cycles_by_engine[identity.unit_id]
        # Index encodes actual observed-row count, even when cycles have gaps.
        eligible = list(enumerate(cycles, start=1))[minimum_history_rows - 1:-1]
        if not eligible:
            raise ValueError(
                f"{dataset_partition} engine {identity.unit_id}: no nonterminal cutoff "
                f"with at least {minimum_history_rows} observed rows."
            )
        prefix_rows, cutoff = generator.choice(eligible)
        prefixes.append({
            **asdict(identity),
            "cutoff_cycle": cutoff,
            "prefix_row_count": prefix_rows,
            "eligible_cutoff_range": {"first": eligible[0][1], "last": eligible[-1][1]},
            "eligible_cutoff_count": len(eligible),
            "full_lifetime": cycles[-1],
            "target_rul": cycles[-1] - cutoff,
        })
    return {
        "schema_version": 1,
        "source": {
            "dataset_partition": dataset_partition,
            "path": source_path,
            "sha256": source_sha256,
            "row_count": len(rows),
            "engine_count": len(cycles_by_engine),
        },
        "split": {
            "seed": split.seed,
            "validation_fraction": split.validation_fraction,
            "algorithm": split.algorithm,
        },
        "cutoff_policy": {
            "seed": cutoff_seed,
            "minimum_history_rows": minimum_history_rows,
            "exclude_terminal": True,
            "algorithm": "python-random-choice-observed-v1",
            "selection": "uniform_over_eligible_observed_cycles",
        },
        "fitting_engines": [asdict(identity) for identity in split.fitting_engines],
        "validation_prefixes": prefixes,
    }
