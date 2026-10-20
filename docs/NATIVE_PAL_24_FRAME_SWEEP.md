# Every synthetic math-frame burst in native PAL x64sc

The [single-burst native PAL/CIA probe](NATIVE_PAL_VIC_CIA_BURST.md)
qualifies one exact linked seven-operation source plan against frame 0 of the
150-public-call/24-frame synthetic test. The `native_pal_vic_cia_sweep.py`
follow-up records **all twenty-four separate source frames** for two linked
operation-first installer choices and two VIC display conditions.

Every frame is *independently* aligned to the native PAL raster-zero transition
and timed by cascaded CIA1 Timer A/B. The test feeds the identical public
operation input order into the actual linked source, checks the live public
results and carry bits, and verifies both display settings produce the same
outputs. The report includes full frame-by-frame elapsed PHI2 slots, nearest-
rank p95, maximum, and a count of **isolated** bursts exceeding 19,656 nominal
PAL raster slots. Unlike CPU-model peaks, elapsed clock slots reflect VIC-II
bus contention and operand-staging overhead in the running native emulator.

Run with pinned x64sc r46284:

```sh
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 -m unittest discover -s tools -p 'test_native_pal_vic_cia_sweep.py' -v
python3 tools/native_pal_vic_cia_sweep.py \
  --profiles both --frames all \
  --out build/pal-vic-cia/24-native-bursts.json
# Smaller opt-in diagnostic:
python3 tools/native_pal_vic_cia_sweep.py --profiles fast31 --frames 0,8,16
```

The two choices are **0-ZP compact MUL + table ISQRT16 + compact 32-bit
signed/unsigned DIV/MOD** and **31-ZP shared FAST31 MUL + table ISQRT16 + V2
signed/unsigned DIV/MOD**. All checked frames derive from the same exact
replay-registered sixteen-choice source producer and linked installer PRG.
The former is a performance baseline, not a recommended PAL real-time build.

## Important qualification boundary

These are 24 **independent emulator startups and raster-aligned bursts per
source/display condition**, not 24 consecutive application frames at 50 Hz.
The profiler intentionally runs with interrupts disabled, no SID music
player, no sprite multiplexing and no REU DMA. It stages operand bytes,
records result/carry bytes and samples CIA registers inside the measured
interval, which a real optimized caller may do differently. The 19,656-slot
comparison therefore reports nominal deadline misses for the **isolated
test bursts**, never a certified game's frame rate. Full profile retirement
still requires a repeatable continuous PAL playback workload with real IRQ,
SID, visual effects, selected REU operations and application-level budgets.

The exact source/PRG SHA values and per-frame input digests are preserved.
The sweep never changes fast/compact arithmetic source, the 56-API linker,
any V1-V5 historical resident or any Turbo/QS16 REU image.
