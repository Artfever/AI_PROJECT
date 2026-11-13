"""P07 raw/context component tests using temporary synthetic saved trees."""

import base64
import copy
import hashlib
import json
from dataclasses import asdict, fields

import joblib
import pytest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split_manifest import build_split_manifest
from fleetpulse.deployment import prediction_manifest
from fleetpulse.features import FeatureConfig
from fleetpulse.features.build_dataset import build_fitting_dataset, build_validation_dataset
from fleetpulse.models.train_tree import train_decision_tree
from fleetpulse.models.tree_artifact import MODEL_FILENAME, save_decision_tree_artifact
from fleetpulse.services import (
    PredictionArtifactError,
    PredictionInputError,
    RawRULPrediction,
    predict_rul,
    predict_rul_with_context,
)


def _row(cycle, unit=99):
    return {
        "unit_id": unit,
        "cycle": cycle,
        **dict.fromkeys(READING_COLUMNS, 0.5),
        "sensor_1": 2 * cycle,
        "sensor_2": 10 * cycle,
    }


def _write_manifest(path, document):
    content = json.dumps(
        document["payload"], sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()
    document["sha256"] = hashlib.sha256(content).hexdigest()
    path.write_text(json.dumps(document), encoding="utf-8")


@pytest.fixture
def synthetic_bundle(tmp_path):
    # Fit toy data only; never open or retrain the real P06 FD001 model.
    rows = [
        _row(cycle, unit)
        for unit, last in ((1, 5), (2, 7), (3, 9), (4, 11))
        for cycle in range(1, last + 1)
    ]
    split = build_split_manifest(
        rows,
        dataset_partition="FD001/train",
        source_path="synthetic/train.txt",
        source_sha256="a" * 64,
        validation_fraction=0.5,
    )
    config = FeatureConfig(channels=("sensor_2", "sensor_1"), window_cycles=2)
    kwargs = {"manifest": split, "source_sha256": "a" * 64, "config": config}
    fitting = build_fitting_dataset(rows, **kwargs)
    validation = build_validation_dataset(rows, **kwargs)
    fitted = train_decision_tree(fitting, validation)
    paths = save_decision_tree_artifact(
        fitted,
        fitting,
        validation,
        tmp_path,
        fitting_dataset_sha256="b" * 64,
        validation_dataset_sha256="c" * 64,
    )
    return paths["manifest_path"], fitted.model


def _predict(history, manifest):
    return predict_rul(
        history, dataset_partition="synthetic/P07-A1", unit_id=99, manifest_path=manifest
    )


def test_saved_channel_order_and_window_drive_prediction_without_mutating_inputs(synthetic_bundle):
    manifest, model = synthetic_bundle
    history = [_row(cycle) for cycle in (1, 2, 3)]
    original = copy.deepcopy(history)
    # Saved order sensor2 then sensor1, saved window2: only cycles2/3.
    expected = float(model.predict(((30, 25, 5, 10, 6, 5, 1, 2),))[0])
    result = _predict(iter(history), manifest)
    assert result == RawRULPrediction(raw_rul_cycles=expected)
    assert asdict(result) == {"raw_rul_cycles": expected}
    assert [field.name for field in fields(result)] == ["raw_rul_cycles"]
    assert history == original


def test_deployment_bundle_is_temporary_validated_and_never_silently_overrides_local(
    synthetic_bundle, tmp_path
):
    manifest, _ = synthetic_bundle
    model_path = manifest.parent / MODEL_FILENAME
    supplied = {
        "manifest_base64": base64.b64encode(manifest.read_bytes()).decode(),
        "model_base64": base64.b64encode(model_path.read_bytes()).decode(),
    }
    expected = _predict([_row(1)], manifest)
    missing_local = tmp_path / "missing" / "manifest.json"
    with prediction_manifest(missing_local, supplied) as staged:
        assert staged.is_file()
        assert _predict([_row(1)], staged) == expected
    assert not staged.exists()
    with prediction_manifest(manifest, supplied) as active:
        assert active == manifest
    with (
        prediction_manifest(missing_local, None) as active,
        pytest.raises(PredictionArtifactError, match="Cannot read"),
    ):
        _predict([_row(1)], active)
    with (
        pytest.raises(PredictionArtifactError, match="Invalid deployment model configuration"),
        prediction_manifest(missing_local, {"model_base64": "not-valid"}),
    ):
        pass
    with (
        pytest.raises(PredictionArtifactError, match="Invalid deployment model configuration"),
        prediction_manifest(missing_local, {**supplied, "model_base64": "!invalid!"}),
    ):
        pass
    corrupt = {**supplied, "model_base64": base64.b64encode(b"wrong").decode()}
    with (
        prediction_manifest(missing_local, corrupt) as staged,
        pytest.raises(PredictionArtifactError, match="model file hash mismatch"),
    ):
        _predict([_row(1)], staged)


@pytest.mark.parametrize("cycles", [(7,), (1, 3)])
def test_short_observed_histories_and_gaps_follow_saved_feature_contract(synthetic_bundle, cycles):
    manifest, _ = synthetic_bundle
    result = _predict([_row(cycle) for cycle in cycles], manifest)
    assert isinstance(result.raw_rul_cycles, float)


@pytest.mark.parametrize("case", ["empty", "nonfinite", "mixed_engines", "target", "duplicate"])
def test_invalid_history_fails_before_loading_any_artifact(tmp_path, case):
    history = [_row(1), _row(2)]
    if case == "empty":
        history = []
    elif case == "nonfinite":
        history[0]["sensor_1"] = float("nan")
    elif case == "mixed_engines":
        history[0]["unit_id"] = 1
    elif case == "target":
        history[0]["true_rul"] = 50
    else:
        history[1]["cycle"] = 1
    with pytest.raises(PredictionInputError):
        _predict(history, tmp_path / "not-present.json")


def test_missing_artifact_has_a_path_and_actionable_error(tmp_path):
    path = tmp_path / "not-present.json"
    with pytest.raises(
        PredictionArtifactError, match="Cannot read saved Decision Tree bundle"
    ) as error:
        _predict([_row(1)], path)
    assert str(path) in str(error.value)


def test_changed_model_bytes_fail_hash_check(synthetic_bundle):
    manifest, _ = synthetic_bundle
    (manifest.parent / MODEL_FILENAME).write_bytes(b"not the saved estimator")
    with pytest.raises(PredictionArtifactError, match="model file hash mismatch"):
        _predict([_row(1)], manifest)


@pytest.mark.parametrize("case", ["feature_version", "feature_order"])
def test_incompatible_saved_feature_contract_fails_clearly(synthetic_bundle, case):
    manifest, _ = synthetic_bundle
    document = json.loads(manifest.read_text())
    if case == "feature_version":
        document["payload"]["training"]["feature_config"]["version"] = "unsupported"
    else:
        document["payload"]["training"]["feature_names"].reverse()
    _write_manifest(manifest, document)
    with pytest.raises(PredictionArtifactError, match="feature"):
        _predict([_row(1)], manifest)


def test_no_scoring_dataset_or_evaluation_labels_are_needed_for_inference(synthetic_bundle):
    manifest, _ = synthetic_bundle
    before = _predict([_row(1)], manifest)
    document = json.loads(manifest.read_text())
    del document["payload"]["evaluation"]
    _write_manifest(manifest, document)
    assert _predict([_row(1)], manifest) == before


def _install_negative_output_tree(manifest):
    # An artificial negative-output estimator exercises the raw-output contract.
    toy = DecisionTreeRegressor(random_state=42, max_depth=8, min_samples_leaf=5)
    toy.fit([[0.0] * 8] * 5, [-2.5] * 5)
    model_path = manifest.parent / MODEL_FILENAME
    joblib.dump(toy, model_path)
    document = json.loads(manifest.read_text())
    document["payload"]["model"]["sha256"] = hashlib.sha256(model_path.read_bytes()).hexdigest()
    _write_manifest(manifest, document)


def test_negative_raw_output_is_preserved_without_display_clipping(synthetic_bundle):
    manifest, _ = synthetic_bundle
    _install_negative_output_tree(manifest)
    assert _predict([_row(1)], manifest).raw_rul_cycles == -2.5
    presentation = predict_rul_with_context(
        [_row(1)],
        dataset_partition="synthetic/P07-A2",
        unit_id=99,
        manifest_path=manifest,
    )
    assert presentation.raw_rul_cycles == -2.5
    assert presentation.displayed_rul_cycles == 0.0
    assert "display_clipped_at_zero" in presentation.warnings


def test_context_fields_match_actual_saved_model_and_input_window(synthetic_bundle):
    manifest, _ = synthetic_bundle
    history = [_row(cycle) for cycle in (1, 2, 3)]
    result = predict_rul_with_context(
        iter(history),
        dataset_partition="synthetic/P07-A2",
        unit_id=99,
        manifest_path=manifest,
    )
    assert result.raw_rul_cycles == _predict(history, manifest).raw_rul_cycles
    assert result.displayed_rul_cycles == result.raw_rul_cycles
    assert result.model_name == "decision-tree-rul"
    assert result.model_version == "decision-tree-rul-v1"
    assert result.observed_cycle == 3
    assert result.input_window_rows == 2  # Saved config, not default30 or prefix length3.
    assert result.warnings == ()
    assert set(asdict(result)) == {
        "raw_rul_cycles",
        "displayed_rul_cycles",
        "model_name",
        "model_version",
        "observed_cycle",
        "input_window_rows",
        "warnings",
    }
    assert set(asdict(_predict(history, manifest))) == {"raw_rul_cycles"}


@pytest.mark.parametrize("cycles", [(7,), (1, 3, 6)])
def test_context_reports_observed_cycle_actual_row_count_and_quality_warnings(
    synthetic_bundle, cycles
):
    manifest, _ = synthetic_bundle
    result = predict_rul_with_context(
        [_row(cycle) for cycle in cycles],
        dataset_partition="synthetic/P07-A2",
        unit_id=99,
        manifest_path=manifest,
    )
    assert result.observed_cycle == cycles[-1]
    assert result.input_window_rows == 1  # Only final cycle falls inside saved2cycle window.
    assert result.warnings == ("cycle_gaps", "short_window")


def _replace_saved_estimator(manifest, estimator):
    model_path = manifest.parent / MODEL_FILENAME
    joblib.dump(estimator, model_path)
    document = json.loads(manifest.read_text())
    document["payload"]["model"]["sha256"] = hashlib.sha256(model_path.read_bytes()).hexdigest()
    _write_manifest(manifest, document)


def test_missing_model_binary_fails_with_manifest_and_model_paths(synthetic_bundle):
    manifest, _ = synthetic_bundle
    model_path = manifest.parent / MODEL_FILENAME
    model_path.unlink()
    with pytest.raises(
        PredictionArtifactError, match="Cannot read saved Decision Tree bundle"
    ) as error:
        _predict([_row(1)], manifest)
    assert str(manifest) in str(error.value)
    assert str(model_path) in str(error.value)


@pytest.mark.parametrize("kind", ["scaler", "pipeline"])
def test_scaler_or_preprocessing_pipeline_cannot_replace_the_plain_P06_tree(synthetic_bundle, kind):
    manifest, _ = synthetic_bundle
    X = [[0.0] * 8, [1.0] * 8]
    if kind == "scaler":
        replacement = StandardScaler().fit(X)
    else:
        replacement = Pipeline(
            [
                ("scale", StandardScaler()),
                ("tree", DecisionTreeRegressor(random_state=42)),
            ]
        ).fit(X, [2, 4])
    _replace_saved_estimator(manifest, replacement)
    with pytest.raises(PredictionArtifactError, match="not a DecisionTreeRegressor"):
        _predict([_row(1)], manifest)


def test_estimator_feature_count_must_match_the_saved_schema(synthetic_bundle):
    manifest, _ = synthetic_bundle
    wrong_width = DecisionTreeRegressor(random_state=42, max_depth=8, min_samples_leaf=5)
    wrong_width.fit([[0.0] * 4] * 5, [3] * 5)  # Saved config requires8 features.
    _replace_saved_estimator(manifest, wrong_width)
    with pytest.raises(PredictionArtifactError, match="dimensions do not match the feature schema"):
        _predict([_row(1)], manifest)


def test_unfitted_estimator_is_rejected_before_predicting(synthetic_bundle):
    manifest, _ = synthetic_bundle
    _replace_saved_estimator(manifest, DecisionTreeRegressor(random_state=42))
    with pytest.raises(
        PredictionArtifactError, match="Cannot load a compatible saved Decision Tree"
    ):
        _predict([_row(1)], manifest)


@pytest.mark.parametrize(
    "case,message",
    [
        ("artifact_schema", "Unsupported Decision Tree artifact schema"),
        ("model_version", "Unsupported Decision Tree model name/version"),
        ("runtime_version", "scikit-learn version does not match"),
        ("parameters", "parameters differ from the manifest"),
    ],
)
def test_rehashed_incompatible_artifact_contract_fails_clearly(synthetic_bundle, case, message):
    manifest, _ = synthetic_bundle
    document = json.loads(manifest.read_text())
    payload = document["payload"]
    if case == "artifact_schema":
        payload["schema_version"] = "unsupported"
    elif case == "model_version":
        payload["model"]["version"] = "unsupported"
    elif case == "runtime_version":
        payload["model"]["scikit_learn_version"] = "incompatible-runtime"
    else:
        payload["training"]["parameters"]["max_depth"] = 9
    _write_manifest(manifest, document)
    with pytest.raises(PredictionArtifactError, match=message):
        _predict([_row(1)], manifest)


def test_manifest_checksum_detects_edited_configuration(synthetic_bundle):
    manifest, _ = synthetic_bundle
    document = json.loads(manifest.read_text())
    document["payload"]["training"]["feature_config"]["window_cycles"] = 30
    manifest.write_text(json.dumps(document), encoding="utf-8")  # Deliberately retain old checksum.
    with pytest.raises(PredictionArtifactError, match="manifest content hash mismatch"):
        _predict([_row(1)], manifest)


def test_cache_reuses_verified_bytes_but_detects_changes_and_missing_files(synthetic_bundle, monkeypatch):
    from fleetpulse.services import predictor

    manifest, _ = synthetic_bundle
    model_path = manifest.parent / MODEL_FILENAME
    original_load = predictor.joblib.load
    calls = []

    def counted_load(*args, **kwargs):
        calls.append(1)
        return original_load(*args, **kwargs)

    predictor._deserialize_tree.cache_clear()
    monkeypatch.setattr(predictor.joblib, "load", counted_load)
    try:
        first = _predict([_row(1)], manifest)
        assert _predict([_row(1)], manifest) == first
        assert len(calls) == 1
        original_manifest = manifest.read_text(encoding="utf-8")
        changed = json.loads(original_manifest)
        changed["payload"]["training"]["parameters"]["max_depth"] = 9
        _write_manifest(manifest, changed)
        with pytest.raises(PredictionArtifactError, match="parameters differ from the manifest"):
            _predict([_row(1)], manifest)
        manifest.write_text(original_manifest, encoding="utf-8")
        original_bytes = model_path.read_bytes()
        model_path.write_bytes(original_bytes + b"corrupt")
        with pytest.raises(PredictionArtifactError, match="model file hash mismatch"):
            _predict([_row(1)], manifest)
        model_path.unlink()
        with pytest.raises(PredictionArtifactError, match="Cannot read"):
            _predict([_row(1)], manifest)
        model_path.write_bytes(original_bytes)
        _install_negative_output_tree(manifest)
        assert _predict([_row(1)], manifest).raw_rul_cycles == -2.5
        assert len(calls) == 2
    finally:
        predictor._deserialize_tree.cache_clear()


def test_invalid_model_serialization_fails_even_when_its_byte_hash_matches(synthetic_bundle):
    manifest, _ = synthetic_bundle
    model_path = manifest.parent / MODEL_FILENAME
    model_path.write_bytes(b"not a serialized model")
    document = json.loads(manifest.read_text())
    document["payload"]["model"]["sha256"] = hashlib.sha256(model_path.read_bytes()).hexdigest()
    _write_manifest(manifest, document)
    with pytest.raises(
        PredictionArtifactError, match="Cannot load a compatible saved Decision Tree"
    ):
        _predict([_row(1)], manifest)


def test_serialized_evaluation_record_keeps_raw_negative_value_separate_from_display(
    synthetic_bundle, tmp_path
):
    manifest, _ = synthetic_bundle
    _install_negative_output_tree(manifest)
    history = [_row(1)]
    raw = _predict(history, manifest)
    context = predict_rul_with_context(
        history,
        dataset_partition="synthetic/P07-A3",
        unit_id=99,
        manifest_path=manifest,
    )
    record = {
        "provenance": "synthetic temporary saved-tree test",
        "units": "cycles",
        "evaluation_prediction": asdict(raw),
        "display_only": {
            "displayed_rul_cycles": context.displayed_rul_cycles,
            "policy": "max(0, raw_rul_cycles)",
        },
    }
    path = tmp_path / "synthetic_raw_prediction.json"
    path.write_text(json.dumps(record, allow_nan=False), encoding="utf-8")
    restored = json.loads(path.read_text())
    assert restored["evaluation_prediction"] == {"raw_rul_cycles": -2.5}
    assert restored["display_only"]["displayed_rul_cycles"] == 0.0
    assert raw.raw_rul_cycles == context.raw_rul_cycles == -2.5
