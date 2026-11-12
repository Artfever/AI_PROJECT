"""Train the initial bounded Decision Tree on saved P06 feature tables."""

import json
from dataclasses import asdict

from fleetpulse import PROJECT_ROOT
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import manifest_digest
from fleetpulse.features.dataset_io import load_feature_dataset
from fleetpulse.models.train_tree import MODEL_VERSION, train_decision_tree

TRAIN_SHA256 = "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8"


def main() -> None:
    artifact_dir = PROJECT_ROOT / "artifacts/development"
    manifest = json.loads((PROJECT_ROOT / "artifacts/split_manifest.json").read_text(encoding="utf-8"))
    fitting = load_feature_dataset(
        artifact_dir / "fitting_features.json",
        expected_source_sha256=TRAIN_SHA256,
        expected_manifest_sha256=manifest_digest(manifest),
        expected_config=FeatureConfig(),
    )
    validation = load_feature_dataset(
        artifact_dir / "validation_features.json",
        expected_source_sha256=TRAIN_SHA256,
        expected_manifest_sha256=manifest_digest(manifest),
        expected_config=FeatureConfig(),
    )
    result = train_decision_tree(fitting, validation)
    print(f"model_version: {MODEL_VERSION}")
    print(f"scikit_learn_version: {__import__('sklearn').__version__}")
    print(f"feature_config: {json.dumps(asdict(fitting.config), sort_keys=True)}")
    print(f"seed: {result.random_seed}")
    print(f"parameters: max_depth={result.max_depth}, min_samples_leaf={result.min_samples_leaf}")
    print(f"fitting_rows: {len(fitting.rows)}")
    print(f"fitting_engines: {len({row.vector.engine_key for row in fitting.rows})}")
    print(f"validation_engines: {result.metrics.engine_count}")
    print(f"mae_cycles: {result.metrics.mae:.12f}")
    print(f"rmse_cycles: {result.metrics.rmse:.12f}")
    print(f"training_and_scoring_runtime_seconds: {result.runtime_seconds:.9f}")
    for row in result.metrics.per_engine[:3]:
        print(
            f"example unit={row.unit_id} cutoff={row.cutoff_cycle}: "
            f"predicted={row.prediction:.6f}, actual={row.true_rul}, "
            f"absolute_error={row.absolute_error:.6f} cycles"
        )


if __name__ == "__main__":
    main()
