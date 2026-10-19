# Mixed SEEK8/SEEK16 source-linked frame-cycle acceptance research

All eight public SEEK calls have independently authenticated source-cycle speed
measurements. This additional gate records the **actual 6510 CPU instruction
cycles of each call** from one final linked binary while both eight-slot DDA
families interleave on representative synthetic frames.

Usage:

```sh
python3 tools/export_seek_frame_trace.py --frames 24 --code-base 0x8000 --io-base 0xc000 --out build/seek_8000.csv
python3 tools/frame_cycle_budget.py --baseline build/seek_8000.csv --frame-count 24
python3 tools/export_seek_frame_trace.py --frames 24 --code-base 0x7123 --io-base 0xc100 --out build/seek_7123.csv
python3 tools/frame_cycle_budget.py --baseline build/seek_7123.csv --frame-count 24
```

The trace alternates 16 concurrent object step calls per frame between two
shared DDA producers (SEEK8 and SEEK16), with eight position slots per
family, zero-length and axis/diagonal targets, and each of STEP,
STEP_INT and STEP1. Every ninth frame reinitializes all 16 movement
targets, exposing the normally infrequent INIT burst in a busy frame.
The 24-frame workload is **synthetic**, not a measured user's application.

Each row carries a deterministic canonical input/state/CPU-register digest,
complete entry-through-RTS cycle count, linked variant, clock basis,
placement and frame/call ordinal. It validates X, SP, carry-on-arrival,
untouched public input bytes, other-slot state isolation and immutable
source, then passes the trace to the existing frame-cycle scorer. The
companion JSON preserves the emitted source-link manifest and CSV digest.

Do not compare the two relocation traces as a paired kernel A/B test:
placement differs by design, and the per-frame scorer properly requires
identical placement for paired comparisons. No speedup is claimed; there is
just one qualified original source per API. This is a step toward a
mixed-frame parity gate; **not** an actual PAL hardware timing
measurement. VIC-II bus steals, display badlines, sprite DMA, IRQ/SID,
REU, Turbo16/Turbo32 and legacy V4 QS16 remain separate acceptance
criteria before fixed V1–V5 profiles can be deprecated.
