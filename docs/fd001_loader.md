# FD001 loader contract

`fleetpulse.data.loader` reads the original, whitespace-separated files described in [the provenance record](fd001_provenance.md). It does not download files, alter them, train models, or load data when imported.

```python
from fleetpulse import PROJECT_ROOT
from fleetpulse.data.loader import load_engine_history

records = load_engine_history(PROJECT_ROOT / "data" / "raw" / "train_FD001.txt")
```

`load_engine_history(path)` returns a list of dictionaries in file order. Each dictionary contains `unit_id` and `cycle` as integers, followed by `setting_1` through `setting_3` and `sensor_1` through `sensor_21` as floats. This is the normalized schema used by `validate_engine_history` and `summarize_engine_history`. The loader rejects a nonempty history line with a different field count or invalid number, reporting its line number. It leaves semantic integrity checks to the quality module. Train and test histories must be kept as separate collections: the same engine number can occur in both.

`load_rul_values(path)` is a separate, explicit reader for a one-column RUL answer file; it returns integer values in file order and never joins them to history records. The history reader does not access this file. The official test answers are not a tuning pool; the automated loader tests use invented answer values only.

The local FD001 histories were checked on 9 November 2026: the training file produced 20,631 rows for 100 distinct engine IDs and the test-history file produced 13,096 rows for 100 distinct engine IDs. Both passed the current quality module with zero errors and zero warnings. These are observed counts, not model scores. The P02-S2 summary did not parse or use real test-answer values. During a later archive-inspection command, output may have exposed the answer file's first lines; see [the summary disclosure](fd001_summary.md). No answer values were used for training, tuning, or reported metrics. The files remain ignored by Git; each checkout needs its own local files.

Both readers raise `FD001LoadError` (a `ValueError` subclass) for missing or
unreadable files, invalid UTF-8, empty inputs, malformed columns, or invalid
numbers. Messages identify the path and, for malformed rows, the line number;
access/encoding failures retain the original exception as `__cause__`.
Missing-file errors point to the provenance instructions. Existing callers
catching `ValueError` still work. Semantic checks remain in the quality module.

The answer reader optionally accepts `expected_engine_count`:

```python
from fleetpulse.data.loader import load_rul_values

# Only when explicitly checking an answer file; never on the prediction path.
test = load_engine_history(PROJECT_ROOT / "data" / "raw" / "test_FD001.txt")
engine_count = len({record["unit_id"] for record in test})
answers = load_rul_values(
    PROJECT_ROOT / "data" / "raw" / "RUL_FD001.txt",
    expected_engine_count=engine_count,
)
```

Use the number of distinct test engines, not sensor rows or training engines.
An answer-count mismatch raises `FD001LoadError` with observed and expected
counts. The optional count must be a positive integer. Count agreement alone
does not prove engine/answer alignment; no answer-to-engine mapping is inferred.
Tests use synthetic answers. Early real-file verification checks only shape,
count and hashes, without printing or using official answer values. Scientific
evaluation remains after the final-model freeze. UI integration is P02-T1.
