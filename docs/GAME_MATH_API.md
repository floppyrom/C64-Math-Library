# Game / fixed-point API

The 28 stable game/fixed-point/movement JMP slots occupy `$5E00-$5E53`. They use the existing `$C000-$C01F` vectors. Inputs are preserved, A/X/Y are volatile and D=0 is required. Division-by-zero returns C=1 with zero q/r.

| Entry | Address | Contract |
|---|---:|---|
| `MATH_UDIV32_32` / `MATH_UMOD32_32` | `$5E00/$5E03` | n32,d32 -> q32,r32 |
| `MATH_SDIV32_32` / `MATH_SMOD32_32` | `$5E06/$5E09` | signed n32,d32 -> q32,r32, trunc toward zero |
| `MATH_UMUL16_SHR8` / `MATH_SMUL16_SHR8` | `$5E0C/$5E0F` | x16*y16 >> 8 -> z24 |
| `MATH_UMUL32_SHR16` / `MATH_SMUL32_SHR16` | `$5E12/$5E15` | x32*y32 >> 16 -> z48 |
| `MATH_UDIV16_SHL8` / `MATH_SDIV16_SHL8` | `$5E18/$5E1B` | (n16<<8)/d16 -> q24,r16 |
| `MATH_URECIP16_Q16` | `$5E1E` | d16 -> q24=`floor(65536/d)` |
| `MATH_SIN8` / `MATH_COS8` | `$5E21/$5E24` | x0 phase -> z0 signed ±127 |
| `MATH_SINCOS8` | `$5E27` | x0 phase -> z0 sin, z1 cos |
| `MATH_ATAN2_8` | `$5E2A` | x0=dx s8, y0=dy s8 -> z0 phase8 |
| `MATH_ISQRT16` | `$5E2D` | n16 -> z16 exact floor sqrt |
| `MATH_ISQRT32` | `$5E30` | n32 -> z16 exact floor sqrt |
| `MATH_DIST8_FAST` | `$5E33` | signed dx,dy -> `max+min/2` |
| `MATH_DIST8_ACCURATE` | `$5E36` | signed dx,dy -> rounded 243/107 minimax form |
| `MATH_VEC2_NORMALIZE_Q8_8` | `$5E39` | signed Q8.8 x,y -> signed Q1.15 unit vector; C=1 only for zero |
| `MATH_SEEK8_INIT` | `$5E3C` | X=slot; target x0,y0 u8; speed n16 (bit 15 = Euclidean) -> slot state; C=1 if already there |
| `MATH_SEEK8_STEP` / `_STEP_INT` / `_STEP1` | `$5E3F/$5E42/$5E45` | X=slot; one frame -> `MATH_SEEK8_POS_X/Y`; C=1 on arrival |
| `MATH_SEEK16_INIT` | `$5E48` | X=slot; target x0..1 u16, y0 u8; speed n16 -> slot state; C=1 if already there |
| `MATH_SEEK16_STEP` / `_STEP_INT` / `_STEP1` | `$5E4B/$5E4E/$5E51` | X=slot; one frame -> `MATH_SEEK16_POS_XL/XH/Y`; C=1 on arrival |

Phase convention: `$00=0°`, `$40=90°`, `$80=180°`, `$C0=270°`. V1 uses the optimized compact 512-byte signed-log ATAN2 tier (**48.447189-cycle mean**); V2/V3 use the 1024-byte carry-clearing sum tier (**44.962814-cycle mean**). Both are within one phase unit of rounded mathematical atan2 over the entire signed-byte plane. V4 is exact against that reference at 48 fixed cycles. `(0,0)` returns zero.

V1 uses `$C040-$C057` RAM scratch. V2–V4 use `$53-$6A` ZP. Native V2–V4 SMUL16 executes from `$80-$F3`. On V3/V4, game-math calls are forbidden while a Turbo BEGIN/END overlay is active.

## Vector normalization

`MATH_VEC2_NORMALIZE_Q8_8` preserves X/Y inputs and returns the Q1.15 direction in `Z[0..3]`. The common precision contract is <=0.3621 degrees / <=202 LSB. V1/V5 use the low-ZP stock backend, V2 uses its faster stock backend, and V3/V4 use the direct REU ratio-index table. See `VEC2_NORMALIZE_Q8_8.md`.

## Moving an object toward a target (seek)

`MATH_SEEK8_*` and `MATH_SEEK16_*` move up to eight objects each to a target pixel at a Q8.8 speed along an exact Bresenham line, landing exactly on the target. They keep the inputs and X (the slot) unchanged, need no `MATH_INIT`, add no zero page, and use the game scratch above only during `*_INIT`. See `SEEK_DDA.md`.
