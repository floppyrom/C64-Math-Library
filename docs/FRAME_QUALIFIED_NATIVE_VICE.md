# Native VICE verification of exact frame-qualified installer binaries

The operation-first exporter creates a **source- and memory-pinned** project
configuration from a measured synthetic 150-call/24-frame multi-operation
workload. The generated PRG must then run correctly in a real emulator,
rather than only passing the Mini6502 instruction model.

This test applies the existing three independent x64sc public ABI oracles
to **the exact byte-identical PRG produced by the normal JSON builder CLI**.

- Two independently qualified code/I/O placements: $8000/$C000 and
  $7123/$C040, with corresponding pinned ZP and scratch origins.
- Two Pareto envelopes per placement: a 31-byte-ZP fast peak-frame choice
  and a 0-byte-ZP compact/RAM-saving choice.
- Three independently checked public exports for each binary:
  unsigned 32×32→64, signed 32×32→64 and ISQRT16.
- 96 edge/random public calls per export and choice (1,152 across four
  project PRGs), verifying complete results, untouched public operands,
  carry and native stack/public result ABI.
- The exact generated PRG SHA-256 is compared to the measurement provenance
  **before** any native call; the source list and resource bounds must match
  the qualification and the selected code/I/O/ZP/scratch addresses.

```sh
python3 -m unittest discover -s tools -p 'test_native_frame_qualified_config.py' -v
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 tools/native_frame_qualified_config.py
```

The dedicated CI builds the revision-pinned headless VICE x64sc and executes
all four images. This checks that an **ordinary exported project installer
config** recreates source-qualified native-correct code at the promised
layout, including both full64 multiply and integer square root.

**Limits:** the 1,152 native calls use independent correctness corpora, not
the 150-call synthetic workload's exact video-frame schedule. This does
not measure physical PAL/NTSC timing, badlines, sprite DMA, IRQ/SID, REU
hardware, or prove a game's busiest frame fits. All five historical
V1–V5 binaries and REU/Turbo/QS16 compatibility packages remain protected.
