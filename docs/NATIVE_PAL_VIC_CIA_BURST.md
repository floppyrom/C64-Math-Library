# Experimental native PAL VIC-II/CIA busy-burst measurement

The existing exact seven-operation frame installer and native x64sc oracles
verify **source-linked math arithmetic correctness**, but the offline
Mini6502 frame cycle totals are **not** PAL-machine elapsed time.

`tools/native_pal_vic_cia_probe.py` is a **separate experimental tool**. It
rebuilds the exact replay-qualified project with the operation-first CLI,
then generates RAM-resident 6510 instructions to stage the *unchanged*
24-call busy burst from synthetic frame 0 and execute the selected seven
public exports in their actual source order. The machine-code probe:

- Runs on pinned native x64sc r46284 in PAL mode with `SEI`, KERNAL/BASIC
  ROMs mapped out and VIC/CIA I/O mapped in via `$01=$35`.
- Waits for the raster high bit to transition from lines 256–311 to the
  line-zero region; never mistakes raster 256 for raster zero.
- Runs with `$D011=$1B` (normal displayed text badlines) and, independently,
  `$D011=$0B` (display off) as a control, under the same call operands.
- Loads CIA1 A and B to `$FFFF`, starts A on PHI2 and B on A underflows,
  and stops both after the exact 24-call burst. The 32-bit combined value
  avoids mistaking a burst beyond 65,536 slots for a short one.
- Dumps timer values and two live output bytes per public call, with an
  independent Python quotient/product/root/carry oracle. It rejects
  mismatched results and verifies whether VIC display overhead is detected.
- Records the installed PRG/source-evidence SHA and observed raster.

Run after building pinned headless VICE:

```sh
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 -m unittest discover -s tools -p 'test_native_pal_vic_cia_probe.py' -v
python3 tools/native_pal_vic_cia_probe.py \
  --frame 0 --out build/pal-vic-cia/native-burst.json
```

**Limitations:** This times a *single, test-generated 24-call arithmetic burst*
plus its native operand-staging/instrumentation overhead. It is NOT a
24-consecutive-frame game loop or a demonstration of 50 Hz viability. The
machine deliberately disables IRQs and does not run a SID player, sprites,
REU DMA, application logic or screen rendering code outside the VIC's normal
DMA. The CIA wall-slot reading is not the same as the offline instruction
cycle tally. A positive nominal margin **cannot certify a demo**. Before
profile retirement, the next stage must test a real 50 Hz loop with IRQ/SID,
VIC-specific bus contention, startup costs and any REU transfers, and report
worst-frame plus repeated-frame deadline misses.

No historical V1–V5, REU or selected math source has been changed.
