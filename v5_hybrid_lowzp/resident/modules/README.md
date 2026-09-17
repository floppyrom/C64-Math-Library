# Resident module sources

This directory publishes readable profile-local source for V5 Hybrid Low-ZP kernels that are composed from the certified V1/V2 source profiles by `tools/build_hybrid.py`.

## ATAN2

`hybrid_atan2.a` is the readable V5 fast ATAN2 kernel at the V5 destination slot beginning `$C814`. It uses the certified V2 four-quadrant algorithm with the V5 physical table map: `$9600` LOG, `$9700` Q0, `$5500` Q1, `$5F00` Q2 and remapped Q3 at `$5700`.

The Q3 remap is required because donor page `$4700` is occupied in the V1-derived V5 base. `HYBRID_BUILD_MANIFEST.json` records the reserved `$C814-$C871` body span and the three extra table pages. Exhaustive validation establishes V2 result/cycle parity: 46.953064 mean public-entry cycles, 30-48 range, 0 ZP, maximum error 1 phase unit.

The canonical donor algorithm and exhaustive standalone benchmark live in `../../../routines/atan2/`.
