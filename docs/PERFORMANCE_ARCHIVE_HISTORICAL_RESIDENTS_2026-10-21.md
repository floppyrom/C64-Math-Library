# Historical performance charts — archived 21 October 2026

> **Historical, not the supported installer interface.** The material below is the original `PERFORMANCE.md` as it stood at the operation-first performance cutover. V1–V5 measurements are preserved for exact reproducibility and independent comparisons, not offered as selectable current installation profiles. The live performance guide is [PERFORMANCE.md](../PERFORMANCE.md). Some historical research-status wording was true only at its original publication time.

---

# Performance

> **Current installer (October 2026):** V1–V5 are *archived benchmark and
> compatibility baselines*, not installation choices. The supported
> operation-first build selects source-qualified variants for the user's
> exact operation set, RAM/ZP constraints and workload weights. Figures below
> describe fixed *historical resident* binaries; they are not guaranteed
> cycle totals or automatically preferred variants of every generated PRG.
> Use [the setup guide](docs/OPERATION_FIRST_USER_SETUP.md), the generated
> `selective_manifest.json`, and the [retirement evidence boundary](docs/PROFILE_RETIREMENT_EVIDENCE.md).


This is the quickest way to answer **“how fast is it?”** for the current C64 Math Library. All figures below are cycles measured at the public entry through `RTS`; caller `JSR` and input stores are excluded unless a row explicitly says otherwise.

The five fixed profiles use different memory/ZP trade-offs, so the fastest number is not automatically the best choice for every program. For exact code size, ZP ranges, stack reservation, corpus and a direct source link for every row, use [`docs/CONSOLIDATED_ROUTINE_TABLE.md`](docs/CONSOLIDATED_ROUTINE_TABLE.md) or [`benchmarks/PUBLIC_PROFILE_RESULTS.csv`](benchmarks/PUBLIC_PROFILE_RESULTS.csv). For a one-row-per-routine view that automatically selects the fastest shipped profile, use [`benchmarks/BEST_PROFILE_RESULTS.csv`](benchmarks/BEST_PROFILE_RESULTS.csv).

The V2/V3/V4 UDIV32 live-high core uses four ZP bytes on the wide-divisor hot path and averages 177.737 fewer cycles on the original paired uniform32 comparison. The finalized public graph also reaches the bounded UDIV32/16 and 17-bit-divisor fallbacks, so its whole-call static resource footprint is larger; see [the full comparison and resource accounting](docs/UDIV32_OPTISEARCH.md).

**Benchmark basis:** The unsigned DIV/MOD rows (UDIV8/16/24/32_16/32_32, UMOD counterparts and UDIV16_SHL8) now use **identical input pairs for all five profiles**. These common-corpus averages are reproducible but workload-dependent: see [the same-input results](benchmarks/UNSIGNED_COMMON_PROFILE_RESULTS.csv) for per-profile p95/worst-case, and the [audit methodology](docs/ISSUE39_BENCHMARK_COMPARABILITY_AUDIT_2026-10-11.md). The remaining published routine rows retain their existing distinct benchmark corpora and should not be treated as automatically comparable until independently certified. For V3/V4 REU-assisted functions, instruction cycles exclude external DMA/bus wait time.**

## Qualified newer source-build candidate (not the frozen shipped profiles)

The default rows below still refer to the **historical SHA-pinned binaries**. Issue #144 has separately integrated new source-level optimizations in the **five canonical source profiles**. The independently reproducible [versioned distribution builder](docs/ISSUE144_VERSIONED_DISTRIBUTION_2026-10-16.md) outputs both memory maps and current `math_api.inc` headers; its ZIP includes a complete same-input current-source-versus-frozen ISQRT32 report. This is **not yet a promoted/tagged production-default release**.

| ISQRT32 profile | Historical frozen PRG | Current canonical-source candidate | Saved per ordinary public call |
|---|---:|---:|---:|
| V1 | 1263.164383 | 1212.164383 | 51.000000 |
| V2 | 1095.127854 | 1048.127854 | 47.000000 |
| V3 | 1095.157534 | 1048.157534 | 47.000000 |
| V4 | 924.082192 | 788.876712 | **135.205479** |
| V5 | 1263.164383 | 1212.164383 | 51.000000 |

**Benchmark basis:** exactly 438 matched N32 operands/profile, 6502-model CPU instruction cycles counted for public calls through RTS. The V4 current-source result includes the [PR #192 direct-REU-to-zero-page improvement](https://github.com/floppyrom/C64-Math-Library/pull/192) (16 more cycles saved per call than the preceding source). These candidate numbers must **not** replace shipped measurements computed from different corpora. Real C64/VIC/REU DMA bus timing and IRQ/NMI safety have **not** been certified. No historical reference PRG/REU is altered.

## Shipped profile means

### Multiply

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_UMUL8` | `mul_u8_u8_u16` | 84.490234 | 72.494141 | 69.000000 | 69.000000 | 84.490234 |
| `MATH_UMUL16` | `mul_u16_u16_u32` | 273.837200 | 216.980037 | 216.980037 | 216.980037 | 273.837200 |
| `MATH_UMUL24` | `mul_u24_u24_u48` | 465.042329 | 417.783224 | 417.783224 | 417.783224 | 465.042329 |
| `MATH_UMUL32` | `mul_u32_u32_u64` | 712.235367 | 690.235367 | 690.235367 | 690.235367 | 712.235367 |
| `MATH_SMUL8` | `mul_s8_s8_s16` | 67.992188 | 67.992188 | 67.992188 | 67.992188 | 67.992188 |
| `MATH_SMUL16` | `mul_s16_s16_s32` | 282.588064 | 245.802333 | 246.107696 | 246.144492 | 282.262957 |
| `MATH_SMUL24` | `mul_s24_s24_s48` | 511.342357 | 467.342357 | 467.342357 | 467.342357 | 511.342357 |
| `MATH_SMUL32` | `mul_s32_s32_s64` | 744.128269 | 711.153591 | 711.447073 | 711.706102 | 743.477377 |

### Divide

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_UDIV8` | `div_u8_u8_u8_8` | 65.093306 | 65.206085 | 52.227992 | 52.227992 | 65.206085 |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | 156.087578 | 161.758520 | 161.758520 | 161.758520 | 161.758520 |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | 164.369661 | 156.996423 | 156.996423 | 156.996423 | 156.996423 |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | 825.041041 | 617.202638 | 617.202638 | 617.202638 | 617.202638 |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | 335.761085 | 242.548553 | 242.548553 | 242.548553 | 275.013192 |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | 88.372650 | 88.372650 | 88.372650 | 89.009821 | 90.272098 |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | 187.131298 | 168.317557 | 170.508833 | 168.673064 | 170.540022 |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | 313.583206 | 248.344384 | 236.810251 | 237.569466 | 253.487023 |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | 955.051690 | 724.392148 | 724.449509 | 721.003490 | 722.170774 |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | 566.839288 | 420.452435 | 416.865672 | 418.153927 | 572.005880 |

V3/V4 `MATH_UDIV8` now uses a quotient-0..3 CPU fast path and falls back to the exact REU quotient/remainder planes only for quotient 4+. The exhaustive 65,536-input mean is **52.852264 cycles** (28–115), with zero errors.

### Modulo / fixed-point

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_UMOD8` | `mod_u8_u8_u8` | 58.439757 | 57.292901 | 48.882759 | 48.882759 | 58.129412 |
| `MATH_UMOD16` | `mod_u16_u16_u16` | 189.127859 | 198.601173 | 198.601173 | 198.601173 | 198.601173 |
| `MATH_UMOD24` | `mod_u24_u24_u24` | 230.804894 | 207.493883 | 207.493883 | 207.493883 | 207.493883 |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | 842.919648 | 591.943109 | 591.943109 | 591.943109 | 591.943109 |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | 399.573607 | 279.619941 | 279.619941 | 279.619941 | 299.582991 |
| `MATH_SMOD8` | `mod_s8_s8_s8` | 98.157813 | 97.066406 | 97.152344 | 99.020313 | 96.707813 |
| `MATH_SMOD16` | `mod_s16_s16_s16` | 229.324910 | 231.801444 | 234.592780 | 228.168231 | 231.605054 |
| `MATH_SMOD24` | `mod_s24_s24_s24` | 427.272924 | 337.075090 | 329.971841 | 326.184838 | 339.607942 |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | 1061.083032 | 710.773285 | 710.713357 | 708.426715 | 704.786282 |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | 766.253430 | 453.633213 | 443.528520 | 458.087365 | 765.857040 |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | 304.804139 | 243.804139 | 243.804139 | 243.804139 | 304.804139 |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | 313.154093 | 276.888787 | 276.888787 | 276.888787 | 313.154093 |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | 777.876404 | 755.876404 | 755.876404 | 755.876404 | 777.876404 |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | 810.544371 | 778.302454 | 778.302454 | 778.302454 | 810.544371 |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | 729.262734 | 550.554416 | 550.554416 | 550.554416 | 550.554416 |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | 846.155071 | 630.032715 | 630.265213 | 628.417884 | 628.885496 |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | 108.497635 | 94.822998 | 57.331436 | 57.331436 | 95.044128 |

V5 now eliminates a repeated divisor-zero check in its shared 32/32 division/modulo slow path, with no new ZP. Its paired 6,801/1,553-case means are **409.633142/537.266581 cycles** (previously 421.077342/548.000000). See [V5 nonzero-gate proof](docs/V5_UDIV32_32_NONZERO_GATE_2026-10-11.md).

V2/V3/V4 now give `MATH_UMOD16`, `MATH_UMOD24`, and `MATH_UMOD32_32` dedicated remainder-only front ends. Quotient-0/1 (or equality) cases return without materializing quotient bytes; harder cases rejoin the exact existing divider. Signed modulo was measured separately and deliberately left unchanged because the analogous front end was slower.

### Trig / roots / game math

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_SIN8` | `sin_u8_s8` | 23.000000 | 23.000000 | 23.000000 | 23.000000 | 23.000000 |
| `MATH_COS8` | `cos_u8_s8` | 29.000000 | 23.000000 | 23.000000 | 23.000000 | 23.000000 |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | 39.000000 | 31.000000 | 31.000000 | 31.000000 | 31.000000 |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | 47.462814 | 43.970627 | 43.970627 | 48.000000 | 43.970627 |
| `MATH_ISQRT16` | `isqrt_u16_u16` | 57.878998 | 58.234467 | 58.277435 | 54.000000 | 57.878998 |
| `MATH_ISQRT32` | `isqrt_u32_u16` | 1219.260533 | 1053.284504 | 1053.325908 | 917.317433 | 1219.260533 |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | 81.550583 | 75.538910 | 75.038910 | 75.038910 | 81.550583 |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | 87.550583 | 81.538910 | 81.038910 | 81.038910 | 87.550583 |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | 159.128794 | 159.128794 | 156.661198 | 156.661198 | 159.128794 |

### Movement (seek)

Exact Bresenham/DDA "move toward target" steppers ([`docs/SEEK_DDA.md`](docs/SEEK_DDA.md)). `*_INIT` is once per move; `*_STEP*` is once per object per frame. Every frame of every benchmark move is verified against the Bresenham model.

| Routine | Typed name | V1 | V2 | V3 | V4 | V5 |
|---|---|---:|---:|---:|---:|---:|
| `MATH_SEEK8_INIT` | `seek_u8_u8_init` | 601.746936 | 543.965482 | 544.686887 | 544.686887 | 601.746936 |
| `MATH_SEEK8_STEP` | `seek_u8_u8_step` | 87.136511 | 87.136511 | 87.136511 | 87.136511 | 87.136511 |
| `MATH_SEEK8_STEP_INT` | `seek_u8_u8_step_int` | 70.992770 | 70.992770 | 70.992770 | 70.992770 | 70.992770 |
| `MATH_SEEK8_STEP1` | `seek_u8_u8_step1` | 65.953959 | 65.953959 | 65.953959 | 65.953959 | 65.953959 |
| `MATH_SEEK16_INIT` | `seek_u16_u8_init` | 783.093546 | 702.606005 | 700.936887 | 700.936887 | 783.093546 |
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
