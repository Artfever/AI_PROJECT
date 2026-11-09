"""Audit only verified split metadata; synthetic data never reaches production views."""

import hashlib
import json

from streamlit.testing.v1 import AppTest

from fleetpulse import PROJECT_ROOT, ui
from fleetpulse.data.loader import HISTORY_COLUMNS, load_engine_history
from fleetpulse.data.split_manifest import build_split_manifest


def test_audit_displays_verified_manifest_and_rejects_tampering(tmp_path, monkeypatch):
    raw = tmp_path / "data" / "raw"
    raw.mkdir(parents=True)
    source = raw / "train_FD001.txt"
    # Ten clearly artificial complete histories, three cycles each.
    source.write_text(
        "\n".join(
            " ".join(map(str, [engine, cycle, *([0.5] * 24)]))
            for engine in range(1, 11)
            for cycle in range(1, 4)
        ) + "\n",
        encoding="utf-8",
    )
    rows = load_engine_history(source)
    manifest = build_split_manifest(
        rows,
        dataset_partition="FD001/train",
        source_path="data/raw/train_FD001.txt",
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    )
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    path = artifacts / "split_manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(ui, "PROJECT_ROOT", tmp_path)
    page = AppTest.from_file(str(PROJECT_ROOT / "app" / "Home.py"), default_timeout=30).run()
    page = page.switch_page("pages/5_Model_Laboratory.py").run()
    assert not page.exception
    assert {item.label: item.value for item in page.metric} == {
        "Fitting engines": "8", "Validation engines": "2"
    }
    assert page.dataframe[1].value["target_rul"].tolist() == [
        row["target_rul"] for row in manifest["validation_prefixes"]
    ]
    assert list(rows[0]) == list(HISTORY_COLUMNS)
    manifest["validation_prefixes"][0]["target_rul"] = 999
    path.write_text(json.dumps(manifest), encoding="utf-8")
    page.run()
    assert not page.exception
    assert any("does not reproduce" in message.value for message in page.warning)
    assert not page.metric and not page.dataframe

    path.write_text(json.dumps(build_split_manifest(
        rows,
        dataset_partition="FD001/train",
        source_path="data/raw/train_FD001.txt",
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    )), encoding="utf-8")
    source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    page.run()
    assert not page.exception
    assert any("does not match" in message.value for message in page.warning)
    assert not page.metric and not page.dataframe
