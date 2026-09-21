# Performance

This is the quickest way to answer **“how fast is it?”** for the current C64 Math Library. All figures below are cycles measured at the public entry through `RTS`; caller `JSR` and input stores are excluded unless a row explicitly says otherwise.

The five fixed profiles use different memory/ZP trade-offs, so the fastest number is not automatically the best choice for every program. For exact code size, ZP ranges, stack reservation, corpus and a direct source link for every row, use [`docs/CONSOLIDATED_ROUTINE_TABLE.md`](docs/CONSOLIDATED_ROUTINE_TABLE.md) or [`benchmarks/PUBLIC_PROFILE_RESULTS.csv`](benchmarks/PUBLIC_PROFILE_RESULTS.csv). For a one-row-per-routine view that automatically selects the fastest shipped profile, use [`benchmarks/BEST_PROFILE_RESULTS.csv`](benchmarks/BEST_PROFILE_RESULTS.csv).

## Shipped profile means

### Multiply

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 90.494644 | 78.494614 | 69.000000 | 69.000000 | 90.494644 |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 273.837200 | 225.837200 | 225.837200 | 225.837200 | 273.837200 |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 489.988792 | 448.291800 | 448.291800 | 448.291800 | 489.988792 |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 712.235367 | 712.235367 | 712.235367 | 712.235367 | 712.235367 |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 67.992188 | 67.992188 | 67.992188 | 67.992188 |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 293.298407 | 252.324882 | 252.623962 | 252.662553 | 292.974871 |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 531.496472 | 487.181818 | 486.816106 | 487.220008 | 530.874222 |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 744.569946 | 743.605230 | 744.033209 | 744.090079 | 743.913242 |

### Divide

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 59.571976 | 59.383011 | 70.863281 | 70.863281 | 59.383011 |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 132.725857 | 127.773827 | 125.423943 | 125.625710 | 126.385862 |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 194.156322 | 183.660846 | 191.745424 | 187.307174 | 187.122028 |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 870.340206 | 753.994530 | 755.944246 | 757.480328 | 756.638544 |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 428.554036 | 401.556389 | 395.884576 | 404.408910 | 421.077342 |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 88.372650 | 88.372650 | 88.372650 | 89.009821 | 90.272098 |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 187.131298 | 169.428135 | 171.806325 | 169.754198 | 171.905344 |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 313.583206 | 248.344384 | 236.810251 | 237.569466 | 253.487023 |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 955.051690 | 833.995638 | 833.572737 | 829.631189 | 958.522137 |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 586.396050 | 553.098146 | 552.481381 | 552.840042 | 591.562641 |

### Modulo / fixed-point

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_UMOD8` | `mod_u8_u8_u8` | 67.167555 | 67.284844 | 49.712110 | 49.725819 | 68.523229 |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 184.082421 | 203.033484 | 203.396008 | 202.557630 | 199.918867 |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 303.233097 | 300.949131 | 302.914359 | 301.613007 | 299.273020 |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 971.613651 | 792.160335 | 789.650998 | 789.841597 | 789.508693 |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 552.220863 | 524.881520 | 518.802962 | 516.780425 | 548.000000 |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 98.157813 | 97.066406 | 97.152344 | 99.020313 | 96.707813 |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 229.324910 | 233.088809 | 235.588448 | 229.269314 | 232.809386 |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 427.272924 | 337.075090 | 329.971841 | 326.184838 | 339.607942 |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 1061.083032 | 861.849097 | 863.249097 | 861.002888 | 1061.475812 |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 785.979061 | 746.032491 | 742.016606 | 754.883032 | 785.582671 |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 314.965600 | 266.965600 | 266.965600 | 266.965600 | 314.965600 |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 333.867232 | 293.411374 | 293.411374 | 293.411374 | 333.867232 |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 779.876404 | 779.876404 | 779.876404 | 779.876404 | 779.876404 |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 812.998853 | 812.998853 | 812.998853 | 812.998853 | 812.998853 |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 877.773617 | 764.129182 | 764.339154 | 764.628235 | 774.734904 |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 952.471538 | 834.061287 | 832.687023 | 831.029880 | 953.277863 |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 119.994705 | 118.523834 | 66.233795 | 66.233795 | 119.307602 |

### Trig / roots / game math

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23.000000 | 23.000000 | 23.000000 | 23.000000 |
| `MATH_COS8` | `cos_u8_s8` | 29.000000 | 23.000000 | 23.000000 | 23.000000 | 23.000000 |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 39.000000 | 31.000000 | 31.000000 | 31.000000 | 31.000000 |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 48.447189 | 44.962814 | 44.962814 | 48.000000 | 44.962814 |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 219.740570 | 205.760590 | 204.992523 | 54.000000 | 219.740570 |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1378.900969 | 1198.619613 | 1197.859322 | 1046.622518 | 1378.900969 |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 86.085602 | 79.570038 | 79.070038 | 79.070038 | 86.085602 |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 92.085602 | 85.570038 | 85.070038 | 85.070038 | 92.085602 |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 160.150080 | 160.150080 | 156.661198 | 156.661198 | 160.150080 |

## Source-backed standalone / Pareto alternatives

These are independently useful kernels or record/Pareto points. They are **not all benchmarked on the same corpus as the shipped public API**, so compare means only when the basis is compatible. Every number in this table has a public source file and evidence path in this repository.

| Typed routine | Variant | Mean | Min | Max | ZP B | Stack-page B | Source | Evidence / basis |
|---|---|---:|---:|---:|---:|---:|---|---|
| `mul_u16_u16_u32` | `shifted99` | 155.646069283 | — | — | 99 | 0 | [mul_u16_u16_u32_shifted99.asm](routines/multiply/mul_u16_u16_u32_shifted99.asm) | [UMUL16_SHIFTED_EXACT.json](validation/records/UMUL16_SHIFTED_EXACT.json); exact full-domain event count |
| `mul_u16_u16_u32` | `shifted106` | 155.031478817 | — | — | 106 | 0 | [mul_u16_u16_u32_shifted106.asm](routines/multiply/mul_u16_u16_u32_shifted106.asm) | [UMUL16_SHIFTED_EXACT.json](validation/records/UMUL16_SHIFTED_EXACT.json); exact full-domain event count |
| `mul_u16_u16_u32` | `shifted116` | 154.417078788 | — | — | 116 | 0 | [mul_u16_u16_u32_shifted116.asm](routines/multiply/mul_u16_u16_u32_shifted116.asm) | [UMUL16_SHIFTED_EXACT.json](validation/records/UMUL16_SHIFTED_EXACT.json); exact full-domain event count |
| `mul_u16_u16_u32` | `shifted134` | 154.297827851 | — | — | 134 | 0 | [mul_u16_u16_u32_shifted134.asm](routines/multiply/mul_u16_u16_u32_shifted134.asm) | [UMUL16_SHIFTED_EXACT.json](validation/records/UMUL16_SHIFTED_EXACT.json); exact full-domain event count |
| `mul_u24_u24_u48` | `fast24` | 357.041715026 | 327 | 412 | 24 | 0 | [mul_u24_u24_u48_fast24.asm](routines/multiply/mul_u24_u24_u48_fast24.asm) | [mul_u24_u24_u48_fast24.asm](routines/multiply/mul_u24_u24_u48_fast24.asm); gmec uniform sample; fresh-X entry through RTS |
| `mul_u32_u32_u64` | `bounded133` | 606.337632 | 542 | 729 | 133 | 177 | [mul_u32_u32_u64_bounded133.asm](routines/multiply/mul_u32_u32_u64_bounded133.asm) | [UMUL32_BOUNDED133_GMEC.json](validation/records/UMUL32_BOUNDED133_GMEC.json); gmec uniform profile/validation corpus |
| `mul_u32_u32_u64` | `bounded133_compact` | 606.864799 | 543 | 733 | 133 | 162 | [mul_u32_u32_u64_bounded133_compact.asm](routines/multiply/mul_u32_u32_u64_bounded133_compact.asm) | [UMUL32_BOUNDED133_COMPACT_GMEC.json](validation/records/UMUL32_BOUNDED133_COMPACT_GMEC.json); gmec uniform profile/validation corpus |
| `mul_s24_s24_s48` | `fast24` | 400.301600 | 339 | 461 | 24 | 0 | [mul_s24_s24_s48_fast24.asm](routines/multiply/mul_s24_s24_s48_fast24.asm) | [SMUL24_FAST24_2026-09-20.json](validation/records/SMUL24_FAST24_2026-09-20.json); deterministic C0FFEE paired-style corpus; native entry through RTS |
| `mul_s32_s32_s64` | `turbo135` | 665.877260 | 560 | 805 | 135 | 0 | [mul_s32_s32_s64_turbo135.asm](routines/multiply/mul_s32_s32_s64_turbo135.asm) | [SMUL32_TURBO135_100K.json](validation/records/SMUL32_TURBO135_100K.json); deterministic 100,000-call native corpus |
| `mul_s32_s32_s64` | `fast31_native` | 697.259440 | 594 | 834 | 31 | 0 | [mul_s32_s32_s64_fast31_native.asm](routines/multiply/mul_s32_s32_s64_fast31_native.asm) | [SMUL32_FAST31_NATIVE_100K.json](validation/records/SMUL32_FAST31_NATIVE_100K.json); deterministic 100,000-call native corpus |
| `atan2_s8_s8_u8` | `compact_opt` | 48.447189 | 29 | 50 | 0 | 0 | [atan2_s8_s8_u8_compact_opt.asm](routines/atan2/standalone/atan2_s8_s8_u8_compact_opt.asm) | [ATAN2_OPTIMIZATION_VALIDATION.json](validation/ATAN2_OPTIMIZATION_VALIDATION.json); exhaustive signed-byte vectors; public JMP+RTS |
| `atan2_s8_s8_u8` | `sum_small` | 45.958908 | 29 | 48 | 0 | 0 | [atan2_s8_s8_u8_sum_small.asm](routines/atan2/standalone/atan2_s8_s8_u8_sum_small.asm) | [ATAN2_OPTIMIZATION_VALIDATION.json](validation/ATAN2_OPTIMIZATION_VALIDATION.json); exhaustive signed-byte vectors; public JMP+RTS |
| `atan2_s8_s8_u8` | `sum_fast` | 44.962814 | 29 | 47 | 0 | 0 | [atan2_s8_s8_u8_sum_fast.asm](routines/atan2/standalone/atan2_s8_s8_u8_sum_fast.asm) | [ATAN2_OPTIMIZATION_VALIDATION.json](validation/ATAN2_OPTIMIZATION_VALIDATION.json); exhaustive signed-byte vectors; public JMP+RTS |

## How to find the exact source

- **Shipped routine:** open the profile’s `standalone/<typed-name>.asm` file. `routines/SOURCE_CATALOG.csv` gives the exact path for every callable entry.
- **Standalone record/Pareto routine:** use the source link in the table above. Variant suffixes come after the typed geometry, e.g. `mul_s24_s24_s48_fast24`.
- **Machine-readable results:** `benchmarks/PUBLIC_PROFILE_RESULTS.csv`, `benchmarks/BEST_PROFILE_RESULTS.csv`, and `benchmarks/STANDALONE_RESULTS.csv`.
- **Naming:** `docs/NAMING_STANDARD.md`. Historical `MATH_*` symbols remain ABI-compatible.
