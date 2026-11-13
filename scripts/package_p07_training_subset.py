"""Package only the three approved FD001/train prefixes used for remote parity."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from fleetpulse import PROJECT_ROOT

EXPECTED_TRAIN_SHA256 = "963b5e22825b34d8b21c69e1aeb4af3e647050eb672ee8834ba4b5d91d2de0f8"
PREFIX_CUTOFFS = {4: 164, 5: 58, 12: 7}
EXPECTED_ROWS = sum(PREFIX_CUTOFFS.values())


def select_prefix_lines(lines: list[str]) -> list[str]:
    """Retain source lines for only the explicitly allowed training prefixes."""
    selected = []
    observed: dict[int, list[int]] = {engine: [] for engine in PREFIX_CUTOFFS}
    for line_number, line in enumerate(lines, start=1):
        fields = line.split()
        if not fields:
            continue
        if len(fields) != 26:
            raise ValueError(f"Source line {line_number} has {len(fields)} values; expected 26.")
        try:
            engine_id, cycle = int(fields[0]), int(fields[1])
        except ValueError as error:
            raise ValueError(f"Source line {line_number} has invalid engine/cycle identifiers.") from error
        cutoff = PREFIX_CUTOFFS.get(engine_id)
        if cutoff is not None and cycle <= cutoff:
            selected.append(line.strip())
            observed[engine_id].append(cycle)

    for engine_id, cutoff in PREFIX_CUTOFFS.items():
        expected = list(range(1, cutoff + 1))
        if observed[engine_id] != expected:
            raise ValueError(
                f"Engine {engine_id} must contain exactly its consecutive cycles 1..{cutoff}."
            )
    if len(selected) != EXPECTED_ROWS:
        raise ValueError(f"Expected {EXPECTED_ROWS} prefix rows, found {len(selected)}.")
    return selected


def package_subset(source: Path, destination: Path) -> str:
    source_bytes = source.read_bytes()
    if hashlib.sha256(source_bytes).hexdigest() != EXPECTED_TRAIN_SHA256:
        raise ValueError("Source file hash differs from the recorded original FD001/train file.")
    lines = source_bytes.decode("utf-8").splitlines()
    selected = select_prefix_lines(lines)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(selected) + "\n", encoding="utf-8", newline="\n")
    return hashlib.sha256(destination.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=PROJECT_ROOT / "data/raw/train_FD001.txt")
    parser.add_argument(
        "--output", type=Path, default=PROJECT_ROOT / "data/demo/fd001_training_prefixes.txt"
    )
    args = parser.parse_args()
    digest = package_subset(args.source, args.output)
    print(
        f"packaged_training_subset: passed; engines={','.join(map(str, PREFIX_CUTOFFS))}; "
        f"rows={EXPECTED_ROWS}; sha256={digest}; output={args.output.relative_to(PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    main()
