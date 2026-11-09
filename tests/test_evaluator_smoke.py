"""Verify the evaluator smoke example against independent hand arithmetic."""

import math

from scripts.smoke_validation import run_smoke


def test_constant_smoke_reports_synthetic_prefixes_and_known_results():
    report = run_smoke()
    assert "synthetic" in report["data_provenance"].lower()
    assert report["visible_cycles"] == [[1, 2, 3, 4], [1, 2, 3]]
    assert [row["true_rul"] for row in report["predictions"]] == [2, 5]
    assert [row["prediction"] for row in report["predictions"]] == [3.0, 3.0]
    assert report["illustrative_metrics_cycles"]["mae"] == 1.5
    assert math.isclose(report["illustrative_metrics_cycles"]["rmse"], math.sqrt(2.5))
