# Native signed arithmetic in the reviewed source release

## Signed division

The active per-profile signed division sources are included under each profile's `resident/native_signed/division/` tree. `NATIVE_SIGNED_SELECTION_FINAL.csv` records the selected implementations and relocation map. The stable signed convention is truncation toward zero, remainder sign follows the numerator, divide-by-zero returns `q=r=0, C=1`, and the two's-complement `INT_MIN/-1` case wraps.

The larger historical benchmark/reference archives are not duplicated in this streamlined source distribution. Their selected results are summarized in `COMPLETE_TECHNICAL_ASSESSMENT.md`, `NATIVE_SIGNED_VALIDATION_FINAL.md`, and the performance CSVs.

## Signed multiplication

V1 uses its profile-native fused signed producer while preserving the 31-byte V1 ZP design. V2–V4 use the independently validated practical native SMUL16 implementation, installed by `MATH_INIT` into configurable executable ZP; 8/24/32-bit signed multiplication uses the active native/profile producer paths documented in `NATIVE_SIGNED_INTEGRATION.md`.

The reviewed source build keeps the stable public memory ABI distinct from workload-specific ready/fixed-X forms. Specialized overlay/ready contracts are never silently substituted for a stable public entry.
