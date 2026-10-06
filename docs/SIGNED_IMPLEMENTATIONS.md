# Signed implementations

## Definition used by this release

A routine is **native signed** when its signed public API owns the executable arithmetic path and never enters the corresponding unsigned executable multiply/divide engine. A native signed implementation may share immutable lookup tables or arithmetic identities with an unsigned implementation; code ownership, not mathematical novelty, is the enforceable boundary. Sign handling remains part of the signed path before it returns.

This definition prevents the previous ambiguity where a signed wrapper could reuse a full unsigned producer and merely correct the result afterward. `tools/validate_signed_layout.py` traces the executable graph of every signed/unsigned pair and requires zero overlap.

For source transparency, every signed API also has an exact per-routine executable mirror under each profile's `resident/signed/{multiply,division}/native/` directory. `tools/validate_published_signed_sources.py` verifies those mirrors byte-for-byte against the initialized resident image.

## Multiplication

| Profile | SMUL8 | SMUL16 | SMUL24 | SMUL32 |
|---|---|---|---|---|
| V1 Balanced | native | native | native | native |
| V2 Pareto-Fast | native | native signed quarter-square ZP kernel | native | native |
| V3 REU 512K | native | native signed quarter-square ZP kernel | native | native |
| V4 REU 16M | native | native signed quarter-square ZP kernel | native | native |
| V5 Hybrid Low-ZP | native (V1 base) | native (V1 base) | native (V1 base) | native (V1 base) |

The V1/V5 low-ZP routines preserve the 31-byte normal-ZP contract. V2–V4 retain the validated executable-ZP `SMUL16` kernel. Wider signed multipliers use private copies of the proven fast arithmetic cores placed in existing reserved holes; their signed finalizers are compacted where safe. The public API addresses remain unchanged. The private refreshed multiply cores extend the resident payload end to `$CF96` while preserving each profile's load address and ABI.

### SMUL32 record/Pareto alternative

The repository also publishes [`mul_s32_s32_s64_compact126.asm`](../routines/multiply/mul_s32_s32_s64_compact126.asm), a native benchmark-ABI SMUL32 record point at **646.354530 cycles**, using **136 ZP bytes** and **126 persistent page-$01 bytes**. It is intentionally not substituted for the fixed-profile public `MATH_SMUL32`: V1/V5 cannot accept the ZP footprint, while V2–V4 already use the same executable-ZP window for their native SMUL16 kernel. A direct standard-ABI transplant was measured at about 757.7 cycles and would regress every shipped public path; current V2/V3/V4 public means are 712.403902 / 712.856787 / 712.948941 cycles. See [`SMUL32_COMPACT126.md`](SMUL32_COMPACT126.md) for the compatibility matrix and validation evidence. The exact record source is also exposed as an optional exclusive overlay in the V2/V3/V4 profile trees; those aliases require preservation/restoration of the documented overlay ranges.

The new [`fast31_native_v2`](SMUL32_FAST31_V2.md) point applies the compact126 NN borrow shortcut and carry-seeding dispatch to the 31-ZP stack-free family, reducing the native mean from 697.259440 to **692.825100 cycles** without changing the low-ZP resource class. The subsequent profile integration keeps V1/V5 on their original 31-ZP public layout, while V2/V3/V4 persist **all six** FAST31 pointer pairs in holes already owned by those profiles. Ordinary calls therefore need no pointer-high repair. This removes **25 cycles** from signed SMUL32/SMUL32_SHR16 and **22 cycles** from unsigned UMUL32/UMUL32_SHR16; the canonical V2/V3/V4 SMUL32 means are now **712.403902 / 712.856787 / 712.948941 cycles**.

## Division

`SDIV8`, `SDIV16`, `SDIV24`, `SDIV32_16`, `SDIV32_32`, and `SDIV16_SHL8` all own signed executable paths. Most resident signed dividers were already executable-independent; `SDIV32_32` was explicitly split from the unsigned 32/32 engine in this release. Signed modulo entries remain aliases of the corresponding signed dividers and therefore inherit the same native implementation.

## Verification

The release uses four independent signed gates: executable-ownership tracing (`SIGNED_LAYOUT_VALIDATION.json`), arithmetic multiply testing (`SIGNED_MULTIPLY_VALIDATION.json`), and arithmetic divide/modulo testing (`SIGNED_DIVISION_VALIDATION.json`). The current multiplication measurements are recorded in `validation/multiply_refresh/MULTIPLY_REFRESH_BENCHMARK.json`; the older `NATIVE_SIGNED_DELTA_AUDIT.json` remains provenance for the pre-refresh ownership split. The broader relocation, hybrid, Pareto and release audits exercise the same binaries in the complete library.
