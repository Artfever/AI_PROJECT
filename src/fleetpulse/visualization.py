"""Build sensor charts from one engine's observed training history."""

from collections.abc import Mapping, Sequence

import plotly.graph_objects as go

from fleetpulse.data.quality import SENSOR_COLUMNS


def sensor_figure(records: Sequence[Mapping[str, int | float]], sensor: str) -> go.Figure:
    """Chart one original sensor against cycle without mixing engine histories."""
    if sensor not in SENSOR_COLUMNS:
        raise ValueError(f"Unknown sensor: {sensor}")
    if not records or len({row["unit_id"] for row in records}) != 1:
        raise ValueError("A sensor chart requires records for exactly one engine.")
    rows = sorted(records, key=lambda row: row["cycle"])
    engine = rows[0]["unit_id"]
    figure = go.Figure(
        go.Scatter(
            x=[row["cycle"] for row in rows],
            y=[row[sensor] for row in rows],
            mode="lines",
            name=sensor,
        )
    )
    figure.update_layout(
        title=f"Training engine {engine}: {sensor}",
        xaxis_title="Operating cycle",
        yaxis_title=f"{sensor} reading",
    )
    return figure
