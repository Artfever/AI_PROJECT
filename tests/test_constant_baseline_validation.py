"""The constant baseline must fit from fitting labels and score saved validation rows."""

from dataclasses import replace
from math import fsum, sqrt

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split_manifest import build_split_manifest
from fleetpulse.evaluation import score_constant_baseline
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import build_fitting_dataset, build_validation_dataset


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


def test_scores_one_constant_prediction_per_saved_validation_engine(
    fitting_and_validation_datasets,
):
    fitting, validation = fitting_and_validation_datasets

    result = score_constant_baseline(fitting, validation)

    expected_constant = fsum(fitting.y) / len(fitting.y)
    assert result.baseline.statistic == "mean"
    assert result.baseline.value_cycles == expected_constant
    assert result.baseline.fitting_label_count == len(fitting.y)
    assert len(result.metrics.per_engine) == len(validation.rows)
    assert [row.engine_key for row in result.metrics.per_engine] == [
        ("FD001/train", row.vector.unit_id) for row in validation.rows
    ]
    assert [row.cutoff_cycle for row in result.metrics.per_engine] == [
        row.vector.selected_cycle for row in validation.rows
    ]
    assert all(row.prediction == expected_constant for row in result.metrics.per_engine)
    errors = [expected_constant - target for target in validation.y]
    assert result.metrics.mae == pytest.approx(fsum(abs(error) for error in errors) / len(errors))
    assert result.metrics.rmse == pytest.approx(
        sqrt(fsum(error * error for error in errors) / len(errors))
    )


def test_validation_features_do_not_change_constant_predictions(fitting_and_validation_datasets):
    fitting, validation = fitting_and_validation_datasets
    altered_rows = tuple(
        replace(
            row,
            vector=replace(row.vector, values=tuple(value + 1_000_000 for value in row.vector.values)),
        )
        for row in validation.rows
    )
    altered_validation = replace(validation, rows=altered_rows)

    original = score_constant_baseline(fitting, validation)
    altered = score_constant_baseline(fitting, altered_validation)

    assert altered.baseline == original.baseline
    assert [row.prediction for row in altered.metrics.per_engine] == [
        row.prediction for row in original.metrics.per_engine
    ]
    assert altered.metrics == original.metrics


def test_rejects_mismatched_dataset_provenance(fitting_and_validation_datasets):
    fitting, validation = fitting_and_validation_datasets
    with pytest.raises(ValueError, match="share source and split provenance"):
        score_constant_baseline(fitting, replace(validation, source_sha256="b" * 64))
