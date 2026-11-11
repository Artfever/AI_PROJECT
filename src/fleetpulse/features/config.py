"""Versioned input channels and ordered schema for past-only FD001 features.

This module declares the contract; it does not extract features or fit filters.
"""

from dataclasses import dataclass, field

from fleetpulse.data.quality import READING_COLUMNS

FEATURE_STATISTICS = ("latest", "mean", "std", "slope")
DEFAULT_CHANNELS = READING_COLUMNS


@dataclass(frozen=True)
class FeatureConfig:
    """Immutable feature contract, with channel-major output ordering.

    A window includes observed rows with cycles in
    ``[selected_cycle - window_cycles + 1, selected_cycle]``. Missing cycles
    are not interpolated. Statistics use available rows, population standard
    deviation and least-squares slope against actual cycle numbers. One row
    gives zero standard deviation and slope. Extraction belongs to P05-S1/S2.
    """

    channels: tuple[str, ...] = DEFAULT_CHANNELS
    window_cycles: int = 30
    version: str = field(default="past-only-v1", init=False)

    def __post_init__(self) -> None:
        if isinstance(self.window_cycles, bool) or not isinstance(self.window_cycles, int):
            raise TypeError("window_cycles must be an integer.")
        if self.window_cycles < 1:
            raise ValueError("window_cycles must be positive.")
        if not isinstance(self.channels, tuple):
            raise TypeError("channels must be an immutable tuple of raw reading names.")
        if not self.channels:
            raise ValueError("At least one reading channel is required.")
        if any(not isinstance(channel, str) for channel in self.channels):
            raise TypeError("Channel names must be strings.")
        if len(set(self.channels)) != len(self.channels):
            raise ValueError("Channel names must be unique.")
        if any(channel not in READING_COLUMNS for channel in self.channels):
            raise ValueError("Only declared FD001 setting and sensor channels are allowed.")

    @property
    def output_schema(self) -> tuple[str, ...]:
        """Return names in the only supported vector order for this config."""
        return tuple(
            f"{channel}_{statistic}"
            for channel in self.channels
            for statistic in FEATURE_STATISTICS
        )
