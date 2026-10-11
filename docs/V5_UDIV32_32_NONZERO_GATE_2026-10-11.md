# V5 zero-ZP UDIV32/32 and UMOD32/32: prechecked nonzero gate

Date: 2026-10-11. Applies to V5 Hybrid Low-ZP only; V1–V4 are unchanged.

## Control-flow transformation

The shared entry at reference address $5957 checks whether D is zero, and handles N<D and N=D. Previously, the N>D path entered $C100, copied operands into private $C040–$C047, then called $C23E to repeat the zero-divisor check.

The optimized builder changes the four N>D BNE offsets to the formerly empty, 3-byte $59D6 jump island, which enters the original $C100 copy block. $C100 now calls $C250 directly because that path has already established D!=0. D=0 instead reaches the existing $C222 Q=R=0, carry-set helper via $59D3. N<D and N=D keep their original result paths.

Addresses are calculated from REG_KERNEL and REG_GAME in the source builder and verified against expected instruction bytes. Public entry addresses and normal ZP usage are unchanged. Only 3 previously-unused implementation bytes become code.

## Paired benchmark

| Routine | Cases | Original mean | New mean | Original min/max | New min/max | Reachable code |
|---|---:|---:|---:|---|---|---|
| MATH_UDIV32_32 | 6,801 | 421.077342 | 409.633142 | 90/2423 | 67/2404 | 946 → 931 |
| MATH_UMOD32_32 | 1,553 | 548.000000 | 537.266581 | 90/2423 | 67/2404 | 946 → 931 |

The independent paired corpus exercised 10,754 N/D pairs for each entry: 21,508 paired native-code calls, zero result/flag errors and zero slowdowns. On each entry, 5,510 cases save 19 cycles, 858 D=0 cases save 106 cycles and 4,386 cases are unchanged.

The full V5 unsigned DIV/MOD validator passed 164,410 calls; the V5 signed DIV/MOD validator passed 36,273 calls. The reference V5 source build is byte-for-byte identical to the diagnostic PRG; alternate-map build and default hybrid validation pass. Standalone-source verification passes 1,617 checks and the lean-package audit passes 30.

## ABI and limits

Q, R, carry and public N/D remain unchanged, as do zero-page resource claims. D=0 skips a copy into **private** $C040–$C047 scratch; private scratch contents after that error return can therefore differ. No additional persistent stack or table data is used.

Cycle means are from deterministic emulator corpora, not exhaustive population averages over all 2^64 operand combinations or physical machine timing. Issue #39's wider unsigned DIV/MOD optimization campaign remains open.
