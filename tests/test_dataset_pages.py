"""Integration checks with a synthetic FD001-shaped file, never real data."""

import csv
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from fleetpulse import PROJECT_ROOT, ui
from fleetpulse.data.loader import HISTORY_COLUMNS

FIXTURE = Path(__file__).parent / "fixtures" / "synthetic_engine_history.csv"


@pytest.fixture
def synthetic_training_root(tmp_path):
    with FIXTURE.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    (raw / "train_FD001.txt").write_text(
        "\n".join(" ".join(row[field] for field in HISTORY_COLUMNS) for row in rows) + "\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.mark.parametrize("page", [None, "pages/2_Engine_Explorer.py"])
def test_dataset_pages_show_counts_and_preview_from_loader(page, synthetic_training_root, monkeypatch):
    monkeypatch.setattr(ui, "PROJECT_ROOT", synthetic_training_root)
    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()
    if page:
        app = app.switch_page(page).run()

    assert not app.exception
    assert {item.label: item.value for item in app.metric} == {"Records": "3", "Engines": "1"}
    assert len(app.dataframe) == 1
    assert app.dataframe[0].value["cycle"].tolist() == [1, 2, 3]
    assert app.dataframe[0].value["unit_id"].tolist() == [900001] * 3
    assert not app.warning


@pytest.mark.parametrize("content", [None, "1 2 3\n"])
def test_missing_or_malformed_data_is_explained_without_fake_counts(content, tmp_path, monkeypatch):
    if content is not None:
        raw = tmp_path / "data" / "raw"
        raw.mkdir(parents=True)
        (raw / "train_FD001.txt").write_text(content, encoding="utf-8")
    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()

    assert not app.exception
    assert any("Engine history data is not available" in item.value for item in app.warning)
    assert not app.metric
    assert not app.dataframe


def test_invalid_history_is_not_presented_as_valid(synthetic_training_root, monkeypatch):
    path = synthetic_training_root / "data" / "raw" / "train_FD001.txt"
    rows = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join([rows[0], rows[0]]) + "\n", encoding="utf-8")
    monkeypatch.setattr(ui, "PROJECT_ROOT", synthetic_training_root)
    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()

    assert not app.exception
    assert any("invalid records" in item.value for item in app.error)
    assert not app.metric
    assert not app.dataframe
