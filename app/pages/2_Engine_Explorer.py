"""Engine Explorer view."""

import streamlit as st

from fleetpulse.ui import render_training_data

st.title("Engine Explorer")
st.caption("Explore an individual engine history.")
render_training_data()
st.write("Engine selection will be available in a later update.")
