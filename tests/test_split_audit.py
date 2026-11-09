"""Hand-authored manifests and deliberate corruption, independent of the builder."""

from copy import deepcopy

import pytest

from fleetpulse.data.quality import READING_COLUMNS
from fleetpulse.data.split_audit import audit_split_manifest


def _case():
    rows = [
        {"unit_id": engine, "cycle": cycle, **dict.fromkeys(READING_COLUMNS, 0.5)}
        for engine, cycles in [(1, [1, 3, 7]), (2, [2, 4, 9])]
        for cycle in cycles
    ]
    identity = {"dataset_partition": "FD001/train", "unit_id": 2}
    manifest = {
        "schema_version": 1,
        "source": {
            "dataset_partition": "FD001/train",
            "sha256": "a" * 64,
            "row_count": 6,
            "engine_count": 2,
        },
        "split": {"seed": 42, "validation_fraction": 0.5, "algorithm": "python-random-sample-v1"},
        "cutoff_policy": {
            "seed": 42,
            "minimum_history_rows": 2,
            "exclude_terminal": True,
            "algorithm": "python-random-choice-observed-v1",
            "selection": "uniform_over_eligible_observed_cycles",
        },
        "fitting_engines": [{**identity, "unit_id": 1}],
        "validation_prefixes": [
            {
                **identity,
                "cutoff_cycle": 4,
                "prefix_row_count": 2,
                "eligible_cutoff_range": {"first": 4, "last": 4},
                "eligible_cutoff_count": 1,
                "full_lifetime": 9,
                "target_rul": 5,
            }
        ],
    }
    return manifest, rows


def test_valid_gapped_prefix_is_checked_without_mutation():
    manifest, rows = _case()
    before = deepcopy((manifest, rows))
    audit_split_manifest(manifest, iter(rows), source_sha256="a" * 64)
    assert (manifest, rows) == before


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("cutoff_cycle", 9, "nonterminal"),
        ("cutoff_cycle", 3, "nonterminal"),
        ("cutoff_cycle", 2, "nonterminal"),
        ("prefix_row_count", 4, "prefix row count"),
        ("eligible_cutoff_range", {"first": 2, "last": 9}, "cutoff range"),
        ("eligible_cutoff_count", 99, "cutoff count"),
        ("target_rul", 0, "target RUL"),
        ("full_lifetime", 7, "lifetime"),
        ("dataset_partition", "FD001/test", "partition"),
        ("unit_id", 999, "unknown"),
    ],
)
def test_corrupt_prefix_metadata_is_rejected(field, value, message):
    manifest, rows = _case()
    manifest["validation_prefixes"][0][field] = value
    with pytest.raises(ValueError, match=message):
        audit_split_manifest(manifest, rows, source_sha256="a" * 64)


def test_overlap_duplicate_missing_engine_and_source_hash_are_rejected():
    for case, message in [
        ("overlap", "overlap"),
        ("duplicate", "duplicate"),
        ("missing", "omit"),
        ("hash", "SHA-256"),
    ]:
        manifest, rows = _case()
        if case == "overlap":
            manifest["fitting_engines"].append({"dataset_partition": "FD001/train", "unit_id": 2})
        elif case == "duplicate":
            manifest["validation_prefixes"].append(deepcopy(manifest["validation_prefixes"][0]))
        elif case == "missing":
            rows.append({**rows[-1], "unit_id": 3})
            manifest["source"].update(row_count=7, engine_count=3)
        else:
            manifest["source"]["sha256"] = "b" * 64
        with pytest.raises(ValueError, match=message):
            audit_split_manifest(manifest, rows, source_sha256="a" * 64)


@pytest.mark.parametrize("section", ["split", "cutoff_policy"])
def test_missing_seed_is_rejected(section):
    manifest, rows = _case()
    manifest[section].pop("seed")
    with pytest.raises(ValueError, match="seed"):
        audit_split_manifest(manifest, rows, source_sha256="a" * 64)


@pytest.mark.parametrize("minimum", [0, True, 10])
def test_bad_or_infeasible_minimum_history_is_rejected(minimum):
    manifest, rows = _case()
    manifest["cutoff_policy"]["minimum_history_rows"] = minimum
    with pytest.raises(ValueError, match="minimum history|no eligible"):
        audit_split_manifest(manifest, rows, source_sha256="a" * 64)


def test_terminal_inclusion_policy_is_rejected():
    manifest, rows = _case()
    manifest["cutoff_policy"]["exclude_terminal"] = False
    with pytest.raises(ValueError, match="terminal cycles must be excluded"):
        audit_split_manifest(manifest, rows, source_sha256="a" * 64)
