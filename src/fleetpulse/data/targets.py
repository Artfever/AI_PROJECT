"""Remaining-cycle labels for complete, run-to-failure training histories."""

from collections.abc import Iterable, Mapping

from fleetpulse.data.quality import validate_engine_history


def calculate_training_rul(records: Iterable[Mapping[str, object]]) -> list[int]:
    """Return each row's engine-specific last cycle minus its observed cycle.

    Input must contain complete training trajectories in the normalized loader
    schema. Completeness and train provenance are the caller's responsibility:
    they cannot be inferred from sensor values. Never use this on truncated test
    histories or a visible prediction prefix. Labels are uncapped cycles in
    input order; no input record is modified and no answer file is accessed.
    """
    rows = tuple(records)
    if not rows:
        raise ValueError("Training RUL requires at least one complete training history.")
    quality = validate_engine_history(rows)
    if not quality.is_valid:
        codes = ", ".join(sorted({finding.code for finding in quality.errors}))
        raise ValueError(f"Cannot calculate training RUL for invalid history: {codes}.")

    last_cycle_by_engine: dict[int, int] = {}
    for row in rows:
        unit_id, cycle = int(row["unit_id"]), int(row["cycle"])
        last_cycle_by_engine[unit_id] = max(last_cycle_by_engine.get(unit_id, cycle), cycle)

    return [last_cycle_by_engine[int(row["unit_id"])] - int(row["cycle"]) for row in rows]
