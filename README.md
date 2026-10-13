# C64 Math Library

High-performance integer, fixed-point and game math for the Commodore 64 / NMOS 6502/6510.

The library exposes one stable **56-entry public API** across five fixed profiles. V3/V4 add stateful Turbo16/Turbo32 calls; V4 also adds QS16. A Custom Pareto Builder can generate a stock-C64 mix for a chosen ZP/RAM budget.

## Start here

- **How fast are the routines?** [`PERFORMANCE.md`](PERFORMANCE.md)
- **Machine-readable results:** [`benchmarks/PUBLIC_PROFILE_RESULTS.csv`](benchmarks/PUBLIC_PROFILE_RESULTS.csv), [`benchmarks/BEST_PROFILE_RESULTS.csv`](benchmarks/BEST_PROFILE_RESULTS.csv), and [`benchmarks/STANDALONE_RESULTS.csv`](benchmarks/STANDALONE_RESULTS.csv)
- **Where is the exact source?** [`routines/SOURCE_CATALOG.csv`](routines/SOURCE_CATALOG.csv)
- **Want just one routine?** [Individual routine pickup guide](docs/INDIVIDUAL_ROUTINE_PICKUP.md) — direct links to V1–V5 source mirrors, resident API use, and portable-module limits
- **Calling/integration manual:** [`USER_MANUAL.md`](USER_MANUAL.md)
- **Naming convention:** [`docs/NAMING_STANDARD.md`](docs/NAMING_STANDARD.md)
- **Repository layout:** [`docs/STRUCTURE.md`](docs/STRUCTURE.md)
- **Moving an object toward a target:** use `MATH_SEEK8_*`/`MATH_SEEK16_*`, the exact Bresenham/DDA steppers ([`docs/SEEK_DDA.md`](docs/SEEK_DDA.md)), not vector normalization
- **Full-width multiply/divide:** use `MATH_UMULDIV16` / `MATH_SMULDIV16` for `(X16*Y16)/D16` without truncating the 32-bit product ([`docs/MULDIV16.md`](docs/MULDIV16.md))

Every published benchmark row now points to a public source file and SHA-256. Run `python3 tools/validate_public_catalog.py` to verify that contract.

## Fixed profiles

| Profile | Hardware | Main goal |
|---|---|---|
| **V1 Balanced** | Stock C64 | Low integration pressure, 31-byte normal ZP contract |
| **V2 Pareto-Fast** | Stock C64 | Faster resident choices where more ZP/private resources are acceptable |
| **V3 REU 512K** | C64 + 512 KiB REU | REU-backed services plus Turbo16/Turbo32 |
| **V4 REU 16M** | C64 + 16 MiB REU-compatible device/emulator | REU-heavy feature set, QS16, Turbo, exact REU ATAN2/ISQRT16 and accelerated exact ISQRT32 |
| **V5 Hybrid Low-ZP** | Stock C64 | V1 31-byte normal-ZP contract with selected faster V2-derived paths |

Use [`docs/VERSION_SELECTION.md`](docs/VERSION_SELECTION.md) for integration trade-offs.

## Performance snapshot

These are current public-entry means, through `RTS`; caller `JSR` and input stores are excluded unless documented otherwise.

| Routine | V1 | V2 | V3 | V4 | V5 |
|---|---:|---:|---:|---:|---:|
| `mul_u16_u16_u32` | 273.837 | 216.980 | 216.980 | 216.980 | 273.837 |
| `mul_s24_s24_s48` | 511.342 | 467.342 | 467.342 | 467.342 | 511.342 |
| `mul_s32_s32_s64` | 744.570 | 711.587 | 711.942 | 712.137 | 743.913 |
| `div_u16_u16_u16_16` | 132.726 | 127.774 | 125.424 | 125.626 | 126.386 |
| `div_u16_u16_u24_16_shl8` | 770.774 | 552.650 | 553.125 | 552.578 | 553.299 |
| `div_s16_s16_s24_16_shl8` | 846.155 | 715.633 | 714.005 | 712.610 | 630.805 |
| `recip_u16_u24_q16` | 108.498 | 94.823 | 66.234 | 66.234 | 95.044 |
| `div_s24_s24_s24_24` | 313.583 | 248.344 | 236.810 | 237.569 | 253.487 |
| `atan2_s8_s8_u8` | 47.463 | 43.971 | 43.971 | 48.000 | 43.971 |
| `seek_u8_u8_step` (per object per frame) | 87.137 | 87.137 | 87.137 | 87.137 | 87.137 |
| `seek_u8_u8_step1` (1 px/frame) | 65.954 | 65.954 | 65.954 | 65.954 | 65.954 |

For the complete table, resource use, min/max, corpora and source links, see [`PERFORMANCE.md`](PERFORMANCE.md).

The repository also publishes standalone record/Pareto alternatives, including the current 24-ZP signed 24x24 FAST24 point at **395.756600 cycles**, the SMUL32 `compact126` absolute native record at **646.354530 cycles** (**136 ZP + 126 persistent stack-page bytes**), and the new **31-ZP / stack-free** `fast31_native_v2` point at **692.825100 cycles**. The older `turbo135` point remains the faster high-ZP stack-free alternative at **665.877260 cycles**. These use their own documented benchmark bases and should not be compared blindly with public-profile means; see [`docs/SMUL32_COMPACT126.md`](docs/SMUL32_COMPACT126.md) and [`docs/SMUL32_FAST31_V2.md`](docs/SMUL32_FAST31_V2.md). The exact compact126 source is also exposed as an optional exclusive overlay in the V2/V3/V4 profile trees.

For the shipped API, V2/V3/V4 keep all six FAST31 pointer pairs in already-owned persistent ZP holes. This removes the ordinary pointer repair entirely: signed 32-bit multiply paths save **25 cycles**, unsigned paths save **22 cycles**, with no added stack-page use and V2 still inside its 221-byte ZP commitment.

## Source layout and naming

The historical `MATH_*` symbols and fixed addresses remain ABI-compatible. Source-facing names encode signedness and geometry, for example:

```text
mul_u8_u8_u16
mul_s16_s16_s32
div_u8_u8_u8_8
div_u32_u16_u32_16
```

Every callable fixed-profile entry has an exact source mirror under `<profile>/standalone/`. Independently benchmarked alternatives live under `routines/`. The complete source index is [`routines/SOURCE_CATALOG.csv`](routines/SOURCE_CATALOG.csv).

## Build

Requirements: Python 3. The deterministic assembler/build path is included; ACME is optional as an independent cross-check.

```sh
# V1-V4 reference and alternate maps
make reference
make alternate

# V5
make hybrid
make hybrid-validate

# Custom stock-C64 Pareto build
python3 tools/pareto_wizard.py
# or
python3 tools/build_pareto.py --zp-budget 60
```

See [`QUICK_START.md`](QUICK_START.md) and [`docs/SOURCE_RELOCATION.md`](docs/SOURCE_RELOCATION.md).

## Current ATAN2 selection

The ATAN2 kernels include the 2026-10-07 Repose dispatch refinement:

- V1: `compact_opt`, **47.462814** mean, 606 B occupied, 0 ZP;
- V2/V3/V5: `sum_fast`, **43.970627** mean, 1,109 B occupied, 0 ZP;
- V4: exact REU lookup, **48 cycles fixed**.

Negative-X inputs save 2 cycles; X=0 costs 4 extra cycles in V1 and 2 in V2/V3/V5. All outputs are unchanged. See the [OptiSearchV2 review](docs/OPTISEARCH_REVIEW_2026-10-07.md) for paired SMUL24 gains and validation.

Standalone `compact_opt`, `sum_small` and `sum_fast` sources remain available under [`routines/atan2/`](routines/atan2/).

## Validation and publication policy

The current tree keeps the buildable profiles, current validation evidence and source-backed benchmark alternatives, while removing the old top-level exploratory `research/` tree. Git history remains the archive for superseded experiments.

Useful checks:

```sh
python3 tools/generate_public_indexes.py
python3 tools/validate_public_catalog.py
python3 tools/validate_standalone_sources.py
make reference
make alternate
make package-audit
```

The library is **not reentrant**. Sequential calls in ordinary game/demo loops are supported; do not enter shared math state from an IRQ/NMI while another library call is active.

- V1 32/32 shared nonzero-divisor gate (issue #39): docs/V1_UDIV32_32_PRECHECKED_GATE_2026-10-11.md; remaining unsigned family audit stays open.

- Issue #39 shared UDIV16/UMOD16 branch transplant: docs/ISSUE39_UDIV16_BRANCH_TRANSPLANT_2026-10-11.md; unsigned family audit remains open.

- Issue #39 UDIV24/UMOD24 live-X equal-high optimization: docs/ISSUE39_UDIV24_EQUAL_HIGH_X_LIFETIME_2026-10-11.md. Wider unsigned family campaign not yet complete.

- Issue #39 same-input performance ranking audit: [methodology](docs/ISSUE39_BENCHMARK_COMPARABILITY_AUDIT_2026-10-11.md), [profile comparison](benchmarks/UNSIGNED_COMMON_PROFILE_RESULTS.csv). Unsigned `BEST_PROFILE_RESULTS.csv` entries are now based on matching operands.

- V1 Balanced UDIV24/UMOD24 narrow-quotient latency escape: docs/ISSUE39_V1_UDIV24_NARROW_ESCAPE_2026-10-11.md (explicit latency/mean trade-off; other issue39 unsigned audits open).

- Issue39 V5 dedicated 24-bit remainder frontend (zero extra ZP; 179 code bytes): docs/ISSUE39_V5_UMOD24_REMAINDER_TRANSPLANT_2026-10-11.md. Unsigned campaign remains open.

- V5 16/24-bit dedicated remainder paths fit within one final-page 256-byte region: docs/ISSUE39_V5_UMOD16_REMAINDER_TRANSPLANT_2026-10-11.md. Unsigned family campaign remains open.

- Issue #39 bounded-high-byte 32/32 V1/V5 q=1 optimization: docs/ISSUE39_UDIV32_32_HIGH_QONE_V1V5_2026-10-11.md. Other unsigned architecture audits remain open.

- [Issue #39 unsigned 32/16 multi-workload audit](docs/ISSUE39_UDIV32_16_WORKLOAD_DECISION_2026-10-11.md) provides reproducible workload-conditioned speed figures alongside the weighted profile ranking; the rejected V1 shortcut is **not** shipped.

- Issue #39 bounded-high-byte 32/32 V1/V5 q=2/3 optimization: docs/ISSUE39_UDIV32_32_HIGH_Q23_V1V5_2026-10-11.md. Other unsigned architecture audits remain open.

- Issue #39 zero-high-byte V1/V5 32/32 fallback bypass: docs/ISSUE39_UDIV32_ZERO_HIGH_BYPASS_2026-10-11.md. Other unsigned architecture audits remain open.

- Issue #39 V1 32/16 dual-loop quotient unroll: docs/ISSUE39_V1_UDIV32_16_DUAL_LOOP_UNROLL_2026-10-11.md. The unsigned DIV/MOD campaign remains open.

- V5 32/32 narrow-divisor shared fast-32/16 path: docs/ISSUE39_V5_3232_NARROW_DELEGATION_2026-10-11.md; the unsigned DIV/MOD family campaign remains open.

- Issue #39 unsigned 8/16/24 seven-workload audit: docs/ISSUE39_UNSIGNED_SMALL_WIDTH_WORKLOADS_2026-10-11.md; 53,760 public calls, negative V1 24-bit selector proof; no resident changes. Overall family campaign remains open.

- Issue #39 V1 Balanced exact unsigned 24/8 narrow-division fast path: docs/ISSUE39_V1_UDIV24_BYTE8_2026-10-11.md. The wider unsigned DIV/MOD campaign remains open.

- Issue #39 source-backed V1 32/32 guarded narrow-D8 divider: docs/ISSUE39_V1_3232_D8_DELEGATION_2026-10-11.md. The full unsigned DIV/MOD campaign remains open.

- Issue #39 V1/V5 source-backed 77-byte guarded remainder-only UMOD8: docs/ISSUE39_V1V5_UMOD8_GUARDED_REMAINDER_2026-10-11.md; exhaustive old/new V1/V5 validation and no ZP growth.

- Issue #39 V2 source-backed 101-byte D>=24 UMOD8: [qualification and resource/ABI contract](docs/ISSUE39_V2_UMOD8_D24_RELEASE_2026-10-12.md); V5 remains byte-for-byte unchanged, no additional ZP.

- Issue #39 signed16 identical-input and rejected V2 donor gate architecture: [docs/ISSUE39_SIGNED16_PAIRED_AND_V2_16BIT_DONOR_SCREEN_2026-10-12.md](docs/ISSUE39_SIGNED16_PAIRED_AND_V2_16BIT_DONOR_SCREEN_2026-10-12.md) (no code promotion).

- Issue39 source-verified no-growth V2–V5 16-bit known-carry branch pruning: [docs/ISSUE39_PR67_KNOWN_CARRY_16BIT_2026-10-12.md](docs/ISSUE39_PR67_KNOWN_CARRY_16BIT_2026-10-12.md); V1 unchanged, DIV/MOD campaign open.

- Issue #39 [V1 UDIV16/UMOD16 direct q=2 branch](docs/ISSUE39_PR68_V1_U16_DIRECT_Q2_EXIT_2026-10-12.md ): source-backed no-growth in-slot short-quotient improvement. Native VICE and 5-profile validation; unsigned family audit remains open.

- Issue #39 V1 UMOD16 OptiSearch-inspired q0 gate no-gain: [ABI and same-input rejection](docs/ISSUE39_V1_UMOD16_REPOSE_Q0_FRONTEND_REJECTION_2026-10-12.md); current shipped division code unchanged.

- Issue #39 V2/V3/V4 UMOD32/32 equality-only divide-by-zero test: [source/VICE/public-ABI proof](docs/ISSUE39_V234_UMOD32_LATE_ZERO_2026-10-12.md); size and ZP unchanged, family campaign open.

- Issue #39 V5 UMOD32/32 full-Q remainder front end: [source/native verified delayed-zero comparator](docs/ISSUE39_V5_UMOD32_QPRESERVING_REORDERED_2026-10-12.md); V1–V4 unchanged, unsigned family campaign remains open.

- Issue #39 V1 Balanced 69-byte 24/8 shared-subtraction DIV/MOD release: docs/ISSUE39_V1_UDIV24_SHARED_SUBTRACTION_RELEASE_2026-10-12.md. The unsigned campaign remains open.

- Issue #39 V1 accumulator 61-byte 24/8 shared DIV/MOD release: docs/ISSUE39_V1_UDIV24_ACCUMULATOR_RELEASE_2026-10-12.md. The unsigned campaign remains open.

- Issue #39 full-resident native VICE x64sc V1 24/8 verification: docs/ISSUE39_V1_24BY8_FULL_RESIDENT_NATIVE_VICE_2026-10-12.md; 384 correct old/new public calls, no native cycle claim.

- Issue #39 published SMC specialist vs 61-byte V1 resident: docs/ISSUE39_V1_UDIV24_ACCUMULATOR_SMC_SCREEN_2026-10-12.md. The 68-byte RAM-only routine remains independent and is not shipped in V1–V5.

- Issue #39 V1 RAM SMC 68-byte shared 24/8 release: docs/ISSUE39_V1_24BY8_SMC_INTEGRATED_RELEASE_2026-10-12.md. Requires writable RAM and non-reentrant execution; 61-byte fallback is retained; family-wide audit remains open.

- Issue #39 V2–V5 UDIV16/UMOD16 D-high gate microarchitecture audit: docs/ISSUE39_V2V5_U16_D1_CUTOFF_SCREEN_2026-10-12.md. Keep #15; no family-wide signoff.

- Issue #39 V2 UMOD8 exact-D24 guard no-gain screen: docs/ISSUE39_V2_UMOD8_GUARD_THRESHOLD_SWEEP_2026-10-12.md.

- Issue39 five-profile 32/16 N16 delegate A/B research: docs/ISSUE39_U3216_N16_DELEGATE_CURRENT_MAIN_2026-10-12.md. No default promotion.

- Issue39 32/16 N16 divisor-high-aware donor research: docs/ISSUE39_U3216_N16_DHI_GATED_SCREEN_2026-10-12.md. No default engine changed; family audit open.

- Issue39 12-byte N16 32/16 opt-in helper: docs/ISSUE39_U3216_N16_12BYTE_OPTIN_2026-10-12.md. Uses installed UDIV16; caller owns memory.

- Issue39 N24->UDIV24 donor no-gain research: docs/ISSUE39_N24_TO_U24_DONOR_SCREEN_2026-10-12.md. Existing 32/16 defaults retained.

- Issue39 32/16 power-of-two caller-opt-in specialist: docs/ISSUE39_U3216_POW2_OPTIN_2026-10-12.md. The divisor precondition is mandatory; public defaults stay unchanged.

- Issue39 current-resident OptiSearch unsigned 32/32 donor resource audit: docs/ISSUE39_U3232_OPTISEARCH_ABI_RESOURCE_SCREEN_2026-10-12.md. No default promotion.

- Issue39 current-resident 16-bit OptiSearch donor ABI matrix: docs/ISSUE39_U16_OPTISEARCH_PUBLIC_ABI_MATRIX_2026-10-13.md. No default promotion.

- Issue39 24÷8 writable-RAM caller-opt-in current resident screen: docs/ISSUE39_U24_D8_RAM_SMC_CURRENT_OPTIN_2026-10-13.md. Mandatory operand guard; no default change.

- Issue39 current-resident UDIV8 quotient-prefix source architecture sweep: docs/ISSUE39_UDIV8_PREFIX_PERPROFILE_SCREEN_2026-10-13.md. No default API/binary change.

- Generic 24-bit live-X high-quotient source proof: docs/ISSUE39_U24_HIGHGT_LIVE_X_2026-10-13.md. Not promoted to stable residents.

- Source-integrated general-purpose UDIV24 live-X optimization: docs/ISSUE39_U24_TXA_SOURCE_INTEGRATION_2026-10-13.md. Native VICE full-resident 960-call correctness verified; family campaign open.

- Issue #39 V1 32÷16 rare divide-zero path research (not installed by default): [verified paired emulator and native VICE evidence](docs/ISSUE39_V1_3216_RARE_ZERO_OUTOFLINE_2026-10-13.md). Full source/alternate/hybrid promotion remains open.

- Source-staged V1 32/16 cold zero-handler release: docs/ISSUE39_V1_3216_OOL_ZERO_PRODUCTION_2026-10-13.md (384 native VICE full-resident calls passed; independent PR/main CI pending).
