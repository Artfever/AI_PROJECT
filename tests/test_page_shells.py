"""Smoke-test each page without requiring data or trained models."""

import pytest
from streamlit.testing.v1 import AppTest

from fleetpulse import PROJECT_ROOT


@pytest.mark.parametrize(
    ("filename", "title", "missing"),
    [
        ("1_Fleet_Overview.py", "Fleet Overview", "data and predictions"),
        ("2_Engine_Explorer.py", "Engine Explorer", "history data"),
        ("3_RUL_Prediction.py", "RUL Prediction", "history data"),
        ("4_Maintenance_Planner.py", "Maintenance Planner", "schedules"),
        ("5_Model_Laboratory.py", "Model Laboratory", "Development split audit is unavailable"),
    ],
)
def test_page_shell_loads_without_data(filename, title, missing, tmp_path, monkeypatch):
    from fleetpulse import ui

    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=10).run()
    assert not app.exception
    page = app.switch_page(f"pages/{filename}").run()

    assert not page.exception
    assert [heading.value for heading in page.title] == [title]
    if title == "Model Laboratory":
        assert any(missing in message.value for message in page.warning)
    else:
        messages = page.warning if title in ("Engine Explorer", "RUL Prediction") else page.info
        assert any(missing in message.value and "not available" in message.value for message in messages)
    assert not page.metric
    assert page.caption
    assert page.markdown

    home = app.switch_page("Home.py").run()
    assert not home.exception
    assert [heading.value for heading in home.title] == ["FleetPulse AI"]
