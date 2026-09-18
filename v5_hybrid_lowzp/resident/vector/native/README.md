# `MATH_VEC2_NORMALIZE_Q8_8` native source

This directory contains the **profile-local standalone source** for the normalization
backend used by V5. V5 is synthesized from the V1 canonical base rather than owning a
separate `math_relocatable.asm`, so its integrated routine is inherited from V1. The
file here is intentionally byte-identical to the V1 native source, and
`tools/build_hybrid.py` rejects the build if the two copies drift.

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

## V1 / V5 low-ZP backend

Performance on the deterministic 107,396-vector corpus:

- V1 Balanced: **198.770271 average cycles**
- V5 Hybrid Low-ZP: **198.770271 average cycles**
- reachable routine code: **392 bytes**
- no increase to the profile's 31-byte ZP contract

`v1_balanced` and `v5_hybrid_lowzp` publish byte-identical copies of the source.
V5's integrated build starts from the V1 canonical build, so this is the exact
backend inherited by V5.

### Required symbols

`MATH_IO`, `ZP_MAIN`, `REG_TABLE`.

### Scratch used

Within the existing V1/V5 `ZP_MAIN` allocation the routine uses offsets
`+$12`, `+$18`, `+$19`, `+$1A`, and `+$1B`.

### Immutable table dependencies

The routine reuses existing resident tables rather than embedding duplicates:

- component planes: `REG_TABLE+$0000`, `+$0100`, `+$0200`, `+$0300`
- reciprocal page: `REG_TABLE+$0400`
- resident quarter-square pages used by the ratio multiply:
  `REG_TABLE+$2000-$23FF`

No initialization beyond the normal library `MATH_INIT` contract is required.

### Minimal integration pattern

```asm
MATH_IO   = $C000
ZP_MAIN   = $02
REG_TABLE = $6000

* = $5E39        ; or any address that fits the routine
!source "vec2_normalize_q8_8.asm"
```

When relocating outside the library, place/copy the immutable table pages above at
the offsets relative to your chosen `REG_TABLE`.
