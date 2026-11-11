"""Rebuild and score the selected mean baseline on saved FD001 validation rows."""

import hashlib
import json
from dataclasses import asdict
from math import fsum, sqrt

from fleetpulse import PROJECT_ROOT
from fleetpulse.evaluation import score_constant_baseline
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import manifest_digest
from fleetpulse.features.dataset_io import load_feature_dataset

TRAIN_SHA256 = "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8"
ARTIFACT_VERSION = "constant-rul-validation-v1"


def _canonical_sha256(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _dataset_payload_sha256(path):
    document = json.loads(path.read_text(encoding="utf-8"))
    return document["sha256"]


def main():
    artifact_dir = PROJECT_ROOT / "artifacts/development"
    manifest = json.loads((PROJECT_ROOT / "artifacts/split_manifest.json").read_text(encoding="utf-8"))
    manifest_sha256 = manifest_digest(manifest)
    config = FeatureConfig()
    fitting_path = artifact_dir / "fitting_features.json"
    validation_path = artifact_dir / "validation_features.json"
    fitting = load_feature_dataset(
        fitting_path,
        expected_source_sha256=TRAIN_SHA256,
        expected_manifest_sha256=manifest_sha256,
        expected_config=config,
    )
    validation = load_feature_dataset(
        validation_path,
        expected_source_sha256=TRAIN_SHA256,
        expected_manifest_sha256=manifest_sha256,
        expected_config=config,
    )
    result = score_constant_baseline(fitting, validation, statistic="mean")

    partitions = {row.dataset_partition for row in result.metrics.per_engine}
    if len(partitions) != 1:
        raise ValueError("Validation result contains mixed dataset partitions.")
    payload = {
        "artifact_version": ARTIFACT_VERSION,
        "baseline": result.baseline.to_artifact(),
        "evaluation": {
            "dataset_partition": next(iter(partitions)),
            "sample_unit": "engine",
            "sample_count": result.metrics.engine_count,
            "feature_config": asdict(config),
            "random_seed": None,
            "source_sha256": TRAIN_SHA256,
            "split_manifest_sha256": manifest_sha256,
            "fitting_dataset_sha256": _dataset_payload_sha256(fitting_path),
            "validation_dataset_sha256": _dataset_payload_sha256(validation_path),
            "mae_cycles": result.metrics.mae,
            "rmse_cycles": result.metrics.rmse,
            "predictions": [
                {
                    "dataset_partition": row.dataset_partition,
                    "unit_id": row.unit_id,
                    "cutoff_cycle": row.cutoff_cycle,
                    "prediction_cycles": row.prediction,
                    "true_rul_cycles": row.true_rul,
                    "absolute_error_cycles": row.absolute_error,
                    "squared_error_cycles": row.squared_error,
                }
                for row in result.metrics.per_engine
            ],
        },
    }
    digest = _canonical_sha256(payload)
    output = artifact_dir / "constant_rul_validation.json"
    output.write_text(
        json.dumps(
            {"payload": payload, "sha256": digest},
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    reloaded = json.loads(output.read_text(encoding="utf-8"))
    if (
        reloaded["sha256"] != digest
        or _canonical_sha256(reloaded["payload"]) != digest
    ):
        raise ValueError("Saved validation artifact did not reload identically.")
    saved_rows = reloaded["payload"]["evaluation"]["predictions"]
    saved_mae = fsum(row["absolute_error_cycles"] for row in saved_rows) / len(saved_rows)
    saved_rmse = sqrt(fsum(row["squared_error_cycles"] for row in saved_rows) / len(saved_rows))
    if (
        len(saved_rows) != result.metrics.engine_count
        or len({(row["dataset_partition"], row["unit_id"]) for row in saved_rows}) != len(saved_rows)
        or saved_mae != result.metrics.mae
        or saved_rmse != result.metrics.rmse
    ):
        raise ValueError("Saved predictions and aggregate metrics are inconsistent.")
    print(f"artifact: {output.relative_to(PROJECT_ROOT)}")
    print(f"artifact_sha256: {digest}")
    print(f"artifact_version: {ARTIFACT_VERSION}")
    print(f"statistic: {result.baseline.statistic}")
    print(f"fitting_label_count: {result.baseline.fitting_label_count}")
    print(f"constant_prediction_cycles: {result.baseline.value_cycles:.12f}")
    print(f"validation_engines: {result.metrics.engine_count}")
    print(f"mae_cycles: {result.metrics.mae:.12f}")
    print(f"rmse_cycles: {result.metrics.rmse:.12f}")
    print("artifact_reload_and_metric_recheck: passed")


if __name__ == "__main__":
    main()
