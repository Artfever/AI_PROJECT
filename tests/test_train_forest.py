"""Forest training obeys the same feature, target and engine boundaries as P06."""

from dataclasses import replace
from unittest.mock import patch

import pytest
from sklearn.ensemble import RandomForestRegressor

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split_manifest import build_split_manifest
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import build_fitting_dataset, build_validation_dataset
from fleetpulse.models.train_forest import train_random_forest


@pytest.fixture
def forest_tables():
    rows = [
        {"unit_id": unit, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, cycle + unit)}
        for unit, lifetime in ((1, 5), (2, 7), (3, 9), (4, 11))
        for cycle in range(1, lifetime + 1)
    ]
    split = build_split_manifest(
        rows,
        dataset_partition="FD001/train",
        source_path="synthetic/train.txt",
        source_sha256="a" * 64,
        validation_fraction=0.5,
    )
    options = {
        "manifest": split,
        "source_sha256": "a" * 64,
        "config": FeatureConfig(channels=("sensor_1",)),
    }
    return build_fitting_dataset(rows, **options), build_validation_dataset(rows, **options)


def test_forest_fits_only_fitting_values_and_is_reproducible(forest_tables):
    fitting, validation = forest_tables
    original_fit = RandomForestRegressor.fit
    captured = []

    def observed(estimator, X, y, **kwargs):
        captured.append((X, y))
        return original_fit(estimator, X, y, **kwargs)

    with patch.object(RandomForestRegressor, "fit", autospec=True, side_effect=observed):
        first = train_random_forest(
            fitting, validation, n_estimators=8, max_depth=4, min_samples_leaf=1
        )
    second = train_random_forest(
        fitting, validation, n_estimators=8, max_depth=4, min_samples_leaf=1
    )
    assert captured == [(fitting.X, fitting.y)]
    assert first.predictions == second.predictions
    assert first.metrics == second.metrics
    assert first.feature_names == fitting.feature_names
    assert first.random_seed == 42 and first.parameters["n_jobs"] == 1
    assert first.parameters["n_estimators"] == len(first.model.estimators_) == 8
    assert [(p.dataset_partition, p.unit_id, p.cutoff_cycle) for p in first.predictions] == list(
        validation.row_keys
    )
    assert [p.true_rul for p in first.predictions] == list(validation.y)
    assert first.runtime_seconds >= 0


@pytest.mark.parametrize("kind", ["overlap", "source", "schema", "role"])
def test_forest_rejects_invalid_tables_before_fitting(forest_tables, kind):
    fitting, validation = forest_tables
    if kind == "overlap":
        validation = replace(validation, rows=(fitting.rows[0],))
    elif kind == "source":
        validation = replace(validation, source_sha256="b" * 64)
    elif kind == "schema":
        validation = replace(validation, config=FeatureConfig(channels=("sensor_2",)))
    else:
        fitting = replace(fitting, role="validation")
    with patch.object(RandomForestRegressor, "fit") as fit:
        with pytest.raises(ValueError):
            train_random_forest(fitting, validation)
        fit.assert_not_called()


@pytest.mark.parametrize(
    "kwargs",
    [{"n_estimators": 0}, {"max_depth": None}, {"min_samples_leaf": 0}, {"random_seed": True}],
)
def test_forest_requires_bounded_explicit_parameters(forest_tables, kwargs):
    with pytest.raises(ValueError):
        train_random_forest(*forest_tables, **kwargs)
