"""Explore the observed records for one FD001 training engine."""

import streamlit as st

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
else:
    st.write("Choose an engine once the training histories are available.")
