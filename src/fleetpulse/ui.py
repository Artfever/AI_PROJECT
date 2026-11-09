"""Shared presentation for the application's initial empty views."""

import streamlit as st


def render_page(title: str, description: str, missing: str, next_step: str) -> None:
    """Show a consistent page introduction and an honest empty state."""
    st.title(title)
    st.caption(description)
    st.info(missing)
    st.write(next_step)
