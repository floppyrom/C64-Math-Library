# Historical signed-wide kernels: matched public-call workload baselines

The builder must not declare itself a full V1-V5 performance replacement
until the fastest historical, OptiSearch, and modern source-linked kernels
have been compared on the **same public ABI and input corpus**, including
busiest-frame costs. Historical profile benchmark means currently have
different corpus provenance from the builder's portable routines, so
standalone means alone are not a valid basis for claiming any speedup.

## First step: benchmark all five real resident historical binaries

```sh
for p in v1_balanced v2_pareto_fast v3_reu_512k v4_reu_16m v5_hybrid_lowzp; do
  python3 tools/export_legacy_signed_frame_trace.py --profile "$p" --frames 24 \
    --out "build/${p}_signed_wide.csv"
  python3 tools/frame_cycle_budget.py --baseline "build/${p}_signed_wide.csv" \
    --frame-count 24 --out "build/${p}_signed_wide.frame.json"
done
```

The producer loads each *actual released resident PRG* and any corresponding
REU image, runs MATH_INIT, then calls all eight signed-wide public API
operations on an identical deterministic synthetic sequence:

- SMUL32, SMUL32_SHR16
- SDIV32_16, SMOD32_16
- SDIV32_32, SMOD32_32
- SDIV24, SMOD24

For every call, the emulator checks the exact signed mathematical output,
carry, stack balance, and public input preservation; logs every observed
entry-through-RTS CPU-model cycle count; and records the public entry, full
source PRG SHA-256, math API SHA-256, REU SHA-256 where applicable, physical
load address, initialized runtime provenance, input hash, and operation.
The deterministic 24-frame workload includes 24-call/8-call bursts among
ordinary 3-call frames. A/X/Y, carry-in and decimal-mode inputs are explicitly
set for every call, independent of MATH_INIT's returned registers.

The same `tools/frame_cycle_budget.py` scorer reports per-operation average
and worst call, p95, worst arithmetic frame, and nominal PAL budget overrun.
Results may differ across released profiles because their physical layouts,
REU assets and initialization differ. The resulting evidence is for
**historical donor triage**; no historical code is altered or relinked and no
profile removal is authorized by this benchmark.

## Next qualification barrier

Recover the fastest published V1–V5 and OptiSearch signed 24/32-bit
arithmetic sources with their complete data tables, writable-code lifetime,
ZP/stack page contract, INIT needs, and any shared unsigned producer. Create
*independently linkable* alternatives for the exact `MATH_*` public ABI.
Then compare the donor and modern alternatives at **identical code and I/O
placements** using the matched call sequence and source manifests, with
native VICE r46284 correctness checks and measured peak-frame budget
analysis. Preserve compact, fastest, and low-ZP Pareto options rather than
switching every configuration to the historical donor.

This research workflow uses the Mini6502 cycle model, not VICE elapsed
time, does not include frame IRQ/SID/VIC/REU-transfer cost, and does not
prove a real game's peak frame consumption.


## Initial observed 24-frame historical frontier (18 October 2026)

The GitHub CI producer passed on the same **150 public calls**, with
**identical full input hashes and call ordering** in all five profile
executions. Every profile's resident PRG starts at `$1000`, with public
math I/O at `$C000`. The source evidence (including exact PRG/REU digests)
is retained in GitHub Actions run `39134772130`, artifact
`historical-signed-wide-frame-baselines`.

| Historical profile | Mean math cycles / frame | P95 math cycles / frame | Peak math cycles / frame | Frames above 19,656 math-only cycles |
|---|---:|---:|---:|---:|
| V1 Balanced | 5,714.750 | 21,324 | 22,916 | 3 |
| V2 Pareto Fast | 3,919.208 | 14,897 | 15,969 | 0 |
| V3 REU 512K | 3,889.542 | 14,816 | **15,907** | 0 |
| V4 REU 16M | 3,889.542 | 14,816 | **15,907** | 0 |
| V5 Hybrid Low-ZP | 4,367.208 | 16,451 | 17,562 | 0 |

V3/V4 save **43,805 total public-call cycles** versus V1 on these
matched inputs, or **7,009 cycles** in the busiest arithmetic frame.
The biggest operation-level sources of this difference (V1 → V3)
are `SDIV32_16` (12,313 cycles), `SMOD24` (11,305),
`SMOD32_32` (9,639), and `SMOD32_16` (8,137).
Therefore the next *donor selection* should prioritize the historical
32/16 signed quotient/magnitude path and the shared signed modulo
substrates, not attempt to optimize a peripheral public wrapper first.

These **are not** unconditional timing claims for every game:
the deterministic stress mix deliberately includes high-quotient and
zero-divisor cases; full program cycles include only mathematical calls
plus the scorer's 6-cycle JSR per call. The 19,656 comparison is a PAL
reference frame, not an available math-only budget after graphics and
music. The old fastest-profile means published on other corpora cannot
replace this matched evidence, and V3/V4's identical arithmetic timing
does not imply identical runtime REU transport costs. Code size,
shared tables, zero-page pressure, and initialization must still be
accounted for when transplanting these donors.
