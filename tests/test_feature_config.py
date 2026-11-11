"""Protect feature order and reject leakage channels before extraction exists."""

from dataclasses import FrozenInstanceError

import pytest

from fleetpulse.features import FeatureConfig


def test_default_schema_matches_explicit_fd001_channel_contract():
    config = FeatureConfig()
    assert config.channels == (
        "setting_1",
        "setting_2",
        "setting_3",
        *(f"sensor_{i}" for i in range(1, 22)),
    )
    assert config.window_cycles == 30
    assert config.version == "past-only-v1"
    assert len(config.output_schema) == len(set(config.output_schema)) == 96
    assert config.output_schema[:8] == (
        "setting_1_latest",
        "setting_1_mean",
        "setting_1_std",
        "setting_1_slope",
        "setting_2_latest",
        "setting_2_mean",
        "setting_2_std",
        "setting_2_slope",
    )
    assert config.output_schema[-4:] == (
        "sensor_21_latest",
        "sensor_21_mean",
        "sensor_21_std",
        "sensor_21_slope",
    )


def test_selected_channels_preserve_explicit_order_and_are_immutable():
    config = FeatureConfig(channels=("sensor_2", "setting_1"), window_cycles=10)
    assert config.output_schema == (
        "sensor_2_latest",
        "sensor_2_mean",
        "sensor_2_std",
        "sensor_2_slope",
        "setting_1_latest",
        "setting_1_mean",
        "setting_1_std",
        "setting_1_slope",
    )
    with pytest.raises(FrozenInstanceError):
        config.window_cycles = 20


@pytest.mark.parametrize(
    "channel",
    [
        "unit_id",
        "cycle",
        "rul",
        "true_rul",
        "full_lifetime",
        "target_rul",
        "prefix_row_count",
        "future_sensor_1",
        "sensor_22",
    ],
)
def test_identity_targets_metadata_and_unknown_channels_are_rejected(channel):
    with pytest.raises(ValueError, match="Only declared FD001"):
        FeatureConfig(channels=(channel,))


@pytest.mark.parametrize(
    "channels,error",
    [
        ((), ValueError),
        (("sensor_1", "sensor_1"), ValueError),
        (["sensor_1"], TypeError),
        ((1,), TypeError),
    ],
)
def test_invalid_channel_definitions_fail_early(channels, error):
    with pytest.raises(error):
        FeatureConfig(channels=channels)


@pytest.mark.parametrize(
    "window,error",
    [
        (0, ValueError),
        (-1, ValueError),
        (True, TypeError),
        (1.5, TypeError),
    ],
)
def test_invalid_window_definitions_fail_early(window, error):
    with pytest.raises(error):
        FeatureConfig(window_cycles=window)
