# Performance

This is the quickest way to answer **“how fast is it?”** for the current C64 Math Library. All figures below are cycles measured at the public entry through `RTS`; caller `JSR` and input stores are excluded unless a row explicitly says otherwise.

The five fixed profiles use different memory/ZP trade-offs, so the fastest number is not automatically the best choice for every program. For exact code size, ZP ranges, stack reservation, corpus and a direct source link for every row, use [`docs/CONSOLIDATED_ROUTINE_TABLE.md`](docs/CONSOLIDATED_ROUTINE_TABLE.md) or [`benchmarks/PUBLIC_PROFILE_RESULTS.csv`](benchmarks/PUBLIC_PROFILE_RESULTS.csv). For a one-row-per-routine view that automatically selects the fastest shipped profile, use [`benchmarks/BEST_PROFILE_RESULTS.csv`](benchmarks/BEST_PROFILE_RESULTS.csv).

The V2/V3/V4 UDIV32 live-high core uses four ZP bytes on the wide-divisor hot path and averages 177.737 fewer cycles on the original paired uniform32 comparison. The finalized public graph also reaches the bounded UDIV32/16 and 17-bit-divisor fallbacks, so its whole-call static resource footprint is larger; see [the full comparison and resource accounting](docs/UDIV32_OPTISEARCH.md).

## Shipped profile means

### Multiply

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 90.494644 | 78.494614 | 69.000000 | 69.000000 | 90.494644 |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 273.837200 | 216.980037 | 216.980037 | 216.980037 | 273.837200 |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 474.042329 | 421.555502 | 421.555502 | 421.555502 | 474.042329 |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 712.235367 | 690.235367 | 690.235367 | 690.235367 | 712.235367 |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 67.992188 | 67.992188 | 67.992188 | 67.992188 |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 282.588064 | 245.802333 | 246.107696 | 246.144492 | 282.262957 |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 511.342357 | 467.342357 | 467.342357 | 467.342357 | 511.342357 |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 744.128269 | 711.153591 | 711.447073 | 711.706102 | 743.477377 |

### Divide

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 59.571976 | 59.383011 | 52.852264 | 52.852264 | 59.383011 |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 132.725857 | 127.773827 | 125.423943 | 125.625710 | 126.385862 |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 194.156322 | 154.338944 | 161.653272 | 158.507048 | 157.776141 |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 870.340206 | 631.739323 | 632.886598 | 634.698506 | 634.079529 |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 428.554036 | 212.304220 | 203.864138 | 209.625349 | 421.077342 |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 88.372650 | 88.372650 | 88.372650 | 89.009821 | 90.272098 |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 187.131298 | 168.393021 | 170.582116 | 168.745038 | 170.631189 |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 313.583206 | 248.344384 | 236.810251 | 237.569466 | 253.487023 |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 955.051690 | 817.550927 | 817.533479 | 813.759215 | 958.522137 |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 566.839288 | 537.452736 | 536.835972 | 537.194633 | 572.005880 |

V3/V4 `MATH_UDIV8` now uses a quotient-0..3 CPU fast path and falls back to the exact REU quotient/remainder planes only for quotient 4+. The exhaustive 65,536-input mean is **52.852264 cycles** (28–115), with zero errors.

### Modulo / fixed-point

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_UMOD8` | `mod_u8_u8_u8` | 67.167555 | 67.284844 | 49.712110 | 49.725819 | 68.523229 |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 184.082421 | 195.951706 | 196.414681 | 195.529942 | 199.918867 |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 303.233097 | 205.325821 | 207.136510 | 205.247263 | 211.248551 |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 971.613651 | 629.783001 | 625.840953 | 626.014810 | 626.658725 |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 552.220863 | 290.452028 | 287.455248 | 285.637476 | 548.000000 |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 98.157813 | 97.066406 | 97.152344 | 99.020313 | 96.707813 |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 229.324910 | 231.872202 | 234.659206 | 228.244765 | 231.667148 |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 427.272924 | 337.075090 | 329.971841 | 326.184838 | 339.607942 |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 1061.083032 | 848.623105 | 850.511191 | 848.283755 | 1061.475812 |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 766.253430 | 730.251986 | 726.236101 | 739.102527 | 765.857040 |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 304.804139 | 243.804139 | 243.804139 | 243.804139 | 304.804139 |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 313.154093 | 276.888787 | 276.888787 | 276.888787 | 313.154093 |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 779.876404 | 757.876404 | 757.876404 | 757.876404 | 779.876404 |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 812.544371 | 780.302454 | 780.302454 | 780.302454 | 812.544371 |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 770.773617 | 552.649695 | 553.124974 | 552.577740 | 553.298759 |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 846.155071 | 715.633370 | 714.004798 | 712.609597 | 630.805016 |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 108.497635 | 94.822998 | 66.233795 | 66.233795 | 95.044128 |

V2/V3/V4 now give `MATH_UMOD16`, `MATH_UMOD24`, and `MATH_UMOD32_32` dedicated remainder-only front ends. Quotient-0/1 (or equality) cases return without materializing quotient bytes; harder cases rejoin the exact existing divider. Signed modulo was measured separately and deliberately left unchanged because the analogous front end was slower.

### Trig / roots / game math

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23.000000 | 23.000000 | 23.000000 | 23.000000 |
| `MATH_COS8` | `cos_u8_s8` | 29.000000 | 23.000000 | 23.000000 | 23.000000 | 23.000000 |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 39.000000 | 31.000000 | 31.000000 | 31.000000 | 31.000000 |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 47.462814 | 43.970627 | 43.970627 | 48.000000 | 43.970627 |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 219.740570 | 205.760590 | 204.992523 | 54.000000 | 219.740570 |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1378.900969 | 1198.619613 | 1197.859322 | 917.317433 | 1378.900969 |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 86.085602 | 79.570038 | 79.070038 | 79.070038 | 86.085602 |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 92.085602 | 85.570038 | 85.070038 | 85.070038 | 92.085602 |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 160.150080 | 160.150080 | 156.661198 | 156.661198 | 160.150080 |

### Movement (seek)

Exact Bresenham/DDA "move toward target" steppers ([`docs/SEEK_DDA.md`](docs/SEEK_DDA.md)). `*_INIT` is once per move; `*_STEP*` is once per object per frame. Every frame of every benchmark move is verified against the Bresenham model.

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_SEEK8_INIT` | `seek_u8_u8_init` | 601.746936 | 543.965482 | 544.686887 | 544.686887 | 601.746936 |
| `MATH_SEEK8_STEP` | `seek_u8_u8_step` | 87.136511 | 87.136511 | 87.136511 | 87.136511 | 87.136511 |
| `MATH_SEEK8_STEP_INT` | `seek_u8_u8_step_int` | 70.992770 | 70.992770 | 70.992770 | 70.992770 | 70.992770 |
| `MATH_SEEK8_STEP1` | `seek_u8_u8_step1` | 65.953959 | 65.953959 | 65.953959 | 65.953959 | 65.953959 |
| `MATH_SEEK16_INIT` | `seek_u16_u8_init` | 783.201389 | 702.713848 | 701.543505 | 701.543505 | 783.201389 |
| `MATH_SEEK16_STEP` | `seek_u16_u8_step` | 118.277360 | 118.688882 | 118.277360 | 118.277360 | 118.277360 |
| `MATH_SEEK16_STEP_INT` | `seek_u16_u8_step_int` | 103.654782 | 103.654782 | 103.654782 | 103.654782 | 103.654782 |
| `MATH_SEEK16_STEP1` | `seek_u16_u8_step1` | 98.183384 | 98.183384 | 98.183384 | 98.183384 | 98.183384 |

`*_INIT` means mix major-axis and Euclidean speeds. By speed mode, V2 cost is: SEEK8 336.5 major-axis, 310.6 integer, 279.4 at 1 px/frame, 751.4 Euclidean; SEEK16 479.6 / 458.1 / 382.7 / 925.8. V1/V5 run init about 10% slower because their init scratch is RAM (V1 low-ZP contract).

SMUL24 now uses a common 10,676-case corpus across all profiles. Against the same corpus on `ff1b602`, carry-primed dispatch saves 4–5 cycles on every case and six code bytes. ATAN2 branch ordering saves 2 cycles for X<0, leaves X>0 unchanged, and costs 4 cycles for X=0 in V1 or 2 in V2/V3/V5. The full-domain average improves by about one cycle. [Review and exact paired results](docs/OPTISEARCH_REVIEW_2026-10-07.md).

## Stateful REU Turbo multiply

V3/V4 can temporarily exchange a larger executable-ZP overlay with the REU for repeated multiply batches. These calls are non-reentrant while the overlay is active.

| Routine | CALL mean | Min–max | Active ZP | BEGIN | END | Approx. crossover vs normal public multiply |
|---|---:|---:|---:|---:|---:|---:|
| `MATH_REU_UMUL16` | 197.046257 | 185–220 | 122 bytes | 300 | 345 | ~33 products |
| `MATH_REU_UMUL32` | 676.185219 | 613–788 | 135 bytes | 326 | 371 | ~50 products |

Turbo16 now writes the complete result directly to `MATH_Z`; its supported zero-penalty ZP origins are `$02-$85`. Turbo32 writes z4 directly and tail-exits through the public result path; its supported origins remain `$02-$79`. The boundary proof is cycle-identical at both supported extremes in V3 and V4.

## Source-backed standalone / Pareto alternatives

These are independently useful kernels or record/Pareto points. They are **not all benchmarked on the same corpus as the shipped public API**, so compare means only when the basis is compatible. Every number in this table has a public source file and evidence path in this repository.

The current SMUL32 native record is `compact126` at **646.354530 cycles** with 136 ZP bytes and a 126-byte persistent stack-page reservation. It is not selected into the fixed public profiles because its executable-ZP window conflicts with V2–V4 SMUL16 and standard-ABI marshalling removes the speed advantage; see [`docs/SMUL32_COMPACT126.md`](docs/SMUL32_COMPACT126.md). V2/V3/V4 also expose the exact record source under `optional/smul32_compact126/` for explicit exclusive-overlay use; those aliases do not change the shipped public timing rows.

For the practical low-resource class, `fast31_native_v2` is the new **31-ZP / stack-free SMUL32 record** at **692.825100 cycles**, improving the previous 697.259440 point by 4.434340 cycles. See [`docs/SMUL32_FAST31_V2.md`](docs/SMUL32_FAST31_V2.md).

For the shipped public API, V2/V3/V4 use a persistent-pointer FAST31/V29 layout: **all six** table-pointer pairs occupy holes already inside each profile's normal ZP ownership, eliminating the ordinary mixed-call pointer repair completely. The stable `MATH_SMUL32` entry now falls directly into the dispatcher instead of paying the legacy self-redirect. Canonical `MATH_SMUL32` means are **711.153591 / 711.447073 / 711.706102 cycles** in V2/V3/V4. Relative to the pre-persistent-pointer path, signed ordinary calls and signed SHR16 now save **28 cycles**; unsigned ordinary calls and unsigned SHR16 save **22 cycles**. READY timings are unchanged. V1/V5 retain the original low-ZP binder. The literal FAST31 v2 `CPY #$00` carry-seeding dispatch was also tested in the public memory ABI and measured exactly neutral, so it was not retained.

**Cross-profile note:** the small V2/V3/V4 spread in the canonical SMUL32 means comes from profile-specific deterministic random seeds. On one identical **6,361-case** corpus, all three current implementations are cycle-identical at **716.802547 cycles**, with identical per-call cycle vectors. The spread is not a relocation or REU penalty.

| Typed routine | Variant | Mean | Min | Max | ZP B | Stack-page B | Source | Evidence / basis |
|---|---|---:|---:|---:|---:|---:|---|---|
| `mul_u16_u16_u32` | `shifted99` | 155.646069283 | — | — | 99 | 0 | [mul_u16_u16_u32_shifted99.asm](routines/multiply/mul_u16_u16_u32_shifted99.asm) | [UMUL16_SHIFTED_EXACT.json](validation/records/UMUL16_SHIFTED_EXACT.json); exact full-domain event count |
| `mul_u16_u16_u32` | `shifted106` | 155.031478817 | — | — | 106 | 0 | [mul_u16_u16_u32_shifted106.asm](routines/multiply/mul_u16_u16_u32_shifted106.asm) | [UMUL16_SHIFTED_EXACT.json](validation/records/UMUL16_SHIFTED_EXACT.json); exact full-domain event count |
| `mul_u16_u16_u32` | `shifted116` | 154.417078788 | — | — | 116 | 0 | [mul_u16_u16_u32_shifted116.asm](routines/multiply/mul_u16_u16_u32_shifted116.asm) | [UMUL16_SHIFTED_EXACT.json](validation/records/UMUL16_SHIFTED_EXACT.json); exact full-domain event count |
| `mul_u16_u16_u32` | `shifted134` | 154.297827851 | — | — | 134 | 0 | [mul_u16_u16_u32_shifted134.asm](routines/multiply/mul_u16_u16_u32_shifted134.asm) | [UMUL16_SHIFTED_EXACT.json](validation/records/UMUL16_SHIFTED_EXACT.json); exact full-domain event count |
| `mul_u24_u24_u48` | `fast24` | 357.041715026 | 327 | 412 | 24 | 0 | [mul_u24_u24_u48_fast24.asm](routines/multiply/mul_u24_u24_u48_fast24.asm) | [mul_u24_u24_u48_fast24.asm](routines/multiply/mul_u24_u24_u48_fast24.asm); gmec uniform sample; fresh-X entry through RTS |
| `mul_u32_u32_u64` | `bounded133` | 606.337632 | 542 | 729 | 133 | 177 | [mul_u32_u32_u64_bounded133.asm](routines/multiply/mul_u32_u32_u64_bounded133.asm) | [UMUL32_BOUNDED133_GMEC.json](validation/records/UMUL32_BOUNDED133_GMEC.json); gmec uniform profile/validation corpus |
| `mul_u32_u32_u64` | `bounded133_compact` | 606.864799 | 543 | 733 | 133 | 162 | [mul_u32_u32_u64_bounded133_compact.asm](routines/multiply/mul_u32_u32_u64_bounded133_compact.asm) | [UMUL32_BOUNDED133_COMPACT_GMEC.json](validation/records/UMUL32_BOUNDED133_COMPACT_GMEC.json); gmec uniform profile/validation corpus |
| `mul_s24_s24_s48` | `fast24` | 395.756600 | 334 | 456 | 24 | 0 | [mul_s24_s24_s48_fast24.asm](routines/multiply/mul_s24_s24_s48_fast24.asm) | [SMUL24_OPTISEARCH_ORACLE.json](validation/records/SMUL24_OPTISEARCH_ORACLE.json); 30,000 deterministic C0FFEE pairs plus 4,265 independent oracle cases; native entry through RTS |
| `mul_s32_s32_s64` | `compact126` | **646.354530** | 548 | 757 | 136 | 126 | [mul_s32_s32_s64_compact126.asm](routines/multiply/mul_s32_s32_s64_compact126.asm) | [SMUL32_COMPACT126_100K.json](validation/records/SMUL32_COMPACT126_100K.json); 100,000-call native corpus; independent seed + edge suite also zero-error; see [profile-fit note](docs/SMUL32_COMPACT126.md) |
| `mul_s32_s32_s64` | `turbo135` | 665.877260 | 560 | 805 | 135 | 0 | [mul_s32_s32_s64_turbo135.asm](routines/multiply/mul_s32_s32_s64_turbo135.asm) | [SMUL32_TURBO135_100K.json](validation/records/SMUL32_TURBO135_100K.json); deterministic 100,000-call native corpus |
| `mul_s32_s32_s64` | `fast31_native_v2` | **692.825100** | 590 | 808 | 31 | 0 | [mul_s32_s32_s64_fast31_native_v2.asm](routines/multiply/mul_s32_s32_s64_fast31_native_v2.asm) | [SMUL32_FAST31_NATIVE_V2_100K.json](validation/records/SMUL32_FAST31_NATIVE_V2_100K.json); independent seed + 1,849-edge suite also zero-error |
| `mul_s32_s32_s64` | `fast31_native` | 697.259440 | 594 | 834 | 31 | 0 | [mul_s32_s32_s64_fast31_native.asm](routines/multiply/mul_s32_s32_s64_fast31_native.asm) | [SMUL32_FAST31_NATIVE_100K.json](validation/records/SMUL32_FAST31_NATIVE_100K.json); deterministic 100,000-call native corpus |
| `atan2_s8_s8_u8` | `compact_opt` | 47.462814 | 33 | 50 | 0 | 0 | [atan2_s8_s8_u8_compact_opt.asm](routines/atan2/standalone/atan2_s8_s8_u8_compact_opt.asm) | [ATAN2_STANDALONE_DISPATCH.json](validation/ATAN2_STANDALONE_DISPATCH.json); exhaustive signed-byte vectors; public JMP+RTS |
| `atan2_s8_s8_u8` | `sum_small` | 45.958908 | 29 | 48 | 0 | 0 | [atan2_s8_s8_u8_sum_small.asm](routines/atan2/standalone/atan2_s8_s8_u8_sum_small.asm) | [ATAN2_OPTIMIZATION_VALIDATION.json](validation/ATAN2_OPTIMIZATION_VALIDATION.json); exhaustive signed-byte vectors; public JMP+RTS |
| `atan2_s8_s8_u8` | `sum_fast` | 43.970627 | 31 | 45 | 0 | 0 | [atan2_s8_s8_u8_sum_fast.asm](routines/atan2/standalone/atan2_s8_s8_u8_sum_fast.asm) | [ATAN2_STANDALONE_DISPATCH.json](validation/ATAN2_STANDALONE_DISPATCH.json); exhaustive signed-byte vectors; public JMP+RTS |

## How to find the exact source

- **Shipped routine:** open the profile’s `standalone/<typed-name>.asm` file. `routines/SOURCE_CATALOG.csv` gives the exact path for every callable entry.
- **Standalone record/Pareto routine:** use the source link in the table above. Variant suffixes come after the typed geometry, e.g. `mul_s24_s24_s48_fast24`.
- **Machine-readable results:** `benchmarks/PUBLIC_PROFILE_RESULTS.csv`, `benchmarks/BEST_PROFILE_RESULTS.csv`, and `benchmarks/STANDALONE_RESULTS.csv`.
- **Naming:** `docs/NAMING_STANDARD.md`. Historical `MATH_*` symbols remain ABI-compatible.
