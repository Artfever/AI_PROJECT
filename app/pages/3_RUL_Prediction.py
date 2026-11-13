"""Predict remaining cycles for a selected simulated training-engine history."""

import streamlit as st

from fleetpulse import ui
from fleetpulse.services import (
    PredictionArtifactError,
    PredictionInputError,
    predict_rul_with_context,
)

st.title("RUL Prediction")
st.caption("Estimate remaining useful life in operating cycles using a saved development model.")

records = ui.render_training_data()
if records is not None:
    engine_ids = sorted({int(row["unit_id"]) for row in records})
    engine = st.selectbox("Training engine ID", engine_ids)
    history = sorted(
        (row for row in records if row["unit_id"] == engine), key=lambda row: row["cycle"]
    )
    cycle = st.selectbox("Observed cycle", [int(row["cycle"]) for row in history])
    st.caption(
        "NASA FD001 data are simulated. The estimate uses only this engine's readings "
        "through the selected cycle; it is not a maintenance guarantee."
    )
    if st.button("Predict remaining cycles"):
        prefix = [row for row in history if row["cycle"] <= cycle]
        manifest = ui.PROJECT_ROOT / "artifacts/development/decision_tree_validation.json"
        try:
            result = predict_rul_with_context(
                prefix, dataset_partition="FD001/train", unit_id=engine, manifest_path=manifest
            )
        except (PredictionArtifactError, PredictionInputError) as error:
            st.warning(f"Prediction is unavailable: {error}")
            st.write("Check the saved development model bundle and the selected training history.")
        else:
            st.metric("Estimated remaining cycles", f"{result.displayed_rul_cycles:.2f}")
            st.write(f"Model: {result.model_name} ({result.model_version})")
            st.caption(
                f"FD001/train engine {engine}, observed cycle {result.observed_cycle}; "
                f"{result.input_window_rows} observed rows in the feature window. "
                f"Raw estimate: {result.raw_rul_cycles:.2f} cycles."
            )
            if "short_window" in result.warnings:
                st.warning("The available feature window is short; the estimate uses fewer observations.")
            if "cycle_gaps" in result.warnings:
                st.warning("The observed history contains gaps between cycles.")
            if "display_clipped_at_zero" in result.warnings:
                st.warning("The displayed estimate is clipped to zero; the raw estimate is shown above.")
else:
    st.write("Choose an engine once the training histories are available.")
