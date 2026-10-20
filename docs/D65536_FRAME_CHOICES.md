# D=$00010000 opt-in frame-objective source selection

The operation-first **frame objective** can now accept a new, explicitly
registered source-replay basis for the opt-in D65536 fast path without
retiring the older 16-way complete project benchmark.

`tools/mixed_seven_d65536_frame.py` defines exactly **nine fully pinned
seven-operation images**: the original complete zero-ZP baseline, two
stock-V2 compact/FAST31 references, and six combinations of independent
signed and unsigned D65536 selections at low-ZP and FAST31 multiply
budgets. All 150 identical calls across 24 synthetic frames are executed
through their full public Q/R/C or MUL/ISQRT16 ABI at **both** original
source-qualified memory placements. Replays record full PRG/source SHA,
caller inputs, measured modeled entry-through-RTS cycles, RAM, ZP and
per-operation call distributions. This is not an estimate from
per-operation averages.

```sh
python3 tools/mixed_seven_d65536_frame.py \
  --out build/d65536-9-frame-report.json
python3 tools/frame_evidence_replay.py \
  --report build/d65536-9-frame-report.json
```

The regression suite additionally invokes the **actual math_builder command-line installer** with the measured nine-plan JSON, RAM/ZP budgets, and frame objective, then checks its published PRG's SHA-256, source pins, and evidence against an independently qualified source-linked build. The unit test is not a substitute for pinned native VICE timing.

The normal `math_builder.py --objective frame --build` accepts this
report via `--frame-report` with an explicit all-seven API selection,
memory map, maximum RAM and ZP. It re-executes all nine linked sources at
both relocations and refuses altered peak cycles, SHA digests, source
plans, public input histories or unqualified physical placements. It
rebuilds the chosen source-pinned installer PRG from scratch, checks the
physical binary checksum and memory usage, and publishes source
evidence only after the complete comparison passes.

Importantly, **0-ZP compact still remains available** when ZP is
constrained. On a 12-ZP budget, the compact-multiply table-square
configurations retain unsigned/signed V2 or D65536 alternatives. On a
31-ZP budget, FAST31 plans can compete based on actual linked workload
math-peak, not mean single-operation timing. A RAM-tight design may
keep original V2 despite the D65536 hotspot saving.

## Workload-specific result (two memory maps)

Source replay identified a stronger Pareto combination than enabling both
signed and unsigned D65536. With a 31-byte zero-page budget, select
**FAST31 + original unsigned V2 + signed D65536** for this exact trace:

| Fully linked seven-API source plan | Worst modeled frame | Worst mapped RAM | ZP |
|---|---:|---:|---:|
| FAST31 and original signed/unsigned V2 | 16,172 cycles | 8,992 B | 31 B |
| FAST31 and both D65536 sources | 13,897 cycles | 9,213 B | 31 B |
| **FAST31, unsigned V2, signed D65536** | **13,849 cycles** | **8,992 B** | **31 B** |

This signed-only configuration saves **2,323 modeled cycles** over stock
while retaining the same measured maximum RAM/ZP. Replacing the unsigned
source as well wastes RAM and slightly *increases* the worst modeled frame,
so the original unsigned V2 source must remain on the Pareto frontier.

These are exact public-call *CPU-model* results, not measured native
PAL/VIC clock slots for the signed-only mixed plan. Its own native
24-frame timing must be tested before claiming it fits a PAL frame.

This nine-choice report is **synthetic CPU-model arithmetic evidence**
and is deliberately separate from the pinned native PAL/VIC
measurement in [PR #357](https://github.com/floppyrom/C64-Math-Library/pull/357).
The latter confirms worst isolated visible PAL burst **19,883 →
17,618 PHI2 slots** for the research-linked D65536 candidate at
**+256 linked RAM bytes**, no extra ZP. The new optional *ordinary
installer* source registration is qualified separately in
[PR #358](https://github.com/floppyrom/C64-Math-Library/pull/358).

None of these prove a continuous 50 Hz demonstration with IRQ/SID,
sprite/badline contention through actual frame boundaries, or REU
DMA. A real application needs a separately re-recorded workload and
native busy-frame latency gate before profile retirement.
