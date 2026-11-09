"""Explore the observed records for one FD001 training engine."""

import streamlit as st

from fleetpulse.data.quality import SENSOR_COLUMNS
from fleetpulse.ui import render_training_data
from fleetpulse.visualization import sensor_figure

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
    selected_sensor = st.selectbox("Sensor", SENSOR_COLUMNS)
    st.plotly_chart(
        sensor_figure(engine_records, selected_sensor),
        width="stretch",
        alt=f"{selected_sensor} readings by cycle for training engine {selected_engine}",
    )
else:
    st.write("Choose an engine once the training histories are available.")
