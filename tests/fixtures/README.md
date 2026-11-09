# Synthetic engine history for tests only

`synthetic_engine_history.csv` contains three made-up readings for one invented
engine, unit `900001`. It is **not NASA C-MAPSS data** and must not be used for
training, model evaluation, demo claims, or app examples.

The CSV has a header with the planned raw-record fields: `unit_id`, `cycle`,
three settings, and 21 sensors. Settings `9001`-`9003` and five-digit sensor
values were chosen to be visibly artificial. Each sensor increases by exactly
one per cycle so future tests can calculate expected values by hand. There is
no RUL or failure label column. This is a test convenience, not a claim that
the official FD001 files have CSV headers or these values.

Read it from `tests/fixtures/` in tests. The local data and artifact folders
remain reserved for separately sourced real files and generated outputs.
