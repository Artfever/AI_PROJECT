"""Compare saved-service predictions with the P06 offline validation oracle."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history
from fleetpulse.services import predict_rul

EXPECTED_VALIDATION_PREFIXES = 20


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def validate_parity_report(report: dict[str, Any]) -> None:
    """Reject incomplete, duplicated, or numerically different parity reports."""
    predictions = report.get("predictions")
    if not isinstance(predictions, list) or len(predictions) != EXPECTED_VALIDATION_PREFIXES:
        actual = len(predictions) if isinstance(predictions, list) else 0
        raise ValueError(
            f"Expected {EXPECTED_VALIDATION_PREFIXES} validation prefixes; got {actual}."
        )

    identities = [
        (row["dataset_partition"], int(row["unit_id"]), int(row["cutoff_cycle"]))
        for row in predictions
    ]
    if len(set(identities)) != EXPECTED_VALIDATION_PREFIXES:
        raise ValueError("Validation oracle must contain 20 unique partition/engine/cycle identities.")
    if report.get("sample_count") != EXPECTED_VALIDATION_PREFIXES:
        raise ValueError("Parity report sample_count does not match its 20 prediction rows.")

    differences = [float(row["absolute_difference_cycles"]) for row in predictions]
    if any(not math.isfinite(value) for value in differences):
        raise ValueError("Parity report contains a non-finite prediction difference.")
    maximum = max(differences)
    if maximum != float(report["max_absolute_difference_cycles"]):
        raise ValueError("Reported maximum difference does not match the prediction rows.")
    exact_count = sum(value == 0.0 for value in differences)
    if report.get("exact_match_count") != exact_count:
        raise ValueError("Reported exact_match_count does not match the prediction rows.")
    if maximum != 0.0:
        raise ValueError(
            f"Saved-service parity failed: maximum absolute difference is {maximum:.12f} cycles."
        )


def compare_saved_predictions(
    *,
    training_path: Path,
    model_manifest_path: Path,
    offline_predictions_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    """Replay each fixed P06 validation prefix through the saved inference service."""
    source_bytes = training_path.read_bytes()
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    training_document = json.loads(model_manifest_path.read_text(encoding="utf-8"))
    training = training_document["payload"]["training"]
    if training["source_sha256"] != source_sha256:
        raise ValueError("FD001/train source SHA-256 differs from the P06 model provenance.")

    offline_document = json.loads(offline_predictions_path.read_text(encoding="utf-8"))
    offline_payload = offline_document["payload"]
    if offline_document["sha256"] != hashlib.sha256(_canonical(offline_payload)).hexdigest():
        raise ValueError("P06 saved prediction manifest content hash mismatch.")
    if offline_payload["training"]["source_sha256"] != source_sha256:
        raise ValueError("P06 saved prediction source SHA-256 differs from FD001/train.")
    if offline_payload["model"] != training_document["payload"]["model"]:
        raise ValueError("P06 validation oracle and model manifest identify different models.")

    histories: dict[int, list[dict[str, int | float]]] = {}
    for row in load_engine_history(training_path):
        histories.setdefault(int(row["unit_id"]), []).append(row)

    compared = []
    for oracle in offline_payload["evaluation"]["predictions"]:
        engine_id = int(oracle["unit_id"])
        cutoff = int(oracle["cutoff_cycle"])
        prefix = [row for row in histories.get(engine_id, ()) if int(row["cycle"]) <= cutoff]
        if not prefix or int(prefix[-1]["cycle"]) != cutoff:
            raise ValueError(f"Training history does not contain engine {engine_id} at cycle {cutoff}.")
        result = predict_rul(
            prefix,
            dataset_partition=oracle["dataset_partition"],
            unit_id=engine_id,
            manifest_path=model_manifest_path,
        )
        offline = float(oracle["prediction_cycles"])
        service = result.raw_rul_cycles
        compared.append(
            {
                "dataset_partition": oracle["dataset_partition"],
                "unit_id": engine_id,
                "cutoff_cycle": cutoff,
                "offline_prediction_cycles": offline,
                "service_prediction_cycles": service,
                "absolute_difference_cycles": abs(service - offline),
                "true_rul_cycles": oracle["true_rul_cycles"],
            }
        )

    if not compared:
        raise ValueError("P06 validation oracle contains no predictions.")
    max_difference = max(row["absolute_difference_cycles"] for row in compared)
    payload = {
        "schema_version": "p07-service-parity-v1",
        "model": {
            "name": training_document["payload"]["model"]["name"],
            "version": training_document["payload"]["model"]["version"],
            "model_sha256": training_document["payload"]["model"]["sha256"],
            "scikit_learn_version": training_document["payload"]["model"]["scikit_learn_version"],
            "random_seed": training["random_seed"],
            "parameters": training["parameters"],
        },
        "partition": offline_payload["evaluation"]["partition"],
        "sample_unit": "engine-prefix",
        "sample_count": len(compared),
        "training_source_sha256": source_sha256,
        "validation_oracle_sha256": offline_document["sha256"],
        "max_absolute_difference_cycles": max_difference,
        "exact_match_count": sum(row["absolute_difference_cycles"] == 0 for row in compared),
        "predictions": compared,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training", type=Path, default=PROJECT_ROOT / "data/raw/train_FD001.txt")
    parser.add_argument(
        "--model-manifest",
        type=Path,
        default=PROJECT_ROOT / "artifacts/development/decision_tree_validation.json",
    )
    parser.add_argument(
        "--offline-predictions",
        type=Path,
        default=PROJECT_ROOT / "artifacts/development/decision_tree_validation.json",
    )
    parser.add_argument(
        "--output", type=Path, default=PROJECT_ROOT / "reports/p07_service_parity.json"
    )
    args = parser.parse_args(argv)
    result = compare_saved_predictions(
        training_path=args.training,
        model_manifest_path=args.model_manifest,
        offline_predictions_path=args.offline_predictions,
        output_path=args.output,
    )
    try:
        validate_parity_report(result)
    except ValueError as error:
        print(f"saved_service_parity: failed; {error}; report={args.output}", file=sys.stderr)
        return 1
    print(
        "saved_service_parity: passed; "
        f"model={result['model']['name']}@{result['model']['version']}; "
        f"predictions={result['sample_count']}; "
        f"exact_matches={result['exact_match_count']}; "
        f"max_difference_cycles={result['max_absolute_difference_cycles']:.12f}; "
        f"report={args.output.relative_to(PROJECT_ROOT)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
