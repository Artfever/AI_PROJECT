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


def _render_training_data_help() -> None:
    """Explain where to obtain or check the local training file."""
    st.markdown(
        "Place the original `train_FD001.txt` file in `data/raw/`. "
        "Get it from the [NASA dataset repository](https://www.nasa.gov/intelligent-systems-division/"
        "discovery-and-systems-health/pcoe/pcoe-data-set-repository/); "
        "see `docs/fd001_provenance.md` for the source and checksums. "
        "If a file already exists, verify it before replacing anything. "
        "A separate illustrative synthetic example is available on RUL Prediction; "
        "it is not NASA data."
    )


def render_training_data() -> list[dict[str, int | float]] | None:
    """Display actual FD001 training histories or an actionable load error."""
    st.subheader("FD001 training histories")
    st.caption("Simulated NASA C-MAPSS training data; engine IDs belong to the training partition.")
    path = PROJECT_ROOT / "data" / "raw" / "train_FD001.txt"
    try:
        records = load_engine_history(path)
    except FD001LoadError as error:
        st.warning(f"Engine history data is not available yet. {error}")
        _render_training_data_help()
        return

    report = validate_engine_history(records)
    if not report.is_valid:
        st.error("The training file contains invalid records; check its contents before continuing.")
        _render_training_data_help()
        return
    if report.warnings:
        st.warning(f"The training history has {len(report.warnings)} quality warnings; review the source.")

    st.write("Preview: first 10 records in file order.")
    render_dataset_preview(
        record_count=len(records),
        engine_count=len({record["unit_id"] for record in records}),
        preview=records[:10],
    )
    return records


def render_packaged_training_subset() -> list[dict[str, int | float]] | None:
    """Load the small, explicitly labeled FD001/train deployment subset."""
    st.subheader("Packaged FD001/train prefix subset")
    st.info(
        "Small simulated NASA training-data subset: engines 4, 5 and 12, truncated at cycles "
        "164, 58 and 7. It supports the three deployment parity examples only; it is not a "
        "complete dataset or evidence of model quality or maintenance readiness."
    )
    path = PROJECT_ROOT / "data" / "demo" / "fd001_training_prefixes.txt"
    try:
        records = load_engine_history(path)
    except FD001LoadError as error:
        st.warning(f"Packaged FD001/train subset is not available. {error}")
        return

    report = validate_engine_history(records)
    expected_cutoffs = {4: 164, 5: 58, 12: 7}
    cycles_by_engine = {
        engine_id: sorted(int(row["cycle"]) for row in records if int(row["unit_id"]) == engine_id)
        for engine_id in expected_cutoffs
    }
    expected_cycles = {
        engine_id: list(range(1, cutoff + 1)) for engine_id, cutoff in expected_cutoffs.items()
    }
    if (
        not report.is_valid
        or {int(row["unit_id"]) for row in records} != set(expected_cutoffs)
        or cycles_by_engine != expected_cycles
        or len(records) != 229
    ):
        st.error("The packaged FD001/train subset failed its expected data checks.")
        return
    return records
