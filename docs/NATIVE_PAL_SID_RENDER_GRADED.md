# Issue #367 phase 1 — graduated native SID and VIC workload admission

**Status: experimental until the exact-head pinned native VICE workflow passes.**

Previous merged PR #366 verified the original varied **150 public arithmetic
calls across 24 PAL frames**, a small three-voice score, 64 screen-character
and 16 colour-cell updates per work item. The signed-only D65536 plan had only
**481** PHI2 slots of minimum observed on-screen cumulative deadline margin;
the both-D65536 plan had **439**. Those thin margins must not be extrapolated
to a production demo.

tools/native_pal_application_stress.py adds a separate, explicitly heavier
deterministic workload with **no NOP reserve** and no change to the source
arithmetic kernels or original 150 calls/300 output+carry oracle bytes.

* Real line-90 VIC raster IRQ runs a score-table-driven **three-voice SID
  player**. Twelve actual SID registers (three voices times frequency low,
  frequency high, and gated waveform plus filter cutoff, resonance/routing,
  and master volume/mode) are updated on every serviced raster event.
  On each write the exact accumulator byte is mirrored to its own safe RAM
  shadow at $3E20-$3E2B. The final on-6510 readback computes the last note
  table index from the *actual serviced IRQ count* and checks all 12 mirrors
  against the registered tables **after IRQs have been disabled**, avoiding
  a race against playback. The player uses an original eight-step score,
  rather than importing somebody else's licensed SID music.
* Each of 24 scheduled frames updates 16 columns across 4, 8, 12, or 16
  text-screen rows at $0400 and every second corresponding colour RAM row
  at $D800 (64/128/192/256 real character cell stores and
  32/64/96/128 colour stores per work item). At completion an on-6510 oracle
  checks the first, last, and final-row screen/colour cells against the
  deterministic frame-23 pattern (the completed-job counter is 24 and is
  decremented before the last-frame witness comparison). A failed SID or
  screen check increments
  the existing error counter and fails native qualification.
* Original per-frame source-linked staged operands, public JSR bytes,
  captured Q/R/C outputs, 24 distinct frame call counts, source PRG hashes
  and standard emitted linker bytes are preserved. The small final-only
  verification code is installed only in the previously unused $7A40..$7B80
  test-harness RAM gap. Its CPU cycles occur **after timer shutdown**, so it
  does not artificially inflate the PAL workload deadlines.
* Every one of the 3 installed plans (stock V2, signed-only D65536, both
  D65536) runs the 4 renderer levels under VIC display off/on in one
  pinned x64sc process **per condition**: 24 native sessions, 576 PAL
  work items, 3600 complete public JSRs. One continuously running 32-bit
  CIA1 A/B measurement per run tracks cumulative elapsed PHI2 slots,
  nominal deadline misses, real IRQ counts, skipped periods, and margin
  under visible VIC badlines. A missed deadline is reported in JSON,
  **not concealed or converted into a passing result**.
* Candidate acceptance is based on 0 actual public-output/SID/screen oracle
  errors plus **0 missed cumulative PAL deadlines**. Preserve the exact
  peak/worst observed cumulative frame margin. No broad production claim
  may be made for a plan with only marginal headroom.

Static:
    python3 -m unittest discover -s tools -p 'test_native_pal_application_stress.py' -v

Pinned native:
    export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
    bash tools/vice/verify_headless.sh "$VICE_WRAPPER"
    python3 tools/native_pal_application_stress.py --rows 4,8,12,16 \
      --out build/pal-consecutive/sid-render-graded.json

**Limitations:** The score is an original *small 6510 SID playback routine*,
not a real-world SID tune with its complete composer data or an external
player's full initialization contract. Shadow RAM verifies the values
immediately written to SID but cannot prove audible output, oscillator state
or register readback. Text/colour updates are an observable VIC rendering
workload, not a complete screen effect or sprites. The test has no REU DMA
and does not claim a full game/demo certificate. The later phase of #367
must test a representative licensed production SID player, a production
effect renderer, sprite contention and, separately, REU DMA and 50 Hz
audio/video artifacts. All historical V1–V5, custom Pareto and REU
compatibility assets stay unchanged.
