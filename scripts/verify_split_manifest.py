"""Read-only audit of the saved manifest against original FD001 train histories."""

import hashlib
import json

from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.split_audit import audit_split_manifest

TRAIN_SHA256 = "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8"


def main() -> None:
    source = PROJECT_ROOT / "data" / "raw" / "train_FD001.txt"
    artifact = PROJECT_ROOT / "artifacts" / "split_manifest.json"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != TRAIN_SHA256:
        raise ValueError("Training source hash differs from docs/fd001_provenance.md.")
    saved = artifact.read_bytes()
    manifest = json.loads(saved)
    if manifest["source"]["path"] != "data/raw/train_FD001.txt":
        raise ValueError("Manifest source path is not the original FD001 training file.")
    audit_split_manifest(manifest, load_engine_history(source), source_sha256=digest)
    if artifact.read_bytes() != saved or hashlib.sha256(source.read_bytes()).hexdigest() != digest:
        raise ValueError("Source or manifest changed during audit.")
    prefixes = manifest["validation_prefixes"]
    print(
        f"Verified {len(manifest['fitting_engines'])} fitting / {len(prefixes)} validation engines; "
        "no overlap; every cutoff observed before failure and meeting the minimum history."
    )
    print(
        f"Split seed {manifest['split']['seed']}; cutoff seed {manifest['cutoff_policy']['seed']}."
    )
    print(f"Manifest SHA-256: {hashlib.sha256(saved).hexdigest()}")


if __name__ == "__main__":
    main()
