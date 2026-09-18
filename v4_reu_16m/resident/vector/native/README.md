# `MATH_VEC2_NORMALIZE_Q8_8` native source

This directory contains the **canonical native implementation** used by this profile.
Unlike the older published signed-source mirrors, `vec2_normalize_q8_8.asm` is not a
post-build listing: the relocatable library build includes this file directly.

The file is deliberately code-only so it can be lifted into a game/demo without
dragging in the rest of the library. To reuse it, provide the documented workspace,
scratch and immutable table pages, set the assembly PC to the desired entry address,
and assemble/include `vec2_normalize_q8_8.asm`.

## ABI

- input `MATH_IO+$00..$01`: signed Q8.8 X
- input `MATH_IO+$04..$05`: signed Q8.8 Y
- output `MATH_IO+$08..$09`: signed Q1.15 normalized X
- output `MATH_IO+$0A..$0B`: signed Q1.15 normalized Y
- inputs are preserved
- `C=0` for non-zero vectors
- `(0,0)` returns `(0,0)` with `C=1`
- A/X/Y are volatile

Public precision contract: maximum angular error `<= 0.3621 degrees` and maximum
component error `<= 202` Q1.15 LSB. The certified current implementation is tighter:
`<= 0.360856382 degrees` and `<= 200` LSB over the full reduced domain.

The sources intentionally use stable NMOS 6502/6510 undocumented `LAX` opcodes,
encoded explicitly with `!byte`, matching the rest of the optimized library.

## V3 / V4 REU direct-index backend

Performance on the deterministic 107,396-vector corpus:

- V3 REU 512K: **170.058633 average cycles**
- V4 REU 16M: **170.058633 average cycles**
- reachable routine code: **346 bytes**

V3 and V4 use byte-identical native code.

### Required symbols

`MATH_IO`, `ZP_MAIN`, `REG_TABLE`, `REU_SCRATCH`, `REU_TURBO16_BANK`.

### C64-side dependencies

- Q1.15 component planes:
  - `REG_TABLE+$0800`
  - `REG_TABLE+$0900`
  - `REG_TABLE+$0A00`
  - `REG_TABLE+$0B00`
- one-byte `REU_SCRATCH` destination used by the direct ratio-index lookup

### REU dependency

The upper 32 KiB of `REU_TURBO16_BANK`, offsets `$8000-$FFFF`, contains a
128 x 256 direct ratio-index table. The row is the normalized major mantissa
`$80-$FF`; the column is the normalized minor mantissa `$00-$FF`.

The normal library build generates this table automatically in
`tools/assemble_sources.py`, so it consumes **no additional REU bank** in V3.

### Minimal integration pattern

```asm
MATH_IO          = $C000
ZP_MAIN          = $02
REG_TABLE        = $6000
REU_SCRATCH      = $C020
REU_TURBO16_BANK = $04

* = $5E39
!source "vec2_normalize_q8_8.asm"
```

An external user must also populate `$8000-$FFFF` of the selected REU bank with
the direct ratio-index table. The canonical generator in `tools/assemble_sources.py`
documents the exact formula used to construct it.
