"""Model inputs and uncapped labels built from audited training histories."""

import hashlib
import json
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from fleetpulse.data.split import TRAIN_PARTITION
from fleetpulse.data.split_audit import audit_split_manifest
from fleetpulse.data.targets import calculate_training_rul
from fleetpulse.features.config import FeatureConfig
from fleetpulse.features.engineering import EngineFeatureVector, engineer_features

DATASET_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class LabeledFeatureRow:
    """Keep one immutable vector attached to its separately held scoring label."""

    vector: EngineFeatureVector
    true_rul: int

    @property
    def key(self) -> tuple[str, int, int]:
        return (*self.vector.engine_key, self.vector.selected_cycle)


@dataclass(frozen=True)
class FeatureDataset:
    """Trainer contract: X, y and metadata projected from the same ordered rows."""

    role: str
    config: FeatureConfig
    rows: tuple[LabeledFeatureRow, ...]
    source_sha256: str
    split_manifest_sha256: str

    @property
    def X(self) -> tuple[tuple[float, ...], ...]:
        return tuple(row.vector.values for row in self.rows)

    @property
    def y(self) -> tuple[int, ...]:
        return tuple(row.true_rul for row in self.rows)

    @property
    def row_keys(self) -> tuple[tuple[str, int, int], ...]:
        return tuple(row.key for row in self.rows)

    @property
    def feature_names(self) -> tuple[str, ...]:
        return self.config.output_schema


def manifest_digest(manifest: Mapping[str, object]) -> str:
    """Hash semantic manifest content using canonical JSON, independent of spacing."""
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _audited_source(records, manifest, source_sha256):
    if not isinstance(source_sha256, str) or re.fullmatch(r"[a-f0-9]{64}", source_sha256) is None:
        raise ValueError("source_sha256 must be a lowercase SHA-256 hex digest.")
    rows = tuple(records)
    audit_split_manifest(manifest, rows, source_sha256=source_sha256)
    by_unit = {}
    for row in rows:
        by_unit.setdefault(int(row["unit_id"]), []).append(row)
    if any(history[0]["cycle"] != 1 for history in by_unit.values()):
        raise ValueError("Complete original training histories must start at cycle 1.")
    return rows, by_unit


def build_fitting_dataset(
    records: Iterable[Mapping[str, object]],
    *,
    manifest: Mapping[str, object],
    source_sha256: str,
    config: FeatureConfig | None = None,
) -> FeatureDataset:
    """Generate one row at every observed fitting cycle, including terminal RUL 0.

    One-row prefixes are supported, so every observed cycle is eligible. Each
    extractor call receives only that fitting engine's prefix; labels come
    separately from complete training trajectories. No file or test answer is
    opened. The caller must hash and supply the original full training source.
    """
    feature_config = config if config is not None else FeatureConfig()
    if not isinstance(feature_config, FeatureConfig):
        raise TypeError("config must be a FeatureConfig.")
    rows, by_unit = _audited_source(records, manifest, source_sha256)
    labels = calculate_training_rul(rows)
    targets = {
        (int(row["unit_id"]), int(row["cycle"])): label
        for row, label in zip(rows, labels, strict=True)
    }
    result = []
    for identity in sorted(manifest["fitting_engines"], key=lambda item: item["unit_id"]):
        unit = identity["unit_id"]
        history = by_unit[unit]
        for index, row in enumerate(history):
            cycle = int(row["cycle"])
            vector = engineer_features(
                history[: index + 1],
                dataset_partition=TRAIN_PARTITION,
                unit_id=unit,
                selected_cycle=cycle,
                config=feature_config,
            )
            result.append(LabeledFeatureRow(vector, targets[unit, cycle]))
    return FeatureDataset(
        "fitting",
        feature_config,
        tuple(result),
        source_sha256,
        manifest_digest(manifest),
    )


def build_validation_dataset(
    records: Iterable[Mapping[str, object]],
    *,
    manifest: Mapping[str, object],
    source_sha256: str,
    config: FeatureConfig | None = None,
) -> FeatureDataset:
    """Emit exactly one row per saved validation engine at its audited cutoff.

    Do not choose a new cutoff or derive a label from the truncated prefix.
    IDs/cutoffs stay in vector metadata; only the numeric readings' statistics
    enter X. Full training lifetimes remain on the scoring side of the call.
    """
    feature_config = config if config is not None else FeatureConfig()
    if not isinstance(feature_config, FeatureConfig):
        raise TypeError("config must be a FeatureConfig.")
    _, by_unit = _audited_source(records, manifest, source_sha256)
    result = []
    for entry in sorted(manifest["validation_prefixes"], key=lambda item: item["unit_id"]):
        unit, cutoff = entry["unit_id"], entry["cutoff_cycle"]
        prefix = [row for row in by_unit[unit] if int(row["cycle"]) <= cutoff]
        vector = engineer_features(
            prefix,
            dataset_partition=TRAIN_PARTITION,
            unit_id=unit,
            selected_cycle=cutoff,
            config=feature_config,
        )
        result.append(LabeledFeatureRow(vector, entry["target_rul"]))
    return FeatureDataset(
        "validation",
        feature_config,
        tuple(result),
        source_sha256,
        manifest_digest(manifest),
    )
