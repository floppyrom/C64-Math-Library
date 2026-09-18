# V4 16 MiB REU architecture

## Target

The reference target is VICE with a 16 MiB REU (`REUsize=16384` KiB) or a modern compatible implementation exposing the full 24-bit REU address. Classic MOS 8726 hardware does not itself provide a 16 MiB physical configuration.

Useful external references:

- VICE manual: https://vice-emu.sourceforge.io/vice_7.html
- REC register description: https://www.zimmers.net/anonftp/pub/cbm/documents/chipdata/reu.registers

## Image map

| REU range | Purpose |
|---|---|
| `$000000-$07FFFF` | exact V3 512 KiB image, byte-for-byte unchanged |
| `$100000-$17FFFB` | 131,071 four-byte `Q(v)=floor(v^2/4)` records |
| remaining space | reserved/zero |
| final page | V4 text signature |

The 512 KiB V3 prefix means all V3 direct 8-bit services and turbo overlays remain available.

## QS16 lookup protocol

`MATH_REU_QS16_BEGIN` configures a four-byte sequential fetch. `MATH_REU_QS16` computes two 17-bit indices (`x+y`, `abs(x-y)`), multiplies each by four using shifts, adds bank base `$10`, performs the two fetches, and subtracts the records. `MATH_REU_QS16_END` restores V3's one-byte fixed lookup configuration.

The self-contained public `MATH_UMUL16` performs BEGIN-like setup and END-like restore internally.

## AUTOLOAD

The QS16 command uses REU->C64 FETCH with AUTOLOAD. After each four-byte record, the REC restores the configured C64 base, REU base and byte count. The next record therefore only needs the new REU address bytes/bank before the command is triggered.

## Scratch and shared state

- normal shared ZP remains `$02-$38` (55 bytes);
- QS16 uses `$10-$1F` transiently inside that union;
- the fetched record buffer is `$C020-$C023`;
- public inputs/results remain `$C000-$C01F`;
- public input vectors are preserved.

## VICE example

```sh
x64sc -reu -reusize 16384 \
  -reuimage reu/c64_math_v4_16m.reu \
  your_program.prg
```

If REU image write-back is not desired, leave image-write mode disabled.


## Superseding game-math image

The table above describes the original V4 image `c64_math_v4_16m.reu`. The current game-math release additionally supplies `c64_math_v4_16m_game_math.reu`. In that image the old statement that the complete first 512 KiB is byte-for-byte identical to V3 no longer applies, because formerly reserved banks are intentionally populated:

| REU bank/range | Game-math purpose |
|---|---|
| bank 6 | exact reciprocal-Q16 low table |
| bank 7 | exact reciprocal-Q16 high/17th-bit table |
| bank 8 | exact signed-byte `ATAN2_8` plane |
| bank 9 | exact `ISQRT16` table |
| `$100000-$17FFFB` | existing QS16 table, preserved byte-for-byte |
| bank 5 `$FF00` | game-math signature |

Banks containing the established V3 direct lookup/turbo payloads remain unchanged. Use the game-math image when calling the new REU-backed game-math services.

## VEC2 normalization

`MATH_VEC2_NORMALIZE_Q8_8` uses a generated 32 KiB direct ratio-index table at `$8000-$FFFF` in `REU_TURBO16_BANK`. This shares the bank with the low-address Turbo16 overlay without overlap and moves with `REU_TURBO16_BANK` in alternate/custom maps. The resulting public-call mean is **170.058633 cycles** on the 107,396-vector corpus, with the same <=0.3621 degree / <=202-LSB contract as all other profiles.
