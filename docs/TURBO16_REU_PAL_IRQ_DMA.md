# Native PAL Turbo16 REU DMA / VIC-II / raster IRQ / SID bounded probe

This research gate extends the merged independent native REU source-package
(PR #383) and the opt-in operation-first two-PRG project (PR #384). It is a
**bounded emulator stress probe**, not a full 50 Hz application or an approval
to share Turbo16's 122-byte executable zero-page overlay with live IRQ code.

## Exact-source test

```sh
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 tools/native_reu_pal_irq_dma.py --out build/reu-pal/irq-vic-dma-cia.json
```

A freshly source-built `math_selective.prg` is co-loaded with an independently
source-built `turbo16_reu.prg`. The operation-first linker has reserved the
whole REU package envelope ($3000–$77FF), public I/O at $C000–$C01F and
the 122-byte ZP overlay ($3E–$B7) **before** building stock UMUL16,
which uses relocated public I/O at $C040.

The native x64sc PAL harness: installs and DMA-probes real REU at either
512 KiB/bank 4 or 16 MiB/bank 200; synchronizes to a raster-frame start;
measures one BEGIN, 24 CALLs of 0x1234 × 0x5678 and one END using cascaded
CIA1 timers A and B; verifies public results, Carry and restored caller ZP;
then checks the normal stock UMUL16 remains correct.

For each hardware tier it repeats matched controls with VIC-II display
disabled/enabled and a **real raster IRQ** at PAL line 23 disabled/enabled,
for eight total runs. The IRQ acknowledges VIC, saves/restores A/X/Y and
writes actual $D400/$D404/$D418 SID registers. It touches **no** bytes of
the reserved Turbo16 executable zero page. A successful interrupt case
must service at least one IRQ *during the timed burst*; a no-IRQ control
must service none. Every IRQ/SID case must show increased elapsed PHI2
wall-clock slots relative to its display-matched no-IRQ control.

The JSON artifact records the paired CIA wall-clock counts, interrupt
counts, resulting products, restored ZP evidence, SHA256 IDs of the
stock/REU generated images and matched IRQ/display deltas. This is
**physical DMA timing included in an application-sized burst**, not the
isolated CPU-only cycle estimates used in historical variants.

## What this does not qualify

- It is not a full SID music player, an authenticated 24-frame arithmetic
  trace, a sustained 50 Hz application, or real-hardware electrical timing.
- It does not test IRQ handlers that themselves use the overlay. Such
  handlers remain prohibited while Turbo16 BEGIN–END is active.
- It does not imply REU execution always beats the stock-C64 variant,
  and does not enable unconditional per-operation auto-selection.
- The REU option retains the explicit INSTALL/BEGIN/CALL/END interface
  and a non-REU UMUL16 fallback.

Any failure is evidence against declaring PAL IRQ/DMA qualification:
do not weaken the expected result or disable hardware assertions merely
to obtain a green check.
