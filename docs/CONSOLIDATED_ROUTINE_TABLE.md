# Consolidated routine performance and memory table

Generated from the shipped reference images by `tools/generate_consolidated_routine_table.py`. This is the single cross-profile index for cycles and resource use. Canonical typed names follow `docs/NAMING_STANDARD.md`; legacy `MATH_*` symbols remain ABI-stable.

**Memory accounting.** `Code B` is the unique executable byte set statically reachable from that entry after `MATH_INIT`; shared callees therefore appear on multiple rows and **must not be summed**. `ZP B` is the concrete page-zero set executable/referenced by the path; Turbo/QS16 rows instead report their exclusive owned overlay. `Stack B` is persistent hardware-stack-page (`$0100-$01FF`) reservation. It is **0 for every shipped choice**; ordinary transient JSR/PHA return/data stack traffic is intentionally not counted. The absolute 606.337632-cycle UMUL32 record is therefore not a shipped fixed-profile kernel because it reserves stack-page space.

**Cycle accounting.** Mean cycles include the public routine through RTS and exclude the caller JSR/input stores. The `Basis` column identifies the validation corpus/model; specialized exact/canonical source files remain authoritative for their own corpora.

## Profile-level memory contracts

| Profile | PRG payload span B | REU image B | Declared shared ZP B | Stable API ZP union touched B | Stack-page reserved B |
|---|---:|---:|---:|---:|---:|
| `v1_balanced` | 49040 | 0 |  | 31 | 0 |
| `v2_pareto_fast` | 49040 | 0 |  | 190 | 0 |
| `v3_reu_512k` | 49040 | 524288 |  | 186 | 0 |
| `v4_reu_16m` | 49040 | 16777216 |  | 185 | 0 |
| `v5_hybrid_lowzp` | 49040 | 0 | 31 | 31 | 0 |

## v1_balanced

| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 90.494644 | 88 | 93 | 55 | 5 | $10-$14 | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | canonical harness |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 273.837200 | 262 | 297 | 208 | 17 | $09-$19 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 474.042329 | 444 | 530 | 357 | 24 | $09-$20 | 0 | FAST24 private 24-ZP carry producer; direct z0-z2 public output | 2026-10-06 UMUL24 direct-output validation |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 282.588064 | 250 | 316 | 259 | 17 | $09-$19 | 0 | FAST17 native signed composition with private 17-ZP magnitude core | current native-signed multiply validation |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 511.342357 | 451 | 568 | 485 | 24 | $09-$20 | 0 | FAST24 carry-primed signed dispatch with shared binder and dead pointer-low correction scratch; direct z0-z2 public output | 2026-10-07 SMUL24 carry-prime/direct-output validation |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 744.128269 | 660 | 873 | 1405 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | 725.808594 | 645 | 813 | 1386 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 59.571976 | 26 | 554 | 297 | 1 | $10 | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 132.725857 | 41 | 1535 | 326 | 2 | $10-$11 | 0 | balanced direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 194.156322 | 56 | 3235 | 1128 | 3 | $10-$12 | 0 | balanced direct-public 24-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 870.340206 | 182 | 2099 | 311 | 12 | $10-$1B | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD8` | `mod_u8_u8_u8` | 67.167555 | 51 | 495 | 83 | 2 | $10-$11 | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 184.082421 | 41 | 1535 | 326 | 2 | $10-$11 | 0 | balanced direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 303.233097 | 56 | 3235 | 1128 | 3 | $10-$12 | 0 | balanced direct-public 24-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 971.613651 | 185 | 1978 | 314 | 12 | $10-$1B | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 88.372650 | 26 | 600 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 187.131298 | 45 | 1604 | 425 | 6 | $10-$15 | 0 | balanced direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 313.583206 | 51 | 5583 | 462 | 6 | $10-$15 | 0 | balanced direct-output native signed 24-bit divider | current native-signed division validation |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 955.051690 | 171 | 2063 | 542 | 12 | $14-$1F | 0 | balanced private signed 32/16 magnitude path | current native-signed division validation |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 98.157813 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 229.324910 | 45 | 1604 | 425 | 6 | $10-$15 | 0 | balanced direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 427.272924 | 51 | 3502 | 462 | 6 | $10-$15 | 0 | balanced direct-output native signed 24-bit divider | current native-signed division validation |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 1061.083032 | 174 | 2066 | 545 | 12 | $14-$1F | 0 | balanced private signed 32/16 magnitude path | current native-signed division validation |
| `MATH_UMULDIV16` | `muldiv_u16_u16_u16_u32_16` | 1289.022331 | 513 | 2300 | 539 | 19 | $09-$1B | 0 | profile-selected resident implementation | 2026-10-07 MULDIV16 9,001-case all-profile/map validation |
| `MATH_SMULDIV16` | `muldiv_s16_s16_s16_s32_16` | 1378.300411 | 490 | 2271 | 821 | 23 | $09-$1F | 0 | profile-selected resident implementation | 2026-10-07 MULDIV16 9,001-case all-profile/map validation |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 428.554036 | 90 | 2423 | 946 | 0 | — | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 552.220863 | 90 | 2423 | 946 | 0 | — | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 566.839288 | 75 | 2454 | 971 | 0 | — | 0 | signed-private balanced 32/32 path | current native-signed division validation |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 766.253430 | 75 | 2454 | 971 | 0 | — | 0 | signed-private balanced 32/32 path | current native-signed division validation |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 304.804139 | 293 | 328 | 227 | 17 | $09-$19 | 0 | profile-selected resident implementation | 2026-10-06 MUL16 SHR8 register-return validation |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 313.154093 | 281 | 345 | 278 | 17 | $09-$19 | 0 | FAST17 SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 812.544371 | 725 | 938 | 1449 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 770.773617 | 182 | 1807 | 313 | 12 | $10-$1B | 0 | fixed-point adapter into selected unsigned 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 846.155071 | 180 | 1893 | 495 | 12 | $14-$1F | 0 | fixed-point adapter into balanced private signed 32/16 divider | current native-signed division validation |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 108.497635 | 41 | 1801 | 637 | 12 | $10-$1B | 0 | exact reciprocal ladder with selected profile division fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_COS8` | `cos_u8_s8` | 29.000000 | 29 | 29 | 18 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 39.000000 | 39 | 39 | 25 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 47.462814 | 33 | 50 | 97 | 0 | — | 0 | compact_opt signed-log kernel; two table pages; exact parity with prior compact outputs | 2026-10-06 exhaustive ATAN2 dispatch validation |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 219.740570 | 205 | 258 | 277 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1378.900969 | 1193 | 1656 | 496 | 0 | — | 0 | profile-selected resident implementation | current deterministic 4,130-case ISQRT32 benchmark |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 86.085602 | 68 | 104 | 67 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 92.085602 | 74 | 110 | 72 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 160.150080 | 84 | 302 | 881 | 4 | $1A-$1D | 0 | quadrant-specific paths; certified logarithmic ratio tables | 2026-09-21 normalize profile-parity deterministic corpus |
| `MATH_SEEK8_INIT` | `seek_u8_u8_init` | 601.746936 | 147 | 995 | 454 | 0 | — | 0 | exact bulk-Bresenham DDA setup; no multiply/divide; init scratch in V1_SCRATCH RAM | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP` | `seek_u8_u8_step` | 87.136511 | 77 | 91 | 176 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP_INT` | `seek_u8_u8_step_int` | 70.992770 | 61 | 74 | 96 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP1` | `seek_u8_u8_step1` | 65.953959 | 54 | 69 | 91 | 0 | — | 0 | NMOS DCP distance countdown; X-indexed per-slot state; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_INIT` | `seek_u16_u8_init` | 783.201389 | 202 | 1305 | 594 | 0 | — | 0 | exact bulk-Bresenham DDA setup; no multiply/divide; init scratch in V1_SCRATCH RAM | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP` | `seek_u16_u8_step` | 118.277360 | 102 | 150 | 282 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP_INT` | `seek_u16_u8_step_int` | 103.654782 | 85 | 132 | 152 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP1` | `seek_u16_u8_step1` | 98.183384 | 77 | 121 | 143 | 0 | — | 0 | NMOS DCP distance countdown; X-indexed per-slot state; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |

## v2_pareto_fast

| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 78.494614 | 77 | 80 | 54 | 5 | $39-$3D | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | canonical harness |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 216.980037 | 205 | 240 | 165 | 16 | $21-$30 | 0 | 16-ZP record-derived fused quarter-square core; A=x1 public entry and direct Z0 output | 2026-10-06 UMUL16 direct-output validation |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 421.555502 | 392 | 477 | 360 | 24 | $21-$38 | 0 | 24-ZP reverse_24zp_carry resident kernel; direct z0-z3 public output with tail-written z4-z5 | 2026-10-06 UMUL24 direct-output validation |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 690.235367 | 630 | 809 | 320 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29-derived private q0 unsigned producer; all six pointer pairs persist in profile-owned ZP holes, eliminating the ordinary mixed-call rebind | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | 697.175781 | 642 | 784 | 320 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29-derived private q0 unsigned producer; all six pointer pairs persist in profile-owned ZP holes, eliminating the ordinary mixed-call rebind | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 245.802333 | 223 | 286 | 213 | 111 | $82-$F0 | 0 | 116-ZP practical native signed quarter-square kernel (retained after FAST17 comparison) | current native-signed multiply validation |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 467.342357 | 407 | 524 | 453 | 24 | $21-$38 | 0 | FAST24 carry-primed signed dispatch with shared binder and dead pointer-low correction scratch; direct z0-z2 public output | 2026-10-07 SMUL24 carry-prime/direct-output validation |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 711.153591 | 630 | 838 | 1371 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 native signed quadrant composition; all six pointer pairs persist in profile-owned ZP holes; direct stable entry eliminates the legacy self-redirect | current native-signed multiply validation |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | 723.100586 | 641 | 798 | 1374 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 native signed quadrant composition; all six pointer pairs persist in profile-owned ZP holes; direct stable entry eliminates the legacy self-redirect | current native-signed multiply validation |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 59.383011 | 26 | 634 | 433 | 1 | $10 | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 127.773827 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 154.338944 | 56 | 1414 | 3539 | 10 | $10-$19 | 0 | Repose q0-counter/direct-public UDIV24 | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 631.739323 | 125 | 1738 | 2025 | 10 | $10-$19 | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD8` | `mod_u8_u8_u8` | 67.284844 | 51 | 495 | 131 | 2 | $10-$11 | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 195.951706 | 32 | 1075 | 1446 | 0 | — | 0 | remainder-only q=0/q=1 front end with exact shared UDIV16 fallback | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 205.325821 | 42 | 1419 | 3557 | 10 | $10-$19 | 0 | remainder-only q=0/q=1 front end with exact Repose UDIV24 fallback | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 629.783001 | 128 | 1741 | 2028 | 10 | $10-$19 | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 88.372650 | 26 | 600 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 168.393021 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 248.344384 | 57 | 3339 | 1570 | 9 | $10-$18 | 0 | fast direct-output native signed 24-bit divider | current native-signed division validation |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 724.392148 | 110 | 1600 | 2182 | 10 | $10-$19 | 0 | thin signed front end around profile-selected UDIV32/16 magnitude substrate | current native-signed division validation |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 97.066406 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 231.872202 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 337.075090 | 57 | 3339 | 1570 | 9 | $10-$18 | 0 | fast direct-output native signed 24-bit divider | current native-signed division validation |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 710.773285 | 113 | 1635 | 2185 | 10 | $10-$19 | 0 | thin signed front end around profile-selected UDIV32/16 magnitude substrate | current native-signed division validation |
| `MATH_UMULDIV16` | `muldiv_u16_u16_u16_u32_16` | 801.646373 | 301 | 1923 | 2173 | 26 | $10-$19;$21-$30 | 0 | profile-selected resident implementation | 2026-10-07 MULDIV16 9,001-case all-profile/map validation |
| `MATH_SMULDIV16` | `muldiv_s16_s16_s16_s32_16` | 860.448172 | 83 | 1869 | 2457 | 26 | $10-$19;$21-$30 | 0 | profile-selected resident implementation | 2026-10-07 MULDIV16 9,001-case all-profile/map validation |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 212.304220 | 72 | 1792 | 2755 | 14 | $10-$19;$53-$56 | 0 | Repose live-high four-ZP divider with preserved narrow-divisor fast paths | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 290.452028 | 72 | 1829 | 2857 | 14 | $10-$19;$53-$56 | 0 | remainder-only compare/q=0-equality front end with Repose live-high four-ZP UDIV32 fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 420.452435 | 141 | 1835 | 3018 | 14 | $10-$19;$53-$56 | 0 | signed normalize/restore wrapper around profile-selected public UDIV32/32 core | current native-signed division validation |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 453.633213 | 141 | 1723 | 3018 | 14 | $10-$19;$53-$56 | 0 | signed normalize/restore wrapper around profile-selected public UDIV32/32 core | current native-signed division validation |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 243.804139 | 232 | 267 | 181 | 16 | $21-$30 | 0 | profile-selected resident implementation | 2026-10-06 MUL16 SHR8 register-return validation |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 276.888787 | 254 | 317 | 232 | 111 | $82-$F0 | 0 | 116-ZP practical native SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 757.876404 | 695 | 874 | 364 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 persistent-pointer UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 780.302454 | 695 | 903 | 1415 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 persistent-pointer direct-entry SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 552.649695 | 122 | 918 | 2024 | 10 | $10-$19 | 0 | fixed-point adapter into selected unsigned 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 630.032715 | 107 | 971 | 2153 | 10 | $10-$19 | 0 | thin signed fixed-point front end around selected UDIV32/16 magnitude substrate | current native-signed division validation |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 94.822998 | 41 | 947 | 2348 | 10 | $10-$19 | 0 | exact reciprocal ladder with selected profile division fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_COS8` | `cos_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 43.970627 | 31 | 45 | 88 | 0 | — | 0 | sum_fast carry-clearing signed-log kernel; four table pages; exact parity with prior fast outputs | 2026-10-06 exhaustive ATAN2 dispatch validation |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 205.760590 | 193 | 246 | 259 | 1 | $66 | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1198.619613 | 1052 | 1428 | 440 | 10 | $54-$5C;$66 | 0 | profile-selected resident implementation | current deterministic 4,130-case ISQRT32 benchmark |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 79.570038 | 64 | 95 | 58 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 85.570038 | 70 | 101 | 63 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 160.150080 | 84 | 302 | 881 | 4 | $1A-$1D | 0 | quadrant-specific paths; certified logarithmic ratio tables | 2026-09-21 normalize profile-parity deterministic corpus |
| `MATH_SEEK8_INIT` | `seek_u8_u8_init` | 543.965482 | 137 | 888 | 392 | 14 | $53-$5F;$65 | 0 | exact bulk-Bresenham DDA setup; no multiply/divide; init scratch in game-scratch ZP | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP` | `seek_u8_u8_step` | 87.136511 | 77 | 91 | 176 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP_INT` | `seek_u8_u8_step_int` | 70.992770 | 61 | 74 | 96 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP1` | `seek_u8_u8_step1` | 65.953959 | 54 | 69 | 91 | 0 | — | 0 | NMOS DCP distance countdown; X-indexed per-slot state; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_INIT` | `seek_u16_u8_init` | 702.713848 | 187 | 1150 | 503 | 18 | $53-$64 | 0 | exact bulk-Bresenham DDA setup; no multiply/divide; init scratch in game-scratch ZP | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP` | `seek_u16_u8_step` | 118.688882 | 102 | 150 | 282 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP_INT` | `seek_u16_u8_step_int` | 103.654782 | 85 | 132 | 152 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP1` | `seek_u16_u8_step1` | 98.183384 | 77 | 121 | 143 | 0 | — | 0 | NMOS DCP distance countdown; X-indexed per-slot state; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |

## v3_reu_512k

| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 69.000000 |  |  | 49 | 0 | — | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | REU transport model |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 216.980037 | 205 | 240 | 165 | 16 | $21-$30 | 0 | 16-ZP record-derived fused quarter-square core; A=x1 public entry and direct Z0 output | 2026-10-06 UMUL16 direct-output validation |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 421.555502 | 392 | 477 | 360 | 24 | $21-$38 | 0 | 24-ZP reverse_24zp_carry resident kernel; direct z0-z3 public output with tail-written z4-z5 | 2026-10-06 UMUL24 direct-output validation |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 690.235367 | 630 | 809 | 320 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29-derived private q0 unsigned producer; all six pointer pairs persist in profile-owned ZP holes, eliminating the ordinary mixed-call rebind | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | 697.175781 | 642 | 784 | 320 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29-derived private q0 unsigned producer; all six pointer pairs persist in profile-owned ZP holes, eliminating the ordinary mixed-call rebind | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 246.107696 | 223 | 286 | 213 | 111 | $82-$F0 | 0 | 116-ZP practical native signed quarter-square kernel (retained after FAST17 comparison) | current native-signed multiply validation |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 467.342357 | 407 | 524 | 453 | 24 | $21-$38 | 0 | FAST24 carry-primed signed dispatch with shared binder and dead pointer-low correction scratch; direct z0-z2 public output | 2026-10-07 SMUL24 carry-prime/direct-output validation |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 711.447073 | 630 | 838 | 1371 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 native signed quadrant composition; all six pointer pairs persist in profile-owned ZP holes; direct stable entry eliminates the legacy self-redirect | current native-signed multiply validation |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | 723.534180 | 644 | 812 | 1374 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 native signed quadrant composition; all six pointer pairs persist in profile-owned ZP holes; direct stable entry eliminates the legacy self-redirect | current native-signed multiply validation |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 52.852264 | 28 | 115 | 136 | 0 | — | 0 | hybrid q=0..3 CPU fast path with exact REU quotient/remainder fallback | 2026-10-06 exhaustive REU UDIV8 hybrid validation |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 125.423943 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 161.653272 | 56 | 1414 | 3539 | 10 | $10-$19 | 0 | Repose q0-counter/direct-public UDIV24 | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 632.886598 | 125 | 1738 | 2025 | 10 | $10-$19 | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD8` | `mod_u8_u8_u8` | 49.712110 | 32 | 50 | 42 | 0 | — | 0 | REU direct remainder plane retained; hybrid UDIV8 selected separately | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 196.414681 | 32 | 1075 | 1446 | 0 | — | 0 | remainder-only q=0/q=1 front end with exact shared UDIV16 fallback | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 207.136510 | 42 | 1419 | 3557 | 10 | $10-$19 | 0 | remainder-only q=0/q=1 front end with exact Repose UDIV24 fallback | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 625.840953 | 128 | 1741 | 2028 | 10 | $10-$19 | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 88.372650 | 26 | 600 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 170.582116 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 236.810251 | 68 | 3314 | 1894 | 9 | $10-$18 | 0 | Repose-derived direct-output native signed 24-bit divider with private magnitude engine | current native-signed division validation |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 724.449509 | 110 | 1669 | 2182 | 10 | $10-$19 | 0 | thin signed front end around profile-selected UDIV32/16 magnitude substrate | current native-signed division validation |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 97.152344 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 234.659206 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 329.971841 | 68 | 3314 | 1894 | 9 | $10-$18 | 0 | Repose-derived direct-output native signed 24-bit divider with private magnitude engine | current native-signed division validation |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 710.713357 | 113 | 1671 | 2185 | 10 | $10-$19 | 0 | thin signed front end around profile-selected UDIV32/16 magnitude substrate | current native-signed division validation |
| `MATH_UMULDIV16` | `muldiv_u16_u16_u16_u32_16` | 801.646373 | 301 | 1923 | 2173 | 26 | $10-$19;$21-$30 | 0 | profile-selected resident implementation | 2026-10-07 MULDIV16 9,001-case all-profile/map validation |
| `MATH_SMULDIV16` | `muldiv_s16_s16_s16_s32_16` | 860.448172 | 83 | 1869 | 2457 | 26 | $10-$19;$21-$30 | 0 | profile-selected resident implementation | 2026-10-07 MULDIV16 9,001-case all-profile/map validation |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 203.864138 | 72 | 1792 | 2755 | 14 | $10-$19;$53-$56 | 0 | Repose live-high four-ZP divider with preserved narrow-divisor fast paths | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 287.455248 | 72 | 1829 | 2857 | 14 | $10-$19;$53-$56 | 0 | remainder-only compare/q=0-equality front end with Repose live-high four-ZP UDIV32 fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 416.865672 | 141 | 1849 | 3018 | 14 | $10-$19;$53-$56 | 0 | signed normalize/restore wrapper around profile-selected public UDIV32/32 core | current native-signed division validation |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 443.528520 | 141 | 1450 | 3018 | 14 | $10-$19;$53-$56 | 0 | signed normalize/restore wrapper around profile-selected public UDIV32/32 core | current native-signed division validation |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 243.804139 | 232 | 267 | 181 | 16 | $21-$30 | 0 | profile-selected resident implementation | 2026-10-06 MUL16 SHR8 register-return validation |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 276.888787 | 254 | 317 | 232 | 111 | $82-$F0 | 0 | 116-ZP practical native SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 757.876404 | 695 | 874 | 364 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 persistent-pointer UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 780.302454 | 695 | 903 | 1415 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 persistent-pointer direct-entry SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 553.124974 | 122 | 918 | 2024 | 10 | $10-$19 | 0 | fixed-point adapter into selected unsigned 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 630.265213 | 107 | 971 | 2153 | 10 | $10-$19 | 0 | thin signed fixed-point front end around selected UDIV32/16 magnitude substrate | current native-signed division validation |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 66.233795 | 41 | 239 | 430 | 0 | — | 0 | exact reciprocal ladder with selected profile division fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_COS8` | `cos_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 43.970627 | 31 | 45 | 88 | 0 | — | 0 | sum_fast carry-clearing signed-log kernel; four table pages; exact parity with prior fast outputs | 2026-10-06 exhaustive ATAN2 dispatch validation |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 204.992523 | 192 | 246 | 259 | 1 | $66 | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1197.859322 | 1051 | 1428 | 440 | 10 | $54-$5C;$66 | 0 | profile-selected resident implementation | current deterministic 4,130-case ISQRT32 benchmark |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 79.070038 | 63 | 95 | 58 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 85.070038 | 69 | 101 | 63 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 156.661198 | 84 | 298 | 849 | 4 | $1A-$1D | 0 | quadrant-specific paths; existing REU ratio-index lookup | 2026-09-21 normalize profile-parity deterministic corpus |
| `MATH_SEEK8_INIT` | `seek_u8_u8_init` | 544.686887 | 137 | 890 | 392 | 14 | $53-$5F;$65 | 0 | exact bulk-Bresenham DDA setup; no multiply/divide; init scratch in game-scratch ZP | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP` | `seek_u8_u8_step` | 87.136511 | 77 | 91 | 176 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP_INT` | `seek_u8_u8_step_int` | 70.992770 | 61 | 74 | 96 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP1` | `seek_u8_u8_step1` | 65.953959 | 54 | 69 | 91 | 0 | — | 0 | NMOS DCP distance countdown; X-indexed per-slot state; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_INIT` | `seek_u16_u8_init` | 701.543505 | 187 | 1150 | 503 | 18 | $53-$64 | 0 | exact bulk-Bresenham DDA setup; no multiply/divide; init scratch in game-scratch ZP | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP` | `seek_u16_u8_step` | 118.277360 | 102 | 150 | 282 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP_INT` | `seek_u16_u8_step_int` | 103.654782 | 85 | 132 | 152 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP1` | `seek_u16_u8_step1` | 98.183384 | 77 | 121 | 143 | 0 | — | 0 | NMOS DCP distance countdown; X-indexed per-slot state; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_REU_UMUL16_BEGIN` | `mul_u16_u16_u32_turbo_begin` | 300.000000 | 300 | 300 | 41 | 122 | $3E-$B7 | 0 | 122-ZP direct-output Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16` | `mul_u16_u16_u32_turbo` | 197.046257 | 185 | 220 | 248 | 122 | $3E-$B7 | 0 | 122-ZP direct-output Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16_END` | `mul_u16_u16_u32_turbo_end` | 345.000000 | 345 | 345 | 73 | 122 | $3E-$B7 | 0 | 122-ZP direct-output Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_BEGIN` | `mul_u32_u32_u64_turbo_begin` | 326.000000 | 326 | 326 | 41 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32` | `mul_u32_u32_u64_turbo` | 676.185219 | 613 | 788 | 357 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_END` | `mul_u32_u32_u64_turbo_end` | 371.000000 | 371 | 371 | 73 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |

## v4_reu_16m

| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 69.000000 |  |  | 49 | 0 | — | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | unchanged V3 path/evidence |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 216.980037 | 205 | 240 | 165 | 16 | $21-$30 | 0 | 16-ZP record-derived fused quarter-square core; A=x1 public entry and direct Z0 output | 2026-10-06 UMUL16 direct-output validation |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 421.555502 | 392 | 477 | 360 | 24 | $21-$38 | 0 | 24-ZP reverse_24zp_carry resident kernel; direct z0-z3 public output with tail-written z4-z5 | 2026-10-06 UMUL24 direct-output validation |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 690.235367 | 630 | 809 | 320 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29-derived private q0 unsigned producer; all six pointer pairs persist in profile-owned ZP holes, eliminating the ordinary mixed-call rebind | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | 697.175781 | 642 | 784 | 320 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29-derived private q0 unsigned producer; all six pointer pairs persist in profile-owned ZP holes, eliminating the ordinary mixed-call rebind | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 246.144492 | 223 | 286 | 213 | 111 | $82-$F0 | 0 | 116-ZP practical native signed quarter-square kernel (retained after FAST17 comparison) | current native-signed multiply validation |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 467.342357 | 407 | 524 | 453 | 24 | $21-$38 | 0 | FAST24 carry-primed signed dispatch with shared binder and dead pointer-low correction scratch; direct z0-z2 public output | 2026-10-07 SMUL24 carry-prime/direct-output validation |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 711.706102 | 630 | 838 | 1371 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 native signed quadrant composition; all six pointer pairs persist in profile-owned ZP holes; direct stable entry eliminates the legacy self-redirect | current native-signed multiply validation |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | 721.444336 | 641 | 816 | 1374 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 native signed quadrant composition; all six pointer pairs persist in profile-owned ZP holes; direct stable entry eliminates the legacy self-redirect | current native-signed multiply validation |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 52.852264 | 28 | 115 | 136 | 0 | — | 0 | hybrid q=0..3 CPU fast path with exact REU quotient/remainder fallback | 2026-10-06 exhaustive REU UDIV8 hybrid validation |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 125.625710 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 158.507048 | 56 | 1414 | 3539 | 10 | $10-$19 | 0 | Repose q0-counter/direct-public UDIV24 | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 634.698506 | 125 | 1738 | 2025 | 10 | $10-$19 | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD8` | `mod_u8_u8_u8` | 49.725819 | 32 | 50 | 42 | 0 | — | 0 | REU direct remainder plane retained; hybrid UDIV8 selected separately | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 195.529942 | 32 | 1075 | 1446 | 0 | — | 0 | remainder-only q=0/q=1 front end with exact shared UDIV16 fallback | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 205.247263 | 42 | 1419 | 3557 | 10 | $10-$19 | 0 | remainder-only q=0/q=1 front end with exact Repose UDIV24 fallback | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 626.014810 | 128 | 1741 | 2028 | 10 | $10-$19 | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 89.009821 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 168.745038 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 237.569466 | 68 | 3314 | 1894 | 9 | $10-$18 | 0 | Repose-derived direct-output native signed 24-bit divider with private magnitude engine | current native-signed division validation |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 721.003490 | 110 | 1633 | 2182 | 10 | $10-$19 | 0 | thin signed front end around profile-selected UDIV32/16 magnitude substrate | current native-signed division validation |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 99.020313 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 228.244765 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 326.184838 | 68 | 3314 | 1894 | 9 | $10-$18 | 0 | Repose-derived direct-output native signed 24-bit divider with private magnitude engine | current native-signed division validation |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 708.426715 | 113 | 1601 | 2185 | 10 | $10-$19 | 0 | thin signed front end around profile-selected UDIV32/16 magnitude substrate | current native-signed division validation |
| `MATH_UMULDIV16` | `muldiv_u16_u16_u16_u32_16` | 801.646373 | 301 | 1923 | 2173 | 26 | $10-$19;$21-$30 | 0 | profile-selected resident implementation | 2026-10-07 MULDIV16 9,001-case all-profile/map validation |
| `MATH_SMULDIV16` | `muldiv_s16_s16_s16_s32_16` | 860.448172 | 83 | 1869 | 2457 | 26 | $10-$19;$21-$30 | 0 | profile-selected resident implementation | 2026-10-07 MULDIV16 9,001-case all-profile/map validation |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 209.625349 | 72 | 2044 | 2755 | 14 | $10-$19;$53-$56 | 0 | Repose live-high four-ZP divider with preserved narrow-divisor fast paths | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 285.637476 | 72 | 1829 | 2857 | 14 | $10-$19;$53-$56 | 0 | remainder-only compare/q=0-equality front end with Repose live-high four-ZP UDIV32 fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 418.153927 | 141 | 2056 | 3018 | 14 | $10-$19;$53-$56 | 0 | signed normalize/restore wrapper around profile-selected public UDIV32/32 core | current native-signed division validation |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 458.087365 | 141 | 2113 | 3018 | 14 | $10-$19;$53-$56 | 0 | signed normalize/restore wrapper around profile-selected public UDIV32/32 core | current native-signed division validation |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 243.804139 | 232 | 267 | 181 | 16 | $21-$30 | 0 | profile-selected resident implementation | 2026-10-06 MUL16 SHR8 register-return validation |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 276.888787 | 254 | 317 | 232 | 111 | $82-$F0 | 0 | 116-ZP practical native SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 757.876404 | 695 | 874 | 364 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 persistent-pointer UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 780.302454 | 695 | 903 | 1415 | 31 | $0E-$20;$3D-$42;$4F-$52;$68-$69 | 0 | FAST31/V29 persistent-pointer direct-entry SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 552.577740 | 122 | 918 | 2024 | 10 | $10-$19 | 0 | fixed-point adapter into selected unsigned 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 628.417884 | 107 | 971 | 2153 | 10 | $10-$19 | 0 | thin signed fixed-point front end around selected UDIV32/16 magnitude substrate | current native-signed division validation |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 66.233795 | 41 | 239 | 430 | 0 | — | 0 | exact reciprocal ladder with selected profile division fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_COS8` | `cos_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 48.000000 | 48 | 48 | 33 | 0 | — | 0 | exact signed-byte phase plane in REU bank 8 | 2026-10-06 exhaustive ATAN2 dispatch validation |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 54.000000 | 54 | 54 | 38 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 917.317433 | 806 | 1067 | 236 | 8 | $54-$5B | 0 | exact 4 MiB REU prefix accelerator plus restoring low-bit refinement | current deterministic 4,130-case ISQRT32 benchmark |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 79.070038 | 63 | 95 | 58 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 85.070038 | 69 | 101 | 63 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 156.661198 | 84 | 298 | 849 | 4 | $1A-$1D | 0 | quadrant-specific paths; existing REU ratio-index lookup | 2026-09-21 normalize profile-parity deterministic corpus |
| `MATH_SEEK8_INIT` | `seek_u8_u8_init` | 544.686887 | 137 | 890 | 392 | 14 | $53-$5F;$65 | 0 | exact bulk-Bresenham DDA setup; no multiply/divide; init scratch in game-scratch ZP | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP` | `seek_u8_u8_step` | 87.136511 | 77 | 91 | 176 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP_INT` | `seek_u8_u8_step_int` | 70.992770 | 61 | 74 | 96 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP1` | `seek_u8_u8_step1` | 65.953959 | 54 | 69 | 91 | 0 | — | 0 | NMOS DCP distance countdown; X-indexed per-slot state; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_INIT` | `seek_u16_u8_init` | 701.543505 | 187 | 1150 | 503 | 18 | $53-$64 | 0 | exact bulk-Bresenham DDA setup; no multiply/divide; init scratch in game-scratch ZP | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP` | `seek_u16_u8_step` | 118.277360 | 102 | 150 | 282 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP_INT` | `seek_u16_u8_step_int` | 103.654782 | 85 | 132 | 152 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP1` | `seek_u16_u8_step1` | 98.183384 | 77 | 121 | 143 | 0 | — | 0 | NMOS DCP distance countdown; X-indexed per-slot state; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_REU_UMUL16_BEGIN` | `mul_u16_u16_u32_turbo_begin` | 300.000000 | 300 | 300 | 41 | 122 | $3E-$B7 | 0 | 122-ZP direct-output Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16` | `mul_u16_u16_u32_turbo` | 197.046257 | 185 | 220 | 248 | 122 | $3E-$B7 | 0 | 122-ZP direct-output Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16_END` | `mul_u16_u16_u32_turbo_end` | 345.000000 | 345 | 345 | 73 | 122 | $3E-$B7 | 0 | 122-ZP direct-output Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_BEGIN` | `mul_u32_u32_u64_turbo_begin` | 326.000000 | 326 | 326 | 41 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32` | `mul_u32_u32_u64_turbo` | 676.185219 | 613 | 788 | 357 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_END` | `mul_u32_u32_u64_turbo_end` | 371.000000 | 371 | 371 | 73 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_QS16_BEGIN` | `mul_u16_u16_u32_qs16_begin` | 18.000000 | 18 | 18 | 11 | 16 | $10-$1F | 0 | V4 16MiB QS16 mode | V4 QS16 source/exact timing classes |
| `MATH_REU_QS16` | `mul_u16_u16_u32_qs16` | 281.541031 | 279 | 293 | 209 | 16 | $10-$1F | 0 | V4 16MiB QS16 mode | V4 QS16 source/exact timing classes |
| `MATH_REU_QS16_END` | `mul_u16_u16_u32_qs16_end` | 18.000000 | 18 | 18 | 11 | 16 | $10-$1F | 0 | V4 16MiB QS16 mode | V4 QS16 source/exact timing classes |

## v5_hybrid_lowzp

| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 90.494644 | 88 | 93 | 55 | 5 | $10-$14 | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | V5 documented v1_balanced path; canonical harness |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 273.837200 | 262 | 297 | 208 | 17 | $09-$19 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel | V5 documented v1_balanced path; 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 474.042329 | 444 | 530 | 357 | 24 | $09-$20 | 0 | FAST24 private 24-ZP carry producer; direct z0-z2 public output | 2026-10-06 UMUL24 direct-output validation |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 282.262957 | 250 | 314 | 259 | 17 | $09-$19 | 0 | FAST17 native signed composition with private 17-ZP magnitude core | current native-signed multiply validation |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 511.342357 | 451 | 568 | 485 | 24 | $09-$20 | 0 | FAST24 carry-primed signed dispatch with shared binder and dead pointer-low correction scratch; direct z0-z2 public output | 2026-10-07 SMUL24 carry-prime/direct-output validation |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 743.477377 | 660 | 873 | 1405 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | 726.260742 | 640 | 807 | 1386 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 59.383011 | 26 | 634 | 433 | 1 | $10 | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 126.385862 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider; V5 repacked into hybrid private RAM | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 157.776141 | 56 | 1414 | 3539 | 10 | $10-$19 | 0 | Repose q0-counter/direct-public UDIV24; V5 repacked hybrid copy | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 634.079529 | 125 | 1738 | 2025 | 10 | $10-$19 | 0 | V2 certified 32/16 divider imported into V5 hybrid private RAM | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD8` | `mod_u8_u8_u8` | 68.523229 | 51 | 495 | 131 | 2 | $10-$11 | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 199.918867 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider; V5 repacked into hybrid private RAM | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 211.248551 | 56 | 1414 | 3539 | 10 | $10-$19 | 0 | Repose q0-counter/direct-public UDIV24; V5 repacked hybrid copy | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 626.658725 | 128 | 1741 | 2028 | 10 | $10-$19 | 0 | V2 certified 32/16 divider imported into V5 hybrid private RAM | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 90.272098 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 170.631189 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider; V5 repacked under 31-ZP contract | current native-signed division validation |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 253.487023 | 57 | 3339 | 1570 | 9 | $10-$18 | 0 | fast direct-output native signed 24-bit divider repacked under V5 31-ZP contract | current native-signed division validation |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 722.170774 | 107 | 1676 | 2179 | 10 | $10-$19 | 0 | thin signed front end around relocated V2 UDIV32/16 magnitude substrate under the 31-ZP contract | current native-signed division validation |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 96.707813 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 231.667148 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider; V5 repacked under 31-ZP contract | current native-signed division validation |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 339.607942 | 57 | 3339 | 1570 | 9 | $10-$18 | 0 | fast direct-output native signed 24-bit divider repacked under V5 31-ZP contract | current native-signed division validation |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 704.786282 | 107 | 1642 | 2179 | 10 | $10-$19 | 0 | thin signed front end around relocated V2 UDIV32/16 magnitude substrate under the 31-ZP contract | current native-signed division validation |
| `MATH_UMULDIV16` | `muldiv_u16_u16_u16_u32_16` | 834.646373 | 334 | 1956 | 2197 | 17 | $09-$19 | 0 | profile-selected resident implementation | 2026-10-07 MULDIV16 9,001-case all-profile/map validation |
| `MATH_SMULDIV16` | `muldiv_s16_s16_s16_s32_16` | 888.154427 | 83 | 1899 | 2473 | 17 | $09-$19 | 0 | profile-selected resident implementation | 2026-10-07 MULDIV16 9,001-case all-profile/map validation |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 421.077342 | 90 | 2423 | 946 | 0 | — | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 548.000000 | 90 | 2423 | 946 | 0 | — | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 572.005880 | 75 | 2454 | 971 | 0 | — | 0 | signed-private balanced 32/32 path | current native-signed division validation |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 765.857040 | 75 | 2454 | 971 | 0 | — | 0 | signed-private balanced 32/32 path | current native-signed division validation |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 304.804139 | 293 | 328 | 227 | 17 | $09-$19 | 0 | profile-selected resident implementation | 2026-10-06 MUL16 SHR8 register-return validation |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 313.154093 | 281 | 345 | 278 | 17 | $09-$19 | 0 | FAST17 SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 812.544371 | 725 | 938 | 1449 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 553.298759 | 122 | 918 | 2024 | 10 | $10-$19 | 0 | fixed-point adapter into selected unsigned 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 628.885496 | 118 | 968 | 2164 | 10 | $10-$19 | 0 | thin signed fixed-point front end around selected UDIV32/16 magnitude substrate | current native-signed division validation |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 95.044128 | 41 | 950 | 2351 | 10 | $10-$19 | 0 | exact reciprocal ladder with selected profile division fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; current exhaustive/profile game-math benchmark |
| `MATH_COS8` | `cos_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; current exhaustive/profile game-math benchmark |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; current exhaustive/profile game-math benchmark |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 43.970627 | 31 | 45 | 88 | 0 | — | 0 | V2 sum_fast kernel imported into V5 with four private table pages | 2026-10-06 exhaustive ATAN2 dispatch validation |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 219.740570 | 205 | 258 | 277 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; current exhaustive/profile game-math benchmark |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1378.900969 | 1193 | 1656 | 496 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; current deterministic 4,130-case ISQRT32 benchmark |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 86.085602 | 68 | 104 | 67 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; current exhaustive/profile game-math benchmark |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 92.085602 | 74 | 110 | 72 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; current exhaustive/profile game-math benchmark |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 160.150080 | 84 | 302 | 881 | 4 | $1A-$1D | 0 | quadrant-specific paths; certified logarithmic ratio tables | 2026-09-21 normalize profile-parity deterministic corpus |
| `MATH_SEEK8_INIT` | `seek_u8_u8_init` | 601.746936 | 147 | 995 | 454 | 0 | — | 0 | exact bulk-Bresenham DDA setup; no multiply/divide; init scratch in V1_SCRATCH RAM | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP` | `seek_u8_u8_step` | 87.136511 | 77 | 91 | 176 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP_INT` | `seek_u8_u8_step_int` | 70.992770 | 61 | 74 | 96 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK8_STEP1` | `seek_u8_u8_step1` | 65.953959 | 54 | 69 | 91 | 0 | — | 0 | NMOS DCP distance countdown; X-indexed per-slot state; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_INIT` | `seek_u16_u8_init` | 783.201389 | 202 | 1305 | 594 | 0 | — | 0 | exact bulk-Bresenham DDA setup; no multiply/divide; init scratch in V1_SCRATCH RAM | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP` | `seek_u16_u8_step` | 118.277360 | 102 | 150 | 282 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP_INT` | `seek_u16_u8_step_int` | 103.654782 | 85 | 132 | 152 | 0 | — | 0 | X-indexed per-slot state; carries pre-biased into stored deltas; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |
| `MATH_SEEK16_STEP1` | `seek_u16_u8_step1` | 98.183384 | 77 | 121 | 143 | 0 | — | 0 | NMOS DCP distance countdown; X-indexed per-slot state; exact arrival | 2026-09-25 seek profile benchmark (408 moves x speeds; every frame verified) |

## Interpretation notes

- V1/V5 keep the 31-byte resident ZP contract. Their upgraded UMUL16/UMUL24 reuse that window and preserve `UMUL32_READY` state.
- V2-V4 use larger profile-selected ZP regions for some native signed/division kernels; per-routine ZP rows show the actual touched/owned set.
- V3/V4 Turbo16 owns 122 ZP bytes while active. Turbo32 now owns 135 ZP bytes (stack-free `ram135` compromise), down from the old 241-byte overlay.
- V4 QS16 owns `$10-$1F` (16 ZP bytes) while active.
- The PRG payload span includes address gaps in the load image and is not “occupied code bytes”. Use `SEGMENTS.csv` for physical segment placement and this table for per-entry reachable executable size.
