"""Generate a reproducible quality report from local FD001 history files."""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from fleetpulse.data.loader import load_engine_history
from fleetpulse.data.summary import summarize_engine_history

ROOT = Path(__file__).resolve().parents[1]
SPLITS = {
    "train": ROOT / "data/raw/train_FD001.txt",
    "test": ROOT / "data/raw/test_FD001.txt",
}
OUTPUT = ROOT / "artifacts/data_quality.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finding_to_dict(finding: Any) -> dict[str, object]:
    return {
        "code": finding.code,
        "severity": finding.severity,
        "row_number": finding.row_number,
        "field": finding.field,
        "message": finding.message,
    }


def build_report() -> dict[str, object]:
    splits: dict[str, object] = {}
    for split_name, path in SPLITS.items():
        if not path.is_file():
            raise FileNotFoundError(
                f"Missing {path.relative_to(ROOT)}; retrieve FD001 histories per "
                "docs/fd001_provenance.md."
            )
        records = load_engine_history(path)
        summary = summarize_engine_history(records)
        report = summary.quality
        splits[split_name] = {
            "source": {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            },
            "observed": {
                "row_count": summary.row_count,
                "engine_count": summary.engine_count,
                "engines": [
                    {
                        "engine_id": engine.engine_id,
                        "row_count": engine.row_count,
                        "first_cycle": engine.first_cycle,
                        "last_cycle": engine.last_cycle,
                    }
                    for engine in summary.engines
                ],
            },
            "quality": {
                "rows_checked": report.rows_checked,
                "is_valid": report.is_valid,
                "error_count": len(report.errors),
                "warning_count": len(report.warnings),
                "findings": [finding_to_dict(item) for item in report.findings],
            },
            "sensor_population_variance_ddof_0": summary.sensor_population_variance,
            "exactly_constant_sensors": list(summary.constant_sensors),
        }

    return {
        "schema_version": 1,
        "dataset": "NASA C-MAPSS FD001",
        "generated_on": date.today().isoformat(),
        "scope": "Train and test sensor-history files only; no test RUL answers.",
        "expected_benchmark_counts": {
            "used_as_acceptance_criteria": False,
            "note": "This report records observations from the hashed local files; "
            "it does not assert expected benchmark counts.",
        },
        "source_provenance": "docs/fd001_provenance.md",
        "loader": "fleetpulse.data.loader.load_engine_history",
        "validator": "fleetpulse.data.quality.validate_engine_history",
        "summary": "fleetpulse.data.summary.summarize_engine_history",
        "validation_rules": [
            "Normalized FD001 columns are present with no unexpected columns.",
            "Engine IDs and cycles are positive finite integers.",
            "Operating settings and sensor readings are numeric and finite.",
            "Engine-cycle pairs are unique.",
            "Cycles increase within each engine; gaps are warnings.",
            "Validation never deletes, sorts, or edits source rows.",
        ],
        "splits": splits,
        "limitations": [
            (
                "These findings describe the local history files and validator rules; "
                "they do not establish physical causes or model performance."
            ),
            "Test RUL answer values are not read by this generator.",
            (
                "Possible incidental answer-file output during earlier inspection is "
                "disclosed in docs/fd001_summary.md."
            ),
        ],
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(build_report(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
