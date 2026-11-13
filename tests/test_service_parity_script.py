from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from scripts import compare_service_parity


def _report(difference: float = 0.0) -> dict[str, Any]:
    predictions = [
        {
            "dataset_partition": "FD001/train",
            "unit_id": engine_id,
            "cutoff_cycle": engine_id + 100,
            "absolute_difference_cycles": difference,
        }
        for engine_id in range(1, 21)
    ]
    return {
        "sample_count": len(predictions),
        "exact_match_count": sum(row["absolute_difference_cycles"] == 0.0 for row in predictions),
        "max_absolute_difference_cycles": difference,
        "predictions": predictions,
    }


def test_parity_report_requires_twenty_unique_exact_matches() -> None:
    compare_service_parity.validate_parity_report(_report())

    mismatch = _report(difference=1.0)
    with pytest.raises(ValueError, match="parity failed"):
        compare_service_parity.validate_parity_report(mismatch)

    duplicate = _report()
    duplicate["predictions"][1]["unit_id"] = duplicate["predictions"][0]["unit_id"]
    duplicate["predictions"][1]["cutoff_cycle"] = duplicate["predictions"][0]["cutoff_cycle"]
    with pytest.raises(ValueError, match="20 unique"):
        compare_service_parity.validate_parity_report(duplicate)


def test_command_writes_diagnostic_report_and_returns_nonzero_on_mismatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    training_path = tmp_path / "train.txt"
    training_path.write_bytes(b"synthetic source bytes")
    source_hash = hashlib.sha256(training_path.read_bytes()).hexdigest()
    model = {
        "name": "test-model",
        "version": "v1",
        "sha256": "model-hash",
        "scikit_learn_version": "1.9.1",
    }
    model_manifest_path = tmp_path / "model.json"
    model_manifest_path.write_text(
        json.dumps(
            {
                "payload": {
                    "training": {
                        "source_sha256": source_hash,
                        "random_seed": 42,
                        "parameters": {"max_depth": 8},
                    },
                    "model": model,
                }
            }
        ),
        encoding="utf-8",
    )
    predictions = [
        {
            "dataset_partition": "FD001/train",
            "unit_id": engine_id,
            "cutoff_cycle": engine_id + 100,
            "prediction_cycles": 5.0,
            "true_rul_cycles": 6.0,
        }
        for engine_id in range(1, 21)
    ]
    oracle_payload = {
        "training": {"source_sha256": source_hash},
        "model": model,
        "evaluation": {"partition": "FD001/train", "predictions": predictions},
    }
    oracle_path = tmp_path / "oracle.json"
    oracle_path.write_text(
        json.dumps(
            {
                "payload": oracle_payload,
                "sha256": hashlib.sha256(compare_service_parity._canonical(oracle_payload)).hexdigest(),
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        compare_service_parity,
        "load_engine_history",
        lambda _path: [
            {"unit_id": row["unit_id"], "cycle": row["cutoff_cycle"]} for row in predictions
        ],
    )

    def fake_predict(history: list[dict[str, int]], **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(raw_rul_cycles=6.0 if history[0]["unit_id"] == 1 else 5.0)

    monkeypatch.setattr(compare_service_parity, "predict_rul", fake_predict)
    output_path = tmp_path / "report.json"

    status = compare_service_parity.main(
        [
            "--training",
            str(tmp_path / "train.txt"),
            "--model-manifest",
            str(model_manifest_path),
            "--offline-predictions",
            str(oracle_path),
            "--output",
            str(output_path),
        ]
    )

    assert status == 1
    assert "saved_service_parity: failed" in capsys.readouterr().err
    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved["exact_match_count"] == 19
    assert saved["max_absolute_difference_cycles"] == 1.0
