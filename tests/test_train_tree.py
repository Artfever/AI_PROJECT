"""The initial tree fits only common fitting rows and scores held-out engines."""

from dataclasses import replace

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split_manifest import build_split_manifest
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import build_fitting_dataset, build_validation_dataset
from fleetpulse.models.train_tree import train_decision_tree


@pytest.fixture
def fitting_and_validation_datasets():
    rows = [
        {"unit_id": unit, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, cycle + unit)}
        for unit, lifetime in ((1, 5), (2, 7), (3, 9), (4, 11))
        for cycle in range(1, lifetime + 1)
    ]
    manifest = build_split_manifest(
        rows,
        dataset_partition="FD001/train",
        source_path="synthetic/train.txt",
        source_sha256="a" * 64,
        validation_fraction=0.5,
    )
    options = {
        "manifest": manifest,
        "source_sha256": "a" * 64,
        "config": FeatureConfig(channels=("sensor_1",)),
    }
    return build_fitting_dataset(rows, **options), build_validation_dataset(rows, **options)


def test_tree_is_reproducible_and_returns_one_score_per_validation_engine(
    fitting_and_validation_datasets,
):
    fitting, validation = fitting_and_validation_datasets

    first = train_decision_tree(fitting, validation)
    second = train_decision_tree(fitting, validation)

    assert first.random_seed == 42
    assert first.max_depth == 8
    assert first.min_samples_leaf == 5
    assert first.feature_names == fitting.feature_names
    assert [row.prediction for row in first.predictions] == [
        row.prediction for row in second.predictions
    ]
    assert first.metrics == second.metrics
    assert len(first.predictions) == len(validation.rows)
    assert [row.unit_id for row in first.predictions] == [row.vector.unit_id for row in validation.rows]
    assert first.metrics.mae >= 0
    assert first.metrics.rmse >= 0


def test_tree_rejects_fitting_validation_engine_overlap(fitting_and_validation_datasets):
    fitting, validation = fitting_and_validation_datasets
    overlapping = replace(validation, rows=(fitting.rows[0],))

    with pytest.raises(ValueError, match="disjoint"):
        train_decision_tree(fitting, overlapping)


def test_tree_rejects_different_input_provenance(fitting_and_validation_datasets):
    fitting, validation = fitting_and_validation_datasets

    with pytest.raises(ValueError, match="share source and split provenance"):
        train_decision_tree(fitting, replace(validation, source_sha256="b" * 64))


@pytest.mark.parametrize("parameters", [{"random_seed": -1}, {"max_depth": 0}, {"min_samples_leaf": 0}])
def test_tree_rejects_invalid_hyperparameters(fitting_and_validation_datasets, parameters):
    fitting, validation = fitting_and_validation_datasets

    with pytest.raises(ValueError):
        train_decision_tree(fitting, validation, **parameters)
