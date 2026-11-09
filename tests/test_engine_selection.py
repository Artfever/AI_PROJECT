"""Exercise selection and isolation using deliberately synthetic histories."""

import csv
import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from fleetpulse import PROJECT_ROOT, ui
from fleetpulse.data.loader import HISTORY_COLUMNS

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_engine_history.csv"


def test_selecting_two_engines_shows_only_their_ordered_cycles(tmp_path, monkeypatch):
    with FIXTURE.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    for index, row in enumerate(rows):
        row["sensor_1"] = "7.0"
        row["sensor_2"] = ("1.0", "3.0", "2.0")[index]
    # Add a second artificial engine and interleave it without reordering either history.
    interleaved = []
    for row in rows:
        interleaved.extend([row, {**row, "unit_id": "900002"}])
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "train_FD001.txt").write_text(
        "\n".join(" ".join(row[field] for field in HISTORY_COLUMNS) for row in interleaved) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()
    page = app.switch_page("pages/2_Engine_Explorer.py").run()

    assert not page.exception
    assert page.selectbox[0].value == 900001
    assert page.dataframe[1].value["unit_id"].tolist() == [900001] * 3
    assert page.dataframe[1].value["cycle"].tolist() == [1, 2, 3]
    assert page.multiselect[0].value == ["sensor_1", "sensor_2", "sensor_9"]
    assert len(page.get("vega_lite_chart")) == 3
    chart_fields = [
        json.loads(chart.proto.spec)["layer"][0]["encoding"]["y"]["field"]
        for chart in page.get("vega_lite_chart")
    ]
    assert chart_fields == ["sensor_1", "sensor_2", "sensor_9"]
    descriptions = "\n".join(element.value for element in page.markdown)
    assert "sensor_1:** flat across observed cycles" in descriptions
    assert "sensor_2:** varies across observed cycles" in descriptions
    assert "1 direction reversals" in descriptions
    page.selectbox[0].set_value(900002).run()
    assert not page.exception
    assert page.dataframe[1].value["unit_id"].tolist() == [900002] * 3
    assert page.dataframe[1].value["cycle"].tolist() == [1, 2, 3]


def test_missing_training_data_has_no_engine_selector(tmp_path, monkeypatch):
    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()
    page = app.switch_page("pages/2_Engine_Explorer.py").run()

    assert not page.exception
    assert page.warning
    assert not page.selectbox
    assert not page.dataframe
