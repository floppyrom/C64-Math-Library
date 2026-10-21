# PAL 50 Hz consecutive-frame CPU reserve sensitivity

Merged [PR #364](https://github.com/floppyrom/C64-Math-Library/pull/364)
measured **24 consecutive synthetic frame-8 workloads** in a single
pinned x64sc r46284 PAL process, with real raster IRQ (line 90), normal VIC-II
display DMA and four SID register writes per physical PAL period.
The signed-only D65536 source passed all 24 nominal deadlines, but its
**smallest native deadline margin was 1,114 PHI2 slots**, so there is
little room for other real application work. The both-D65536 source
had a smaller minimum margin of **840 slots**.

`tools/native_pal_consecutive_reserve.py` adds actual, deliberately
minimal **NOP instruction work** to the original 24-call source-linked
math routine on every scheduled period. The original arithmetic opcodes,
inputs, public Q/R/C captures, per-frame 48-byte live result oracle,
CIA1 A/B continuous 32-bit counter, real VIC raster IRQ and SID writes
are unchanged. Only the extra NOP instructions before return change.

Each injected `NOP` takes **two 6510 instruction cycles without VIC
contention**; the native CIA counter measures elapsed **PHI2 clock
slots** including VIC contention and real interrupt activity. These
numbers should never be used interchangeably without measurement.

Both signed-only D65536 and both-D65536 installed source plans run
24 consecutive original frame-8 math repetitions at seven controlled
extra CPU loads: 0, 256, 512, 768, 1,024, 1,536, and 2,048 nominal
NOP instruction cycles per repeated math burst. Each is executed
with the VIC display on and off. The report preserves all 24 native
cumulative deadline snapshots, exact source PRG and output digests,
IRQ counts, first tested over-budget level, and worst observed deadline
margin, without assuming that deadline miss counts are monotonic under
raster scheduling.

```sh
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 -m unittest discover -s tools -p 'test_native_pal_consecutive_reserve.py' -v
python3 tools/native_pal_consecutive_reserve.py \
  --reserves 0,256,512,768,1024,1536,2048 \
  --out build/pal-consecutive/nonmath-reserve-24frame.json
```

**What this measures:** Native PAL 50 Hz scheduling sensitivity to
simple additional CPU instructions, alongside the same repeated,
source-qualified busiest synthetic math frame, raster IRQ and SID I/O
writes. It also checks real per-frame public output bytes so the extra
work cannot silently corrupt arithmetic results.

**What it does not measure:** an actual SID music player's data-dependent
runtime, screen updates, sprite multiplexing, REU DMA, real changing
150-call/24-frame application inputs, a raster IRQ graph with multiple
real hardware priorities, or a 50 Hz game/demo. Passing a NOP reserve is
not a substitute for benchmarking those components directly.

Stock V2, historic V1–V5 profiles, selectable arithmetic kernels,
the normal operation-first installer and REU/Turbo/QS16 release assets
are unchanged. Do not merge this experiment until exact-head static
and pinned VICE native CI pass.
