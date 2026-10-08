# Signed implementations

## Definition used by this release

A routine is **native signed** when the signed public API owns its sign semantics, input normalization and result correction. The arithmetic magnitude substrate may either be signed-private or an explicitly audited shared unsigned core.

The earlier release rule required zero signed/unsigned executable overlap. The signed-core reuse audit showed that rule could force slower duplicate arithmetic without adding a semantic guarantee: V5 already demonstrated that a thin signed front end can bind magnitudes into a certified unsigned divider, then restore quotient/remainder signs correctly. The validator therefore now permits only named, audited magnitude-substrate exceptions. All other signed/unsigned pairs remain executable-disjoint.

`tools/validate_signed_layout.py` traces every pair and rejects any overlap not listed as an approved shared-core relationship. In the current division family, V2-V5 `SDIV16_SHL8` and V2-V5 `SDIV32_16` may share the selected UDIV32/16 magnitude graph; V2-V4 `SDIV32_32` may call the selected public UDIV32/32 core after temporary magnitude normalization. V1 keeps its Balanced private 32/32 path, and V5 keeps the inherited Balanced 32/32 path.

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

The repository also publishes [`mul_s32_s32_s64_compact126.asm`](../routines/multiply/mul_s32_s32_s64_compact126.asm), a native benchmark-ABI SMUL32 record point at **646.354530 cycles**, using **136 ZP bytes** and **126 persistent page-$01 bytes**. It is intentionally not substituted for the fixed-profile public `MATH_SMUL32`: V1/V5 cannot accept the ZP footprint, while V2–V4 already use the same executable-ZP window for their native SMUL16 kernel. A direct standard-ABI transplant was measured at about 757.7 cycles and would regress every shipped public path; current V2/V3/V4 public means are 711.153591 / 711.447073 / 711.706102 cycles. See [`SMUL32_COMPACT126.md`](SMUL32_COMPACT126.md) for the compatibility matrix and validation evidence. The exact record source is also exposed as an optional exclusive overlay in the V2/V3/V4 profile trees; those aliases require preservation/restoration of the documented overlay ranges.

The new [`fast31_native_v2`](SMUL32_FAST31_V2.md) point applies the compact126 NN borrow shortcut and carry-seeding dispatch to the 31-ZP stack-free family, reducing the native mean from 697.259440 to **692.825100 cycles** without changing the low-ZP resource class. The subsequent profile integration keeps V1/V5 on their original 31-ZP public layout, while V2/V3/V4 persist **all six** FAST31 pointer pairs in holes already owned by those profiles. Ordinary calls therefore need no pointer-high repair. This removes **25 cycles** from signed SMUL32/SMUL32_SHR16 and **22 cycles** from unsigned UMUL32/UMUL32_SHR16; the canonical V2/V3/V4 SMUL32 means are now **711.153591 / 711.447073 / 711.706102 cycles**.

## Division

`SDIV8`, `SDIV16`, and `SDIV24` retain signed-private arithmetic. `SDIV16_SHL8` and `SDIV32_16` now use thin signed sign/magnitude front ends around the fastest qualified UDIV32/16 magnitude substrate in V2-V5. V2-V4 `SDIV32_32` similarly normalize public N/D temporarily, call the profile-selected UDIV32/32 core, restore N/D, and correct output signs. V1 and V5 keep their Balanced private 32/32 path. Signed modulo entries remain aliases of the corresponding signed dividers and inherit the same semantics and selected magnitude architecture.

## Verification

The release uses independent signed gates: executable-ownership/shared-core tracing (`SIGNED_LAYOUT_VALIDATION.json`), arithmetic multiply testing (`SIGNED_MULTIPLY_VALIDATION.json`), arithmetic divide/modulo testing (`SIGNED_DIVISION_VALIDATION.json`), and byte-exact published-source validation. Approved overlap is explicit rather than inferred. The current multiplication measurements are recorded in `validation/multiply_refresh/MULTIPLY_REFRESH_BENCHMARK.json`; the older `NATIVE_SIGNED_DELTA_AUDIT.json` remains provenance for the pre-refresh ownership split. The broader relocation, hybrid, Pareto and release audits exercise the same binaries in the complete library.
