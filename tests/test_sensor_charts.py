"""Sensor charts use only the selected artificial engine and channel."""

import csv
import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from fleetpulse import PROJECT_ROOT, ui
from fleetpulse.data.loader import HISTORY_COLUMNS
from fleetpulse.visualization import sensor_figure

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_engine_history.csv"


def test_sensor_figure_sorts_cycles_and_rejects_mixed_engines():
    records = [
        {"unit_id": 1, "cycle": 2, "sensor_1": 4.5},
        {"unit_id": 1, "cycle": 1, "sensor_1": 3.5},
    ]
    figure = sensor_figure(records, "sensor_1")
    assert list(figure.data[0].x) == [1, 2]
    assert list(figure.data[0].y) == [3.5, 4.5]
    with pytest.raises(ValueError, match="exactly one engine"):
        sensor_figure([*records, {"unit_id": 2, "cycle": 1, "sensor_1": 7.0}], "sensor_1")
    with pytest.raises(ValueError, match="Unknown sensor"):
        sensor_figure(records, "unit_id")


def test_chart_tracks_engine_and_sensor_selection(tmp_path, monkeypatch):
    with FIXTURE.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    interleaved = []
    for row in rows:
        other = {**row, "unit_id": "900002", "sensor_2": str(int(row["sensor_2"]) + 5000)}
        interleaved.extend([row, other])
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "train_FD001.txt").write_text(
        "\n".join(" ".join(row[field] for field in HISTORY_COLUMNS) for row in interleaved) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()
    page = app.switch_page("pages/2_Engine_Explorer.py").run()
    page.selectbox[0].set_value(900002).run()
    page.selectbox[1].set_value("sensor_2").run()

    assert not page.exception
    chart = json.loads(page.get("plotly_chart")[0].proto.spec)
    assert chart["data"][0]["name"] == "sensor_2"
    assert chart["data"][0]["x"] == [1, 2, 3]
    assert chart["data"][0]["y"] == [15201.0, 15202.0, 15203.0]
    assert "900002" in chart["layout"]["title"]["text"]
