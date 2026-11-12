"""Deterministic JSON storage with schema, provenance and row-alignment checks."""

import hashlib
import json
import math
import re
from dataclasses import asdict
from pathlib import Path

from fleetpulse.data.split import TRAIN_PARTITION
from fleetpulse.features.build_dataset import (
    DATASET_SCHEMA_VERSION,
    FeatureDataset,
    LabeledFeatureRow,
)
from fleetpulse.features.config import FeatureConfig
from fleetpulse.features.engineering import EngineFeatureVector


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _require(condition, message):
    if not condition:
        raise ValueError(f"Invalid feature dataset: {message}")


def _sha(value):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def _positive(value):
    return type(value) is int and value > 0


def _parse(payload):
    _require(
        type(payload["schema_version"]) is int
        and payload["schema_version"] == DATASET_SCHEMA_VERSION,
        "unsupported schema version.",
    )
    role = payload["role"]
    _require(role in ("fitting", "validation"), "unknown dataset role.")
    saved_config = payload["feature_config"]
    _require(isinstance(saved_config["channels"], list), "channels must be an ordered list.")
    config = FeatureConfig(
        channels=tuple(saved_config["channels"]), window_cycles=saved_config["window_cycles"]
    )
    _require(
        saved_config == json.loads(_canonical(asdict(config))),
        "unsupported feature config/version.",
    )
    _require(
        payload["feature_names"] == list(config.output_schema), "feature order/schema mismatch."
    )
    hashes = payload["input_hashes"]
    _require(
        _sha(hashes["source_sha256"]) and _sha(hashes["split_manifest_sha256"]),
        "invalid source/manifest hash.",
    )
    _require(
        hashes["feature_config_sha256"] == _digest(saved_config), "feature config hash mismatch."
    )
    _require(isinstance(payload["rows"], list) and bool(payload["rows"]), "no feature rows.")
    rows = []
    for saved in payload["rows"]:
        metadata = saved["metadata"]
        _require(metadata["dataset_partition"] == TRAIN_PARTITION, "unexpected source partition.")
        _require(
            all(
                _positive(metadata[name])
                for name in (
                    "unit_id",
                    "selected_cycle",
                    "observed_row_count",
                    "window_row_count",
                )
            ),
            "invalid integer metadata.",
        )
        _require(
            metadata["window_row_count"]
            <= metadata["observed_row_count"]
            <= metadata["selected_cycle"],
            "inconsistent observation counts.",
        )
        _require(
            metadata["window_row_count"] <= config.window_cycles, "window count exceeds config."
        )
        key = [metadata["dataset_partition"], metadata["unit_id"], metadata["selected_cycle"]]
        _require(saved["key"] == key, "row key and metadata alignment mismatch.")
        values = saved["features"]
        _require(
            isinstance(values, list) and len(values) == len(config.output_schema),
            "feature width mismatch.",
        )
        _require(
            all(type(value) in (int, float) and math.isfinite(value) for value in values),
            "features must be finite numbers.",
        )
        label = saved["true_rul"]
        _require(
            type(label) is int and label >= (1 if role == "validation" else 0), "invalid RUL label."
        )
        vector = EngineFeatureVector(**metadata, config=config, values=tuple(values))
        rows.append(LabeledFeatureRow(vector, label))
    keys = [row.key for row in rows]
    _require(keys == sorted(set(keys)), "duplicate or noncanonical row keys.")
    if role == "validation":
        _require(
            len({row.vector.engine_key for row in rows}) == len(rows),
            "multiple validation rows per engine.",
        )
    return FeatureDataset(
        role, config, tuple(rows), hashes["source_sha256"], hashes["split_manifest_sha256"]
    )


def save_feature_dataset(dataset: FeatureDataset, path: str | Path) -> str:
    """Save an LF UTF-8 JSON table and return its canonical payload SHA-256.

    The per-row key binds numeric features and label to metadata. The content
    digest detects accidental reordering or edits; it is not an authenticity
    signature. Raw source and semantic manifest hashes come from the builder.
    """
    _require(
        all(row.vector.config == dataset.config for row in dataset.rows), "mixed feature configs."
    )
    config = asdict(dataset.config)
    payload = {
        "schema_version": DATASET_SCHEMA_VERSION,
        "role": dataset.role,
        "feature_config": config,
        "feature_names": dataset.feature_names,
        "input_hashes": {
            "source_sha256": dataset.source_sha256,
            "split_manifest_sha256": dataset.split_manifest_sha256,
            "feature_config_sha256": _digest(config),
        },
        "rows": [],
    }
    for row in dataset.rows:
        vector = row.vector
        payload["rows"].append(
            {
                "key": row.key,
                "features": vector.values,
                "true_rul": row.true_rul,
                "metadata": {
                    "dataset_partition": vector.dataset_partition,
                    "unit_id": vector.unit_id,
                    "selected_cycle": vector.selected_cycle,
                    "observed_row_count": vector.observed_row_count,
                    "window_row_count": vector.window_row_count,
                },
            }
        )
    # Validate through the same JSON types and contract used by a fresh process.
    _parse(json.loads(_canonical(payload)))
    digest = _digest(payload)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        _canonical({"payload": payload, "sha256": digest}) + "\n", encoding="utf-8", newline="\n"
    )
    return digest


def load_feature_dataset(
    path: str | Path,
    *,
    expected_source_sha256: str | None = None,
    expected_manifest_sha256: str | None = None,
    expected_config: FeatureConfig | None = None,
) -> FeatureDataset:
    """Verify stored content and optional caller-pinned inputs before exposing X/y."""
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        payload = document["payload"]
        _require(
            document["sha256"] == _digest(payload),
            "content hash mismatch; row alignment may have changed.",
        )
        result = _parse(payload)
    except (KeyError, TypeError, OverflowError) as error:
        raise ValueError("Invalid feature dataset structure.") from error
    if expected_source_sha256 is not None:
        _require(
            result.source_sha256 == expected_source_sha256,
            "source hash differs from expected input.",
        )
    if expected_manifest_sha256 is not None:
        _require(
            result.split_manifest_sha256 == expected_manifest_sha256,
            "manifest hash differs from expected input.",
        )
    if expected_config is not None:
        _require(result.config == expected_config, "config differs from expected input.")
    return result
