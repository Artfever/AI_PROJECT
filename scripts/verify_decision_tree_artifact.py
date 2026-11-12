"""Reload and check a saved P06 Decision Tree in an independent process."""

import json
import sys
from pathlib import Path

from fleetpulse.features.dataset_io import load_feature_dataset
from fleetpulse.models.tree_artifact import verify_decision_tree_artifact


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify_decision_tree_artifact.py MANIFEST VALIDATION_FEATURES")
    manifest_path, validation_path = map(Path, sys.argv[1:])
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))["payload"]
    training = payload["training"]
    validation = load_feature_dataset(
        validation_path,
        expected_source_sha256=training["source_sha256"],
        expected_manifest_sha256=training["split_manifest_sha256"],
    )
    result = verify_decision_tree_artifact(manifest_path, validation)
    print(
        "fresh_process_reload: passed; "
        f"predictions={result['prediction_count']}; "
        f"mae_cycles={result['mae_cycles']:.12f}; "
        f"rmse_cycles={result['rmse_cycles']:.12f}"
    )


if __name__ == "__main__":
    main()
