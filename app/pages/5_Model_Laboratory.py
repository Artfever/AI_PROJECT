"""Model Laboratory view."""

import streamlit as st

from fleetpulse import ui
from fleetpulse.data.split_audit_view import verified_split_manifest
from fleetpulse.ui import render_page

render_page(
    "Model Laboratory",
    "Inspect model development and evaluation.",
    "Trained models and evaluation results are not available yet.",
    "Model comparisons will appear here when measured results are available.",
)

st.subheader("Development split audit")
st.caption(
    "NASA FD001 simulated training engines only. Official test engines and answers "
    "are separate and are not used here."
)
try:
    manifest = verified_split_manifest(
        ui.PROJECT_ROOT / "artifacts" / "split_manifest.json",
        ui.PROJECT_ROOT / "data" / "raw" / "train_FD001.txt",
    )
except (OSError, ValueError, KeyError, TypeError) as error:
    st.warning(f"Development split audit is unavailable: {error}")
    st.write("Check the saved manifest and its matching local training file.")
else:
    fitting = manifest["fitting_engines"]
    validation = manifest["validation_prefixes"]
    st.caption(
        f"Verified against the local training source: split seed {manifest['split']['seed']}; "
        f"cutoff seed {manifest['cutoff_policy']['seed']}. "
        "These are development settings, not model results."
    )
    cols = st.columns(2)
    cols[0].metric("Fitting engines", len(fitting))
    cols[1].metric("Validation engines", len(validation))
    st.write("Fitting group (dataset-qualified engine IDs)")
    st.dataframe(fitting, hide_index=True)
    st.write("Validation prefixes and known targets — analysis only")
    st.caption(
        "Prefix length counts observed rows through the cutoff. Target RUL and "
        "full lifetime use hidden future information; never use them as model inputs."
    )
    st.dataframe(validation, hide_index=True)
    targets = [row["target_rul"] for row in validation]
    st.write(f"Validation target RUL range: {min(targets)}–{max(targets)} cycles.")
