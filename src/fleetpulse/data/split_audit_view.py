"""Verify saved development metadata for the Model Laboratory view."""

import hashlib
import json
from pathlib import Path

from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.split_audit import audit_split_manifest


def verified_split_manifest(manifest_path: Path, training_path: Path) -> dict:
    """Audit a saved manifest against its training source without resampling it.

    The caller fixes the paths; the manifest cannot redirect file access. Official
    test histories and answer files are never read.
    """
    saved = manifest_path.read_bytes()
    manifest = json.loads(saved)
    if not isinstance(manifest, dict):
        raise TypeError("The split manifest must be an object.")
    source = manifest.get("source")
    if not isinstance(source, dict) or source.get("path") != "data/raw/train_FD001.txt":
        raise ValueError("The manifest does not identify the expected FD001 training source.")
    digest = hashlib.sha256(training_path.read_bytes()).hexdigest()
    rows = load_engine_history(training_path)
    audit_split_manifest(manifest, rows, source_sha256=digest)
    if manifest_path.read_bytes() != saved or hashlib.sha256(training_path.read_bytes()).hexdigest() != digest:
        raise ValueError("The training file or manifest changed during the audit.")
    return manifest
