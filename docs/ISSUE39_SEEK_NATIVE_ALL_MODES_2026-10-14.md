# SEEK8/16: native VICE qualification of all stepper modes

**Result: PASS native research; no native cycle timing measured.**

The real x64sc 6502 execution harness invokes each of eight public
SEEK modes using shipped V1–V5 PRGs. It tests STEP with major-axis
fraction and Euclidean flag, STEP_INT and STEP1 at 16 frames per test;
all eight INIT routes are invoked. It records the actual frame-by-frame
X and Y positions, carry flag, X register and CPU stack pointer through
the monitor's saved RAM, then checks each against the independent
Bresenham/reference movement model, including post-arrival repeats.

| Metric | Observed calls |
|---|---:|
| Native public INIT calls | 40 |
| Native public STEP/STEP_INT/STEP1 calls | 640 |
| Profiles | V1, V2, V3, V4, V5 |
| REU simulation | V3 512KiB, V4 16MiB |

The prior eight-slot CPU-model campaign independently passed 480 INIT
calls, 246,480 STEP calls and 86,960 movement frames across both
source relocations, plus 18,280 mixed DIV/MOD coexistence calls.

## Per-profile native evidence

| Profile | Native STEP calls | Dump SHA256 |
|---|---:|---|
| v1_balanced | 128 | a12dbb6a52760259eee5a0906e8073879ed5e875d3040b937d4333a476fe3649 |
| v2_pareto_fast | 128 | a12dbb6a52760259eee5a0906e8073879ed5e875d3040b937d4333a476fe3649 |
| v3_reu_512k | 128 | a12dbb6a52760259eee5a0906e8073879ed5e875d3040b937d4333a476fe3649 |
| v4_reu_16m | 128 | 43ab37f5752560395e9a97a6d2bd495d8e32f8e8253a081ff52c0f03c0feaf3b |
| v5_hybrid_lowzp | 128 | a12dbb6a52760259eee5a0906e8073879ed5e875d3040b937d4333a476fe3649 |

This adds a native correctness check for SEEK8 INIT/STEP/STEP_INT/STEP1
and SEEK16 INIT/STEP/STEP_INT/STEP1 without modifying any public API
address, production PRG, REU image, normal zero page or lookup table.
Its hardware emulator run does **not** provide native cycle counts.
Private OptiSearch code is not published. A final family review and
postmerge main CI check are still required before checking Issue #39.

Native harness: tools/native_issue39_seek_all_modes.py
Evidence: validation/review/ISSUE39_SEEK_ALL_MODES_NATIVE_VICE_2026-10-14.json
Green CI: https://github.com/floppyrom/C64-Math-Library/actions/runs/38626688576
