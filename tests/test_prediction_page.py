"""Prediction-page behavior with synthetic history and controlled service results."""

from streamlit.testing.v1 import AppTest

from fleetpulse import PROJECT_ROOT, services, ui
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
    page.selectbox[0].select(2).run()
    page.selectbox[1].select(2).run()
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
    page.selectbox[1].select(1).run()
    assert not page.metric


def test_missing_bundle_shows_error_without_fabricating_prediction(monkeypatch, tmp_path):
    page = _page(monkeypatch, tmp_path).run()
    page.button[0].click().run()
    assert not page.exception
    assert not page.metric
    assert any("Prediction is unavailable" in item.value for item in page.warning)
