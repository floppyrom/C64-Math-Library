# Native PAL arithmetic-burst headroom after a hypothetical non-math reservation

The independently measured installed-source seven-operation benchmark in
[PR #361](https://github.com/floppyrom/C64-Math-Library/pull/361) includes
**three pinned x64sc r46284 PAL configurations** for 24 separate synthetic
math bursts: stock V2, signed+unsigned D65536, and signed-only D65536.
Each emits 150 public Q/R/C calls per VIC display condition, and all three
plans produce the same public output digests on the original input history.

Run this **offline, non-hardware** evaluator on the _original downloadable
Actions artifact_ `native-installed-d65536-stock-signed-only-both`
(`d65536-installed-native-three-plan-pal.json`):

```sh
python3 tools/native_pal_reserved_workload.py \
  --native-report build/d65536-installed-native-three-plan-pal.json \
  --max-ram 8957 --max-zp 31 \
  --reserve-nonmath-slots 2050 --require-headroom \
  --out build/pal-reservation-evidence.json
```

For this particular measured report, the **signed-only D65536** plan is the
only one of these three that passes that hypothetical reservation and RAM
budget. It has a 17,580-slot native worst burst, 8,957 linked RAM bytes and
31 ZP bytes; 19,656 - 17,580 - 2,050 = **26 nominal slots remain**.
Stock peaks at 19,883 and both-D65536 peaks at 17,618 but consumes 9,213
linked RAM bytes. If a fixed reservation exceeds 2,076, none of the three
measured plans fits. This says nothing about smaller unmeasured plans: the
full separate nine-source model basis retains low-ZP and compact choices.

This tool **fails closed** on missing/duplicated frame and source records,
mismatched PRG hashes, mismatched per-frame output digests or call histories,
incorrect elapsed-slot arithmetic, forged peaks, inconsistent deadlines,
unrecognized source basis, or insufficient RAM/ZP/headroom. It never
reconstructs measurements or fabricates real-time scheduling.

## Important evidence boundary

The inputs were **24 independent raster-aligned arithmetic bursts**, not
24 consecutive 50 Hz application frames. A user's
`--reserve-nonmath-slots` is an *estimate* for additional
IRQ, SID, rendering, REU or application work, **not a clock measurement**.
Actual VIC contention, sprite DMA, IRQ jitter, scheduling across PAL frame
boundaries and REU transfer costs may invalidate simple addition.
Passing this estimator **does not certify a 50 Hz game/demo**.

Use the original native-CI-produced artifact. The offline checker validates
internal consistency, but cannot prove an arbitrary input JSON was captured
from real hardware/emulation without independent source/authenticated
CI provenance. This is an engineering planning and rejection gate, not
a substitute for a later continuous-frame native test.

Existing original V2, compact, V1–V5 profiles, REU/Turbo/QS16 artifacts
and the operation-first source selection policy are unchanged.
