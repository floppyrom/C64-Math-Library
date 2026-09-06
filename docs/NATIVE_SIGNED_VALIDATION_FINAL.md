# Native signed final validation

## Uploaded SMUL16 archive

- archive SHA-256: `08c680919cac818e4a4bf24317f4da5997820a6a63471bd6ea8d535b5f827964`
- internal release manifest: 28/28 entries verified before integration
- active V2/V3/V4 source: `smul16_practical_116zp.a`
- publication evidence in uploaded archive: 2,097,152 canonical cases + 267,148 signed edge cases, zero errors
- relocated public-ABI machine regression in this build: **231,241 cases, 0 errors**, min/max 227–290 cycles
- exact stable-memory adapter cost: 61 cycles; canonical public mean = **250.562251 cycles**

The relocation keeps the ZP code within one page and preserves every table's 512-byte alignment/low-byte geometry, so the published native core timing remains applicable.

## Native signed DIV

All SDIV active cores are direct selections from the signed division reference library. 8-bit published validation is exhaustive; wider published means use the fixed 2^21 corpus plus structured edges. The final integration changes only address relocation and stable-memory marshalling; no public UDIV routine is called. V1 code is repacked below `$6000`; V2–V4 native signed DIV code remains below `$9300`.

## SMUL8/24/32 and V1 SMUL16

These are producer-fused native signed implementations: the selected profile's validated multiplication producer is entered directly and its terminal return is replaced by the signed two's-complement upper-half continuation. They do **not** call `MATH_UMUL*`. The correction identity was validated exhaustively at 8 bits and by deterministic structured/random checks at wider widths in the prior native build.
