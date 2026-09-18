# REU guide — V3 and V4

## REU is DMA memory, not directly executable RAM

The 6510 cannot fetch instructions directly from REU memory. Code overlays must be transferred to C64-visible RAM/ZP first. This is why the library does not simply store every Extreme routine in the REU.

## V3: 512 KiB

The table below is the **reference map**. V3 uses four full 64 KiB 8-bit planes, two hot-kernel overlays and two reciprocal planes; all active bank roles are build-time configurable:

```text
bank 0  UMUL8 product low
bank 1  UMUL8 product high
bank 2  UDIV8 quotient
bank 3  UDIV8 remainder / UMOD8
bank 4  Turbo16 ZP image; `$8000-$FFFF` also holds VEC2 normalize ratio-index table
bank 5  Turbo32 ZP image
bank 6  reciprocal low
bank 7  reciprocal high
```

This makes UMUL8, UDIV8 and UMOD8 direct REU services rather than resident arithmetic loops.

In the reference build Turbo16 swaps a 113-byte kernel into `$003E-$00AE`; Turbo32 swaps the stack-free 135-byte `ram135` record compromise into `$000A-$0090`. These are no longer fixed: `TURBO16_ZP_BASE`/`TURBO32_ZP_BASE` choose the ZP origins and `REU_TURBO16_BANK`/`REU_TURBO32_BANK` choose the storage banks. The overlays are assembled from source for the selected map, so there is no runtime relocation pass. The release model charges one clock/byte for one-way transfers and two clocks/byte for SWAP, plus the normal 6510 instructions used to program the REC.

## V4: 16 MiB

VICE accepts `REUsize=16384` KiB. V4 preserves the same logical services but its operational banks are also configurable at build time. It additionally provides the aligned QS16 region:

```text
$100000-$17FFFB  Q(v)=floor(v^2/4), v=0..131070, 4 bytes each
```

The historical REC register description notes that the original bank register uses fewer bits, but a clone using all eight bits can address 2^24 bytes = 16 MiB. V4 therefore targets VICE/modern compatible implementations rather than claiming classic 1750 hardware has 16 MiB.

## V4 QS16

The identity

```text
xy = Q(x+y) - Q(abs(x-y))
```

is exact because both indices have the same parity. Two four-byte REU record fetches plus subtraction replace four 8x8 partial products.

Recommended UMUL16 mode:

```text
1 call   public MATH_UMUL16
2-8      QS16 BEGIN / repeated CALL / END
9+       Turbo16 BEGIN / repeated CALL / END
```

## VICE examples

V3:

```sh
x64sc -reu -reusize 512 \
  -reuimage v3_reu_512k/reu/c64_math_v3_512k_game_math.reu \
  your_program.prg
```

V4:

```sh
x64sc -reu -reusize 16384 \
  -reuimage v4_reu_16m/reu/c64_math_v4_16m_game_math.reu \
  your_program.prg
```

## Timing caveat

REU DMA competes with the VIC-II bus. The deterministic model in these releases does not claim raster-exact wall-clock timing under every display state or every modern REU implementation. Use the model for architecture/relative-cost selection and remeasure the exact binary on the intended hardware/emulator when raster timing matters.


## Signed calls on REU profiles — final native revision

V3/V4 signed multiplication no longer calls the public unsigned operation as a wrapper. SMUL8/24/32 enter profile-native producer paths directly. SMUL16 uses the validated 116-ZP native practical implementation in normal C64 RAM, with four 511-byte tables at `$2800/$2A00/$2C00/$2E00` and executable ZP at `$80-$F3`. Signed DIV uses native signed cores with `$3E-$52` scratch. These resources are sequentially shared with REU Turbo modes; obey the existing BEGIN/END ownership contracts.

## 2026-09-06 game-math REU additions

For `MATH_VEC2_NORMALIZE_Q8_8`, V3/V4 generate a 32 KiB final ratio-index table at `$8000-$FFFF` of the configured `REU_TURBO16_BANK`. The Turbo16 overlay remains at the low start of the same bank, so no extra REU bank is consumed. The game-math REU images intentionally use previously reserved banks 6–7 for reciprocal tables. V4 additionally uses banks 8–9 for exact signed-byte atan2 and exact ISQRT16. The V4 QS16 region `$100000-$17FFFB` is preserved. The former statement that the first 512 KiB of V4 is byte-for-byte identical to the old V3 image does not apply to the new game-math image because reserved banks 6–7 now carry defined tables.


## Game-math extension — FINAL 2026-09-06

V3 adds exact reciprocal low/high planes in two 64 KiB REU banks. V4 adds the same planes plus one exact signed-byte atan2 bank and one exact ISQRT16 bank. Use `v3_reu_512k/reu/c64_math_v3_512k_game_math.reu` or `v4_reu_16m/reu/c64_math_v4_16m_game_math.reu`. The diff audit reports zero changes outside declared extension ranges and preserves V4 QS16 data exactly.

Game math uses normal-profile ZP that can overlap a configured Turbo overlay, so it is forbidden while Turbo BEGIN/END overlays are active. `END` restores the caller's prior ZP bytes exactly. See `TURBO_RELOCATION.md` for reference/alternate maps and validation.
