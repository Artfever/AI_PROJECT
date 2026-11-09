"""Exercise the dataset display with artificial, test-only readings."""

from streamlit.testing.v1 import AppTest


def test_preview_displays_supplied_counts_and_rows():
    def preview_app():
        import pandas as pd

        from fleetpulse import PROJECT_ROOT
        from fleetpulse.ui import render_dataset_preview

        # This synthetic fixture is test-only and is not NASA data.
        frame = pd.read_csv(PROJECT_ROOT / "tests" / "fixtures" / "synthetic_engine_history.csv")
        render_dataset_preview(
            record_count=len(frame),
            engine_count=frame["unit_id"].nunique(),
            preview=frame.head(2),
        )

    app = AppTest.from_function(preview_app, default_timeout=30).run()

    assert not app.exception
    assert {item.label: item.value for item in app.metric} == {"Records": "3", "Engines": "1"}
    assert len(app.dataframe) == 1
    assert app.dataframe[0].value["cycle"].tolist() == [1, 2]
