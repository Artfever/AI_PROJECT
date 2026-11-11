"""Training ground truth is isolated from raw synthetic engine histories."""

import csv
from pathlib import Path

from streamlit.testing.v1 import AppTest

from fleetpulse import PROJECT_ROOT, ui
from fleetpulse.data.loader import HISTORY_COLUMNS


def test_ground_truth_is_separate_and_changes_with_training_engine(tmp_path, monkeypatch):
    fixture = Path(__file__).parent / "fixtures" / "synthetic_engine_history.csv"
    with fixture.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    # Synthetic complete lifetimes have 3 and 2 cycles respectively.
    rows += [{**row, "unit_id": "900002"} for row in rows[:2]]
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "train_FD001.txt").write_text(
        "\n".join(" ".join(row[field] for field in HISTORY_COLUMNS) for row in rows) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    page = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()
    page = page.switch_page("pages/2_Engine_Explorer.py").run()

    assert not page.exception
    assert [tab.label for tab in page.tabs] == ["Sensor histories", "Training ground truth", "Development feature preview"]
    raw_engine = page.dataframe[1].value
    truth = page.dataframe[2].value
    assert list(raw_engine.columns) == list(HISTORY_COLUMNS)
    assert truth.to_dict("list") == {"cycle": [1, 2, 3], "known_training_rul_cycles": [2, 1, 0]}
    assert any("not model predictions" in caption.value for caption in page.caption)
    page.selectbox[0].set_value(900002).run()
    assert not page.exception
    assert page.dataframe[2].value.to_dict("list") == {
        "cycle": [1, 2],
        "known_training_rul_cycles": [1, 0],
    }
    assert list(page.dataframe[1].value.columns) == list(HISTORY_COLUMNS)


def test_missing_training_file_has_no_ground_truth_tab(tmp_path, monkeypatch):
    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    page = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()
    page = page.switch_page("pages/2_Engine_Explorer.py").run()
    assert not page.exception
    assert page.warning
    assert not page.tabs
