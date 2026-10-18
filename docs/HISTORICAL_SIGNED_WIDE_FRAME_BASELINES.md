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
