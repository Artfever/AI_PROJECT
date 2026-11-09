# Hand-calculated RUL example

This example uses one **synthetic** engine whose failure/end-of-life cycle is
12. It is a small arithmetic check, not NASA C-MAPSS data and not a measured
FD001 result.

For an observation at cycle `t`, the remaining useful life is
`end_cycle - t`. Here `end_cycle = 12`, so:

| Observed cycle | Calculation | RUL (cycles) |
| ---: | ---: | ---: |
| 3 | 12 - 3 | 9 |
| 8 | 12 - 8 | 4 |
| 12 | 12 - 12 | 0 |

All three rows belong to the same engine. The label uses the known synthetic
end cycle only; it does not add future sensor readings to the observed input.
RUL is measured in cycles. This hand check does not establish any real engine
lifetime or model performance.
