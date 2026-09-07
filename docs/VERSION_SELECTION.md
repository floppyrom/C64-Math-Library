# Version selection — 2026-09-07

| Profile / builder | Best use | Key trade-off |
|---|---|---|
| V1 Balanced | stock C64, tight ZP **and** RAM | 31-byte normal ZP; smallest integration claim; slower resident paths |
| V2 Pareto-Fast | stock C64, speed first | faster general kernels; 221-byte ZP commitment and mandatory `MATH_INIT` |
| V3 REU 512K | standard 512 KiB REU | REU acceleration + Turbo ownership discipline |
| V4 REU 16M | VICE / modern 16 MiB REU | fastest feature set; large REU requirement |
| V5 Hybrid Low-ZP | fixed 31-ZP stock-C64 preset | faster V2 division/modulo/trig with 4608-byte private RAM region |
| **Custom Pareto Builder** | games/demos with a known ZP/RAM budget | generates the fastest certified V1/V2 combination fitting the requested resources |

## Recommended choice

For a new stock-C64 integration, start with the **Custom Pareto Builder**:

```sh
python3 tools/pareto_wizard.py
```

or:

```sh
python3 tools/build_pareto.py --zp-budget N
```

V1, V2 and V5 remain useful as simple, reproducible presets and validation anchors. The builder naturally reproduces them at resource endpoints: 31 ZP + zero extra RAM gives byte-identical V1; 31 ZP + `--init-policy optional` gives byte-identical V5; 221 ZP selects complete V2 when its resident budget fits.

## Default equal-weight Pareto breakpoints

| ZP | Default result | Exact extra RAM vs V1 |
|---:|---|---:|
| 31 | V5 zero-ZP imports + initialized UMUL32 | 4976 B |
| 36 | above + UMUL8/16 | 5698 B |
| 60 | above + UMUL24 | 6086 B |
| 147 | V5 imports + initialized UMUL32 + native SMUL16 | 5162 B |
| 176 | all certified hybrid packs | 6272 B |
| 221 | complete V2 | 208 B resident increase |

The optimizer maximizes weighted cycle savings, so RAM usage need not increase monotonically with ZP. Workload weights can change the selected pack at the same resource budget.

`MATH_INIT` is mandatory on V2–V4 and on generated Pareto profiles whose manifest says `math_init_required: true`. It remains optional on V1/V5 and on generated profiles selected with `--init-policy optional`.

All fixed resident profiles and all generated Pareto builds expose the same 45-entry stable API. V3/V4 additionally expose Turbo16/Turbo32 lifecycle entries; V4 also exposes QS16.
