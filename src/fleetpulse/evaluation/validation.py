"""Score a development prediction made from a visible training-history prefix."""

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from math import isfinite
from numbers import Integral, Real

from fleetpulse.data.quality import validate_engine_history

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
    if dataset_partition != "train":
        raise ValueError("Development validation labels must come from the train partition.")
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
        dataset_partition="train",
        unit_id=requested_unit,
        cutoff_cycle=cutoff,
        prediction=prediction,
        true_rul=full_lifetime - cutoff,
    )
