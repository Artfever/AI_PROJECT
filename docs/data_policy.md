# FD001 raw and demo data

## Get the raw files

The app currently reads the original simulated NASA C-MAPSS FD001 training history from `data/raw/train_FD001.txt` in this clone. The raw files are not included in Git. To set up a fresh checkout:

1. Download **Turbofan Engine Degradation Simulation** from the [NASA PCoE dataset repository](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/).
2. Open the downloaded archive, then its nested `CMAPSSData.zip`. Extract the original `train_FD001.txt` into this clone's `data/raw/` directory. Preserve its bytes; do not edit the source file.
3. Compare the file's SHA-256 with [the provenance record](fd001_provenance.md). If an existing file differs, keep it and investigate before replacing it.
4. Start or refresh the app. Home and Engine Explorer will show counts and a preview when the file loads and passes the current quality checks.

The source archive also includes `test_FD001.txt` and `RUL_FD001.txt`. They may be stored alongside the training file for later work, but the current UI does not load them. The RUL file contains official test answers and must not be used for training or tuning. The three raw files and their hashes are documented separately in the provenance record.

If the app reports a missing, unreadable, malformed, or invalid file, check the location, read permissions, file format and hash. A ZIP file or a renamed file is not a substitute for the extracted original. The app does not fabricate counts when loading fails.

## Demo and test data

`data/demo/` is a reserved directory; only its `.gitkeep` marker is tracked. **No packaged demo dataset is currently supplied**, and the app does not fall back to one. Other contents of `data/demo/`, like contents of `data/raw/`, are ignored by Git under the current policy.

The small synthetic fixture in `tests/fixtures/` is explicitly artificial and exists only for tests. It is not NASA data, a model-training set, or a packaged app demo. Any future demo package requires an explicit reviewed decision on source, redistribution rights, provenance, contents, and how it is labeled. Keep raw data, synthetic test fixtures, future demo data, and model or evaluation artifacts distinguishable.
