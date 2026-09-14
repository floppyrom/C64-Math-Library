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

The V1/V5 low-ZP routines preserve the 31-byte normal-ZP contract. V2–V4 retain the validated executable-ZP `SMUL16` kernel. Wider signed multipliers use private copies of the proven fast arithmetic cores placed in existing reserved holes; their signed finalizers are compacted where safe. No profile's resident load/end range is expanded.

## Division

`SDIV8`, `SDIV16`, `SDIV24`, `SDIV32_16`, `SDIV32_32`, and `SDIV16_SHL8` all own signed executable paths. Most resident signed dividers were already executable-independent; `SDIV32_32` was explicitly split from the unsigned 32/32 engine in this release. Signed modulo entries remain aliases of the corresponding signed dividers and therefore inherit the same native implementation.

## Verification

The release uses four independent signed gates: executable-ownership tracing (`SIGNED_LAYOUT_VALIDATION.json`), arithmetic multiply testing (`SIGNED_MULTIPLY_VALIDATION.json`), and arithmetic divide/modulo testing (`SIGNED_DIVISION_VALIDATION.json`). A fourth same-corpus delta audit (`NATIVE_SIGNED_DELTA_AUDIT.json`) verifies that the ownership split introduces no signed-multiply or SDIV32_32 timing regressions. The broader relocation, hybrid, Pareto and release audits then exercise the same binaries in the complete library.
