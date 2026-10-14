# SEEK8/16 all-slots public ABI research — Issue #39

**Status: research PASS.** No production code/PRG/REU changes or new
performance winner is asserted. The overall SEEK campaign remains open.

V1–V5 were source-built in both relocations. Eight objects were initialized
concurrently for each width and mode; every frame matched the independent
Bresenham reference path, carry, X and stack pointer. State/planes for
the other seven slots were checked byte-for-byte after every call,
including two post-arrival calls per slot.

| Check | Total |
|---|---:|
| INIT public calls | 480 |
| STEP, STEP_INT and STEP1 public calls | 246,480 |
| Independent movement frames | 86,960 |

Additionally, the permanent Issue #136 mixed DIV/MOD coexistence test
passed 18,280 DIV/MOD calls and 13,580 SEEK steps, while the full
SEEK memory-placement tracer passed on both relocations.

## Same-case CPU-model performance (not native hardware timing)

| Profile | Map | Mode | INIT average cycles | STEP average cycles | STEP calls |
|---|---|---|---:|---:|---:|
| v1_balanced | reference | SEEK8_STEP | 516.750 | 80.715 | 4,096 |
| v1_balanced | reference | SEEK8_INT | 352.375 | 63.955 | 2,056 |
| v1_balanced | reference | SEEK8_ONE | 277.625 | 62.215 | 2,056 |
| v1_balanced | reference | SEEK16_STEP | 662.875 | 107.631 | 5,480 |
| v1_balanced | reference | SEEK16_INT | 556.625 | 90.512 | 2,752 |
| v1_balanced | reference | SEEK16_ONE | 387.875 | 82.422 | 8,208 |
| v1_balanced | alternate | SEEK8_STEP | 516.750 | 80.715 | 4,096 |
| v1_balanced | alternate | SEEK8_INT | 352.375 | 63.955 | 2,056 |
| v1_balanced | alternate | SEEK8_ONE | 277.625 | 62.215 | 2,056 |
| v1_balanced | alternate | SEEK16_STEP | 662.875 | 107.631 | 5,480 |
| v1_balanced | alternate | SEEK16_INT | 556.625 | 90.512 | 2,752 |
| v1_balanced | alternate | SEEK16_ONE | 387.875 | 82.422 | 8,208 |
| v2_pareto_fast | reference | SEEK8_STEP | 468.125 | 80.733 | 4,096 |
| v2_pareto_fast | reference | SEEK8_INT | 320.875 | 63.955 | 2,056 |
| v2_pareto_fast | reference | SEEK8_ONE | 255.500 | 62.215 | 2,056 |
| v2_pareto_fast | reference | SEEK16_STEP | 596.875 | 107.542 | 5,480 |
| v2_pareto_fast | reference | SEEK16_INT | 501.625 | 90.512 | 2,752 |
| v2_pareto_fast | reference | SEEK16_ONE | 354.000 | 82.422 | 8,208 |
| v2_pareto_fast | alternate | SEEK8_STEP | 468.125 | 80.733 | 4,096 |
| v2_pareto_fast | alternate | SEEK8_INT | 320.875 | 63.955 | 2,056 |
| v2_pareto_fast | alternate | SEEK8_ONE | 255.500 | 62.215 | 2,056 |
| v2_pareto_fast | alternate | SEEK16_STEP | 596.875 | 107.542 | 5,480 |
| v2_pareto_fast | alternate | SEEK16_INT | 501.625 | 90.512 | 2,752 |
| v2_pareto_fast | alternate | SEEK16_ONE | 354.000 | 82.422 | 8,208 |
| v3_reu_512k | reference | SEEK8_STEP | 468.250 | 80.733 | 4,096 |
| v3_reu_512k | reference | SEEK8_INT | 321.000 | 63.955 | 2,056 |
| v3_reu_512k | reference | SEEK8_ONE | 255.625 | 62.215 | 2,056 |
| v3_reu_512k | reference | SEEK16_STEP | 595.375 | 107.407 | 5,480 |
| v3_reu_512k | reference | SEEK16_INT | 498.750 | 90.512 | 2,752 |
| v3_reu_512k | reference | SEEK16_ONE | 353.125 | 82.422 | 8,208 |
| v3_reu_512k | alternate | SEEK8_STEP | 468.250 | 80.733 | 4,096 |
| v3_reu_512k | alternate | SEEK8_INT | 321.000 | 63.955 | 2,056 |
| v3_reu_512k | alternate | SEEK8_ONE | 255.625 | 62.215 | 2,056 |
| v3_reu_512k | alternate | SEEK16_STEP | 595.375 | 107.407 | 5,480 |
| v3_reu_512k | alternate | SEEK16_INT | 498.750 | 90.512 | 2,752 |
| v3_reu_512k | alternate | SEEK16_ONE | 353.125 | 82.422 | 8,208 |
| v4_reu_16m | reference | SEEK8_STEP | 468.250 | 80.733 | 4,096 |
| v4_reu_16m | reference | SEEK8_INT | 321.000 | 63.955 | 2,056 |
| v4_reu_16m | reference | SEEK8_ONE | 255.625 | 62.215 | 2,056 |
| v4_reu_16m | reference | SEEK16_STEP | 595.375 | 107.407 | 5,480 |
| v4_reu_16m | reference | SEEK16_INT | 498.750 | 90.512 | 2,752 |
| v4_reu_16m | reference | SEEK16_ONE | 353.125 | 82.422 | 8,208 |
| v4_reu_16m | alternate | SEEK8_STEP | 468.250 | 80.733 | 4,096 |
| v4_reu_16m | alternate | SEEK8_INT | 321.000 | 63.955 | 2,056 |
| v4_reu_16m | alternate | SEEK8_ONE | 255.625 | 62.215 | 2,056 |
| v4_reu_16m | alternate | SEEK16_STEP | 595.375 | 107.407 | 5,480 |
| v4_reu_16m | alternate | SEEK16_INT | 498.750 | 90.512 | 2,752 |
| v4_reu_16m | alternate | SEEK16_ONE | 353.125 | 82.422 | 8,208 |
| v5_hybrid_lowzp | reference | SEEK8_STEP | 516.750 | 80.715 | 4,096 |
| v5_hybrid_lowzp | reference | SEEK8_INT | 352.375 | 63.955 | 2,056 |
| v5_hybrid_lowzp | reference | SEEK8_ONE | 277.625 | 62.215 | 2,056 |
| v5_hybrid_lowzp | reference | SEEK16_STEP | 662.875 | 107.631 | 5,480 |
| v5_hybrid_lowzp | reference | SEEK16_INT | 556.625 | 90.512 | 2,752 |
| v5_hybrid_lowzp | reference | SEEK16_ONE | 387.875 | 82.422 | 8,208 |
| v5_hybrid_lowzp | alternate | SEEK8_STEP | 516.750 | 80.715 | 4,096 |
| v5_hybrid_lowzp | alternate | SEEK8_INT | 352.375 | 63.955 | 2,056 |
| v5_hybrid_lowzp | alternate | SEEK8_ONE | 277.625 | 62.215 | 2,056 |
| v5_hybrid_lowzp | alternate | SEEK16_STEP | 662.875 | 107.631 | 5,480 |
| v5_hybrid_lowzp | alternate | SEEK16_INT | 556.625 | 90.512 | 2,752 |
| v5_hybrid_lowzp | alternate | SEEK16_ONE | 387.875 | 82.422 | 8,208 |

## Optimization disposition

The current hot steppers use no scratch or additional ZP. Any replacement
must retain per-frame carry, all stored movement planes, all eight slots
and the exact public ABI. The existing SEEK16 Euclidean init branch
improvement was source-published in PR #135. OptiSearch P40 raw-delta
Bresenham and clock-precise kernels use different state/speed contracts,
so their standalone sizes are not comparable to the full SEEK8/16 ABI.
Private OptiSearch code is not included. An axis-aligned init shortcut
remains a research hypothesis, not a measured public speed win.

The native all-stepper qualification, final optimizer audit and
postmerge main CI closeout remain pending. This research result
does not claim native emulator cycle measurements.

Source: tools/validate_issue39_seek_all_slots.py
Evidence: validation/review/ISSUE39_SEEK_ALL_SLOTS_RESEARCH_2026-10-14.json
CI: https://github.com/floppyrom/C64-Math-Library/actions/runs/38625412203
