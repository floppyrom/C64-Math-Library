# Necessary PAL arithmetic-frame headroom preflight

The source-replay-verified mixed-frame installer chooses measured complete
linked-image math plans. Its `peak_frame_math_cycles` metric is **not** a
physical 50 Hz PAL timing test. Before treating one of these synthetic frames
as a deadline, compare its measured arithmetic-only peak against the nominal
PAL frame capacity: **312 raster lines × 63 clock slots = 19,656 slots**.

`tools/pal_math_frame_headroom.py` reexecutes the original deterministic
benchmark producer and independently validates the same sources, complete
public-ABI inputs, relocation maps and measured peaks before emitting a
conservative resource-aware comparison. Only previously replay-registered
producers are accepted. It never marks a choice physically PAL-certified.

```sh
python3 tools/mixed_seven_cross_pareto.py --out build/seven-cross/frames.json
python3 tools/pal_math_frame_headroom.py \
  --in-report build/seven-cross/frames.json \
  --ram-budget 16000 --zp-budget 31 \
  --out build/seven-cross/pal-model-headroom.json
# An optional hypothetical nonmath reserve, NOT a measured VIC/SID cost:
python3 tools/pal_math_frame_headroom.py \
  --in-report build/seven-cross/frames.json \
  --reserve-nonmath-cycles 3500 --require-model-headroom
```

On the current fixed 150-call/24-synthetic-frame seven-API corpus, 15 of the
16 complete source-pinned combinations exceed the **entire** nominal PAL
frame capacity in their worst measured math-only frame. Only the 31-ZP
fast-MUL/table-root/V2-DIV/MOD combination is under the nominal arithmetic
bound: 16,172 cycles, leaving **3,484 nominal slots** before anything else.
Even that alternative is **not certified to fit** a real 50 Hz frame. With a
hypothetical 3,500-cycle nonmath reserve all sixteen are over the budget.
Zero-ZP combinations all exceed the nominal budget on this specific workload.

A negative headroom is evidence of model overrun, not a measured hardware
failure; a positive headroom is **not evidence of hardware feasibility**.
The comparison does **not** account for VIC-II BA/AEC bus steals, badlines,
interrupts, SID updates, code executed outside math, REU DMA, initialisation,
frame jitter, undocumented-opcode timing deviations, or the application's
actual call history. The synthetic corpus is not representative of every
C64 game or demo. Do not extrapolate from this workload to all 56 APIs.

For actual PAL closure the follow-up must capture native x64sc/hardware
per-frame beginning/end raster timing with realistic IRQ, screen fetches,
music, other application code, and (when selected) REU DMA. Preserve all
V1–V5 and REU compatibility images until that independent acceptance gate
passes. The `--max-peak-math-cycles` frame-selection parameter already
supports strict arithmetic-only budget caps; it must not be presented as
hardware certification either.
