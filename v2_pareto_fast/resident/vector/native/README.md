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

## V2 Pareto-Fast backend

Performance on the deterministic 107,396-vector corpus:

- **189.260317 average cycles**
- reachable routine code: **383 bytes**

### Required symbols

`MATH_IO`, `ZP_MAIN`, `REG_TABLE`, `REG_LOW`, `REG_KERNEL`.

### Scratch used

The routine uses existing V2 scratch in `ZP_MAIN`, notably offsets
`+$10..+$13` and the UMUL8 pointer bytes around `+$37..+$39`.
`MATH_INIT` must have initialized the resident UMUL8 pointer high bytes in the
same way as the normal V2 library initialization.

### Immutable table dependencies

- reciprocal page: `REG_TABLE+$3300`
- resident UMUL8 quarter-square region: `REG_TABLE+$0800-$0DFF`
- Q1.15 component planes:
  - `REG_LOW+$1400`
  - `REG_LOW+$1700`
  - `REG_KERNEL+$0700`
  - `REG_KERNEL+$0D00`

### Minimal integration pattern

```asm
MATH_IO    = $C000
ZP_MAIN    = $02
REG_TABLE  = $6000
REG_LOW    = $1000
REG_KERNEL = $4000

* = $5E39
!source "vec2_normalize_q8_8.asm"
```

For an external standalone use, either preserve the V2 `MATH_INIT` UMUL8 pointer
setup or initialize the corresponding pointer high bytes before calling the routine.
