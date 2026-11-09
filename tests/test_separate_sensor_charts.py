"""Check chart separation using synthetic engine history only."""

import csv
import json
from pathlib import Path

import pyarrow as pa
from streamlit.testing.v1 import AppTest

from fleetpulse import PROJECT_ROOT, ui
from fleetpulse.data.loader import HISTORY_COLUMNS


def test_selected_channels_have_separate_labeled_charts(tmp_path, monkeypatch):
    fixture = Path(__file__).parent / "fixtures" / "synthetic_engine_history.csv"
    with fixture.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "train_FD001.txt").write_text(
        "\n".join(" ".join(row[field] for field in HISTORY_COLUMNS) for row in rows) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    page = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()
    page = page.switch_page("pages/2_Engine_Explorer.py").run()
    page.multiselect[0].set_value(["sensor_1", "sensor_20"]).run()

    assert not page.exception
    charts = page.get("vega_lite_chart")
    assert len(charts) == 2
    for chart, sensor in zip(charts, ["sensor_1", "sensor_20"], strict=True):
        spec = json.loads(chart.proto.spec)
        axes = spec["layer"][0]["encoding"]
        assert axes["x"]["field"] == "cycle"
        assert axes["x"]["title"] == "Cycle"
        assert axes["y"]["field"] == axes["y"]["title"] == sensor
        data = pa.ipc.open_stream(chart.proto.datasets[0].data.data).read_all().to_pydict()
        assert data == {
            "cycle": [int(row["cycle"]) for row in rows],
            sensor: [float(row[sensor]) for row in rows],
        }
