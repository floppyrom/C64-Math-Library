# Liftable MULDIV16 sources

This directory contains the human-facing source modules for the library's 16-bit multiply/divide family.

These are **source modules**, not generated resident disassemblies. The integrated library includes the same files, so a developer who lifts one is starting from the source that actually builds the shipped profile.

## Variants

- `muldiv16_composed.inc` — portable composition used by the balanced source path. It calls the public `MATH_UMUL16` / `MATH_SMUL16` and `MATH_UDIV32_16` / `MATH_SDIV32_16` APIs. It is the easiest variant to transplant when those four primitives already exist.
- `muldiv16_fast_v2v4.inc` — fused V2/V3/V4 implementation. It bypasses public product materialization and feeds the UMUL16 producer directly into the private UDIV32/16 state.

## Dependencies

Both modules use the normal library ABI symbols (`MATH_X`, `MATH_Y`, `MATH_D`, `MATH_Q`, `MATH_R`, and the public entry symbols).

The fused V2/V3/V4 module additionally requires the private symbols exported by:

- `relocatable_source/multiply/umul16_directout.asm`: `U16_X0`, `U16_X1`, `U16_Y1`, `U16_UMULT_AX1`
- `relocatable_source/division/udiv32_16_split_direct.inc`: `U3216_LN0`, `U3216_LN1`, `U3216_N0`, `U3216_N1`, `U3216_D0`, `U3216_D1`, `U3216_ENTRY`, `U3216_ZERO`

The `REG_*` symbols only choose placement. They can be changed when transplanting the module, provided its islands do not overlap the caller's code/data.

## Audit mirrors vs liftable source

The files under `<profile>/standalone/` remain exact address/byte mirrors of the shipped executable and are useful for auditing. They intentionally omit shared tables and are not the canonical editing surface.

For copy/paste reuse, prefer the symbolic modules in `routines/` such as the two files here. Exact profile mirrors remain available so the lifted source can be compared with the shipped implementation.
