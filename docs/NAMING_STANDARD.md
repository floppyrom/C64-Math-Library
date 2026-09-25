# Public routine naming standard

The library keeps the historical `MATH_*` ABI for compatibility, but the canonical source-facing names now encode operand signedness, operand width, and result geometry. This follows the naming convention requested by Jackasser on CSDb.

## Binary arithmetic grammar

- Multiply: `mul_<A type><A bits>_<B type><B bits>_<result type><result bits>`; for example `mul_u8_u8_u16` and `mul_s16_s16_s32`. Mixed-sign future routines use the same form, for example `mul_u16_s8_s24`.
- Division without a returned remainder: `div_<N>_<D>_<Q>`.
- Division with a returned remainder: `div_<N>_<D>_<Q>_<R bits>`. For example, `div_u8_u8_u8_8` means unsigned 8-bit numerator, unsigned 8-bit divisor, unsigned 8-bit quotient, and 8-bit remainder.
- Modulo-only entry points use `mod_<N>_<D>_<R>`. Legacy modulo aliases that also happen to return a quotient retain `mod_...` canonical aliases because the requested operation is modulo; their extra quotient is documented, not hidden.
- Movement steppers use `seek_<x type><x bits>_<y type><y bits>_<method>`; for example `seek_u16_u8_dda` works on unsigned 16-bit x and unsigned 8-bit y coordinates.
- `_ready`, `_shr8`, `_shr16`, and `_shl8` are explicit operational/precondition suffixes and do not replace the A/B/result geometry.

`u` means unsigned and `s` means two’s-complement signed. Widths are decimal bit counts. The result type is explicit even where it is implied by the operands.

## Compatibility rule

Every canonical name is an alias of the existing fixed-address `MATH_*` symbol in each profile’s `resident/math_api.inc`. No legacy symbol or address is renamed or removed. The generated `standalone/` directories use canonical filenames and also identify the legacy API in each file header.

## Current mapping

| Legacy API | Canonical name | Address | Standalone file |
|---|---|---:|---|
| `MATH_UMUL8` | `mul_u8_u8_u16` | `$3000` | `mul_u8_u8_u16.asm` |
| `MATH_UMUL16` | `mul_u16_u16_u32` | `$3020` | `mul_u16_u16_u32.asm` |
| `MATH_UMUL24` | `mul_u24_u24_u48` | `$3060` | `mul_u24_u24_u48.asm` |
| `MATH_UMUL32` | `mul_u32_u32_u64` | `$30B0` | `mul_u32_u32_u64.asm` |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | `$30C0` | `mul_u32_u32_u64_ready.asm` |
| `MATH_SMUL8` | `mul_s8_s8_s16` | `$3B80` | `mul_s8_s8_s16.asm` |
| `MATH_SMUL16` | `mul_s16_s16_s32` | `$3BB0` | `mul_s16_s16_s32.asm` |
| `MATH_SMUL24` | `mul_s24_s24_s48` | `$3BF0` | `mul_s24_s24_s48.asm` |
| `MATH_SMUL32` | `mul_s32_s32_s64` | `$3C40` | `mul_s32_s32_s64.asm` |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | `$3FE0` | `mul_s32_s32_s64_ready.asm` |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | `$3120` | `div_u8_u8_u8_8.asm` |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | `$3140` | `div_u16_u16_u16_16.asm` |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | `$3170` | `div_u24_u24_u24_24.asm` |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | `$31B0` | `div_u32_u16_u32_16.asm` |
| `MATH_UMOD8` | `mod_u8_u8_u8` | `$3200` | `mod_u8_u8_u8.asm` |
| `MATH_UMOD16` | `mod_u16_u16_u16` | `$3220` | `mod_u16_u16_u16__math_umod16.asm` |
| `MATH_UMOD24` | `mod_u24_u24_u24` | `$3223` | `mod_u24_u24_u24__math_umod24.asm` |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | `$3226` | `mod_u32_u16_u16__math_umod32_16.asm` |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | `$3CA0` | `div_s8_s8_s8_8.asm` |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | `$3D20` | `div_s16_s16_s16_16.asm` |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | `$3DE0` | `div_s24_s24_s24_24.asm` |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | `$3EE0` | `div_s32_s16_s32_16.asm` |
| `MATH_SMOD8` | `mod_s8_s8_s8` | `$3FD4` | `mod_s8_s8_s8__math_smod8.asm` |
| `MATH_SMOD16` | `mod_s16_s16_s16` | `$3FD7` | `mod_s16_s16_s16__math_smod16.asm` |
| `MATH_SMOD24` | `mod_s24_s24_s24` | `$3FDA` | `mod_s24_s24_s24__math_smod24.asm` |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | `$3FDD` | `mod_s32_s16_s16__math_smod32_16.asm` |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | `$5E00` | `div_u32_u32_u32_32.asm` |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | `$5E03` | `mod_u32_u32_u32__math_umod32_32.asm` |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | `$5E06` | `div_s32_s32_s32_32.asm` |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | `$5E09` | `mod_s32_s32_s32__math_smod32_32.asm` |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | `$5E0C` | `mul_u16_u16_u24_shr8.asm` |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | `$5E0F` | `mul_s16_s16_s24_shr8.asm` |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | `$5E12` | `mul_u32_u32_u48_shr16.asm` |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | `$5E15` | `mul_s32_s32_s48_shr16.asm` |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | `$5E18` | `div_u16_u16_u24_16_shl8.asm` |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | `$5E1B` | `div_s16_s16_s24_16_shl8.asm` |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | `$5E1E` | `recip_u16_u24_q16.asm` |
| `MATH_SIN8` | `sin_u8_s8` | `$5E21` | `sin_u8_s8.asm` |
| `MATH_COS8` | `cos_u8_s8` | `$5E24` | `cos_u8_s8.asm` |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | `$5E27` | `sincos_u8_s8_s8.asm` |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | `$5E2A` | `atan2_s8_s8_u8.asm` |
| `MATH_ISQRT16` | `isqrt_u16_u16` | `$5E2D` | `isqrt_u16_u16.asm` |
| `MATH_ISQRT32` | `isqrt_u32_u16` | `$5E30` | `isqrt_u32_u16.asm` |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | `$5E33` | `dist_s8_s8_u8_fast.asm` |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | `$5E36` | `dist_s8_s8_u8_accurate.asm` |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | `$5E39` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15.asm` |

The same mapping is machine-readable in `docs/PUBLIC_API_COMPLETE.csv`.

## Variant suffixes for standalone alternatives

The typed geometry is always the base name. A benchmarked implementation variant adds a descriptive suffix after it, for example:

- `mul_s24_s24_s48_fast24`
- `mul_s32_s32_s64_turbo135`
- `mul_s32_s32_s64_fast31_native`
- `mul_u32_u32_u64_bounded133`

The suffix describes an implementation/resource point, not a different arithmetic contract. Profile ABI names remain the unsuffixed typed names.

## Publication requirement

Every published benchmark row must point to an exact source file and source SHA-256. The authoritative indexes are `routines/SOURCE_CATALOG.csv`, `benchmarks/PUBLIC_PROFILE_RESULTS.csv`, `benchmarks/BEST_PROFILE_RESULTS.csv`, and `benchmarks/STANDALONE_RESULTS.csv`. `tools/validate_public_catalog.py` enforces source presence, naming and hash consistency.
