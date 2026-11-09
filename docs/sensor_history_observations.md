# FD001 sensor history observations

The Engine Explorer plots the selected training engine's readings by cycle. It
plots each chosen sensor separately so channels with different numeric ranges
remain readable. Defaults show `sensor_1`, `sensor_2`, and `sensor_9`; all 21
sensors are selectable.

## Reproduce

Place the original training history at `data/raw/train_FD001.txt`, then run:

```powershell
streamlit run app/Home.py
```

Open **Engine Explorer**, select a training engine, and inspect its sensor
histories. No test history or RUL answer file is loaded on this page.

## Observed example

Verified with the local training file whose SHA-256 is recorded in
`artifacts/data_quality.json`, for training engine 1 (192 observed cycles,
cycles 1–192):

- `sensor_1` was exactly constant at 518.67 over these observed cycles.
- `sensor_2` varied from 641.71 to 644.21 and had 130 direction reversals
  between successive cycle-to-cycle changes.
- `sensor_9` varied from 9033.22 to 9061.21 and had 128 such reversals.

These ranges and reversals describe the observed series. A jagged or changing
curve does not establish a physical cause, fault, or degradation state. Each
plot has its own vertical scale, so its shape can be inspected without treating
the different sensors' numeric magnitudes as comparable.

## Automated verification

`tests/test_engine_selection.py` checks the three default chart channels, the
flat and varying descriptions, a hand-computed reversal count, sorted cycles,
and isolation when switching between two deliberately synthetic engine IDs.
The synthetic fixture is not NASA data.
