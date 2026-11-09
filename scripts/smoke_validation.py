"""Run a tiny evaluator example on artificial histories; never train a model."""

import json
from dataclasses import asdict

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.evaluation import calculate_validation_metrics, evaluate_validation_prefix


def run_smoke() -> dict:
    """Evaluate a fixed three-cycle callback on two wholly synthetic histories."""
    observed = []

    def constant_predictor(prefix):
        observed.append([int(row["cycle"]) for row in prefix])
        return 3.0

    cases = ((900001, 6, 4), (900002, 8, 3))
    results = []
    for unit_id, terminal_cycle, cutoff in cases:
        history = [
            {"unit_id": unit_id, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 0.5)}
            for cycle in range(1, terminal_cycle + 1)
        ]
        results.append(
            evaluate_validation_prefix(
                history,
                dataset_partition="FD001/train",
                unit_id=unit_id,
                cutoff_cycle=cutoff,
                predictor=constant_predictor,
            )
        )
    metrics = calculate_validation_metrics(results)
    return {
        "data_provenance": "Artificial synthetic histories; not NASA data or model performance",
        "partition_note": "FD001/train is the evaluator's required interface; these rows are synthetic",
        "predictor": "Fixed illustrative callback: 3.0 cycles for every prefix; no training",
        "visible_cycles": observed,
        "predictions": [asdict(result) for result in results],
        "illustrative_metrics_cycles": {"mae": metrics.mae, "rmse": metrics.rmse},
    }


def main() -> None:
    print(json.dumps(run_smoke(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
