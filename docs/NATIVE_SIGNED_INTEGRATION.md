# Native signed integration — final profile-selected revision

This is the publication replacement for the earlier wrapper-based signed compatibility build. Every public signed entry now reaches a native signed path.

## Multiplication

`SMUL8`, `SMUL24`, and `SMUL32` (plus V1 `SMUL16`) are **producer-fused native implementations**: the profile-selected unsigned arithmetic producer is retained, but its terminal path is replaced by the signed two’s-complement continuation. There is no `JSR MATH_UMUL*` or `JMP MATH_UMUL*` in those signed implementations. This is the same producer/consumer optimization principle demonstrated by the dedicated SMUL16 work.

For V2, V3 and V4, `SMUL16` now uses the uploaded, independently validated **`smul16_practical_116zp.a` native implementation**. It measures 189.562251 cycles at its native ABI and 250.562251 cycles through the stable memory API after the exact 61-cycle marshalling adapter. The routine owns `$80-$F3`, 60 bytes at `$5A00`, and four 511-byte quarter-square planes at `$2800/$2A00/$2C00/$2E00`. It passed the original 2^21 + 267,148 edge validation and a fresh relocated machine regression in this integration.

V1 deliberately does not adopt the uploaded 75–173 ZP SMUL16 variants: doing so would defeat the defining 31-byte-ZP Balanced profile. Its native fused SMUL16 therefore remains the best implementation *under V1's resource contract*. The full uploaded native SMUL16 family is included as reference/optional specialization.

## Division

All signed divisions are native signed DIV sources from the validated division Pareto library. V1 uses smaller native Pareto points chosen to stay within its original 31-byte shared-ZP contract; V2–V4 use the practical Fast points. Public adapters only move data between the stable `$C000-$C01F` vectors and each native routine's ZP ABI. No signed DIV path calls a public unsigned divider.

V1's signed DIV code has been repacked into free RAM at `$5000-$5CE8`, below the `$8000` table bank. V2–V4 signed DIV code is below `$92E8`. V3/V4 signed DIV scratch was remapped to `$3E-$52`, leaving `$80-$F3` available for active native SMUL16.

## Semantics

Signed values are two's-complement, little endian. Signed division truncates toward zero; remainder has the numerator's sign; divide-by-zero returns `C=1` and zero q/r; `INT_MIN/-1` wraps at quotient width. Public operands are preserved; A/X/Y are volatile; decimal mode must be clear.
