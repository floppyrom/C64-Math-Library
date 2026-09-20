# Standalone public routines

This directory exposes every stable public routine shipped by **v5_hybrid_lowzp** as one readable `.asm` file.
The files are generated exact executable source mirrors, not jump-only placeholders. Each mirror contains every instruction statically reachable from that public entry after `MATH_INIT`, with resident address and byte annotations.

The historical `MATH_*` ABI remains supported. New code should prefer the typed canonical names documented in `docs/NAMING_STANDARD.md`. For multiplication the form is `mul_<A>_<B>_<result>`; division that returns a remainder uses `div_<A>_<B>_<quotient>_<remainder-bits>`.

**Important:** immutable lookup tables and REU payload data are shared by the profile and are not duplicated into every mirror. The canonical integrated relocatable sources remain under `relocatable_source/`. These standalone files are designed for inspection, extraction, adaptation, and exact comparison with the shipped image.

| Legacy API | Canonical name | File | Alias of | Reachable instructions |
|---|---|---|---|---:|
| `MATH_UMUL8` | `mul_u8_u8_u16` | `mul_u8_u8_u16.asm` |  | 27 |
| `MATH_UMUL16` | `mul_u16_u16_u32` | `mul_u16_u16_u32.asm` |  | 104 |
| `MATH_UMUL24` | `mul_u24_u24_u48` | `mul_u24_u24_u48.asm` |  | 179 |
| `MATH_UMUL32` | `mul_u32_u32_u64` | `mul_u32_u32_u64.asm` |  | 159 |
| `MATH_UMUL32_READY` | `mul_u32_u32_u64_ready` | `mul_u32_u32_u64_ready.asm` |  | 151 |
| `MATH_SMUL8` | `mul_s8_s8_s16` | `mul_s8_s8_s16.asm` |  | 19 |
| `MATH_SMUL16` | `mul_s16_s16_s32` | `mul_s16_s16_s32.asm` |  | 136 |
| `MATH_SMUL24` | `mul_s24_s24_s48` | `mul_s24_s24_s48.asm` |  | 248 |
| `MATH_SMUL32` | `mul_s32_s32_s64` | `mul_s32_s32_s64.asm` |  | 669 |
| `MATH_SMUL32_READY` | `mul_s32_s32_s64_ready` | `mul_s32_s32_s64_ready.asm` |  | 660 |
| `MATH_UDIV8` | `div_u8_u8_u8_8` | `div_u8_u8_u8_8.asm` |  | 182 |
| `MATH_UDIV16` | `div_u16_u16_u16_16` | `div_u16_u16_u16_16.asm` |  | 626 |
| `MATH_UDIV24` | `div_u24_u24_u24_24` | `div_u24_u24_u24_24.asm` |  | 583 |
| `MATH_UDIV32_16` | `div_u32_u16_u32_16` | `div_u32_u16_u32_16.asm` |  | 1043 |
| `MATH_UMOD8` | `mod_u8_u8_u8` | `mod_u8_u8_u8.asm` |  | 69 |
| `MATH_UMOD16` | `mod_u16_u16_u16` | `mod_u16_u16_u16__math_umod16.asm` | `MATH_UDIV16` | 626 |
| `MATH_UMOD24` | `mod_u24_u24_u24` | `mod_u24_u24_u24__math_umod24.asm` | `MATH_UDIV24` | 583 |
| `MATH_UMOD32_16` | `mod_u32_u16_u16` | `mod_u32_u16_u16__math_umod32_16.asm` | `MATH_UDIV32_16` | 1044 |
| `MATH_SDIV8` | `div_s8_s8_s8_8` | `div_s8_s8_s8_8.asm` |  | 235 |
| `MATH_SDIV16` | `div_s16_s16_s16_16` | `div_s16_s16_s16_16.asm` |  | 804 |
| `MATH_SDIV24` | `div_s24_s24_s24_24` | `div_s24_s24_s24_24.asm` |  | 658 |
| `MATH_SDIV32_16` | `div_s32_s16_s32_16` | `div_s32_s16_s32_16.asm` |  | 274 |
| `MATH_SMOD8` | `mod_s8_s8_s8` | `mod_s8_s8_s8__math_smod8.asm` | `MATH_SDIV8` | 235 |
| `MATH_SMOD16` | `mod_s16_s16_s16` | `mod_s16_s16_s16__math_smod16.asm` | `MATH_SDIV16` | 804 |
| `MATH_SMOD24` | `mod_s24_s24_s24` | `mod_s24_s24_s24__math_smod24.asm` | `MATH_SDIV24` | 658 |
| `MATH_SMOD32_16` | `mod_s32_s16_s16` | `mod_s32_s16_s16__math_smod32_16.asm` | `MATH_SDIV32_16` | 275 |
| `MATH_UDIV32_32` | `div_u32_u32_u32_32` | `div_u32_u32_u32_32.asm` |  | 362 |
| `MATH_UMOD32_32` | `mod_u32_u32_u32` | `mod_u32_u32_u32__math_umod32_32.asm` | `MATH_UDIV32_32` | 362 |
| `MATH_SDIV32_32` | `div_s32_s32_s32_32` | `div_s32_s32_s32_32.asm` |  | 380 |
| `MATH_SMOD32_32` | `mod_s32_s32_s32` | `mod_s32_s32_s32__math_smod32_32.asm` | `MATH_SDIV32_32` | 380 |
| `MATH_UMUL16_SHR8` | `mul_u16_u16_u24_shr8` | `mul_u16_u16_u24_shr8.asm` |  | 114 |
| `MATH_SMUL16_SHR8` | `mul_s16_s16_s24_shr8` | `mul_s16_s16_s24_shr8.asm` |  | 146 |
| `MATH_UMUL32_SHR16` | `mul_u32_u32_u48_shr16` | `mul_u32_u32_u48_shr16.asm` |  | 175 |
| `MATH_SMUL32_SHR16` | `mul_s32_s32_s48_shr16` | `mul_s32_s32_s48_shr16.asm` |  | 685 |
| `MATH_UDIV16_SHL8` | `div_u16_u16_u24_16_shl8` | `div_u16_u16_u24_16_shl8.asm` |  | 1070 |
| `MATH_SDIV16_SHL8` | `div_s16_s16_s24_16_shl8` | `div_s16_s16_s24_16_shl8.asm` |  | 304 |
| `MATH_URECIP16_Q16` | `recip_u16_u24_q16` | `recip_u16_u24_q16.asm` |  | 760 |
| `MATH_SIN8` | `sin_u8_s8` | `sin_u8_s8.asm` |  | 6 |
| `MATH_COS8` | `cos_u8_s8` | `cos_u8_s8.asm` |  | 6 |
| `MATH_SINCOS8` | `sincos_u8_s8_s8` | `sincos_u8_s8_s8.asm` |  | 8 |
| `MATH_ATAN2_8` | `atan2_s8_s8_u8` | `atan2_s8_s8_u8.asm` |  | 46 |
| `MATH_ISQRT16` | `isqrt_u16_u16` | `isqrt_u16_u16.asm` |  | 113 |
| `MATH_ISQRT32` | `isqrt_u32_u16` | `isqrt_u32_u16.asm` |  | 199 |
| `MATH_DIST8_FAST` | `dist_s8_s8_u8_fast` | `dist_s8_s8_u8_fast.asm` |  | 30 |
| `MATH_DIST8_ACCURATE` | `dist_s8_s8_u8_accurate` | `dist_s8_s8_u8_accurate.asm` |  | 31 |
| `MATH_VEC2_NORMALIZE_Q8_8` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15` | `normalize_s16_s16_s16_s16_q8_8_to_q1_15.asm` |  | 183 |

The machine-readable version of this table is `MANIFEST.csv`.
