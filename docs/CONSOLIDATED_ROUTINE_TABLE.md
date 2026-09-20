# Consolidated routine performance and memory table

Generated from the shipped reference images by `tools/generate_consolidated_routine_table.py`. This is the single cross-profile index for cycles and resource use. Canonical typed names follow `docs/NAMING_STANDARD.md`; legacy `MATH_*` symbols remain ABI-stable.

**Memory accounting.** `Code B` is the unique executable byte set statically reachable from that entry after `MATH_INIT`; shared callees therefore appear on multiple rows and **must not be summed**. `ZP B` is the concrete page-zero set executable/referenced by the path; Turbo/QS16 rows instead report their exclusive owned overlay. `Stack B` is persistent hardware-stack-page (`$0100-$01FF`) reservation. It is **0 for every shipped choice**; ordinary transient JSR/PHA return/data stack traffic is intentionally not counted. The absolute 606.337632-cycle UMUL32 record is therefore not a shipped fixed-profile kernel because it reserves stack-page space.

**Cycle accounting.** Mean cycles include the public routine through RTS and exclude the caller JSR/input stores. The `Basis` column identifies the validation corpus/model; specialized exact/canonical source files remain authoritative for their own corpora.

## Profile-level memory contracts

| Profile | PRG payload span B | REU image B | Declared shared ZP B | Stable API ZP union touched B | Stack-page reserved B |
|---|---:|---:|---:|---:|---:|
| `v1_balanced` | 44951 | 0 |  | 31 | 0 |
| `v2_pareto_fast` | 44951 | 0 |  | 207 | 0 |
| `v3_reu_512k` | 49047 | 524288 |  | 196 | 0 |
| `v4_reu_16m` | 49047 | 16777216 |  | 195 | 0 |
| `v5_hybrid_lowzp` | 44951 | 0 | 31 | 31 | 0 |

## v1_balanced

| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 90.494644 | 88 | 93 | 55 | 5 | $10-$14 | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | canonical harness |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 273.837200 | 262 | 297 | 208 | 17 | $09-$19 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 489.988792 | 462 | 542 | 369 | 24 | $09-$20 | 0 | FAST24 private 24-ZP carry producer with stable public adapter | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 293.298407 | 260 | 327 | 273 | 17 | $09-$19 | 0 | FAST17 native signed composition with private 17-ZP magnitude core | current native-signed multiply validation |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 531.496472 | 474 | 591 | 505 | 24 | $09-$20 | 0 | FAST24 four-quadrant native signed composition; immutable quarter-square tables shared | current native-signed multiply validation |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 744.569946 | 660 | 873 | 1406 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | 726.388672 | 645 | 813 | 1387 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
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
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 955.051690 | 171 | 2063 | 542 | 12 | $14-$1F | 0 | direct-output native signed 32/16 divider | current native-signed division validation |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 98.157813 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 229.324910 | 45 | 1604 | 425 | 6 | $10-$15 | 0 | balanced direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 427.272924 | 51 | 3502 | 462 | 6 | $10-$15 | 0 | balanced direct-output native signed 24-bit divider | current native-signed division validation |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 1061.083032 | 174 | 2066 | 545 | 12 | $14-$1F | 0 | direct-output native signed 32/16 divider | current native-signed division validation |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 428.554036 | 90 | 2423 | 946 | 0 | — | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 552.220863 | 90 | 2423 | 946 | 0 | — | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 586.396050 | 75 | 2474 | 987 | 0 | — | 0 | native signed 32/32 magnitude path with redundant zero-test removed | current native-signed division validation |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 785.979061 | 75 | 2474 | 987 | 0 | — | 0 | native signed 32/32 magnitude path with redundant zero-test removed | current native-signed division validation |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 314.965600 | 303 | 338 | 234 | 17 | $09-$19 | 0 | profile-selected resident implementation | 2026-09-14 post-upgrade deterministic comparison corpus |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 333.867232 | 301 | 366 | 299 | 17 | $09-$19 | 0 | FAST17 SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 812.998853 | 725 | 938 | 1450 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 877.773617 | 289 | 1914 | 388 | 12 | $10-$1B | 0 | fixed-point adapter into selected unsigned 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 952.471538 | 281 | 2007 | 625 | 12 | $14-$1F | 0 | fixed-point adapter into selected native signed 32/16 divider | current native-signed division validation |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 119.994705 | 41 | 2179 | 1559 | 3 | $10-$12 | 0 | exact reciprocal ladder with selected profile division fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_COS8` | `cos_u8_s8` | 29.000000 | 29 | 29 | 18 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 39.000000 | 39 | 39 | 25 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 48.447189 | 29 | 50 | 97 | 0 | — | 0 | compact_opt signed-log kernel; two table pages; exact parity with prior compact outputs | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 219.740570 | 205 | 258 | 277 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1378.900969 | 1193 | 1656 | 496 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 86.085602 | 68 | 104 | 67 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 92.085602 | 74 | 110 | 72 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 198.770271 | 129 | 333 | 392 | 5 | $14;$1A-$1D | 0 | profile-selected resident implementation | 2026-09-18 normalize profile-parity deterministic corpus |

## v2_pareto_fast

| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 78.494614 | 77 | 80 | 54 | 5 | $39-$3D | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | canonical harness |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 225.837200 | 214 | 249 | 171 | 17 | $21-$31 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 448.291800 | 418 | 503 | 369 | 24 | $21-$38 | 0 | 24-ZP reverse_24zp_carry certified resident kernel (retained; refresh candidate did not win) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 252.324882 | 230 | 293 | 217 | 116 | $80-$F3 | 0 | 116-ZP practical native signed quarter-square kernel (retained after FAST17 comparison) | current native-signed multiply validation |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 487.181818 | 430 | 544 | 473 | 24 | $21-$38 | 0 | FAST24 four-quadrant native signed composition; immutable quarter-square tables shared | current native-signed multiply validation |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 743.605230 | 660 | 873 | 1406 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | 728.041992 | 643 | 802 | 1387 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 59.383011 | 26 | 634 | 433 | 1 | $10 | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 127.773827 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 183.660846 | 56 | 3188 | 1468 | 3 | $10-$12 | 0 | Repose q0-counter/direct-public UDIV24 | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 753.994530 | 175 | 1880 | 1890 | 12 | $10-$1B | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD8` | `mod_u8_u8_u8` | 67.284844 | 51 | 495 | 131 | 2 | $10-$11 | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 203.033484 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 300.949131 | 56 | 3188 | 1468 | 3 | $10-$12 | 0 | Repose q0-counter/direct-public UDIV24 | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 792.160335 | 178 | 1883 | 1893 | 12 | $10-$1B | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 88.372650 | 26 | 600 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 169.428135 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 248.344384 | 57 | 3339 | 1570 | 9 | $10-$18 | 0 | fast direct-output native signed 24-bit divider | current native-signed division validation |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 833.995638 | 166 | 1973 | 2122 | 12 | $44-$4F | 0 | direct-output native signed 32/16 divider | current native-signed division validation |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 97.066406 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 233.088809 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 337.075090 | 57 | 3339 | 1570 | 9 | $10-$18 | 0 | fast direct-output native signed 24-bit divider | current native-signed division validation |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 861.849097 | 169 | 1976 | 2125 | 12 | $44-$4F | 0 | direct-output native signed 32/16 divider | current native-signed division validation |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 401.556389 | 90 | 2285 | 869 | 8 | $53-$5A | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 524.881520 | 90 | 2285 | 869 | 8 | $53-$5A | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 553.098146 | 75 | 2384 | 894 | 10 | $53-$5C | 0 | native signed 32/32 magnitude path with redundant zero-test removed | current native-signed division validation |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 746.032491 | 75 | 2384 | 894 | 10 | $53-$5C | 0 | native signed 32/32 magnitude path with redundant zero-test removed | current native-signed division validation |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 266.965600 | 255 | 290 | 197 | 17 | $21-$31 | 0 | profile-selected resident implementation | 2026-09-14 post-upgrade deterministic comparison corpus |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 293.411374 | 271 | 334 | 243 | 116 | $80-$F3 | 0 | 116-ZP practical native SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 812.998853 | 725 | 938 | 1450 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 764.129182 | 272 | 1849 | 1957 | 16 | $10-$1B;$53-$56 | 0 | fixed-point adapter into selected unsigned 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 834.061287 | 266 | 1908 | 2195 | 16 | $44-$4F;$53-$56 | 0 | fixed-point adapter into selected native signed 32/16 divider | current native-signed division validation |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 118.523834 | 41 | 2138 | 1887 | 9 | $10-$12;$61-$64;$67-$68 | 0 | exact reciprocal ladder with selected profile division fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_COS8` | `cos_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 44.962814 | 29 | 47 | 92 | 0 | — | 0 | sum_fast carry-clearing signed-log kernel; four table pages; exact parity with prior fast outputs | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 205.760590 | 193 | 246 | 259 | 1 | $66 | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1198.619613 | 1052 | 1428 | 440 | 10 | $54-$5C;$66 | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 79.570038 | 64 | 95 | 58 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 85.570038 | 70 | 101 | 63 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 189.260317 | 127 | 323 | 383 | 8 | $12-$15;$39-$3C | 0 | profile-selected resident implementation | 2026-09-18 normalize profile-parity deterministic corpus |

## v3_reu_512k

| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 69.000000 |  |  | 49 | 0 | — | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | REU transport model |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 225.837200 | 214 | 249 | 171 | 17 | $21-$31 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 448.291800 | 418 | 503 | 369 | 24 | $21-$38 | 0 | 24-ZP reverse_24zp_carry certified resident kernel (retained; refresh candidate did not win) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 252.623962 | 230 | 293 | 217 | 116 | $80-$F3 | 0 | 116-ZP practical native signed quarter-square kernel (retained after FAST17 comparison) | current native-signed multiply validation |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 486.816106 | 430 | 546 | 473 | 24 | $21-$38 | 0 | FAST24 four-quadrant native signed composition; immutable quarter-square tables shared | current native-signed multiply validation |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 744.033209 | 660 | 873 | 1406 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | 728.544922 | 648 | 809 | 1387 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 70.863281 | 36 | 71 | 61 | 0 | — | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 125.423943 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 191.745424 | 56 | 3188 | 1468 | 3 | $10-$12 | 0 | Repose q0-counter/direct-public UDIV24 | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 755.944246 | 175 | 1880 | 1890 | 12 | $10-$1B | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD8` | `mod_u8_u8_u8` | 49.712110 | 32 | 50 | 42 | 0 | — | 0 | REU direct remainder plane retained; direct-public UDIV8 selected separately | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 203.396008 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 302.914359 | 56 | 3188 | 1468 | 3 | $10-$12 | 0 | Repose q0-counter/direct-public UDIV24 | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 789.650998 | 178 | 1883 | 1893 | 12 | $10-$1B | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 88.372650 | 26 | 600 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 171.806325 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 236.810251 | 68 | 3314 | 1894 | 9 | $10-$18 | 0 | Repose-derived direct-output native signed 24-bit divider with private magnitude engine | current native-signed division validation |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 833.572737 | 166 | 1973 | 2122 | 12 | $44-$4F | 0 | direct-output native signed 32/16 divider | current native-signed division validation |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 97.152344 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 235.588448 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 329.971841 | 68 | 3314 | 1894 | 9 | $10-$18 | 0 | Repose-derived direct-output native signed 24-bit divider with private magnitude engine | current native-signed division validation |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 863.249097 | 169 | 1976 | 2125 | 12 | $44-$4F | 0 | direct-output native signed 32/16 divider | current native-signed division validation |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 395.884576 | 90 | 2285 | 869 | 8 | $53-$5A | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 518.802962 | 90 | 2285 | 869 | 8 | $53-$5A | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 552.481381 | 75 | 2384 | 894 | 10 | $53-$5C | 0 | native signed 32/32 magnitude path with redundant zero-test removed | current native-signed division validation |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 742.016606 | 75 | 2384 | 894 | 10 | $53-$5C | 0 | native signed 32/32 magnitude path with redundant zero-test removed | current native-signed division validation |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 266.965600 | 255 | 290 | 197 | 17 | $21-$31 | 0 | profile-selected resident implementation | 2026-09-14 post-upgrade deterministic comparison corpus |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 293.411374 | 271 | 334 | 243 | 116 | $80-$F3 | 0 | 116-ZP practical native SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 812.998853 | 725 | 938 | 1450 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 764.339154 | 272 | 1849 | 1957 | 16 | $10-$1B;$53-$56 | 0 | fixed-point adapter into selected unsigned 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 832.687023 | 266 | 1908 | 2195 | 16 | $44-$4F;$53-$56 | 0 | fixed-point adapter into selected native signed 32/16 divider | current native-signed division validation |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 66.233795 | 41 | 239 | 430 | 0 | — | 0 | exact reciprocal ladder with selected profile division fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_COS8` | `cos_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 44.962814 | 29 | 47 | 92 | 0 | — | 0 | sum_fast carry-clearing signed-log kernel; four table pages; exact parity with prior fast outputs | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 204.992523 | 192 | 246 | 259 | 1 | $66 | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1197.859322 | 1051 | 1428 | 440 | 10 | $54-$5C;$66 | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 79.070038 | 63 | 95 | 58 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 85.070038 | 69 | 101 | 63 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 170.058633 | 133 | 306 | 346 | 4 | $12-$15 | 0 | profile-selected resident implementation | 2026-09-18 normalize profile-parity deterministic corpus |
| `MATH_REU_UMUL16_BEGIN` | `mul_u16_u16_u32_turbo_begin` | 282.000000 | 282 | 282 | 41 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16` | `mul_u16_u16_u32_turbo` | 215.544111 | 203 | 240 | 41 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16_END` | `mul_u16_u16_u32_turbo_end` | 327.000000 | 327 | 327 | 73 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_BEGIN` | `mul_u32_u32_u64_turbo_begin` | 326.000000 | 326 | 326 | 41 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32` | `mul_u32_u32_u64_turbo` | 728.947080 | 666 | 840 | 125 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_END` | `mul_u32_u32_u64_turbo_end` | 371.000000 | 371 | 371 | 73 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |

## v4_reu_16m

| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 69.000000 |  |  | 49 | 0 | — | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | unchanged V3 path/evidence |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 225.837200 | 214 | 249 | 171 | 17 | $21-$31 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 448.291800 | 418 | 503 | 369 | 24 | $21-$38 | 0 | 24-ZP reverse_24zp_carry certified resident kernel (retained; refresh candidate did not win) | 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 252.662553 | 230 | 293 | 217 | 116 | $80-$F3 | 0 | 116-ZP practical native signed quarter-square kernel (retained after FAST17 comparison) | current native-signed multiply validation |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 487.220008 | 430 | 550 | 473 | 24 | $21-$38 | 0 | FAST24 four-quadrant native signed composition; immutable quarter-square tables shared | current native-signed multiply validation |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 744.090079 | 660 | 873 | 1406 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | 726.368164 | 643 | 825 | 1387 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 70.863281 | 36 | 71 | 61 | 0 | — | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 125.625710 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 187.307174 | 56 | 3188 | 1468 | 3 | $10-$12 | 0 | Repose q0-counter/direct-public UDIV24 | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 757.480328 | 175 | 1880 | 1890 | 12 | $10-$1B | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD8` | `mod_u8_u8_u8` | 49.725819 | 32 | 50 | 42 | 0 | — | 0 | REU direct remainder plane retained; direct-public UDIV8 selected separately | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 202.557630 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 301.613007 | 56 | 3188 | 1468 | 3 | $10-$12 | 0 | Repose q0-counter/direct-public UDIV24 | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 789.841597 | 178 | 1883 | 1893 | 12 | $10-$1B | 0 | profile-selected native 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 89.009821 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 169.754198 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 237.569466 | 68 | 3314 | 1894 | 9 | $10-$18 | 0 | Repose-derived direct-output native signed 24-bit divider with private magnitude engine | current native-signed division validation |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 829.631189 | 166 | 1973 | 2122 | 12 | $44-$4F | 0 | direct-output native signed 32/16 divider | current native-signed division validation |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 99.020313 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 229.269314 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider | current native-signed division validation |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 326.184838 | 68 | 3314 | 1894 | 9 | $10-$18 | 0 | Repose-derived direct-output native signed 24-bit divider with private magnitude engine | current native-signed division validation |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 861.002888 | 169 | 1976 | 2125 | 12 | $44-$4F | 0 | direct-output native signed 32/16 divider | current native-signed division validation |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 404.408910 | 90 | 2285 | 869 | 8 | $53-$5A | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 516.780425 | 90 | 2285 | 869 | 8 | $53-$5A | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 552.840042 | 75 | 2384 | 894 | 10 | $53-$5C | 0 | native signed 32/32 magnitude path with redundant zero-test removed | current native-signed division validation |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 754.883032 | 75 | 2384 | 894 | 10 | $53-$5C | 0 | native signed 32/32 magnitude path with redundant zero-test removed | current native-signed division validation |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 266.965600 | 255 | 290 | 197 | 17 | $21-$31 | 0 | profile-selected resident implementation | 2026-09-14 post-upgrade deterministic comparison corpus |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 293.411374 | 271 | 334 | 243 | 116 | $80-$F3 | 0 | 116-ZP practical native SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 812.998853 | 725 | 938 | 1450 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 764.628235 | 272 | 1849 | 1957 | 16 | $10-$1B;$53-$56 | 0 | fixed-point adapter into selected unsigned 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 831.029880 | 266 | 1908 | 2195 | 16 | $44-$4F;$53-$56 | 0 | fixed-point adapter into selected native signed 32/16 divider | current native-signed division validation |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 66.233795 | 41 | 239 | 430 | 0 | — | 0 | exact reciprocal ladder with selected profile division fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_COS8` | `cos_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 48.000000 | 48 | 48 | 33 | 0 | — | 0 | exact signed-byte phase plane in REU bank 8 | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 54.000000 | 54 | 54 | 38 | 0 | — | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1046.622518 | 899 | 1237 | 219 | 9 | $54-$5C | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 79.070038 | 63 | 95 | 58 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 85.070038 | 69 | 101 | 63 | 2 | $5D-$5E | 0 | profile-selected resident implementation | current exhaustive/profile game-math benchmark |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 170.058633 | 133 | 306 | 346 | 4 | $12-$15 | 0 | profile-selected resident implementation | 2026-09-18 normalize profile-parity deterministic corpus |
| `MATH_REU_UMUL16_BEGIN` | `mul_u16_u16_u32_turbo_begin` | 282.000000 | 282 | 282 | 41 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16` | `mul_u16_u16_u32_turbo` | 215.544111 | 203 | 240 | 41 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL16_END` | `mul_u16_u16_u32_turbo_end` | 327.000000 | 327 | 327 | 73 | 113 | $3E-$AE | 0 | 113-ZP Turbo16 overlay | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_BEGIN` | `mul_u32_u32_u64_turbo_begin` | 326.000000 | 326 | 326 | 41 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32` | `mul_u32_u32_u64_turbo` | 728.947080 | 666 | 840 | 125 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_UMUL32_END` | `mul_u32_u32_u64_turbo_end` | 371.000000 | 371 | 371 | 73 | 135 | $0A-$90 | 0 | 135-ZP stack-free ram135 Turbo32 record compromise | Turbo relocation canonical reference corpus |
| `MATH_REU_QS16_BEGIN` | `mul_u16_u16_u32_qs16_begin` | 18.000000 | 18 | 18 | 11 | 16 | $10-$1F | 0 | V4 16MiB QS16 mode | V4 QS16 source/exact timing classes |
| `MATH_REU_QS16` | `mul_u16_u16_u32_qs16` | 281.541031 | 279 | 293 | 209 | 16 | $10-$1F | 0 | V4 16MiB QS16 mode | V4 QS16 source/exact timing classes |
| `MATH_REU_QS16_END` | `mul_u16_u16_u32_qs16_end` | 18.000000 | 18 | 18 | 11 | 16 | $10-$1F | 0 | V4 16MiB QS16 mode | V4 QS16 source/exact timing classes |

## v5_hybrid_lowzp

| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |
|---|---|---:|---:|---:|---:|---:|---|---:|---|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 90.494644 | 88 | 93 | 55 | 5 | $10-$14 | 0 | profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract | V5 documented v1_balanced path; canonical harness |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 273.837200 | 262 | 297 | 208 | 17 | $09-$19 | 0 | 17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep) | V5 documented v1_balanced path; 2026-09-14 record-upgrade deterministic comparison corpus |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 489.988792 | 462 | 542 | 369 | 24 | $09-$20 | 0 | FAST24 private 24-ZP carry producer with stable public adapter | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 712.235367 | 652 | 831 | 336 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | 697.175781 | 642 | 784 | 320 | 31 | $02-$20 | 0 | FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 66 | 70 | 46 | 0 | — | 0 | direct signed-domain quarter-square kernel with private signed-sum planes | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 292.974871 | 260 | 325 | 273 | 17 | $09-$19 | 0 | FAST17 native signed composition with private 17-ZP magnitude core | current native-signed multiply validation |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 530.874222 | 474 | 588 | 505 | 24 | $09-$20 | 0 | FAST24 four-quadrant native signed composition; immutable quarter-square tables shared | current native-signed multiply validation |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 743.913242 | 660 | 873 | 1406 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | 726.739258 | 640 | 807 | 1387 | 31 | $02-$20 | 0 | FAST31/V29 native signed quadrant composition; mixed-call-safe public path | current native-signed multiply validation |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 59.383011 | 26 | 634 | 433 | 1 | $10 | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 126.385862 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider; V5 repacked into hybrid private RAM | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 187.122028 | 56 | 3188 | 1468 | 3 | $10-$12 | 0 | Repose q0-counter/direct-public UDIV24; V5 repacked hybrid copy | 2026-09-20 unsigned division-family validation |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 756.638544 | 175 | 1880 | 1890 | 12 | $10-$1B | 0 | V2 certified 32/16 divider imported into V5 hybrid private RAM | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD8` | `mod_u8_u8_u8` | 68.523229 | 51 | 495 | 131 | 2 | $10-$11 | 0 | direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 199.918867 | 41 | 1076 | 1469 | 0 | — | 0 | fast direct-public 16-bit divider; V5 repacked into hybrid private RAM | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 299.273020 | 56 | 3188 | 1468 | 3 | $10-$12 | 0 | Repose q0-counter/direct-public UDIV24; V5 repacked hybrid copy | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 789.508693 | 178 | 1883 | 1893 | 12 | $10-$1B | 0 | V2 certified 32/16 divider imported into V5 hybrid private RAM | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 90.272098 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 171.905344 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider; V5 repacked under 31-ZP contract | current native-signed division validation |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 253.487023 | 57 | 3339 | 1570 | 9 | $10-$18 | 0 | fast direct-output native signed 24-bit divider repacked under V5 31-ZP contract | current native-signed division validation |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 958.522137 | 171 | 2063 | 542 | 12 | $14-$1F | 0 | refreshed low-ZP native signed 32/16 divider retained in V5 | current native-signed division validation |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 96.707813 | 26 | 598 | 533 | 1 | $10 | 0 | direct-output native signed 8-bit divider; executable-disjoint from UDIV8 | current native-signed division validation |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 232.809386 | 54 | 1159 | 1771 | 4 | $10-$13 | 0 | fast direct-output native signed 16-bit divider; V5 repacked under 31-ZP contract | current native-signed division validation |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 339.607942 | 57 | 3339 | 1570 | 9 | $10-$18 | 0 | fast direct-output native signed 24-bit divider repacked under V5 31-ZP contract | current native-signed division validation |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 1061.475812 | 174 | 2066 | 545 | 12 | $14-$1F | 0 | refreshed low-ZP native signed 32/16 divider retained in V5 | current native-signed division validation |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 421.077342 | 90 | 2423 | 946 | 0 | — | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 548.000000 | 90 | 2423 | 946 | 0 | — | 0 | native tiered 32/32 divider with early q=0 gate | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 591.562641 | 75 | 2474 | 987 | 0 | — | 0 | native signed 32/32 magnitude path with redundant zero-test removed | current native-signed division validation |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 785.582671 | 75 | 2474 | 987 | 0 | — | 0 | native signed 32/32 magnitude path with redundant zero-test removed | current native-signed division validation |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 314.965600 | 303 | 338 | 234 | 17 | $09-$19 | 0 | profile-selected resident implementation | 2026-09-14 post-upgrade deterministic comparison corpus |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 333.867232 | 301 | 366 | 299 | 17 | $09-$19 | 0 | FAST17 SMUL16 plus SHR8 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 779.876404 | 717 | 896 | 380 | 31 | $02-$20 | 0 | FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 812.998853 | 725 | 938 | 1450 | 31 | $02-$20 | 0 | FAST31/V29 SMUL32 producer plus existing SHR16 extraction | 2026-09-20 multiply-refresh deterministic cross-profile corpus |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 774.734904 | 282 | 1859 | 1967 | 12 | $10-$1B | 0 | fixed-point adapter into selected unsigned 32/16 divider | 2026-09-20 unsigned division-family validation |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 953.277863 | 281 | 2007 | 625 | 12 | $14-$1F | 0 | fixed-point adapter into selected native signed 32/16 divider | current native-signed division validation |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 119.307602 | 41 | 2150 | 1899 | 3 | $10-$12 | 0 | exact reciprocal ladder with selected profile division fallback | 2026-09-20 unsigned division-family validation |
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; current exhaustive/profile game-math benchmark |
| `MATH_COS8` | `cos_u8_s8` | 23.000000 | 23 | 23 | 14 | 0 | — | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; current exhaustive/profile game-math benchmark |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 31.000000 | 31 | 31 | 20 | 0 | — | 0 | V2 certified kernel imported into V5 hybrid private RAM | V5 documented v2_pareto_fast path; current exhaustive/profile game-math benchmark |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 44.962814 | 29 | 47 | 92 | 0 | — | 0 | V2 sum_fast kernel imported into V5 with four private table pages | V5 documented v2_pareto_fast path; current exhaustive/profile game-math benchmark |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 219.740570 | 205 | 258 | 277 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; current exhaustive/profile game-math benchmark |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1378.900969 | 1193 | 1656 | 496 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; current exhaustive/profile game-math benchmark |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 86.085602 | 68 | 104 | 67 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; current exhaustive/profile game-math benchmark |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 92.085602 | 74 | 110 | 72 | 0 | — | 0 | profile-selected resident implementation | V5 documented v1_balanced path; current exhaustive/profile game-math benchmark |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 198.770271 | 129 | 333 | 392 | 5 | $14;$1A-$1D | 0 | profile-selected resident implementation | 2026-09-18 normalize profile-parity deterministic corpus |

## Interpretation notes

- V1/V5 keep the 31-byte resident ZP contract. Their upgraded UMUL16/UMUL24 reuse that window and preserve `UMUL32_READY` state.
- V2-V4 use larger profile-selected ZP regions for some native signed/division kernels; per-routine ZP rows show the actual touched/owned set.
- V3/V4 Turbo16 owns 113 ZP bytes while active. Turbo32 now owns 135 ZP bytes (stack-free `ram135` compromise), down from the old 241-byte overlay.
- V4 QS16 owns `$10-$1F` (16 ZP bytes) while active.
- The PRG payload span includes address gaps in the load image and is not “occupied code bytes”. Use `SEGMENTS.csv` for physical segment placement and this table for per-entry reachable executable size.
