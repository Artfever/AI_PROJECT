"""Saved stopping points, scoring labels and IDs must stay separate from X."""

import copy
from unittest.mock import patch

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split_manifest import build_split_manifest
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import build_fitting_dataset, build_validation_dataset
from fleetpulse.features.engineering import engineer_features


@pytest.fixture
def validation_source():
    rows = [
        {"unit_id": unit, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 2 * cycle)}
        for unit, last in ((1, 3), (2, 4))
        for cycle in range(1, last + 1)
    ]
    manifest = build_split_manifest(
        rows,
        dataset_partition="FD001/train",
        source_path="synthetic/train.txt",
        source_sha256="a" * 64,
        validation_fraction=0.5,
    )
    return rows, manifest


def test_saved_validation_cutoff_is_the_only_predictor_input_and_label_uses_full_lifetime(
    validation_source,
):
    rows, manifest = validation_source
    original = copy.deepcopy((rows, manifest))
    assert manifest["validation_prefixes"][0]["cutoff_cycle"] == 1
    calls = []

    def observed(prefix, **kwargs):
        calls.append(copy.deepcopy(prefix))
        assert kwargs["selected_cycle"] == 1
        assert [(row["unit_id"], row["cycle"]) for row in prefix] == [(1, 1)]
        assert all(set(row) == {"unit_id", "cycle", *READING_COLUMNS} for row in prefix)
        return engineer_features(prefix, **kwargs)

    with patch("fleetpulse.features.build_dataset.engineer_features", side_effect=observed):
        result = build_validation_dataset(
            iter(rows),
            manifest=manifest,
            source_sha256="a" * 64,
            config=FeatureConfig(channels=("sensor_1",)),
        )
    assert result.role == "validation"
    assert result.row_keys == (("FD001/train", 1, 1),)
    assert result.y == (2,)  # Full lifetime3 - saved cutoff1; not prefix lifetime1 - 1.
    assert result.X == ((2, 2, 0, 0),)
    assert len(calls) == 1
    assert (rows, manifest) == original


def test_fitting_and_validation_have_matching_feature_schema_and_disjoint_engines(
    validation_source,
):
    rows, manifest = validation_source
    kwargs = {"manifest": manifest, "source_sha256": "a" * 64}
    fit = build_fitting_dataset(rows, **kwargs)
    validation = build_validation_dataset(rows, **kwargs)
    assert fit.feature_names == validation.feature_names
    assert {key[:2] for key in fit.row_keys}.isdisjoint(key[:2] for key in validation.row_keys)
    assert len(validation.rows) == len(manifest["validation_prefixes"]) == 1


@pytest.mark.parametrize(
    "field,value", [("cutoff_cycle", 3), ("target_rul", 0), ("prefix_row_count", 2)]
)
def test_corrupted_saved_cutoff_metadata_is_rejected_before_extraction(
    validation_source, field, value
):
    rows, manifest = validation_source
    manifest["validation_prefixes"][0][field] = value
    with patch("fleetpulse.features.build_dataset.engineer_features") as extract:
        with pytest.raises(ValueError, match="Split manifest audit failed"):
            build_validation_dataset(rows, manifest=manifest, source_sha256="a" * 64)
        extract.assert_not_called()
