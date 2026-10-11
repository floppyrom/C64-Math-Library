# Issue #39 — cross-profile benchmark comparability and V1 divider audit

**Date:** 2026-10-11. **Status:** independently remeasured and published, without changing shipped arithmetic code or ABI. The overall unsigned DIV/MOD campaign remains open.

## Root cause of the suspicious V2–V4 differences

`tools/validate_unsigned_division.py` deliberately varies its random-number seed with `pi=PROFILES.index(p)`: `0xD1700000 + pi*0x10000 + …` for quotient operations, and `0xA7700000 + pi*0x1000 + …` for modulo aliases. This expands correctness coverage across different operands, but means the resulting public-entry means cannot be compared as if they were paired trials. Because division latency depends enormously on operand ratio and zero/high bytes, apparent V3 slowdowns of several cycles were artifacts of different inputs, not necessarily different code.

We **retain this broad varied-seed correctness audit unchanged**, and introduce a separate `tools/benchmark_unsigned_common_corpus.py` that runs exactly the same dividend/divisor pairs across all profiles, validates every arithmetic output/carry and input-preservation contract, and publishes class-specific mean, p95, worst-case and SHA-256 case fingerprints. All 11 unsigned public APIs are included: UDIV8/16/24/32_16/32_32; UMOD8/16/24/32_16/32_32; UDIV16_SHL8. These are fixed deterministic sampled/edge/stress corpora, not a distribution-independent full-domain mean. Exhaustive UDIV8 and reciprocal validation remain separate.

The full common corpus makes **136,335 public machine-code calls** using original PR #49 main-branch resident binaries. Exact per-input equality is confirmed for all 4,753 UDIV24 cases across V2–V5 and all 1,553 UMOD24 cases across V2–V4. 0 wrong results or mutated inputs.

## Same-corpus results (mean CPU instruction cycles)

| API | V1 | V2 | V3 | V4 | V5 |
|---|---:|---:|---:|---:|---:|
| UDIV8 | 65.093 | 65.206 | 52.228 | 52.228 | 65.206 |
| UMOD8 | 67.295 | 66.848 | 48.883 | 48.883 | 66.848 |
| UDIV16 | **156.348** | 161.761 | 161.761 | 161.761 | 161.761 |
| UMOD16 | **189.384** | 198.611 | 198.611 | 198.611 | 205.029 |
| UDIV24 | 189.742 | **157.851** | **157.851** | **157.851** | **157.851** |
| UMOD24 | 306.578 | **207.491** | **207.491** | **207.491** | 214.992 |
| UDIV32/16 | 896.062 | **617.203** | **617.203** | **617.203** | **617.203** |
| UMOD32/16 | 916.280 | **591.943** | **591.943** | **591.943** | **591.943** |
| UDIV32/32 | 470.756 | **242.549** | **242.549** | **242.549** | 470.756 |
| UMOD32/32 | 523.280 | **295.998** | **295.998** | **295.998** | 523.280 |
| UDIV16_SHL8 | 798.612 | **550.554** | **550.554** | **550.554** | **550.554** |

The fastest-profile source index uses these identical-input metrics for the listed routines; identical minima are resolved by stable profile order. It still retains the resource costs of the selected profile. Other routine families' rankings remain on their previously published benchmark bases pending their own corpus audits.

## Is V1 UDIV24/UMOD24 actually that slow?

**Yes, for large quotients; no, not universally.** V1's Balanced implementation uses the compact `q0counter t19/k9` source under `REG_TABLE+$1200`, whereas V2–V4 use a larger, more unrolled `q0counter t13/k13` implementation under `REG_KERNEL+$0800`. V5 imports the faster V2 24-bit donor despite its low-ZP base. On the common UDIV24 set, quotient 0 paths are identical (58.0 cycles in both V1/V2), and large quotient differences dominate:

| Input class | V1 UDIV24 | V2 UDIV24 | V1 UMOD24 | V2 UMOD24 |
|---|---:|---:|---:|---:|
| Uniform random component | 135.457 | 132.597 | 134.827 | 120.954 |
| Quotient 0 | 57.99 | 57.99 | 61.92 | 51.30 |
| Quotient >255 | **2,098.8** | **859.9** | **2,151.3** | **876.2** |
| Maximum latency in tested corpus | 3,235 | 1,412 | 3,235 | 1,419 |

Examples: 0xFFFFFF / 1 takes **3,235 cycles V1 vs 989 V2**; 0xFFFFFF / 2 takes **3,097 vs 984**. The structured edge inputs intentionally oversample narrow divisors compared with uniformly random 24-bit dividends/divisors. Thus V1's 24-bit *overall* mean is very sensitive to workload mix. The lower V1 `UDIV16`/`UMOD16` common-corpus means also demonstrate that it is wrong to treat V1 as generally inferior for every width.

V1's **31-byte normal shared-ZP contract** is a genuine profile constraint; V2 has a more expansive normal-ZP scratch envelope. A faster V1 high-quotient dispatch or transplant must be validated under V1's actual source-region size, normal-ZP ownership, alternate relocation, signed/shared callers and current resident code. Do **not** substitute V2 binary blindly. This audit identifies a candidate search direction but does not claim an integrated V1 optimization.

## Additional benchmark caveats and release contract

- **Paired comparison:** same bits, same list, same call semantics, source-built reference residents; `mini6502` instruction cycles include RTS, exclude caller JSR/input stores.
- **Distribution:** report means separately for zero divisor, quotient 0, quotient 1, quotient 2–9, quotient 10–255 and quotient 256+, as well as original edge/random/stress classes. p95 and maximum are in `benchmarks/UNSIGNED_COMMON_PROFILE_RESULTS.csv`.
- **REU:** V3/V4 may use REU-backed accelerators (notably UDIV8); 6502 instruction-cycle totals **exclude external REU DMA/bus time and hardware stalls**, so they are not direct PAL raster-cycle performance guarantees.
- **Stable ranking:** `benchmarks/BEST_PROFILE_RESULTS.csv` selects these eleven unsigned winners only using `validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json`. Other entries retain the original basis. Generator and validator reject stale SHA-256 reference PRGs.
- **Correctness:** keep running `tools/validate_unsigned_division.py` on differently seeded profiles; the common-input benchmark is a distinct independent performance gate.
- **OptiSearch:** a constrained superoptimizer was useful for a small UDIV16 unreachable-branch improvement, and earlier native/algorithmic architectures informed faster V2/V3/V4 code. The V1 24-bit tail opportunity is an architecture/resource problem and cannot be declared solved by the existing small OptiSearch transplant.

This report is tied to issue #39. The unsigned DIV/MOD family and the broader library-wide campaign are **not** marked finished.
