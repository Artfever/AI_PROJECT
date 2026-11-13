"""Print three saved-model local reference predictions without reading test answers."""

import hashlib
import json

import sklearn

from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history
from fleetpulse.services import predict_rul_with_context

TRAIN_SHA256 = "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8"
EXAMPLES = ((4, 164), (5, 58), (12, 7))


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = PROJECT_ROOT / "data/raw/train_FD001.txt"
    manifest = PROJECT_ROOT / "artifacts/development/decision_tree_validation.json"
    if sha256_file(source) != TRAIN_SHA256:
        raise ValueError("Local training history does not match the recorded FD001 source hash.")
    rows = load_engine_history(source)
    outputs = []
    for unit, cutoff in EXAMPLES:
        history = [row for row in rows if row["unit_id"] == unit and row["cycle"] <= cutoff]
        if not history or history[-1]["cycle"] != cutoff:
            raise ValueError(f"Engine {unit} does not have the requested cycle {cutoff}.")
        result = predict_rul_with_context(
            history, dataset_partition="FD001/train", unit_id=unit, manifest_path=manifest
        )
        outputs.append(
            {
                "unit_id": unit,
                "selected_cycle": cutoff,
                "observed_rows": len(history),
                "raw_rul_cycles": result.raw_rul_cycles,
                "displayed_rul_cycles": result.displayed_rul_cycles,
                "model_name": result.model_name,
                "model_version": result.model_version,
                "warnings": result.warnings,
            }
        )
    print(
        json.dumps(
            {
                "data_source": "NASA C-MAPSS FD001 simulated training histories",
                "source_sha256": TRAIN_SHA256,
                "model_sha256": sha256_file(manifest.parent / "decision_tree_model.joblib"),
                "manifest_sha256": sha256_file(manifest),
                "scikit_learn_version": sklearn.__version__,
                "examples": outputs,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
