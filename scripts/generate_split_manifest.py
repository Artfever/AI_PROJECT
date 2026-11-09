"""Save the declared development split using only the original FD001 train file."""

import hashlib
import json

from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.split import TRAIN_PARTITION
from fleetpulse.data.split_manifest import build_split_manifest

TRAIN_SHA256 = "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8"


def main() -> None:
    source = PROJECT_ROOT / "data" / "raw" / "train_FD001.txt"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    if digest != TRAIN_SHA256:
        raise ValueError("Training source hash differs from docs/fd001_provenance.md.")
    rows = load_engine_history(source)
    manifest = build_split_manifest(
        rows, dataset_partition=TRAIN_PARTITION,
        source_path=source.relative_to(PROJECT_ROOT).as_posix(), source_sha256=digest,
        split_seed=42, cutoff_seed=42, validation_fraction=0.2, minimum_history_rows=1,
    )
    if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
        raise ValueError("Training source changed during manifest generation.")
    output = PROJECT_ROOT / "artifacts" / "split_manifest.json"
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        f"Saved {output.relative_to(PROJECT_ROOT)}: "
        f"{len(manifest['fitting_engines'])} fitting engines / "
        f"{len(manifest['validation_prefixes'])} validation prefixes."
    )


if __name__ == "__main__":
    main()
