# Native repeated PAL busiest-frame stress — 24 raster-zero-scheduled repetitions

Merged #363 measured *one independently raster-aligned math burst per native
x64sc startup* with a real VIC-II raster IRQ on line 90 and four SID register
writes. The signed-only D65536 installed source's busiest burst required
**17,658 native PHI2 slots** with the display on; nominal margin was
**1,998 slots**. That did not test sustained scheduling from one real
PAL frame to the next.

`tools/native_pal_consecutive_busiest.py` now runs a distinct experimental
**24 raster-zero-scheduled repeated work items inside one x64sc process**.
The workload is the exact original source-linked **frame 8**, all 24
public calls, repeated 24 times rather than the original varying 24-frame
corpus. Three ordinary installer PRGs compete: stock V2, both signed and
unsigned D65536, and the signed-only D65536 winner.

- Compile the identical frame-8 public operand writes and 24 original JSRs
  *once* into RAM at `$8000`. A separate `$7000` driver calls them on
  24 raster-zero opportunities, counting skipped physical PAL periods, with a real RAM IRQ at
  `$7E00` and `$D019` acknowledgement on raster line 90.
- Keep cascaded CIA1 A/B **running continuously**, starting only at the first
  scheduled raster-zero transition. Record the actual 32-bit timer counters
  after each arithmetic burst without resetting them. Any skipped raster
  boundary or busy-frame backlog shows up in cumulative deadlines
  `19,656 × (frame index + 1)`.
- Execute the real IRQ's A/X/Y preservation and four SID voice/control/
  volume register stores on each raster event. Record the actual IRQ count rather than falsely requiring 24: 
  **47 raster IRQs for 24 work items**, for instance, indicates a heavy
  trace missed raster-zero opportunities. Such extra IRQs must not be
  mistaken for an arithmetic failure.
- Verify **every one** of the 24 × 48 live public output/carry bytes against
  its original oracle by executing a 6510 comparison loop *every frame*,
  recording an explicit mismatch counter; the final 48-byte output snapshot
  must also match exactly.
- Link each test image via the normal source-replayed builder with source
  and installer PRG SHA checks. Record final source hashes, per-period
  accumulated CIA snapshots, deadline lateness, full IRQ counts and all
  source/output identities for both VIC display enabled and disabled.

```sh
python3 -m unittest discover -s tools -p 'test_native_pal_consecutive_busiest.py' -v
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 tools/native_pal_consecutive_busiest.py \
  --out build/pal-consecutive/consecutive-frame8-irq-sid.json
```

This is a **stronger but deliberately scoped** 50 Hz stress measurement.
It runs one identical worst-frame synthetic arithmetic workload repeatedly,
not the original varied 150-call 24-frame sequence. It includes explicit
per-frame output checking and timer-snapshot overhead, normal VIC text
display contention, a minimal raster IRQ and SID register *writes*.
It **does not** run a complete SID music player, a sprite multiplexer,
game/effect renderer, CIA keyboard input, REU DMA or screen updates.
Only after native CI has completed and the actual report is inspected
may the measured deadline results be reported; source-model cycles alone
must never be presented as consecutive real-frame measurements.

Historical V1–V5 profiles, the original V2/compact alternatives, stock
operation-first selection, and REU/Turbo/QS16 images remain unchanged.

**Native qualification finding during the initial run:** Stock V2's
visible-disabled control executed 24 repeated math work items, but the CPU
serviced **47 real raster IRQs**. The initial test correctly caught this
but mistakenly asserted it was invalid. The revised verifier separates
*raster events* from *completed work items* and records all cumulative CIA
deadline misses. The isolated static workflow still must be rerun on the
revised head before claiming a complete native result for all source plans.
