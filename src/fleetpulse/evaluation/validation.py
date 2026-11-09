"""Score a development prediction made from a visible training-history prefix."""

import re
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from math import isfinite
from numbers import Integral, Real

from fleetpulse.data.quality import validate_engine_history
from fleetpulse.data.split import TRAIN_PARTITION

HistoryRow = Mapping[str, object]
PrefixPredictor = Callable[[tuple[dict[str, object], ...]], Real]


@dataclass(frozen=True)
class ValidationPrediction:
    """One prediction and label, identified by its source partition and engine."""

    dataset_partition: str
    unit_id: int
    cutoff_cycle: int
    prediction: float
    true_rul: int

    @property
    def engine_key(self) -> tuple[str, int]:
        """Return a dataset-qualified engine identity."""
        return self.dataset_partition, self.unit_id


def _positive_integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 1:
        raise ValueError(f"{name} must be a positive integer.")
    return int(value)


def evaluate_validation_prefix(
    history: Iterable[HistoryRow],
    *,
    dataset_partition: str,
    unit_id: int,
    cutoff_cycle: int,
    predictor: PrefixPredictor,
) -> ValidationPrediction:
    """Predict from cycles through ``cutoff_cycle`` and label from train lifetime.

    ``history`` must be one complete original training trajectory. The final
    cycle supplies the scoring-only lifetime; the predictor receives copied
    rows at or before the cutoff and cannot access later rows through its input.
    This function intentionally does not read development or official-test RUL
    answer files and does not choose the split or cutoff.
    """
    if dataset_partition != TRAIN_PARTITION:
        raise ValueError(f"Development validation requires {TRAIN_PARTITION} histories.")
    requested_unit = _positive_integer(unit_id, "unit_id")
    cutoff = _positive_integer(cutoff_cycle, "cutoff_cycle")

    rows = tuple(history)
    if not rows:
        raise ValueError("A complete training history is required.")
    report = validate_engine_history(rows)
    if not report.is_valid:
        codes = ", ".join(sorted({finding.code for finding in report.errors}))
        raise ValueError(f"Cannot score an invalid engine history: {codes}.")

    unit_ids = {int(row["unit_id"]) for row in rows}
    if unit_ids != {requested_unit}:
        raise ValueError("History must contain only the requested unit_id.")

    cycles = [int(row["cycle"]) for row in rows]
    full_lifetime = max(cycles)
    if cycles[0] != 1:
        raise ValueError("A complete training history must start at cycle 1.")
    if cutoff >= full_lifetime:
        raise ValueError("cutoff_cycle must be before the engine's terminal cycle.")
    if cutoff not in cycles:
        raise ValueError("cutoff_cycle must identify an observed cycle in the history.")

    prefix = tuple(dict(row) for row in rows if int(row["cycle"]) <= cutoff)
    raw_prediction = predictor(prefix)
    if isinstance(raw_prediction, bool) or not isinstance(raw_prediction, Real):
        raise TypeError("predictor must return a numeric RUL estimate.")
    prediction = float(raw_prediction)
    if not isfinite(prediction):
        raise ValueError("predictor must return a finite numeric RUL estimate.")

    return ValidationPrediction(
        dataset_partition=TRAIN_PARTITION,
        unit_id=requested_unit,
        cutoff_cycle=cutoff,
        prediction=prediction,
        true_rul=full_lifetime - cutoff,
    )


def evaluate_validation_manifest(
    history: Iterable[HistoryRow],
    *,
    manifest: Mapping[str, object],
    source_sha256: str,
    predictor: PrefixPredictor,
) -> tuple[ValidationPrediction, ...]:
    """Score every validation prefix in a schema-v1 P04 split manifest.

    ``history`` must be the complete original FD001 training source used to
    generate the manifest. The caller supplies that source's independently
    calculated SHA-256; it is compared with the manifest before any prediction
    is requested. Each manifest cutoff, lifetime, target and prefix row count
    is checked against observed histories. Fitting engines are never sent to
    ``predictor``. Full lifetime and target RUL remain scoring metadata.
    """
    if not isinstance(manifest, Mapping):
        raise TypeError("Manifest must be a mapping.")
    if manifest.get("schema_version") != 1 or isinstance(manifest.get("schema_version"), bool):
        raise ValueError("Only split manifest schema_version 1 is supported.")
    source = manifest.get("source")
    if not isinstance(source, Mapping):
        raise TypeError("Manifest source metadata must be a mapping.")
    if source.get("dataset_partition") != TRAIN_PARTITION:
        raise ValueError(f"Manifest source must be {TRAIN_PARTITION}.")
    manifest_sha256 = source.get("sha256")
    if (
        not isinstance(manifest_sha256, str)
        or re.fullmatch(r"[a-f0-9]{64}", manifest_sha256) is None
        or source_sha256 != manifest_sha256
    ):
        raise ValueError("Training source SHA-256 does not match the split manifest.")

    rows = tuple(history)
    if not rows:
        raise ValueError("A complete training history is required.")
    report = validate_engine_history(rows)
    if not report.is_valid:
        codes = ", ".join(sorted({finding.code for finding in report.errors}))
        raise ValueError(f"Cannot score an invalid training history: {codes}.")

    rows_by_unit: dict[int, list[HistoryRow]] = {}
    for row in rows:
        rows_by_unit.setdefault(int(row["unit_id"]), []).append(row)
    if _positive_integer(source.get("row_count"), "source.row_count") != len(rows):
        raise ValueError("Training history row count does not match the split manifest.")
    if _positive_integer(source.get("engine_count"), "source.engine_count") != len(rows_by_unit):
        raise ValueError("Training history engine count does not match the split manifest.")

    fitting_engines = _manifest_engine_ids(manifest.get("fitting_engines"), "fitting_engines")
    if not fitting_engines:
        raise ValueError("Manifest must contain at least one fitting engine.")
    validation_entries = manifest.get("validation_prefixes")
    if not isinstance(validation_entries, Sequence) or isinstance(validation_entries, (str, bytes)):
        raise TypeError("Manifest validation_prefixes must be a sequence.")
    if not validation_entries:
        raise ValueError("Manifest must contain at least one validation prefix.")

    validation_ids: set[int] = set()
    predictions: list[ValidationPrediction] = []
    for index, entry in enumerate(validation_entries):
        if not isinstance(entry, Mapping):
            raise TypeError(f"Manifest validation prefix {index} must be a mapping.")
        if entry.get("dataset_partition") != TRAIN_PARTITION:
            raise ValueError(f"Manifest validation prefix {index} is not qualified as {TRAIN_PARTITION}.")
        unit = _positive_integer(entry.get("unit_id"), f"validation_prefixes[{index}].unit_id")
        if unit in validation_ids:
            raise ValueError(f"Manifest contains duplicate validation engine {unit}.")
        validation_ids.add(unit)
        if unit in fitting_engines:
            raise ValueError(f"Engine {unit} is assigned to both fitting and validation.")
        engine_rows = rows_by_unit.get(unit)
        if engine_rows is None:
            raise ValueError(f"Manifest validation engine {unit} is absent from training history.")

        cutoff = _positive_integer(entry.get("cutoff_cycle"), f"validation_prefixes[{index}].cutoff_cycle")
        expected_lifetime = _positive_integer(
            entry.get("full_lifetime"), f"validation_prefixes[{index}].full_lifetime"
        )
        expected_target = _positive_integer(
            entry.get("target_rul"), f"validation_prefixes[{index}].target_rul"
        )
        expected_prefix_count = _positive_integer(
            entry.get("prefix_row_count"), f"validation_prefixes[{index}].prefix_row_count"
        )
        cycles = [int(row["cycle"]) for row in engine_rows]
        observed_lifetime = max(cycles)
        observed_target = observed_lifetime - cutoff
        observed_prefix_count = sum(cycle <= cutoff for cycle in cycles)
        if observed_lifetime != expected_lifetime:
            raise ValueError(f"Manifest lifetime does not match training history for engine {unit}.")
        if observed_target != expected_target:
            raise ValueError(f"Manifest target RUL does not match training history for engine {unit}.")
        if observed_prefix_count != expected_prefix_count:
            raise ValueError(f"Manifest prefix row count does not match training history for engine {unit}.")
        result = evaluate_validation_prefix(
            engine_rows,
            dataset_partition=TRAIN_PARTITION,
            unit_id=unit,
            cutoff_cycle=cutoff,
            predictor=predictor,
        )
        predictions.append(result)

    if validation_ids & fitting_engines:
        raise ValueError("Manifest fitting and validation engine groups must be disjoint.")
    if fitting_engines | validation_ids != set(rows_by_unit):
        raise ValueError("Manifest engine groups must cover the complete training history.")
    return tuple(predictions)


def _manifest_engine_ids(value: object, name: str) -> set[int]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError(f"Manifest {name} must be a sequence.")
    engine_ids: set[int] = set()
    for index, entry in enumerate(value):
        if not isinstance(entry, Mapping) or entry.get("dataset_partition") != TRAIN_PARTITION:
            raise ValueError(f"Manifest {name}[{index}] must be qualified as {TRAIN_PARTITION}.")
        unit = _positive_integer(entry.get("unit_id"), f"{name}[{index}].unit_id")
        if unit in engine_ids:
            raise ValueError(f"Manifest {name} contains duplicate engine {unit}.")
        engine_ids.add(unit)
    return engine_ids
