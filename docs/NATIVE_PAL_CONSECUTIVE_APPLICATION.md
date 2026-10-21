# Experimental PAL application-style acceptance: original 24-frame math trace, SID and renderer

The repeated source frame-8 proof in PR #364 and the NOP sensitivity experiment
in PR #365 leave two important questions open: does varied arithmetic meet real
successive PAL periods, and how much of the native budget can *real*
music/rendering work consume?

The tool tools/native_pal_consecutive_application.py is a **new separate experiment**.
It retains the original source-linked 150 public calls, grouped in their
unaltered 24 frame/order/operand sequence (24, 3, 3, 3, 8, 3, 3, 3,
24, 3, 3, 3, 8, 3, 3, 3, 24, 3, 3, 3, 8, 3, 3, 3).
It rebuilds ordinary installer PRGs for the stock V2, signed-only D65536 and
both-D65536 source plans without editing any arithmetic kernels. Each source
frame's exact staged operands and public JSRs are copied byte-for-byte from
the independently checked native source harness.

Each plan runs two pinned x64sc r46284 experiments (VIC display on and off).
All 24 frame jobs run in **one** PAL process per plan/display combination:

- A continuously running 32-bit cascaded CIA1 A/B elapsed-slot counter,
  started at the first raster-zero synchronization. No timer reloading on
  subsequent periods; cumulative 19,656-slot deadlines detect frame slips.
- A hardware raster IRQ at PAL line 90 which saves A/X/Y, acknowledges $D019,
  and executes a small actual **three-voice SID music sequencer**. Three
  independently gated voices have different ADSR/waveforms and eight pitched
  notes per pattern; pitches advance every four IRQ ticks. This *is* real
  SID register synthesis/score sequencing, but not playback of an existing
  SID file or a cycle-heavy production tune.
- A main-thread renderer executes on every scheduled frame. It rewrites
  **64 VIC screen character cells across four rows** plus **16 colour-RAM
  cells**, with the original frame count affecting the animated pattern.
  Normal display-on mode incurs actual VIC-II screen DMA contention. The
  display-off comparison runs exactly the same CPU rendering code.
- A live on-6510 per-frame comparison against the complete original
  **300-byte Q/R/carry oracle**, checking each frame's own output bytes.
  The final 48-byte monitor snapshot also checks the most recent live
  results. A machine-code renderer count enforces exactly 24 calls.
- Actual complete IRQ count, frame output error count, full source and
  PRG provenance hashes, each cumulative CIA sample, per-frame lateness,
  minimum margin, and per-frame public-call counts are retained in JSON.
  Extra raster IRQs caused by skipped frame opportunities are **reported**,
  not silently discarded or mistaken for arithmetic errors.
  Because the final short 3-call frame can complete *before* its line-90
  raster IRQ, **23 observed IRQs for 24 completed frame jobs is valid**;
  the unobserved late-in-frame interrupt is never invented. Counts of 24
  or more still require scrutiny alongside actual cumulative CIA deadlines.

Run static regression checks:

    python3 -m unittest discover -s tools -p 'test_native_pal_consecutive_application.py' -v

Run *only* against independently verified pinned VICE:

    export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
    bash tools/vice/verify_headless.sh "$VICE_WRAPPER"
    python3 tools/native_pal_consecutive_application.py \
      --out build/pal-consecutive/original-varied-sid-render.json

**Qualification boundary:** This is an application-*style* benchmark. It does
not sample audio output, render a finished effect, run an external SID player
or song, exercise sprite DMA/multiplexing, process REU DMA, or certify an
arbitrary real game or demo. The original 150-call sequence is itself a
synthetic public-ABI trace; only its inputs and call grouping are unchanged.
Source-model cycles or successful static tests **must not** be reported as
a native 50 Hz pass before pinned VICE has produced verified JSON.

The source-linked installer, historical V1–V5 profiles, Pareto alternatives,
and all REU/Turbo/QS16 release binaries are unchanged. The independently
measured NOP experiment remains available for controlled comparison.
