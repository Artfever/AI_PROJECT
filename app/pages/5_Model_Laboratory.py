"""Model Laboratory view."""

import json

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from fleetpulse import ui
from fleetpulse.data.split_audit_view import verified_split_manifest
from fleetpulse.evaluation.model_comparison import load_model_comparison
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import manifest_digest
from fleetpulse.features.dataset_io import load_feature_dataset
from fleetpulse.ui import render_page

render_page(
    "Model Laboratory",
    "Inspect model development and evaluation.",
    "Compare the constant baseline and Decision Tree using verified held-out development results.",
    "This page reports held-out development results only; it does not show official test performance.",
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
    fitting_engines = manifest["fitting_engines"]
    validation_engines = manifest["validation_prefixes"]
    st.caption(
        f"Verified against the local training source: split seed {manifest['split']['seed']}; "
        f"cutoff seed {manifest['cutoff_policy']['seed']}. "
        "These are development settings, not model results."
    )
    cols = st.columns(2)
    cols[0].metric("Fitting engines", len(fitting_engines))
    cols[1].metric("Validation engines", len(validation_engines))
    st.write("Fitting group (dataset-qualified engine IDs)")
    st.dataframe(fitting_engines, hide_index=True)
    st.write("Validation prefixes and known targets — analysis only")
    st.caption(
        "Prefix length counts observed rows through the cutoff. Target RUL and "
        "full lifetime use hidden future information; never use them as model inputs."
    )
    st.dataframe(validation_engines, hide_index=True)
    targets = [row["target_rul"] for row in validation_engines]
    st.write(f"Validation target RUL range: {min(targets)}–{max(targets)} cycles.")

    artifact_dir = ui.PROJECT_ROOT / "artifacts" / "development"
    try:
        expected_manifest_sha = manifest_digest(manifest)
        feature_config = FeatureConfig()
        fitting_path = artifact_dir / "fitting_features.json"
        validation_path = artifact_dir / "validation_features.json"
        fitting = load_feature_dataset(
            fitting_path,
            expected_source_sha256=manifest["source"]["sha256"],
            expected_manifest_sha256=expected_manifest_sha,
            expected_config=feature_config,
        )
        validation_features = load_feature_dataset(
            validation_path,
            expected_source_sha256=manifest["source"]["sha256"],
            expected_manifest_sha256=expected_manifest_sha,
            expected_config=feature_config,
        )
        fitting_sha = json.loads(fitting_path.read_text(encoding="utf-8"))["sha256"]
        validation_sha = json.loads(validation_path.read_text(encoding="utf-8"))["sha256"]
        comparison = load_model_comparison(
            artifact_dir,
            fitting,
            validation_features,
            fitting_dataset_sha256=fitting_sha,
            validation_dataset_sha256=validation_sha,
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        st.info(
            "Verified model comparison is unavailable. Run `python scripts/run_p06_validation.py` "
            f"from the repository root and check the local FD001 setup. Detail: {error}"
        )
    else:
        st.subheader("Constant baseline and Decision Tree")
        st.caption(
            f"Both models use the same {comparison.validation_engine_count} held-out FD001 training "
            "engines and saved cutoff cycles. These are development-validation measurements, "
            "not official test results."
        )
        metric_rows = [
            {
                "Model": comparison.baseline_name,
                "MAE (cycles)": comparison.baseline_metrics.mae,
                "RMSE (cycles)": comparison.baseline_metrics.rmse,
            },
            {
                "Model": comparison.tree_name,
                "MAE (cycles)": comparison.tree_metrics.mae,
                "RMSE (cycles)": comparison.tree_metrics.rmse,
            },
        ]
        st.dataframe(metric_rows, hide_index=True, width="stretch")
        st.write(
            f"The constant baseline predicts {comparison.baseline_prediction:.2f} cycles for every engine. "
            "The tree uses the saved sensor and setting features. On this split, the tree has "
            f"{'lower' if comparison.tree_metrics.mae < comparison.baseline_metrics.mae else 'higher or equal'} "
            f"MAE by {abs(comparison.baseline_metrics.mae - comparison.tree_metrics.mae):.2f} cycles and "
            f"{'lower' if comparison.tree_metrics.rmse < comparison.baseline_metrics.rmse else 'higher or equal'} "
            f"RMSE by {abs(comparison.baseline_metrics.rmse - comparison.tree_metrics.rmse):.2f} cycles. "
            "These differences describe this held-out development split only; they do not establish "
            "future or official-test performance."
        )
        figure = px.scatter(
            comparison.predictions,
            x="Actual RUL (cycles)",
            y="Predicted RUL (cycles)",
            color="Model",
            hover_data=["Engine", "Cutoff cycle"],
            title="Predicted versus actual RUL on held-out development engines",
        )
        upper = max(
            max(row["Actual RUL (cycles)"] for row in comparison.predictions),
            max(row["Predicted RUL (cycles)"] for row in comparison.predictions),
        )
        figure.add_trace(
            go.Scatter(
                x=[0, upper],
                y=[0, upper],
                mode="lines",
                name="Ideal prediction",
                line={"dash": "dash", "color": "gray"},
            )
        )
        figure.update_layout(
            xaxis_title="Actual RUL (cycles)",
            yaxis_title="Predicted RUL (cycles)",
        )
        st.plotly_chart(figure, width="stretch")
        st.caption(
            "Points closer to the dashed line have smaller absolute error. Each point is one engine at its "
            "saved validation cutoff. RUL estimates are not clipped."
        )
