"""Tests for the deterministic fitting-label-only constant RUL baseline."""

import json

import pytest

from fleetpulse.models import ConstantRULBaseline


def test_mean_baseline_fits_only_the_explicit_labels_and_repeats_constant():
    model = ConstantRULBaseline.fit([0, 3, 9], statistic="mean")

    assert model.value_cycles == 4
    assert model.fitting_label_count == 3
    assert model.statistic == "mean"
    assert model.random_seed is None
    assert model.predict(sample_count=4) == (4.0, 4.0, 4.0, 4.0)


def test_median_baseline_is_available_only_when_explicitly_selected():
    model = ConstantRULBaseline.fit([0, 3, 9, 100], statistic="median")

    assert model.value_cycles == 6
    assert model.statistic == "median"
    assert model.predict(sample_count=2) == (6.0, 6.0)


def test_json_artifact_reload_preserves_predictions_and_provenance():
    fitted = ConstantRULBaseline.fit([2, 4, 8], statistic="mean")
    reloaded = ConstantRULBaseline.from_artifact(
        json.loads(json.dumps(fitted.to_artifact()))
    )

    assert reloaded == fitted
    assert reloaded.to_artifact() == {
        "artifact_version": "constant-rul-v1",
        "statistic": "mean",
        "value_cycles": 14 / 3,
        "target_name": "rul_cycles",
        "fitting_label_count": 3,
        "random_seed": None,
    }
    assert reloaded.predict(sample_count=3) == fitted.predict(sample_count=3)


@pytest.mark.parametrize(
    "labels,error,message",
    [
        ([], ValueError, "At least one"),
        ([1, float("nan")], ValueError, "finite"),
        ([1, float("inf")], ValueError, "finite"),
        ([1, -1], ValueError, "nonnegative"),
        ([1, True], TypeError, "numeric"),
        ([1, "2"], TypeError, "numeric"),
    ],
)
def test_fit_rejects_empty_invalid_or_non_rul_labels(labels, error, message):
    with pytest.raises(error, match=message):
        ConstantRULBaseline.fit(labels, statistic="mean")


def test_statistic_must_be_explicit_and_supported():
    with pytest.raises(TypeError):
        ConstantRULBaseline.fit([1, 2])  # type: ignore[call-arg]
    with pytest.raises(ValueError, match="statistic"):
        ConstantRULBaseline.fit([1, 2], statistic="minimum")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "count,error",
    [(-1, ValueError), (True, TypeError), (1.5, TypeError)],
)
def test_predict_validates_requested_row_count(count, error):
    model = ConstantRULBaseline.fit([1, 2], statistic="mean")
    with pytest.raises(error):
        model.predict(sample_count=count)  # type: ignore[arg-type]


def test_artifact_rejects_wrong_version_and_extra_fields():
    artifact = ConstantRULBaseline.fit([1], statistic="mean").to_artifact()
    with pytest.raises(ValueError, match="artifact version"):
        ConstantRULBaseline.from_artifact({**artifact, "artifact_version": "future"})
    with pytest.raises(ValueError, match="fields"):
        ConstantRULBaseline.from_artifact({**artifact, "validation_labels": [1]})
