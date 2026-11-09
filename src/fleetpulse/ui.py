"""Shared presentation for the application's initial empty views."""

import streamlit as st

from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import FD001LoadError, load_engine_history
from fleetpulse.data.quality import validate_engine_history


def render_page(title: str, description: str, missing: str, next_step: str) -> None:
    """Show a consistent page introduction and an honest empty state."""
    st.title(title)
    st.caption(description)
    st.info(missing)
    st.write(next_step)


def render_dataset_preview(record_count: int, engine_count: int, preview: object) -> None:
    """Render caller-supplied counts and rows without loading or modifying data."""
    st.subheader("Dataset overview")
    records, engines = st.columns(2)
    records.metric("Records", record_count)
    engines.metric("Engines", engine_count)
    st.dataframe(preview, hide_index=True)


def render_training_data() -> None:
    """Display actual FD001 training histories or an actionable load error."""
    st.subheader("FD001 training histories")
    st.caption("Simulated NASA C-MAPSS training data; engine IDs belong to the training partition.")
    path = PROJECT_ROOT / "data" / "raw" / "train_FD001.txt"
    try:
        records = load_engine_history(path)
    except FD001LoadError as error:
        st.warning(f"Engine history data is not available yet. {error}")
        return

    report = validate_engine_history(records)
    if not report.is_valid:
        st.error("The training file contains invalid records; check its contents before continuing.")
        return
    if report.warnings:
        st.warning(f"The training history has {len(report.warnings)} quality warnings; review the source.")

    st.write("Preview: first 10 records in file order.")
    render_dataset_preview(
        record_count=len(records),
        engine_count=len({record["unit_id"] for record in records}),
        preview=records[:10],
    )
