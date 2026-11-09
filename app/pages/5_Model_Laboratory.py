"""Model Laboratory view."""

import streamlit as st

from fleetpulse.ui import render_page

render_page(
    'Model Laboratory',
    'Inspect model development and evaluation.',
    'Trained models and evaluation results are not available yet.',
    'Model comparisons will appear here when measured results are available.',
)


st.subheader("Development split audit")
st.info(
    "A development split manifest is not available yet. Split counts, validation "
    "cutoffs, prefix lengths, and target ranges will appear after it is provided."
)
st.caption("Official test data and answers are separate from development validation.")
