# Experimental native PAL raster IRQ + minimal SID-write arithmetic bursts

The existing native C64 math workload tests use actual pinned
x64sc r46284 PAL VIC-II bus contention and cascaded CIA timing, but they
deliberately **disable IRQs and SID playback**. The three source-qualified
seven-operation installer configurations in #361 have measured isolated
worst-burst costs of 19,883 (stock), 17,580 (signed-only D65536),
and 17,618 (signed+unsigned D65536) PHI2 slots respectively.

`tools/native_pal_irq_sid_burst.py` is an **additional experimental
hardware-emulated interference test**. It constructs exactly those three
ordinary installer-linked PRGs, replays the source-authenticated 150-call
history from the two physical relocations, and times the original busiest
24-public-call synthetic frames 0, 8 and 16 under normal visible VIC-II DMA
and a display-off control.

Each compared pair has identical CPU-origin, math operands, original
public-call order, code placement and CIA timer setup. Both runs also set
the C64 hardware IRQ vector to a RAM-resident interrupt handler at `$7E00`.
Only the single VIC-II IRQ enable immediate differs, after the test resets
the IRQ count precisely at the raster-zero synchronization barrier.

With IRQ enabled, the real VIC-II raster match at line 90 asserts the CPU
IRQ. The handler saves A/X/Y and returns with RTI to preserve the public
caller's P and stack, acknowledges `$D019`, increments a RAM count, and
writes four actual SID voice/volume register locations (`$D400/$D401/
$D404/$D418`). The timing data includes VIC bus contention, interrupt
entry/exit, register preservation, SID writes and the same source-verified
public Q/R/C oracles. It rejects missing or duplicate observations,
altered input/output/source hashes, absent or repeated IRQs, and measured
IRQ-on time not exceeding the matched IRQ-off control.

Run the pinned emulator locally:

```sh
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 -m unittest discover -s tools -p 'test_native_pal_irq_sid_burst.py' -v
python3 tools/native_pal_irq_sid_burst.py \
  --out build/irq-sid-pal/installed-math-bursts.json
```

**The qualification boundary is important.** The handler makes simple,
fixed SID **register writes**, not actual music synthesis, sample streaming
or a complete 50 Hz SID player. Each sample is a separately initialized,
raster-synchronized single-frame arithmetic burst. Although a real VIC-II
IRQ is serviced and timed, the test does **not** run 24 *consecutive* frames
of a game/demo; it has no full raster effect, sprite multiplexing, serial
or REU transfers, and does not establish application-level frame deadlines
or meaningful command integration.

The measured handler overhead is not automatically a fixed additive reserve
for any real project; interrupt phase, VIC steals, other source data and the
actual routine call schedule affect elapsed slots. This work provides the
next physical control experiment before instrumenting a persistent 24-frame
PAL run with an actual IRQ/SID player and effect code. It does not alter
or release the five historical profiles or REU/Turbo/QS16 binaries.
