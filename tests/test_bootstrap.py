from fleetpulse import PROJECT_ROOT


def test_project_paths_and_entrypoint():
    assert (PROJECT_ROOT / "pyproject.toml").is_file()
    assert (PROJECT_ROOT / "app" / "Home.py").is_file()


def test_home_empty_state():
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py")).run()
    assert not app.exception
    assert any("no data, trained models" in item.value for item in app.info)
