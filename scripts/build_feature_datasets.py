"""Rebuild ignored fitting/validation JSON datasets from the original FD001 train."""

import hashlib
import json

from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import (
    build_fitting_dataset,
    build_validation_dataset,
    manifest_digest,
)
from fleetpulse.features.dataset_io import load_feature_dataset, save_feature_dataset

TRAIN_SHA256 = "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8"


def main():
    source = PROJECT_ROOT / "data/raw/train_FD001.txt"
    manifest_path = PROJECT_ROOT / "artifacts/split_manifest.json"
    if hashlib.sha256(source.read_bytes()).hexdigest() != TRAIN_SHA256:
        raise ValueError(
            "Requires the reviewed original FD001 training file; see docs/fd001_provenance.md."
        )
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    records = load_engine_history(source)
    config = FeatureConfig()
    for builder in (build_fitting_dataset, build_validation_dataset):
        dataset = builder(records, manifest=manifest, source_sha256=TRAIN_SHA256, config=config)
        if (
            hashlib.sha256(source.read_bytes()).hexdigest() != TRAIN_SHA256
            or manifest_path.read_bytes() != manifest_bytes
        ):
            raise ValueError("Inputs changed during dataset construction.")
        path = PROJECT_ROOT / "artifacts/development" / f"{dataset.role}_features.json"
        digest = save_feature_dataset(dataset, path)
        restored = load_feature_dataset(
            path,
            expected_source_sha256=TRAIN_SHA256,
            expected_manifest_sha256=manifest_digest(manifest),
            expected_config=config,
        )
        if restored != dataset:
            raise ValueError("Saved dataset did not reload identically.")
        print(
            f"{dataset.role}: {len(dataset.rows)} rows x {len(dataset.feature_names)} features; payload SHA-256 {digest}"
        )


if __name__ == "__main__":
    main()
