"""Rebuild P06 development tables and verify both model validation outputs."""

import json
import subprocess
import sys

from fleetpulse import PROJECT_ROOT
from fleetpulse.evaluation.model_comparison import load_model_comparison
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import manifest_digest
from fleetpulse.features.dataset_io import load_feature_dataset


def main() -> None:
    for script in (
        "build_feature_datasets.py",
        "score_constant_baseline.py",
        "train_decision_tree.py",
    ):
        subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / script)],
            cwd=PROJECT_ROOT,
            check=True,
        )

    artifact_dir = PROJECT_ROOT / "artifacts" / "development"
    manifest = json.loads((PROJECT_ROOT / "artifacts" / "split_manifest.json").read_text(encoding="utf-8"))
    expected_source = manifest["source"]["sha256"]
    expected_manifest = manifest_digest(manifest)
    config = FeatureConfig()
    fitting_path = artifact_dir / "fitting_features.json"
    validation_path = artifact_dir / "validation_features.json"
    fitting = load_feature_dataset(
        fitting_path,
        expected_source_sha256=expected_source,
        expected_manifest_sha256=expected_manifest,
        expected_config=config,
    )
    validation = load_feature_dataset(
        validation_path,
        expected_source_sha256=expected_source,
        expected_manifest_sha256=expected_manifest,
        expected_config=config,
    )
    comparison = load_model_comparison(
        artifact_dir,
        fitting,
        validation,
        fitting_dataset_sha256=_payload_hash(fitting_path),
        validation_dataset_sha256=_payload_hash(validation_path),
    )
    print(f"shared_validation_engines: {comparison.validation_engine_count}")
    print(f"constant_mean_mae_cycles: {comparison.baseline_metrics.mae:.12f}")
    print(f"constant_mean_rmse_cycles: {comparison.baseline_metrics.rmse:.12f}")
    print(f"decision_tree_mae_cycles: {comparison.tree_metrics.mae:.12f}")
    print(f"decision_tree_rmse_cycles: {comparison.tree_metrics.rmse:.12f}")
    print("comparison_and_prediction_alignment: passed")


def _payload_hash(path) -> str:
    return json.loads(path.read_text(encoding="utf-8"))["sha256"]


if __name__ == "__main__":
    main()
