"""Audit saved split metadata against source histories without regenerating it."""

import math
from collections.abc import Iterable, Mapping

from fleetpulse.data.quality import validate_engine_history
from fleetpulse.data.split import TRAIN_PARTITION


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(f"Split manifest audit failed: {message}")


def audit_split_manifest(
    manifest: Mapping[str, object],
    records: Iterable[Mapping[str, object]],
    *,
    source_sha256: str,
) -> None:
    """Raise ValueError for an invalid saved split; never alter inputs or files.

    The caller hashes the actual original training source. This checks persisted
    assignments/cutoffs directly against it, without calling the split builder
    or sampling a replacement split. It does not audit a predictor's inputs.
    """
    rows = tuple(records)
    _require(validate_engine_history(rows).is_valid, "source history is invalid.")
    cycles_by_engine: dict[int, list[int]] = {}
    for row in rows:
        cycles_by_engine.setdefault(int(row["unit_id"]), []).append(int(row["cycle"]))
    _require(
        type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1,
        "unsupported schema version.",
    )
    source = manifest.get("source")
    split = manifest.get("split")
    policy = manifest.get("cutoff_policy")
    _require(all(isinstance(item, dict) for item in (source, split, policy)), "missing metadata.")
    _require(
        source.get("dataset_partition") == TRAIN_PARTITION, "source partition is not FD001/train."
    )
    _require(source.get("sha256") == source_sha256, "source SHA-256 mismatch.")
    _require(
        type(source.get("row_count")) is int and source["row_count"] == len(rows),
        "source row count mismatch.",
    )
    _require(
        type(source.get("engine_count")) is int and source["engine_count"] == len(cycles_by_engine),
        "source engine count mismatch.",
    )
    _require(type(split.get("seed")) is int, "missing or invalid split seed.")
    _require(type(policy.get("seed")) is int, "missing or invalid cutoff seed.")
    _require(split.get("algorithm") == "python-random-sample-v1", "unsupported split algorithm.")
    _require(
        policy.get("algorithm") == "python-random-choice-observed-v1"
        and policy.get("selection") == "uniform_over_eligible_observed_cycles",
        "unsupported cutoff policy.",
    )
    _require(policy.get("exclude_terminal") is True, "terminal cycles must be excluded.")
    minimum = policy.get("minimum_history_rows")
    _require(type(minimum) is int and minimum > 0, "minimum history must be a positive integer.")
    fraction = split.get("validation_fraction")
    _require(
        type(fraction) in (int, float) and math.isfinite(fraction) and 0 < fraction < 1,
        "invalid validation fraction.",
    )

    fitting = manifest.get("fitting_engines")
    prefixes = manifest.get("validation_prefixes")
    _require(isinstance(fitting, list) and isinstance(prefixes, list), "missing assignment arrays.")
    _require(bool(fitting) and bool(prefixes), "both engine groups must be nonempty.")

    def identities(entries: list) -> set[int]:
        ids = []
        for entry in entries:
            _require(isinstance(entry, dict), "engine entry must be an object.")
            _require(
                entry.get("dataset_partition") == TRAIN_PARTITION, "engine partition mismatch."
            )
            unit = entry.get("unit_id")
            _require(type(unit) is int and unit in cycles_by_engine, "unknown source engine ID.")
            ids.append(unit)
        _require(len(set(ids)) == len(ids), "duplicate engine assignment.")
        return set(ids)

    fitting_ids, validation_ids = identities(fitting), identities(prefixes)
    _require(not fitting_ids & validation_ids, "fitting/validation trajectory overlap.")
    _require(
        fitting_ids | validation_ids == set(cycles_by_engine), "assignments omit source engines."
    )
    expected_count = min(len(cycles_by_engine) - 1, math.ceil(len(cycles_by_engine) * fraction))
    _require(len(prefixes) == expected_count, "validation count differs from declared fraction.")
    for prefix in prefixes:
        cycles = cycles_by_engine[prefix["unit_id"]]
        lifetime = max(cycles)
        eligible = [
            cycle for count, cycle in enumerate(cycles, 1) if count >= minimum and cycle < lifetime
        ]
        _require(bool(eligible), "validation engine has no eligible observed cutoff.")
        cutoff = prefix.get("cutoff_cycle")
        _require(
            type(cutoff) is int and cutoff in eligible,
            "cutoff is not an eligible nonterminal cycle.",
        )
        observed_prefix = [cycle for cycle in cycles if cycle <= cutoff]
        _require(len(observed_prefix) >= minimum, "validation prefix is shorter than the minimum.")
        _require(
            type(prefix.get("prefix_row_count")) is int
            and prefix["prefix_row_count"] == len(observed_prefix),
            "prefix row count mismatch.",
        )
        _require(
            prefix.get("eligible_cutoff_range") == {"first": min(eligible), "last": max(eligible)},
            "eligible cutoff range mismatch.",
        )
        _require(
            type(prefix.get("eligible_cutoff_count")) is int
            and prefix["eligible_cutoff_count"] == len(eligible),
            "eligible cutoff count mismatch.",
        )
        _require(
            type(prefix.get("full_lifetime")) is int and prefix["full_lifetime"] == lifetime,
            "full lifetime mismatch.",
        )
        _require(
            type(prefix.get("target_rul")) is int and prefix["target_rul"] == lifetime - cutoff > 0,
            "positive target RUL mismatch.",
        )
