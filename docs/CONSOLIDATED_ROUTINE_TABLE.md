# Consolidated routine performance and memory table

Generated from the shipped reference images by `tools/generate_consolidated_routine_table.py`. This is the single cross-profile index for cycles and resource use.

**Memory accounting.** `Code B` is the unique executable byte set statically reachable from that entry after `MATH_INIT`; shared callees therefore appear on multiple rows and **must not be summed**. `ZP B` is the concrete page-zero set executable/referenced by the path; Turbo/QS16 rows instead report their exclusive owned overlay. `Stack B` is persistent hardware-stack-page (`$0100-$01FF`) reservation. It is **0 for every shipped choice**; ordinary transient JSR/PHA return/data stack traffic is intentionally not counted. The absolute 606.337632-cycle UMUL32 record is therefore not a shipped fixed-profile kernel because it reserves stack-page space.

**Cycle accounting.** Mean cycles include the public routine through RTS and exclude the caller JSR/input stores. The `Basis` column identifies the validation corpus/model; specialized exact/canonical source files remain authoritative for their own corpora.

## Profile-level memory contracts

| Profile | PRG payload span B | REU image B | Declared shared ZP B | Stable API ZP union touched B | Stack-page reserved B |
|---|---:|---:|---:|---:|---:|
| `v1_balanced` | 44951 | 0 |  | 31 | 0 |
| `v2_pareto_fast` | 44951 | 0 |  | 216 | 0 |
| `v3_reu_512k` | 49047 | 524288 |  | 205 | 0 |
| `v4_reu_16m` | 49047 | 16777216 |  | 204 | 0 |
| `v5_hybrid_lowzp` | 44951 | 0 | 31 | 31 | 0 |

## v1_balanced

| Routine | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | 90.494644 | 88 | 93 | 55 | 5 | $10-$14 | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | canonical harness |
| `MATH_UMUL16` | 273.837200 | 262 | 297 | 208 | 17 | $09-$19 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | 489.988792 | 462 | 542 | 369 | 24 | $09-$20 | 0 | FAST24 private 24-ZP carry producer with stable public adapter | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | 293.298407 | 260 | 327 | 273 | 17 | $09-$19 | 0 | FAST17 native signed composition with private 17-ZP magnitude core | current native-signed multiply validation |
| `MATH_SMUL24` | 531.496472 | 474 | 591 | 505 | 24 | $09-$20 | 0 | FAST24 four-quadrant native signed composition; immutable quarter-square tables shared | current native-signed multiply validation |
| `MATH_SMUL32` | 744.569946 | 660 | 873 | 1406 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | 726.388672 | 645 | 813 | 1387 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | 87.445969 | 60 | 607 | 359 | 5 | $10-$14 | 0 | profile-selected resident implementation | canonical harness |
| `MATH_UDIV16` | 160.064966 | 100 | 1630 | 299 | 10 | $10-$19 | 0 | profile-selected resident implementation | canonical harness |
| `MATH_UDIV24` | 224.668396 | 149 | 2465 | 320 | 15 | $10-$1E | 0 | profile-selected resident implementation | canonical harness |
| `MATH_UDIV32_16` | 857.373105 | 182 | 2380 | 311 | 12 | $10-$1B | 0 | profile-selected resident implementation | canonical harness |
| `MATH_UMOD8` | 65.285156 | 51 | 495 | 83 | 2 | $10-$11 | 0 | profile-selected resident implementation | exhaustive final-image |
| `MATH_UMOD16` | 163.064966 | 103 | 1633 | 302 | 10 | $10-$19 | 0 | profile-selected resident implementation | derived exact path |
| `MATH_UMOD24` | 227.668396 | 152 | 2468 | 323 | 15 | $10-$1E | 0 | profile-selected resident implementation | derived exact path |
| `MATH_UMOD32_16` | 860.373105 | 185 | 2383 | 314 | 12 | $10-$1B | 0 | profile-selected resident implementation | derived exact path |
| `MATH_SDIV8` | 120.786713 | 63 | 613 | 486 | 5 | $0E-$12 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV16` | 235.629662 | 107 | 1529 | 401 | 14 | $0E-$1B | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV24` | 367.885278 | 138 | 4795 | 440 | 18 | $0E-$1F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV32_16` | 989.689422 | 209 | 2098 | 547 | 18 | $0E-$1F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD8` | 133.330469 | 66 | 614 | 489 | 5 | $0E-$12 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD16` | 277.520578 | 110 | 1532 | 404 | 14 | $0E-$1B | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD24` | 470.872202 | 141 | 3051 | 443 | 18 | $0E-$1F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD32_16` | 1095.697473 | 212 | 2101 | 550 | 18 | $0E-$1F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_UDIV32_32` | 434.110992 | 151 | 2389 | 819 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_UMOD32_32` | 434.110992 | 151 | 2389 | 819 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SDIV32_32` | 604.974974 | 75 | 2493 | 1005 | 0 | — | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD32_32` | 804.718412 | 75 | 2493 | 1005 | 0 | — | 0 | native signed private executable path | current native-signed division validation |
| `MATH_UMUL16_SHR8` | 314.965600 | 303 | 338 | 234 | 17 | $09-$19 | 0 | profile-selected resident implementation | 2026-09-14 post-upgrade deterministic comparison corpus |
| `MATH_SMUL16_SHR8` | 333.867232 | 301 | 366 | 299 | 17 | $09-$19 | 0 | FAST17 SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | 812.998853 | 725 | 938 | 1450 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | 855.681132 | 289 | 1914 | 388 | 12 | $10-$1B | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SDIV16_SHL8` | 987.091167 | 319 | 2042 | 630 | 18 | $0E-$1F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_URECIP16_Q16` | 126.175720 | 41 | 2588 | 751 | 15 | $10-$1E | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SIN8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_COS8` | 29.000000 | 29 | 29 | 18 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SINCOS8` | 39.000000 | 39 | 39 | 25 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ATAN2_8` | 50.441345 | 30 | 53 | 109 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ISQRT16` | 219.740570 | 205 | 258 | 277 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ISQRT32` | 1378.900969 | 1193 | 1656 | 496 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_DIST8_FAST` | 86.085602 | 68 | 104 | 67 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_DIST8_ACCURATE` | 92.085602 | 74 | 110 | 72 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_VEC2_NORMALIZE_Q8_8` | 198.770271 | 129 | 333 | 392 | 5 | $14;$1A-$1D | 0 | profile-selected resident implementation | 2026-09-18 normalize profile-parity deterministic corpus |

## v2_pareto_fast

| Routine | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | 78.494614 | 77 | 80 | 54 | 5 | $39-$3D | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | canonical harness |
| `MATH_UMUL16` | 225.837200 | 214 | 249 | 171 | 17 | $21-$31 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | 448.291800 | 418 | 503 | 369 | 24 | $21-$38 | 0 | 24-ZP reverse_24zp_carry certified resident kernel (retained; refresh candidate did not win) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL32` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | 252.324882 | 230 | 293 | 217 | 116 | $80-$F3 | 0 | 116-ZP practical native signed quarter-square kernel (retained after FAST17 comparison) | current native-signed multiply validation |
| `MATH_SMUL24` | 487.181818 | 430 | 544 | 473 | 24 | $21-$38 | 0 | FAST24 four-quadrant native signed composition; immutable quarter-square tables shared | current native-signed multiply validation |
| `MATH_SMUL32` | 743.605230 | 660 | 873 | 1406 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | 728.041992 | 643 | 802 | 1387 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | 87.445969 | 60 | 607 | 359 | 5 | $10-$14 | 0 | profile-selected resident implementation | canonical harness |
| `MATH_UDIV16` | 137.282268 | 99 | 939 | 1133 | 8 | $10-$17 | 0 | profile-selected resident implementation | canonical harness |
| `MATH_UDIV24` | 203.612991 | 137 | 2394 | 1255 | 15 | $10-$1E | 0 | profile-selected resident implementation | canonical harness |
| `MATH_UDIV32_16` | 759.730823 | 210 | 1794 | 1890 | 12 | $10-$1B | 0 | profile-selected resident implementation | canonical harness |
| `MATH_UMOD8` | 64.819153 | 51 | 495 | 131 | 2 | $10-$11 | 0 | profile-selected resident implementation | exhaustive final-image/direct path |
| `MATH_UMOD16` | 140.282268 | 102 | 942 | 1136 | 8 | $10-$17 | 0 | profile-selected resident implementation | exact +3-cycle JMP path |
| `MATH_UMOD24` | 206.612991 | 140 | 2397 | 1258 | 15 | $10-$1E | 0 | profile-selected resident implementation | exact +3-cycle JMP path |
| `MATH_UMOD32_16` | 762.730823 | 213 | 1797 | 1893 | 12 | $10-$1B | 0 | profile-selected resident implementation | exact +3-cycle JMP path |
| `MATH_SDIV8` | 120.786713 | 63 | 613 | 486 | 5 | $3E-$42 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV16` | 216.402835 | 114 | 1073 | 1499 | 12 | $3E-$49 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV24` | 304.121483 | 153 | 3089 | 1744 | 21 | $3E-$52 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV32_16` | 868.632061 | 204 | 2008 | 2127 | 18 | $3E-$4F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD8` | 132.223437 | 66 | 614 | 489 | 5 | $3E-$42 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD16` | 275.264260 | 117 | 1076 | 1502 | 12 | $3E-$49 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD24` | 387.576173 | 156 | 3092 | 1747 | 21 | $3E-$52 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD32_16` | 896.480866 | 207 | 2011 | 2130 | 18 | $3E-$4F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_UDIV32_32` | 401.972551 | 139 | 2251 | 742 | 8 | $53-$5A | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_UMOD32_32` | 401.972551 | 139 | 2251 | 742 | 8 | $53-$5A | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SDIV32_32` | 567.765717 | 75 | 2399 | 908 | 10 | $53-$5C | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD32_32` | 760.826715 | 75 | 2399 | 908 | 10 | $53-$5C | 0 | native signed private executable path | current native-signed division validation |
| `MATH_UMUL16_SHR8` | 266.965600 | 255 | 290 | 197 | 17 | $21-$31 | 0 | profile-selected resident implementation | 2026-09-14 post-upgrade deterministic comparison corpus |
| `MATH_SMUL16_SHR8` | 293.411374 | 271 | 334 | 243 | 116 | $80-$F3 | 0 | 116-ZP practical native SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | 812.998853 | 725 | 938 | 1450 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | 762.606368 | 272 | 1849 | 1957 | 16 | $10-$1B;$53-$56 | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SDIV16_SHL8` | 868.689640 | 304 | 1943 | 2200 | 22 | $3E-$4F;$53-$56 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_URECIP16_Q16` | 119.577560 | 41 | 2079 | 1674 | 21 | $10-$1E;$61-$64;$67-$68 | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SIN8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_COS8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SINCOS8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ATAN2_8` | 46.953064 | 30 | 48 | 97 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ISQRT16` | 205.760590 | 193 | 246 | 259 | 1 | $66 | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ISQRT32` | 1198.619613 | 1052 | 1428 | 440 | 10 | $54-$5C;$66 | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_DIST8_FAST` | 79.570038 | 64 | 95 | 58 | 2 | $5D-$5E | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_DIST8_ACCURATE` | 85.570038 | 70 | 101 | 63 | 2 | $5D-$5E | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_VEC2_NORMALIZE_Q8_8` | 189.260317 | 127 | 323 | 383 | 8 | $12-$15;$39-$3C | 0 | profile-selected resident implementation | 2026-09-18 normalize profile-parity deterministic corpus |

## v3_reu_512k

| Routine | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | 69.000000 |  |  | 49 | 0 | — | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | REU transport model |
| `MATH_UMUL16` | 225.837200 | 214 | 249 | 171 | 17 | $21-$31 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | 448.291800 | 418 | 503 | 369 | 24 | $21-$38 | 0 | 24-ZP reverse_24zp_carry certified resident kernel (retained; refresh candidate did not win) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL32` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | 252.623962 | 230 | 293 | 217 | 116 | $80-$F3 | 0 | 116-ZP practical native signed quarter-square kernel (retained after FAST17 comparison) | current native-signed multiply validation |
| `MATH_SMUL24` | 486.816106 | 430 | 546 | 473 | 24 | $21-$38 | 0 | FAST24 four-quadrant native signed composition; immutable quarter-square tables shared | current native-signed multiply validation |
| `MATH_SMUL32` | 744.033209 | 660 | 873 | 1406 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | 728.544922 | 648 | 809 | 1387 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | 70.863281 |  |  | 61 | 0 | — | 0 | profile-selected resident implementation | REU transport model |
| `MATH_UDIV16` | 137.282268 |  |  | 1133 | 8 | $10-$17 | 0 | profile-selected resident implementation | unchanged v2 canonical |
| `MATH_UDIV24` | 203.612991 |  |  | 1255 | 15 | $10-$1E | 0 | profile-selected resident implementation | unchanged v2 canonical |
| `MATH_UDIV32_16` | 759.730823 |  |  | 1890 | 12 | $10-$1B | 0 | profile-selected resident implementation | unchanged v2 canonical |
| `MATH_UMOD8` | 49.929688 |  |  | 42 | 0 | — | 0 | profile-selected resident implementation | REU transport model |
| `MATH_UMOD16` | 140.282268 |  |  | 1136 | 8 | $10-$17 | 0 | profile-selected resident implementation | unchanged v2 canonical |
| `MATH_UMOD24` | 206.612991 |  |  | 1258 | 15 | $10-$1E | 0 | profile-selected resident implementation | unchanged v2 canonical |
| `MATH_UMOD32_16` | 762.730823 |  |  | 1893 | 12 | $10-$1B | 0 | profile-selected resident implementation | unchanged v2 canonical |
| `MATH_SDIV8` | 120.786713 | 63 | 613 | 486 | 5 | $3E-$42 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV16` | 218.538059 | 114 | 1073 | 1499 | 12 | $3E-$49 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV24` | 305.640131 | 153 | 3089 | 1744 | 21 | $3E-$52 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV32_16` | 868.222028 | 204 | 2008 | 2127 | 18 | $3E-$4F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD8` | 132.328906 | 66 | 614 | 489 | 5 | $3E-$42 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD16` | 277.501083 | 117 | 1076 | 1502 | 12 | $3E-$49 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD24` | 393.343682 | 156 | 3092 | 1747 | 21 | $3E-$52 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD32_16` | 897.883032 | 207 | 2011 | 2130 | 18 | $3E-$4F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_UDIV32_32` | 401.972551 | 139 | 2251 | 742 | 8 | $53-$5A | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_UMOD32_32` | 401.972551 | 139 | 2251 | 742 | 8 | $53-$5A | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SDIV32_32` | 567.148952 | 75 | 2399 | 908 | 10 | $53-$5C | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD32_32` | 756.810830 | 75 | 2399 | 908 | 10 | $53-$5C | 0 | native signed private executable path | current native-signed division validation |
| `MATH_UMUL16_SHR8` | 266.965600 | 255 | 290 | 197 | 17 | $21-$31 | 0 | profile-selected resident implementation | 2026-09-14 post-upgrade deterministic comparison corpus |
| `MATH_SMUL16_SHR8` | 293.411374 | 271 | 334 | 243 | 116 | $80-$F3 | 0 | 116-ZP practical native SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | 812.998853 | 725 | 938 | 1450 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | 762.606368 | 272 | 1849 | 1957 | 16 | $10-$1B;$53-$56 | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SDIV16_SHL8` | 867.317339 | 304 | 1943 | 2200 | 22 | $3E-$4F;$53-$56 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_URECIP16_Q16` | 66.233795 | 41 | 239 | 430 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SIN8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_COS8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SINCOS8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ATAN2_8` | 46.953064 | 30 | 48 | 97 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ISQRT16` | 204.992523 | 192 | 246 | 259 | 1 | $66 | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ISQRT32` | 1197.859322 | 1051 | 1428 | 440 | 10 | $54-$5C;$66 | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_DIST8_FAST` | 79.070038 | 63 | 95 | 58 | 2 | $5D-$5E | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_DIST8_ACCURATE` | 85.070038 | 69 | 101 | 63 | 2 | $5D-$5E | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_VEC2_NORMALIZE_Q8_8` | 170.058633 | 133 | 306 | 346 | 4 | $12-$15 | 0 | profile-selected resident implementation | 2026-09-18 normalize profile-parity deterministic corpus |
| `MATH_REU_UMUL16_BEGIN` | 282.000000 | 282 | 282 | 41 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16` | 215.544111 | 203 | 240 | 41 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16_END` | 327.000000 | 327 | 327 | 73 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_BEGIN` | 326.000000 | 326 | 326 | 41 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32` | 728.947080 | 666 | 840 | 125 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_END` | 371.000000 | 371 | 371 | 73 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |

## v4_reu_16m

| Routine | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | 69.000000 |  |  | 49 | 0 | — | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | unchanged V3 path/evidence |
| `MATH_UMUL16` | 225.837200 | 214 | 249 | 171 | 17 | $21-$31 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | 448.291800 | 418 | 503 | 369 | 24 | $21-$38 | 0 | 24-ZP reverse_24zp_carry certified resident kernel (retained; refresh candidate did not win) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL32` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | 252.662553 | 230 | 293 | 217 | 116 | $80-$F3 | 0 | 116-ZP practical native signed quarter-square kernel (retained after FAST17 comparison) | current native-signed multiply validation |
| `MATH_SMUL24` | 487.220008 | 430 | 550 | 473 | 24 | $21-$38 | 0 | FAST24 four-quadrant native signed composition; immutable quarter-square tables shared | current native-signed multiply validation |
| `MATH_SMUL32` | 744.090079 | 660 | 873 | 1406 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | 726.368164 | 643 | 825 | 1387 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | 70.863281 |  |  | 61 | 0 | — | 0 | profile-selected resident implementation | unchanged V3 path/evidence |
| `MATH_UDIV16` | 137.282268 |  |  | 1133 | 8 | $10-$17 | 0 | profile-selected resident implementation | unchanged V3 path/evidence |
| `MATH_UDIV24` | 203.612991 |  |  | 1255 | 15 | $10-$1E | 0 | profile-selected resident implementation | unchanged V3 path/evidence |
| `MATH_UDIV32_16` | 759.730823 |  |  | 1890 | 12 | $10-$1B | 0 | profile-selected resident implementation | unchanged V3 path/evidence |
| `MATH_UMOD8` | 49.929688 |  |  | 42 | 0 | — | 0 | profile-selected resident implementation | unchanged V3 path/evidence |
| `MATH_UMOD16` | 140.282268 |  |  | 1136 | 8 | $10-$17 | 0 | profile-selected resident implementation | unchanged V3 path/evidence |
| `MATH_UMOD24` | 206.612991 |  |  | 1258 | 15 | $10-$1E | 0 | profile-selected resident implementation | unchanged V3 path/evidence |
| `MATH_UMOD32_16` | 762.730823 |  |  | 1893 | 12 | $10-$1B | 0 | profile-selected resident implementation | unchanged V3 path/evidence |
| `MATH_SDIV8` | 121.487723 | 63 | 611 | 486 | 5 | $3E-$42 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV16` | 216.681352 | 114 | 1073 | 1499 | 12 | $3E-$49 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV24` | 306.378190 | 153 | 3089 | 1744 | 21 | $3E-$52 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV32_16` | 864.277208 | 204 | 2008 | 2127 | 18 | $3E-$4F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD8` | 134.164844 | 66 | 614 | 489 | 5 | $3E-$42 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD16` | 271.908303 | 117 | 1076 | 1502 | 12 | $3E-$49 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD24` | 390.018051 | 156 | 3092 | 1747 | 21 | $3E-$52 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD32_16` | 895.632491 | 207 | 2011 | 2130 | 18 | $3E-$4F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_UDIV32_32` | 401.972551 | 139 | 2251 | 742 | 8 | $53-$5A | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_UMOD32_32` | 401.972551 | 139 | 2251 | 742 | 8 | $53-$5A | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SDIV32_32` | 567.507613 | 75 | 2399 | 908 | 10 | $53-$5C | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD32_32` | 769.677256 | 75 | 2399 | 908 | 10 | $53-$5C | 0 | native signed private executable path | current native-signed division validation |
| `MATH_UMUL16_SHR8` | 266.965600 | 255 | 290 | 197 | 17 | $21-$31 | 0 | profile-selected resident implementation | 2026-09-14 post-upgrade deterministic comparison corpus |
| `MATH_SMUL16_SHR8` | 293.411374 | 271 | 334 | 243 | 116 | $80-$F3 | 0 | 116-ZP practical native SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | 812.998853 | 725 | 938 | 1450 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | 762.606368 | 272 | 1849 | 1957 | 16 | $10-$1B;$53-$56 | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SDIV16_SHL8` | 865.650818 | 304 | 1943 | 2200 | 22 | $3E-$4F;$53-$56 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_URECIP16_Q16` | 66.233795 | 41 | 239 | 430 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SIN8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_COS8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_SINCOS8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ATAN2_8` | 48.000000 | 48 | 48 | 33 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ISQRT16` | 54.000000 | 54 | 54 | 38 | 0 | — | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_ISQRT32` | 1046.622518 | 899 | 1237 | 219 | 9 | $54-$5C | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_DIST8_FAST` | 79.070038 | 63 | 95 | 58 | 2 | $5D-$5E | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_DIST8_ACCURATE` | 85.070038 | 69 | 101 | 63 | 2 | $5D-$5E | 0 | profile-selected resident implementation | published game-math benchmark 2026-09-06 |
| `MATH_VEC2_NORMALIZE_Q8_8` | 170.058633 | 133 | 306 | 346 | 4 | $12-$15 | 0 | profile-selected resident implementation | 2026-09-18 normalize profile-parity deterministic corpus |
| `MATH_REU_UMUL16_BEGIN` | 282.000000 | 282 | 282 | 41 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16` | 215.544111 | 203 | 240 | 41 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16_END` | 327.000000 | 327 | 327 | 73 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_BEGIN` | 326.000000 | 326 | 326 | 41 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32` | 728.947080 | 666 | 840 | 125 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_END` | 371.000000 | 371 | 371 | 73 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_QS16_BEGIN` | 18.000000 | 18 | 18 | 11 | 16 | $10-$1F | 0 | V4 16MiB QS16 mode | V4 QS16 source/exact timing classes |
| `MATH_REU_QS16` | 281.541031 | 279 | 293 | 209 | 16 | $10-$1F | 0 | V4 16MiB QS16 mode | V4 QS16 source/exact timing classes |
| `MATH_REU_QS16_END` | 18.000000 | 18 | 18 | 11 | 16 | $10-$1F | 0 | V4 16MiB QS16 mode | V4 QS16 source/exact timing classes |

## v5_hybrid_lowzp

| Routine | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | 90.494644 | 88 | 93 | 55 | 5 | $10-$14 | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | V5 documented v1_balanced path; canonical harness |
| `MATH_UMUL16` | 273.837200 | 262 | 297 | 208 | 17 | $09-$19 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep) | V5 documented v1_balanced path; 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | 489.988792 | 462 | 542 | 369 | 24 | $09-$20 | 0 | FAST24 private 24-ZP carry producer with stable public adapter | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | 292.974871 | 260 | 325 | 273 | 17 | $09-$19 | 0 | FAST17 native signed composition with private 17-ZP magnitude core | current native-signed multiply validation |
| `MATH_SMUL24` | 530.874222 | 474 | 588 | 505 | 24 | $09-$20 | 0 | FAST24 four-quadrant native signed composition; immutable quarter-square tables shared | current native-signed multiply validation |
| `MATH_SMUL32` | 743.913242 | 660 | 873 | 1406 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | 726.739258 | 640 | 807 | 1387 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | 87.445969 | 60 | 607 | 359 | 5 | $10-$14 | 0 | profile-selected resident implementation | V5 documented v1_balanced path; canonical harness |
| `MATH_UDIV16` | 137.282268 | 99 | 939 | 1133 | 8 | $10-$17 | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; canonical harness |
| `MATH_UDIV24` | 203.612991 | 137 | 2394 | 1255 | 15 | $10-$1E | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; canonical harness |
| `MATH_UDIV32_16` | 759.730823 | 210 | 1794 | 1890 | 12 | $10-$1B | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; canonical harness |
| `MATH_UMOD8` | 64.819153 | 51 | 495 | 131 | 2 | $10-$11 | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; exhaustive final-image/direct path |
| `MATH_UMOD16` | 140.282268 | 102 | 942 | 1136 | 8 | $10-$17 | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; exact +3-cycle JMP path |
| `MATH_UMOD24` | 206.612991 | 140 | 2397 | 1258 | 15 | $10-$1E | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; exact +3-cycle JMP path |
| `MATH_UMOD32_16` | 762.730823 | 213 | 1797 | 1893 | 12 | $10-$1B | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; exact +3-cycle JMP path |
| `MATH_SDIV8` | 122.724107 | 63 | 611 | 486 | 5 | $0E-$12 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV16` | 237.010033 | 107 | 1529 | 401 | 14 | $0E-$1B | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV24` | 376.778408 | 138 | 3997 | 440 | 18 | $0E-$1F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SDIV32_16` | 993.148310 | 209 | 2098 | 547 | 18 | $0E-$1F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD8` | 131.951562 | 66 | 614 | 489 | 5 | $0E-$12 | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD16` | 282.327798 | 110 | 1532 | 404 | 14 | $0E-$1B | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD24` | 468.334296 | 141 | 2306 | 443 | 18 | $0E-$1F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD32_16` | 1096.083032 | 212 | 2101 | 550 | 18 | $0E-$1F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_UDIV32_32` | 434.110992 | 151 | 2389 | 819 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; published game-math benchmark 2026-09-06 |
| `MATH_UMOD32_32` | 434.110992 | 151 | 2389 | 819 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; published game-math benchmark 2026-09-06 |
| `MATH_SDIV32_32` | 610.141565 | 75 | 2493 | 1005 | 0 | — | 0 | native signed private executable path | current native-signed division validation |
| `MATH_SMOD32_32` | 804.322022 | 75 | 2493 | 1005 | 0 | — | 0 | native signed private executable path | current native-signed division validation |
| `MATH_UMUL16_SHR8` | 314.965600 | 303 | 338 | 234 | 17 | $09-$19 | 0 | profile-selected resident implementation | 2026-09-14 post-upgrade deterministic comparison corpus |
| `MATH_SMUL16_SHR8` | 333.867232 | 301 | 366 | 299 | 17 | $09-$19 | 0 | FAST17 SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | 812.998853 | 725 | 938 | 1450 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | 762.606368 | 272 | 1849 | 1967 | 12 | $10-$1B | 0 | profile-selected resident implementation | V5 documented v2_pareto_fast path; published game-math benchmark 2026-09-06 |
| `MATH_SDIV16_SHL8` | 987.898146 | 319 | 2042 | 630 | 18 | $0E-$1F | 0 | native signed private executable path | current native-signed division validation |
| `MATH_URECIP16_Q16` | 119.577560 | 41 | 2079 | 1686 | 15 | $10-$1E | 0 | profile-selected resident implementation | V5 documented v2_pareto_fast path; published game-math benchmark 2026-09-06 |
| `MATH_SIN8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; published game-math benchmark 2026-09-06 |
| `MATH_COS8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; published game-math benchmark 2026-09-06 |
| `MATH_SINCOS8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; published game-math benchmark 2026-09-06 |
| `MATH_ATAN2_8` | 46.953064 | 30 | 48 | 97 | 0 | — | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; published game-math benchmark 2026-09-06 |
| `MATH_ISQRT16` | 219.740570 | 205 | 258 | 277 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; published game-math benchmark 2026-09-06 |
| `MATH_ISQRT32` | 1378.900969 | 1193 | 1656 | 496 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; published game-math benchmark 2026-09-06 |
| `MATH_DIST8_FAST` | 86.085602 | 68 | 104 | 67 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; published game-math benchmark 2026-09-06 |
| `MATH_DIST8_ACCURATE` | 92.085602 | 74 | 110 | 72 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; published game-math benchmark 2026-09-06 |
| `MATH_VEC2_NORMALIZE_Q8_8` | 198.770271 | 129 | 333 | 392 | 5 | $14;$1A-$1D | 0 | profile-selected resident implementation | 2026-09-18 normalize profile-parity deterministic corpus |

## Interpretation notes

- V1/V5 keep the 31-byte resident ZP contract. Their upgraded UMUL16/UMUL24 reuse that window and preserve `UMUL32_READY` state.
- V2-V4 use larger profile-selected ZP regions for some native signed/division kernels; per-routine ZP rows show the actual touched/owned set.
- V3/V4 Turbo16 owns 113 ZP bytes while active. Turbo32 now owns 135 ZP bytes (stack-free `ram135` compromise), down from the old 241-byte overlay.
- V4 QS16 owns `$10-$1F` (16 ZP bytes) while active.
- The PRG payload span includes address gaps in the load image and is not “occupied code bytes”. Use `SEGMENTS.csv` for physical segment placement and this table for per-entry reachable executable size.
