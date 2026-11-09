"""Independently compare local training RUL labels with the FD001 audit report."""

from __future__ import annotations

import hashlib
import json

from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.targets import calculate_training_rul


def main() -> None:
    train_path = PROJECT_ROOT / "data" / "raw" / "train_FD001.txt"
    report_path = PROJECT_ROOT / "artifacts" / "data_quality.json"
    if not train_path.is_file():
        raise FileNotFoundError(
            "Missing data/raw/train_FD001.txt; follow docs/fd001_provenance.md."
        )
    if not report_path.is_file():
        raise FileNotFoundError("Missing artifacts/data_quality.json.")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    train_report = report["splits"]["train"]
    digest = hashlib.sha256(train_path.read_bytes()).hexdigest()
    if digest != train_report["source"]["sha256"]:
        raise ValueError("The local training history does not match the audited file.")

    last_cycle_by_engine = {
        engine["engine_id"]: engine["last_cycle"]
        for engine in train_report["observed"]["engines"]
    }
    rows = load_engine_history(train_path)
    original_rows = [row.copy() for row in rows]
    labels = calculate_training_rul(rows)
    expected = [last_cycle_by_engine[row["unit_id"]] - row["cycle"] for row in rows]

    if labels != expected:
        raise AssertionError("Training RUL labels differ from the independent per-engine audit.")
    if rows != original_rows:
        raise AssertionError("Target calculation modified the training records.")
    if not labels or any(type(label) is not int or label < 0 for label in labels):
        raise AssertionError("Expected nonnegative integer training labels.")
    if sum(label == 0 for label in labels) != len(last_cycle_by_engine):
        raise AssertionError("Expected one terminal zero per complete training engine.")

    print(
        f"Verified {len(labels)} labels across {len(last_cycle_by_engine)} engines; "
        f"one terminal zero per engine; range {min(labels)}..{max(labels)} cycles."
    )
    for engine_id in (1, 2, 100):
        engine_rows = [
            (row["cycle"], label)
            for row, label in zip(rows, labels, strict=True)
            if row["unit_id"] == engine_id
        ]
        first_cycle, first_label = engine_rows[0]
        last_cycle, last_label = engine_rows[-1]
        print(
            f"Engine {engine_id}: cycles {first_cycle}-{last_cycle}; "
            f"first RUL {first_label}; terminal RUL {last_label}."
        )


if __name__ == "__main__":
    main()
