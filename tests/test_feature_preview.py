"""Check the development feature preview using deliberately synthetic histories."""

import csv
from pathlib import Path

from streamlit.testing.v1 import AppTest

from fleetpulse import PROJECT_ROOT, features, ui
from fleetpulse.data.loader import HISTORY_COLUMNS


def test_feature_preview_passes_only_selected_engine_prefix(tmp_path, monkeypatch):
    fixture = Path(__file__).parent / "fixtures" / "synthetic_engine_history.csv"
    with fixture.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    rows += [{**row, "unit_id": "900002", "sensor_1": str(200 + i)}
             for i, row in enumerate(rows, start=1)]
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "train_FD001.txt").write_text(
        "\n".join(" ".join(row[field] for field in HISTORY_COLUMNS) for row in rows) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    calls = []
    original = features.engineer_features

    def capture(history, **kwargs):
        calls.append([row.copy() for row in history])
        return original(history, **kwargs)

    monkeypatch.setattr(features, "engineer_features", capture)
    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()
    page = app.switch_page("pages/2_Engine_Explorer.py").run()
    page.selectbox[0].set_value(900002).run()
    page.selectbox[2].set_value(2).run()
    assert not page.exception
    assert [r["cycle"] for r in calls[-1]] == [1, 2]
    assert {r["unit_id"] for r in calls[-1]} == {900002}
    assert all(set(r) == set(HISTORY_COLUMNS) for r in calls[-1])
    prefix = page.dataframe[3].value
    assert prefix["cycle"].tolist() == [1, 2]
    assert prefix["unit_id"].tolist() == [900002, 900002]
    table = page.dataframe[4].value.set_index("feature")["value"]
    assert len(table) == 96
    assert table["sensor_1_latest"] == 202
    assert table["sensor_1_mean"] == 201.5
    assert table["sensor_1_std"] == 0.5
    assert table["sensor_1_slope"] == 1

    ordered = page.dataframe[4].value
    assert ordered["position"].tolist() == list(range(96))
    assert ordered["feature"].tolist() == list(features.FeatureConfig().output_schema)
    assert any("FD001/train engine 900002" in item.value for item in page.caption)
    page.selectbox[2].set_value(1).run()
    assert not page.exception
    assert [row["cycle"] for row in calls[-1]] == [1]
    assert page.dataframe[3].value["cycle"].tolist() == [1]
    earlier = page.dataframe[4].value.set_index("feature")["value"]
    assert earlier["sensor_1_latest"] == 201
    assert earlier["sensor_1_mean"] == 201
    assert earlier["sensor_1_std"] == 0
    assert earlier["sensor_1_slope"] == 0
