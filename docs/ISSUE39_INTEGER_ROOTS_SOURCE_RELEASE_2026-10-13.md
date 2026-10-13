# Issue39 — integer square roots source integration (release stage)

13 October 2026. Production staging, native VICE and PR/main CI not yet qualified.

A manually implemented exact ISQRT16 upper-bound table seeds the root from the radicand high byte, then compares candidate-square bytes against the existing two resident square planes and decreases the candidate until the floor root is exact. The 294-byte executable + 256-byte seed table occupies the original 304-byte V2/V3 root-search island (V1 had 329 bytes), replacing code rather than growing the resident. No extra normal ZP or additional RAM table pages.

V1, V2, V3 and V5 apply this improvement. V4 retains its faster exact 54-cycle REU ISQRT16 service and its released PRG/REU images. ISQRT32 inherits a high-byte seed improvement for V1/V2/V3/V5; all four root32 implementations still compute exact floor(sqrt(N)).

| Profile | ISQRT16 before | ISQRT16 new | ISQRT32 before | ISQRT32 new |
|---|---:|---:|---:|---:|
| v1_balanced | 219.740570 | 57.878998 | 1378.900969 | 1219.260533 |
| v2_pareto_fast | 205.760590 | 58.234467 | 1198.619613 | 1053.284504 |
| v3_reu_512k | 204.992523 | 58.277435 | 1197.859322 | 1053.325908 |
| v4_reu_16m | 54.000000 | 54.000000 | 917.317433 | 917.317433 |
| v5_hybrid_lowzp | 219.740570 | 57.878998 | 1378.900969 | 1219.260533 |

ISQRT16 timing is an actual exhaustive 65,536-case public-entry 6502 instruction count on each optimized profile. ISQRT32 uses the existing exact same 4,130-case corpus. These are not cycle-exact native hardware or REU bus-time measurements.

V1/V2/V3/V5 source reference/alternate regeneration passed. V4 untouched. Stable public ABI, input ownership, stack and carry preserved. OptiSearch source remains private and is NOT included or transcribed into this repository.

**Pending before release:** native VICE on installed source-built resident images, independent PR tests, post-merge main CI. Issue #39 remains OPEN; unrelated unsigned closure also remains unchecked until documented.
