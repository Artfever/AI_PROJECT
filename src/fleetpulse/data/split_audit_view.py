"""Read and verify the saved development manifest against training histories."""

import hashlib
import json
from pathlib import Path

from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.split import TRAIN_PARTITION
from fleetpulse.data.split_manifest import build_split_manifest


def verified_split_manifest(manifest_path: Path, training_path: Path) -> dict:
    """Return a manifest only if it reproduces from its declared training source.

    Training source and output paths are supplied by the caller; the manifest cannot
    redirect file access. Official test histories and answer files are never read.
    """
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["schema_version"] != 1:
        raise ValueError("Unsupported split manifest schema.")
    source = manifest["source"]
    if source["dataset_partition"] != TRAIN_PARTITION or source["path"] != "data/raw/train_FD001.txt":
        raise ValueError("The manifest does not identify the expected FD001 training source.")
    digest = hashlib.sha256(training_path.read_bytes()).hexdigest()
    if source["sha256"] != digest:
        raise ValueError("The training file does not match the manifest's source hash.")
    rows = load_engine_history(training_path)
    if hashlib.sha256(training_path.read_bytes()).hexdigest() != digest:
        raise ValueError("The training file changed while verifying the manifest.")
    rebuilt = build_split_manifest(
        rows,
        dataset_partition=TRAIN_PARTITION,
        source_path="data/raw/train_FD001.txt",
        source_sha256=digest,
        split_seed=manifest["split"]["seed"],
        cutoff_seed=manifest["cutoff_policy"]["seed"],
        validation_fraction=manifest["split"]["validation_fraction"],
        minimum_history_rows=manifest["cutoff_policy"]["minimum_history_rows"],
    )
    if rebuilt != manifest:
        raise ValueError("The manifest does not reproduce from the local training histories.")
    return manifest
