"""Contract checks for past-only feature extraction from engine histories."""

import math

import pytest

from fleetpulse.features import FeatureConfig, engineer_features


def row(cycle: int, sensor_1: float, *, unit_id: int = 1, **extra: object):
    return {"unit_id": unit_id, "cycle": cycle, "sensor_1": sensor_1, **extra}


def test_linear_example_has_expected_population_statistics_and_metadata():
    result = engineer_features(
        [row(1, 2), row(2, 4), row(3, 6)],
        dataset_partition="FD001/train",
        unit_id=1,
        selected_cycle=3,
        config=FeatureConfig(channels=("sensor_1",)),
    )

    assert result.engine_key == ("FD001/train", 1)
    assert result.selected_cycle == 3
    assert result.observed_row_count == result.window_row_count == 3
    assert result.values == pytest.approx((6, 4, math.sqrt(8 / 3), 2))
    assert result.as_dict() == pytest.approx(
        {"sensor_1_latest": 6, "sensor_1_mean": 4, "sensor_1_std": math.sqrt(8 / 3), "sensor_1_slope": 2}
    )


def test_inclusive_cycle_window_uses_gaps_actual_cycles_and_excludes_future():
    result = engineer_features(
        [row(10, -500), row(11, 2), row(20, 20), row(40, 60), row(41, 900)],
        dataset_partition="FD001/train",
        unit_id=1,
        selected_cycle=40,
        config=FeatureConfig(channels=("sensor_1",), window_cycles=30),
    )

    assert result.observed_row_count == 4
    assert result.window_row_count == 3
    assert result.values == pytest.approx((60, 82 / 3, math.sqrt(5288 / 9), 2))


def test_future_rows_do_not_change_features_or_visible_row_metadata():
    config = FeatureConfig(channels=("sensor_1",), window_cycles=3)
    prefix = [row(1, 2), row(2, 4), row(3, 6)]
    first = engineer_features(
        [*prefix, row(4, 100)],
        dataset_partition="FD001/train",
        unit_id=1,
        selected_cycle=3,
        config=config,
    )
    changed_future = engineer_features(
        [*prefix, row(4, -1_000_000), row(5, 99_999_999)],
        dataset_partition="FD001/train",
        unit_id=1,
        selected_cycle=3,
        config=config,
    )

    assert changed_future == first


def test_single_observation_has_zero_population_std_and_slope():
    result = engineer_features(
        [row(7, 5)],
        dataset_partition="FD001/train",
        unit_id=1,
        config=FeatureConfig(channels=("sensor_1",)),
    )

    assert result.values == (5, 5, 0, 0)
    assert result.observed_row_count == result.window_row_count == 1


def test_custom_channel_order_matches_the_configured_schema():
    result = engineer_features(
        [row(1, 2, setting_1=10), row(2, 4, setting_1=20)],
        dataset_partition="FD001/train",
        unit_id=1,
        config=FeatureConfig(channels=("setting_1", "sensor_1")),
    )

    assert tuple(result.as_dict()) == result.config.output_schema
    assert result.values == pytest.approx((20, 15, 5, 10, 4, 3, 1, 2))


@pytest.mark.parametrize(
    "history,kwargs,error,message",
    [
        ([row(1, 2), row(1, 3)], {}, ValueError, "Duplicate cycle"),
        ([row(1, 2, unit_id=2)], {}, ValueError, "requested unit_id"),
        ([row(1, 2)], {"selected_cycle": 2}, ValueError, "observed cycle"),
        ([{"unit_id": 1, "cycle": 1}], {}, TypeError, "sensor_1"),
        ([row(1, float("nan"))], {}, ValueError, "finite"),
        ([row(1, True)], {}, TypeError, "numeric"),
    ],
)
def test_invalid_or_mixed_history_is_rejected(history, kwargs, error, message):
    options = {
        "dataset_partition": "FD001/train",
        "unit_id": 1,
        "config": FeatureConfig(channels=("sensor_1",)),
        **kwargs,
    }

    with pytest.raises(error, match=message):
        engineer_features(history, **options)


def test_dataset_partition_is_required_for_engine_identity():
    with pytest.raises(ValueError, match="dataset_partition"):
        engineer_features(
            [row(1, 2)],
            dataset_partition=" ",
            unit_id=1,
            config=FeatureConfig(channels=("sensor_1",)),
        )
