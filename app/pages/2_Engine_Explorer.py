"""Explore the observed records for one FD001 training engine."""

from itertools import pairwise

import streamlit as st

from fleetpulse.data.quality import SENSOR_COLUMNS
from fleetpulse.ui import render_training_data

st.title("Engine Explorer")
st.caption("Explore an individual engine history.")
records = render_training_data()
if records is not None:
    engine_ids = sorted({int(record["unit_id"]) for record in records})
    selected_engine = st.selectbox("Training engine ID", engine_ids)
    engine_records = sorted(
        (record for record in records if record["unit_id"] == selected_engine),
        key=lambda record: record["cycle"],
    )
    st.subheader(f"Training engine {selected_engine}")
    st.caption("Observed records, sorted by cycle.")
    st.dataframe(engine_records, hide_index=True)

    st.subheader("Sensor histories")
    st.caption(
        "Each sensor has its own y-axis because their numeric ranges differ. "
        "Descriptions summarize observed values only; they do not identify a physical fault."
    )
    selected_sensors = st.multiselect(
        "Sensors to plot",
        options=list(SENSOR_COLUMNS),
        default=["sensor_1", "sensor_2", "sensor_9"],
    )
    for sensor in selected_sensors:
        values = [float(record[sensor]) for record in engine_records]
        differences = [right - left for left, right in pairwise(values)]
        reversals = sum(
            (left < 0 < right) or (left > 0 > right)
            for left, right in pairwise(differences)
        )
        pattern = (
            "flat across observed cycles"
            if max(values) == min(values)
            else "varies across observed cycles"
        )
        st.markdown(
            f"**{sensor}:** {pattern}; observed range "
            f"{min(values):.6g} to {max(values):.6g}; {reversals} direction reversals."
        )
        st.line_chart(
            {"cycle": [record["cycle"] for record in engine_records], sensor: values},
            x="cycle",
            y=sensor,
            y_label=sensor,
            x_label="Cycle",
        )
    st.caption(
        "Repeated direction reversals can appear as noisy variation in a plot. "
        "This is a visual description of readings, not a fault or degradation diagnosis."
    )
else:
    st.write("Choose an engine once the training histories are available.")
