# `MATH_VEC2_NORMALIZE_Q8_8` native source

This directory contains the canonical REU ratio-index implementation for `v3_reu_512k`. The integrated build consumes `vec2_normalize_q8_8.asm`; it includes the adjacent generated `vec2_normalize_tables.asm`. Copy both files for standalone reuse. V1/V5 sources are identical; V3/V4 sources are identical.

## Contract

- Inputs: signed Q8.8 X at `MATH_IO+$00..+$01`, Y at `MATH_IO+$04..+$05`, preserved.
- Outputs: signed Q1.15 X at `MATH_IO+$08..+$09`, Y at `MATH_IO+$0A..+$0B`.
- `C=0` for nonzero input; `(0,0)` returns four zero bytes and `C=1`.
- A/X/Y are volatile; decimal mode must be clear.
- Scratch: four bytes, `ZP_MAIN+$18..+$1B`. No persistent stack-page reservation.
- Public accuracy: <=0.3621 degrees and <=202 component LSB against unit scale 32767.
- Current full-domain certificate: <=0.360856382 degrees and <=200 LSB.

The routine selects the sign quadrant once and writes signed outputs directly. It uses the stable NMOS 6502/6510 undocumented `LAX` opcode, encoded explicitly as bytes. Calls are sequential and non-reentrant.

## Performance and placement

**156.661198 cycles mean**, 84–298 cycles on 107,396 deterministic vectors. This includes the public entry and RTS, excluding the caller JSR. Both supported maps have identical cycle and output vectors.

Code: **849 bytes**, including the public three-byte JMP at `REG_GAME_API+$0039`. Code islands: `REG_LOW+$0200..+$02E3`, `REG_LOW+$0300..+$03C7`, `REG_LOW+$0720..+$07F9`, `REG_LOW+$0B00..+$0BC7`. Tables in C64 RAM: **1024 bytes**.

- Component planes: `REG_TABLE+$0800`, `+$0900`, `+$0A00`, `+$0B00` (1,024 bytes).
- Existing REU ratio table: `$8000–$FFFF` within `REU_TURBO16_BANK` (32 KiB).

Load the profile REU image, or generate its ratio table with `tools/assemble_sources.py`, and initialize the normal one-byte REU transport with `MATH_INIT`. Normal calls remain forbidden during Turbo BEGIN/END modes. The component tables and REU mapping are unchanged from the previous implementation.

Stock-profile reference PRGs now load at $1000; reserve the expanded range. V1/V5 retain their 31-byte shared ZP allocation. Full memory and baseline comparisons are in `docs/VEC2_NORMALIZE_Q8_8.md`.

## Standalone include

Required symbols: `MATH_IO`, `ZP_MAIN`, `REG_LOW`, `REG_TABLE`, `REG_GAME_API`, `REU_SCRATCH`, `REU_TURBO16_BANK`. Region bases must retain their documented page alignment and avoid overlaps. The source sets the code/table origins itself and restores the assembly PC to `REG_GAME_API+$003C` after inclusion.

```asm
MATH_IO = $C000
ZP_MAIN = $02
REG_LOW = $1000
REG_TABLE = $6000
REG_GAME_API = $5E00
REU_SCRATCH = $C020
REU_TURBO16_BANK = $04

* = REG_GAME_API+$0039
!source "vec2_normalize_q8_8.asm"
```

Run `make normalize` to check generated tables, isolated/integrated source parity, all five profile benchmarks, reduced-plane coverage, mixed calls, ZP confinement, cold stock loads, and the full-domain certificates.
