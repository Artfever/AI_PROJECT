"""Explore the observed records for one FD001 training engine."""

from itertools import pairwise

import streamlit as st

from fleetpulse.data.quality import SENSOR_COLUMNS
from fleetpulse.data.targets import calculate_training_rul
from fleetpulse.features import FeatureConfig, engineer_features
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

    sensors_tab, truth_tab, features_tab = st.tabs(
        ["Sensor histories", "Training ground truth", "Development feature preview"]
    )
    with sensors_tab:
        st.subheader("Selected sensor")
        selected_sensor = st.selectbox("Sensor", SENSOR_COLUMNS)
        st.plotly_chart(
            sensor_figure(engine_records, selected_sensor),
            width="stretch",
            alt=f"{selected_sensor} readings by cycle for training engine {selected_engine}",
        )

        st.subheader("Sensor histories")
        st.caption(
            "Each sensor has its own y-axis because their numeric ranges differ. "
            "Descriptions summarize observed values only; they do not identify a physical fault."
        )
        selected_sensors = st.multiselect(
            "Sensors to plot",
            options=list(SENSOR_COLUMNS),
            default=["sensor_1", "sensor_2", "sensor_9"],
        )
        for sensor in selected_sensors:
            values = [float(record[sensor]) for record in engine_records]
            differences = [right - left for left, right in pairwise(values)]
            reversals = sum(
                (left < 0 < right) or (left > 0 > right)
                for left, right in pairwise(differences)
            )
            pattern = (
                "flat across observed cycles"
                if max(values) == min(values)
                else "varies across observed cycles"
            )
            st.markdown(
                f"**{sensor}:** {pattern}; observed range "
                f"{min(values):.6g} to {max(values):.6g}; {reversals} direction reversals."
            )
            st.line_chart(
                {"cycle": [record["cycle"] for record in engine_records], sensor: values},
                x="cycle",
                y=sensor,
                y_label=sensor,
                x_label="Cycle",
            )
        st.caption(
            "Repeated direction reversals can appear as noisy variation in a plot. "
            "This is a visual description of readings, not a fault or degradation diagnosis."
        )
    with truth_tab:
        st.subheader("Known training RUL ? analysis only")
        st.caption(
            "Uncapped remaining cycles calculated from the complete training engine's "
            "final cycle. These labels use the future failure cycle and must never be "
            "used as prediction inputs. They are not model predictions."
        )
        labels = calculate_training_rul(engine_records)
        analysis_rows = [
            {"cycle": row["cycle"], "known_training_rul_cycles": label}
            for row, label in zip(engine_records, labels, strict=True)
        ]
        st.dataframe(analysis_rows, hide_index=True)

    with features_tab:
        st.subheader("Development feature preview")
        st.caption(
            "Simulated FD001 training data; inspection only. Features use the selected "
            "engine's observed history through the selected cycle, not future rows or RUL labels."
        )
        selected_cycle = st.selectbox(
            "Feature preview cycle", [int(row["cycle"]) for row in engine_records]
        )
        prefix = [row for row in engine_records if row["cycle"] <= selected_cycle]
        config = FeatureConfig()
        try:
            vector = engineer_features(
                prefix,
                dataset_partition="FD001/train",
                unit_id=selected_engine,
                selected_cycle=selected_cycle,
                config=config,
            )
        except (ValueError, TypeError) as error:
            st.warning(f"Feature preview is unavailable: {error}")
        else:
            st.caption(
                f"Visible input: {vector.observed_row_count} rows through cycle "
                f"{vector.selected_cycle}; {vector.window_row_count} rows in the "
                f"{config.window_cycles}-cycle window. Configuration: {config.version}."
            )
            st.write("Visible input history")
            st.dataframe(prefix, hide_index=True)
            st.write("Calculated features")
            st.caption(
                "Latest, mean and standard deviation use source channel units; "
                "slopes use source units per cycle."
            )
            st.dataframe(
                [{"feature": name, "value": value} for name, value in vector.as_dict().items()],
                hide_index=True,
            )

else:
    st.write("Choose an engine once the training histories are available.")
