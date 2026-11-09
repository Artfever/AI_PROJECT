"""Shared presentation for the application's initial empty views."""

import streamlit as st


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
