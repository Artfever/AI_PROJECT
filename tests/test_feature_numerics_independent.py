"""Abdullah's independent synthetic acceptance cases for P05-A2.

Expected fractions come from hand calculations, not another feature extractor.
"""

import math
from types import MappingProxyType

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.features import FeatureConfig, engineer_features


def _extract(rows, *, cycle, channels=("sensor_2", "sensor_1"), window=30):
    return engineer_features(
        rows,
        dataset_partition="synthetic/P05-A2",
        unit_id=17,
        selected_cycle=cycle,
        config=FeatureConfig(channels=channels, window_cycles=window),
    )


def test_gapped_nonlinear_channel_and_constant_have_hand_calculated_statistics():
    # x=[2,5,9], y=[2,8,5]: mean(y)=5, population variance=6.
    # Sum centered x*y=9; sum centered x*x=74/3; slope=27/74.
    rows = [
        MappingProxyType({"unit_id": 17, "cycle": x, "sensor_1": y, "sensor_2": 7})
        for x, y in ((2, 2), (5, 8), (9, 5))
    ]
    result = _extract(rows, cycle=9)
    assert result.engine_key == ("synthetic/P05-A2", 17)
    assert result.observed_row_count == result.window_row_count == 3
    assert result.as_dict() == pytest.approx(
        {
            "sensor_2_latest": 7,
            "sensor_2_mean": 7,
            "sensor_2_std": 0,
            "sensor_2_slope": 0,
            "sensor_1_latest": 5,
            "sensor_1_mean": 5,
            "sensor_1_std": math.sqrt(6),
            "sensor_1_slope": 27 / 74,
        }
    )
    assert tuple(result.as_dict()) == result.config.output_schema
    assert [row["sensor_1"] for row in rows] == [2, 8, 5]


def test_known_linear_values_with_negative_slope_and_constant_channel():
    rows = [
        {"unit_id": 17, "cycle": x, "sensor_1": y, "sensor_2": -3}
        for x, y in ((1, 6), (2, 4), (3, 2))
    ]
    result = _extract(rows, cycle=3)
    assert result.values == pytest.approx((-3, -3, 0, 0, 2, 4, math.sqrt(8 / 3), -2))


def test_one_observation_supports_every_default_channel_with_finite_features():
    readings = {channel: number / 4 for number, channel in enumerate(READING_COLUMNS)}
    result = _extract(
        [{"unit_id": 17, "cycle": 12, **readings}],
        cycle=12,
        channels=READING_COLUMNS,
    )
    assert len(result.values) == 96
    assert all(map(math.isfinite, result.values))
    for index, channel in enumerate(READING_COLUMNS):
        assert result.values[4 * index : 4 * index + 4] == (
            readings[channel],
            readings[channel],
            0,
            0,
        )
    assert result.observed_row_count == result.window_row_count == 1


def test_short_gapped_window_uses_cycles_not_row_positions():
    # Window [7,9] contains only cycle9; older rows remain visible metadata.
    rows = [{"unit_id": 17, "cycle": x, "sensor_1": y} for x, y in ((2, -20), (5, 100), (9, 5))]
    result = _extract(rows, cycle=9, channels=("sensor_1",), window=3)
    assert result.values == (5, 5, 0, 0)
    assert result.observed_row_count == 3
    assert result.window_row_count == 1


@pytest.mark.parametrize(
    "value,error",
    [
        (None, TypeError),
        (True, TypeError),
        ("4", TypeError),
        (float("nan"), ValueError),
        (float("inf"), ValueError),
        (float("-inf"), ValueError),
    ],
)
@pytest.mark.parametrize("bad_cycle", [1, 2])
def test_invalid_requested_reading_at_any_window_position_is_rejected(value, error, bad_cycle):
    rows = [{"unit_id": 17, "cycle": cycle, "sensor_1": 4} for cycle in (1, 2)]
    rows[bad_cycle - 1]["sensor_1"] = value
    with pytest.raises(error, match=f"sensor_1 at cycle {bad_cycle}"):
        _extract(rows, cycle=2, channels=("sensor_1",))


def test_missing_requested_channel_is_rejected_without_imputation():
    rows = [{"unit_id": 17, "cycle": 1, "sensor_1": 2}]
    with pytest.raises(TypeError, match="sensor_2 at cycle 1"):
        _extract(rows, cycle=1)


def test_empty_input_is_rejected_instead_of_producing_zero_features():
    with pytest.raises(ValueError, match="At least one engine-history row"):
        _extract([], cycle=1)
