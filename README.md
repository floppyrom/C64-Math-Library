# C64 Math Library

High-performance integer, fixed-point and game math for the Commodore 64 / NMOS 6502/6510.

The **operation-first builder** is the default way to configure a stock C64 library: select from **56 independently linkable public operations**, specify resource limits and emit only the needed code. The five historical fixed profiles are retained as verified compatibility/performance references while their fastest kernels are migrated. V3/V4 additionally provide REU/Turbo services, and V4 QS16, that are not yet replaced by the operation-first builder.

The builder also offers a **tableless ISQRT16** for memory-constrained C64
programs (137 bytes code + 6 bytes scratch, no ZP), preserving the original
fast square-table implementation as the automatic speed-preferred option.

The certified original V1/V5 signed Q8.8 vector normalizer is now also eligible for authenticated `speed` builds: it retains its 3,587-byte aligned code/table image, four private ZP bytes and self-modifying code requiring executable RAM. Its single unchanged source is compared on 512 identical complete public calls at two origins; see `docs/VEC2_STOCK_PUBLIC_SPEED.md`.

The signed 16-bit quotient/remainder APIs additionally offer a shared source-linked historical V2 magnitude divider with a signed public adapter. This fast donor occupies 1,705 code bytes and eight ordinary scratch bytes, with zero ZP. The existing 206-byte compact zero-ZP implementation remains selectable when RAM is constrained. See `docs/SDIV16_SMOD16_V2_SHARED.md`.

SEEK8/SEEK16 INIT and per-frame steppers now have original-source full-public movement-cycle provenance, including arrival and post-arrival, for all eight public entries. Two physical code/I/O placements and native VICE proofs preserve the one-producer-per-family state layout; see `docs/SEEK_PUBLIC_SPEED.md`. No alternative slower DDA kernel was introduced. These timings remain CPU-model estimates, not PAL badline/IRQ budgets.

The **profile-retirement evidence gate** now distinguishes the 56 source-speed-qualified stock APIs from nine additional V3/V4 REU/Turbo/QS16 public lifecycle exports. It inventories profile symbol files and mode-private ZP ownership, and refuses to mark full hardware and historical speed parity as complete. Run `python3 tools/profile_retirement_audit.py --out build/retirement.json`; see `docs/PROFILE_RETIREMENT_EVIDENCE.md`. No legacy profiles or REU images are deleted.

A **five-way, identical-public-input UMUL32 busiest-frame parity audit** is now available: the compact zero-ZP, unified shared, quarter-square, original FAST31 and physically shared FAST31 versions are built at two identical addresses and scored on 150 full64 public calls across 24 synthetic frames. The report preserves resource, per-call regression, worst-frame and SHA provenance; see `docs/UMUL32_ALL_FIVE_PAIRED_FRAME_PARITY.md`. These are CPU-model cycles, not PAL/VIC-II/IRQ or REU timing.

The historical `SMUL32` signed full64 variants can now be compared on **150 identical complete public calls over 24 synthetic frames**, at two code/I/O relocations. The report preserves full64 correctness, carry/stack/inputs, permitted FAST31 SMC operands, source/PRG hashes, peak and p95 math-frame cycles, individual-call regressions, RAM/ZP and shared-source costs; see `docs/SMUL32_FOUR_PAIRED_FRAME_PARITY.md`. This is a CPU-model math-only measurement and does not replace PAL/VIC-II/IRQ hardware qualification.

A **project-level joint signed/unsigned 32×32→64 multiplication comparison** now distinguishes the one-image original FAST31 shared producer from two independent FAST31 images, compact sources and the six-entry unified compact source. It measures 150 identical interleaved public calls over 24 synthetic frames at two memory origins and reports actual shared code/table RAM cost, 31-ZP requirements, slower calls and peak-frame math CPU-model cycles. See `docs/MUL32_JOINT_SHARED_VS_SEPARATE.md`. This does not certify physical PAL timing.

The signed/unsigned 32-bit shared-vs-separate comparison also provides an **offline peak-frame and RAM/ZP Pareto frontier**, checking both memory placements and exact input/source hashes before selecting a full two-API plan. See [the project-level frame selection gate](docs/MUL32_JOINT_SHARED_VS_SEPARATE.md); it does not yet replace weighted-mean automatic builder selection or certify physical PAL time.

**Start without profiles:**

```sh
make builder-list
make builder-measure
make builder
# Or: make builder CONFIG=your-operations.json OUT=build_my_game
```

The example selects UMUL16, UDIV16 and ISQRT16. Output is a minimal
`math_selective.prg`, `math_api.inc`, and a machine-readable selection manifest.
For arbitrary operations, edit a copy of [`examples/operation-first.json`](examples/operation-first.json).

**Performance is a separate objective:** the normal `make builder` example
uses `balanced` and can select a slower source to save RAM or zero page.
It is **not** a fastest-possible profile. To compare qualified sources on
complete same-input public calls, use:

```sh
make builder-speed OUT=build_speed
# Or set SPEED_CONFIG=your-speed-operations.json with positive per-frame
# workload_calls for every operation and realistic RAM/ZP budgets.
```

The exact V1–V5 SIN8/COS8/SINCOS8 public sources now have authenticated,
all-256-phase same-call speed models at two origins, sharing **one** immutable
256-byte sine table. No historical routine is replaced by a slower source;
see `docs/TRIG8_SHARED_PUBLIC_SPEED.md`.

A new source-identical SEEK8/SEEK16 frame-trace experiment compares synchronized bursts versus four INIT retargets per frame over four frames, retaining the same cold-start cost and 48 INIT calls across 24 frames. This is a scheduling change with different object histories, **not a faster kernel**; see `docs/SEEK_MIXED_FRAME_PARITY.md`.

The operation-first builder now has a deterministic mixed SEEK8/SEEK16 50 Hz-style math-only trace from the actual linked binary: 16 concurrent sprite-slot step calls per frame, periodic INIT bursts, and a source/manifest-backed CSV for worst-frame scoring. This is a **synthetic CPU-model** workload, not actual PAL/VIC-II/IRQ elapsed timing; see `docs/SEEK_MIXED_FRAME_PARITY.md`.

The original V1–V5 signed8 `SDIV8` and `SMOD8` Q/R producer now has
identical-corpus complete-public-call speed provenance for both exports.
Both names continue to share one 530-byte physical source and one ZP byte;
see `docs/SDIV8_SMOD8_SHARED_PUBLIC_SPEED.md`.

`DIST8_FAST` also authenticates the unchanged historical V1 61-byte
signed8 approximate-distance source over 512 identical full-public calls.
Its max/min approximation is preserved, not substituted with a slower
or more precise source; see `docs/DIST8_FAST_PUBLIC_SPEED.md`.

Speed selection now covers all 56 of the 56 APIs, including signed 24-bit and both signed 32-bit DIV/MOD families. Unsupported speed
comparisons **fail closed**, not silently fall back to a slower size-selected
routine. The remaining historical V1–V5 speed donors still require transplantation,
matched-public-ABI comparisons and worst-frame qualification before profiles
can be retired. See the [performance-parity checklist](docs/PERFORMANCE_PARITY_GATE.md).

A new stock-C64 **read-only `SMUL8` quarter-square** option complements the
original V1–V5 signed8 self-modifying producer. On 512 identical full-public
calls, historical V1 averages about **68 cycles** while the smaller, read-only
source averages **123 cycles**. It uses 1,159 code+table bytes and two scratch
bytes with 0 ZP, rather than V1's four original 511-byte lookup planes and
46-byte self-modifying code. Keep V1 as the speed winner when eligible; the
read-only candidate is a RAM/ROM-safety Pareto choice, not a speed upgrade.
See [SMUL8 source tradeoffs](docs/SMUL8_READONLY_QS.md).

The historical $CA-biased 24-bit quarter-square multiply source can now
serve **both** unsigned UMUL24 and signed SMUL24 calls using **one physical
producer, four shared table planes and 24 ZP bytes**, rather than duplicating
the lookup image. For the faster measured variants use:

```sh
make builder-speed SPEED_CONFIG=examples/operation-first-shared24-speed.json OUT=build_shared24
```

The signed `SDIV16_SHL8` now retains both the 237-byte zero-ZP portable
kernel and a 2,624-byte/12-ZP source-linked canonical V2 fast magnitude
producer. Its Q24/R16/C public-call performance is independently certified;
see `docs/SDIV16_SHL8_V2_BUILDER.md`.

The signed Q8.8-scaled `SMUL16_SHR8` adds a separate 1,383-byte,
zero-ZP quarter-square fast public source, four scratch bytes, and preserves
the portable 184-byte six-scratch choice. Qualified timing uses complete
signed24 public calls and synthetic busy-frame models; see
`docs/SMUL16_SHR8_QS_BUILDER.md`.

The signed `SMUL16` operation also offers a 0-ZP source-linked quarter-square
1,351-byte code/table producer with four ordinary scratch bytes, preserving
the compact 161-byte/zero-ZP six-scratch alternative. Both have identical
full signed32 public-call comparisons, and the historical profiles remain
available until performance parity is certified. See `docs/SMUL16_QS_BUILDER.md`.

A stock-C64 reciprocal speed frontier now offers the original 99-byte compact,
448-byte historical-threshold and 1,544-byte exact-table alternatives for
`URECIP16_Q16`. All three use zero ZP and require no REU; automatic speed
selection uses identical complete public-call source-model comparisons, not
historic REU resident timing. [Qualification and resource details](docs/RECIP16_THRESHOLD_STOCK_BUILDER.md).

The historical V2 32/16 fast division core is now independently linkable for
UDIV16_SHL8: approximately 719 full public-call model cycles versus 1,777
for the 129-byte portable 0-ZP fallback on identical 384-case inputs.
The fast variant requires 2,368 code bytes and 12 call-exclusive ZP bytes,
and keeps the slower source for constrained projects. The 24-frame model
workload and native VICE qualifications are not physical PAL timing.

The existing compact 156-byte unsigned / 227-byte signed 0-ZP kernels
remain independently selectable when code RAM or ZP is constrained.
Native VICE, same-corpus public-call and mixed-frame qualification are
required before treating this as a complete speed-parity upgrade.

The [biased quarter-square carry-offset strategy](docs/BIASED_QUARTERSQUARE_CARRY_OFFSETS.md)
from the historical shifted UMUL16 family is explicitly preserved, with
exhaustive table-arithmetic tests (`make builder-biased-qs-test`).
[Full setup and legacy transition notes](docs/PROFILE_RETIREMENT_PLAN.md).
For workload-aware speed optimization of the measured operations, including 32-bit multiplication and 32/16 division, try
`make builder CONFIG=examples/operation-first-speed.json OUT=build_speed`.
For unrestricted `UDIV32_32` the selector compares the 4-ZP and
4-byte RAM-scratch 32/32 quotient/remainder implementations on the same
384-pair public-call corpus; `UMOD32_32` has an independently measured
specialized zero-ZP remainder producer (one published candidate so far).
The optional `link:shared-aligned-zerozp` variant lets both public 32/32
DIV and MOD reuse one aligned quotient/remainder producer: 576 code bytes,
4 ordinary scratch bytes, 0 ZP, and 612 B main RAM including I/O. The
independently selectable specialized modulo implementation remains available.
The optional `link:v2-lowdivisor-hybrid` incorporates the source-validated
V2 Pareto-fast 32/16 public producer and an unrestricted 32/32 fallback.
It exports both Q32/R32 public calls from one 2,496-byte image with 12
call-exclusive ZP bytes (2,528 B main RAM including public I/O at `$8000`).
The speed selector compares it on the same 384-pair unrestricted corpus,
retaining all lower-memory options. Hardware-native timing is not claimed.
The source-qualified signed 24/24 `SDIV24` and `SMOD24` implementations
now participate in matched 512-input full-public-call speed selection:
compact restoring (0 ZP), quotient-zero guard (0 ZP), or the relocated
historical V3-magnitude kernel (9 ZP). The signed24 option is selected
according to the actual workload, RAM and zero-page budget, never by
incomparable historical resident timing. For example:

```sh
make builder-speed SPEED_CONFIG=examples/operation-first-signed24-speed.json OUT=build_signed24
```

For historical V2 signed `SDIV32_16` and `SMOD32_16`, the operation-first
installer retains the original compact 260-byte/0-ZP shared kernel alongside
the V2-magnitude 2,880-byte/12-ZP shared producer. The speed objective
compares both on the identical 384-case complete public-call corpus. It can
select the faster V2 implementation automatically with a sufficient RAM/ZP
budget, rather than asking the user to choose a historical profile:

```sh
make builder-speed SPEED_CONFIG=examples/operation-first-signed32-speed.json OUT=build_signed32
# Unsigned 24-bit full 48-bit result, qualified historical V2 biased tables:
make builder-speed SPEED_CONFIG=examples/operation-first-umul24-speed.json OUT=build_fast_umul24
# Full-width signed 32/32, automatically selecting the qualified V2 hybrid:
make builder-speed SPEED_CONFIG=examples/operation-first-signed3232-speed.json OUT=build_signed3232
```

The busy-frame source-model comparison covers both layouts and records the
worst frame; native VICE qualification covers both public DIV/MOD aliases.
This does not establish full-56-operation or physical-PAL worst-frame parity.

For `UDIV32_16` / `UMOD32_16`, the builder independently measures both
zero-ZP shared quotient/remainder producers on identical 384-input public-call
corpora; the zero-ZP 1771-byte statically unrolled accumulator derivative is an
additional selectable speed-over-RAM candidate. It retains one ordinary
scratch byte and independent shared Q/R public aliases. The historical V2 12-ZP 32/16 size-fast producer can also be independently
linked behind the complete public ABI using `link:v2-sizefast-public`.
Its measured same-input full-public average is approximately 933 cycles,
versus 1,774 cycles for the unrolled zero-ZP implementation; choosing it
requires 12 ZP and 2,400 B total main RAM at `$8000`. No fixed profile
needs to be loaded.
The operation-first binary backend currently targets **stock C64 only**;
1541/1571/1581 remain planning-only, and historic REU/Turbo/QS16 functionality
still requires the corresponding legacy profile. For UMUL32, the historical V2 FAST31 public-ABI kernel is now a selectable
31-byte-ZP, writable-code candidate with four page-aligned quarter-square
lookup tables. The builder compares its complete public-call cycle cost with
three alternative algorithms on the same 192 operand pairs. The signed SMUL32 implementation also now supports historical FAST31.
Select `link:fast31-shared-full64` for BOTH operations and the builder
links one arithmetic core and four page-aligned table slots: 2,592 B RAM
(including 32 B public I/O) and 31 call-exclusive ZP at a page-aligned
`$8000` start, versus 5,152 B RAM for two separately linked FAST31 images.
The workload-aware selector can choose this shared producer automatically
when both public APIs and their RAM/ZP budgets permit it.
The same `link:fast31-shared-full64` producer can now be pinned for
`UMUL32_READY`, `SMUL32_READY`, `UMUL32_SHR16`, and `SMUL32_SHR16`.
These six operations then use just one code+table image and 31 bytes of ZP.
The four READY/SHR16 operations additionally have their own matched-input
complete-public-call CPU-model speed rankings. Under the `speed` objective,
the optimizer can choose the shared FAST31 image across all six 32-bit APIs,
or retain a 0-ZP compact source when memory limits make FAST31 infeasible. Historical-core means are not compared with
public-call timing. Other operations still need fast-kernel migration; the
selection model's timing is a CPU-model estimate, not native VICE cycle data.

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

## Legacy fixed profiles (reference and compatibility)

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

**Default: operation-first.** Run `make builder` or `make builder CONFIG=your-operations.json`.
The historical profile build commands below remain opt-in release tools.

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

- Source-staged V1 32/16 cold zero-handler release: docs/ISSUE39_V1_3216_OOL_ZERO_PRODUCTION_2026-10-13.md (384 native VICE full-resident calls passed; PR #102 merged; PR/main CI green).

- Root optimization release-stage evidence: docs/ISSUE39_INTEGER_ROOTS_SOURCE_RELEASE_2026-10-13.md (native VICE: 768 old/new full-resident calls PASS; PR #102 merged; PR/main CI green).

- V2 UMUL8 public direct-result source release: docs/ISSUE39_V2_UMUL8_DIRECT_OUTPUT_2026-10-13.md (native x64sc 128 old/new public calls PASS; independent PR/main CI pending).

The standard unsigned multiply family (UMUL8/16/24/32 and stateful READY) is [qualified and complete](docs/ISSUE39_UNSIGNED_MULTIPLY_FAMILY_REVIEW_2026-10-14.md). REU Turbo/QS multiply modes are separate.

For the signed SMUL8/16/24/32 and conditional SMUL32_READY profiles see the [Issue #39 signed multiply ABI/resource and OptiSearch audit](docs/ISSUE39_SIGNED_MULTIPLY_FAMILY_2026-10-14.md).

The [REU Turbo16/Turbo32 and V4 QS16 matched-input multiply audit](docs/ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md) documents batch break-even, pointer ownership and REU-specific hardware caveats.
