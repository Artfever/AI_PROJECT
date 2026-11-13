"""Prediction-page behavior with synthetic history and controlled service results."""

from streamlit.testing.v1 import AppTest

from fleetpulse import PROJECT_ROOT, services, ui
from fleetpulse.data.loader import HISTORY_COLUMNS
from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.services import RULPrediction


def _page(monkeypatch, tmp_path):
    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    rows = [
        {"unit_id": unit, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 0.5)}
        for unit in (1, 2)
        for cycle in (1, 2, 3)
    ]
    monkeypatch.setattr(ui, "render_training_data", lambda: rows)
    return AppTest.from_file(str(PROJECT_ROOT / "app/pages/3_RUL_Prediction.py"), default_timeout=30)


def test_selected_engine_and_cutoff_reach_service_without_future_or_target(monkeypatch, tmp_path):
    page = _page(monkeypatch, tmp_path)
    calls = []

    def predict(history, **kwargs):
        calls.append((history, kwargs))
        return RULPrediction(12.5, 12.5, "test-model", "test-v1", 2, 2, ("short_window",))

    monkeypatch.setattr(services, "predict_rul_with_context", predict)
    page.run()
    assert not calls
    page.selectbox[1].select(2).run()
    page.selectbox[2].select(2).run()
    page.button[0].click().run()
    assert not page.exception
    assert [row["cycle"] for row in calls[0][0]] == [1, 2]
    assert all(row["unit_id"] == 2 and set(row) == {"unit_id", "cycle", *READING_COLUMNS} for row in calls[0][0])
    assert calls[0][1]["dataset_partition"] == "FD001/train"
    assert calls[0][1]["unit_id"] == 2
    assert calls[0][1]["manifest_path"] == tmp_path / "artifacts/development/decision_tree_validation.json"
    assert page.metric[0].value == "12.50"
    assert any("test-model" in item.value and "test-v1" in item.value for item in page.markdown)
    assert any("short" in item.value for item in page.warning)
    page.selectbox[2].select(1).run()
    assert not page.metric


def test_missing_bundle_shows_error_without_fabricating_prediction(monkeypatch, tmp_path):
    page = _page(monkeypatch, tmp_path).run()
    page.button[0].click().run()
    assert not page.exception
    assert not page.metric
    assert any("Prediction is unavailable" in item.value for item in page.warning)


def test_packaged_illustrative_history_is_distinct_and_has_no_future_rows(monkeypatch, tmp_path):
    page = _page(monkeypatch, tmp_path)
    demo_dir = tmp_path / "data/demo"
    demo_dir.mkdir(parents=True)
    (demo_dir / "illustrative_history.txt").write_bytes(
        (PROJECT_ROOT / "data/demo/illustrative_history.txt").read_bytes()
    )
    calls = []

    def predict(history, **kwargs):
        calls.append((history, kwargs))
        return RULPrediction(3.0, 3.0, "test-model", "test-v1", 2, 2, ())

    monkeypatch.setattr(services, "predict_rul_with_context", predict)
    page.run()
    page.selectbox[0].select("Illustrative synthetic example").run()
    assert any("not NASA data" in item.value for item in page.warning)
    page.selectbox[2].select(2).run()
    page.button[0].click().run()
    assert not page.exception
    assert [row["cycle"] for row in calls[0][0]] == [1, 2]
    assert calls[0][1]["dataset_partition"] == "illustrative/synthetic"
    assert calls[0][1]["unit_id"] == 900001
    assert page.metric[0].value == "3.00"


def test_packaged_fd001_subset_uses_only_selected_training_prefix(monkeypatch, tmp_path):
    page = _page(monkeypatch, tmp_path)
    rows = [
        {"unit_id": engine, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 0.5)}
        for engine, cutoff in ((4, 164), (5, 58), (12, 7))
        for cycle in range(1, cutoff + 1)
    ]
    subset_path = tmp_path / "data/demo/fd001_training_prefixes.txt"
    subset_path.parent.mkdir(parents=True)
    subset_path.write_text(
        "\n".join(" ".join(str(row[column]) for column in HISTORY_COLUMNS) for row in rows)
        + "\n",
        encoding="utf-8",
    )
    calls = []

    def predict(history, **kwargs):
        calls.append((history, kwargs))
        return RULPrediction(
            34.19607843137255, 34.20, "decision-tree-rul", "decision-tree-rul-v1", 164, 30, ()
        )

    monkeypatch.setattr(services, "predict_rul_with_context", predict)
    page.run()
    page.selectbox[0].select("Packaged FD001/train parity subset").run()
    assert any("not a complete dataset" in item.value for item in page.info)
    page.selectbox[2].select(164).run()
    page.button[0].click().run()

    assert not page.exception
    assert len(calls[0][0]) == 164
    assert {row["unit_id"] for row in calls[0][0]} == {4}
    assert max(row["cycle"] for row in calls[0][0]) == 164
    assert all(set(row) == {"unit_id", "cycle", *READING_COLUMNS} for row in calls[0][0])
    assert calls[0][1]["dataset_partition"] == "FD001/train"
    assert calls[0][1]["unit_id"] == 4
    assert page.metric[0].value == "34.20"
