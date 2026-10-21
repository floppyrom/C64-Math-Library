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

## Cold-start reproducibility and monitor hygiene

The native qualification uses **normal-speed PAL x64sc**, not emulator
`-warp`. The initial warp-mode runs intermittently stalled at the 16 MiB
high-bank IRQ case, including a fresh-run isolated replay, even though
other identical inputs passed. This is a limitation of that test setup,
**not proof** of an actual C64 hardware or Turbo16 arithmetic defect.
An explicit `--warp` flag remains available for investigating that
difference, but no warp-mode timing result is accepted as a release gate.

[Native cold-start run #39656111190](https://github.com/floppyrom/C64-Math-Library/actions/runs/39656111190)
passed the high-bank 16 MiB IRQ case as the **first machine process**,
then passed **three complete eight-case matrices** without diagnostic
warmup. It checked 24 separate cases with native REU DMA, true raster
IRQs, SID writes, real CIA wall-clock counters and intact caller ZP,
and retained per-case source-image hashes. Representative normal-speed
results were **6,408** PHI2 slots with display disabled and no IRQ,
**6,491** with an IRQ, **6,751–6,752** with the display enabled and no IRQ,
and **6,834–6,835** with both display and IRQ enabled.

The monitor uses an address-free `g` rather than `g <address>`,
because the latter is implicated in
[VICE monitor bug #2024](https://sourceforge.net/p/vice-emu/bugs/2024/).
The experimental alternative of setting PC **before** the breakpoints
failed the cold 16 MiB IRQ test despite normal-speed emulation. It was
reverted to the previously passing source to avoid claiming an unproved
fix. The emulator monitor remains a qualification uncertainty even when
a specific native test run completes successfully.

Only the displayed, no-warp, bounded PAL result is qualified; no
unconditional claim of IRQ-safe calls on actual hardware follows.

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
