# REU architecture and timing model

## Hardware model used

The MOS 8726 REC is memory-mapped at `$DF00-$DF0A`. The v3 source uses:

- `$DF01` command
- `$DF02-$DF03` C64 address
- `$DF04-$DF06` REU address/bank
- `$DF07-$DF08` transfer length
- `$DF0A` address control

References:

- Commodore 1764 RAM Expansion Module User's Guide: https://files.commodore.software/reference-material/manuals/commodore-64-manuals/hardware-manuals/1764-ram-expansion-module-users-guide.pdf
- Codebase64 REU register notes: https://www.codebase64.net/doku.php?id=base:reu_registers

The documented behavior important to this library is:

- REU->C64 / C64->REU transfer: one 1 MHz clock per byte.
- SWAP: two clocks per byte.
- DMA pauses while BA is low.
- without AUTOLOAD the byte counter finishes at 1.
- `$DF0A` can hold either/both addresses fixed.

The supplied validation model charges those DMA clocks plus ordinary 6510 instruction timing. It does **not** model VIC-II BA stalls. Therefore these are deterministic no-contention timing-model numbers, not a claim of raster-exact physical-hardware timing.

## REU image layout (512 KiB)

| Bank | Contents |
|---:|---|
| 0 | 65,536-byte UMUL8 product-low plane |
| 1 | 65,536-byte UMUL8 product-high plane |
| 2 | 65,536-byte UDIV8 quotient plane |
| 3 | 65,536-byte UDIV8 remainder / UMOD8 plane |
| 4 | 113-byte relocated UMUL16 turbo overlay at bank offset 0 |
| 5 | 135-byte stack-free relocated UMUL32 turbo overlay at bank offset 0 |
| 6 | reserved |
| 7 | metadata; `FIREMATH-REU-V3` signature near `$FF00` |

The 8-bit lookup address is simply `operand0 + 256*operand1`, so no index arithmetic is needed.

## Why direct REU UMUL16

A one-shot 16x16 product needs only four 8x8 products. v3 fetches `p00`, `p01`, `p10`, `p11` from REU banks 0/1 and combines them in the existing transient ZP union. This makes public UMUL16 339 cycles exact in the transport model while deleting the v2 resident UMUL16 kernel, its internal UMUL8 kernel, and the 1.5 KiB UMUL8 table bank.

## Reference Turbo16 geometry (`$003E-$00AE`)

The record source originally used `$0002-$0072`. Relocating the executable ZP body to `$003E-$00AE` leaves the normal v3 `$02-$38` shared workspace untouched. The relocated source was rerun through the canonical arithmetic harness: 2^21 products + 262,430 edges, zero errors, unchanged 156.341188 native mean.

The same `$CA` quarter-square contents already exist in the v3 resident UMUL32 bank at `$7000/$7200/$7400/$7600`; the overlay was assembled against those pages. This avoids duplicating 2,044 C64 bytes.

## Reference Turbo32 geometry (`$000A-$0090`)

The selected stack-free 135-byte `ram135` record-family kernel uses `$000A-$0090` in the reference build; source-relocatable builds may choose any legal `TURBO32_ZP_BASE` from `$02` through `$79`. Turbo32 remains an explicit exclusive mode, but BEGIN/END now swap 106 fewer bytes than the former 241-byte overlay.

## VEC2 normalization

`MATH_VEC2_NORMALIZE_Q8_8` uses a generated 32 KiB direct ratio-index table at `$8000-$FFFF` in `REU_TURBO16_BANK`. This shares the bank with the low-address Turbo16 overlay without overlap and moves with `REU_TURBO16_BANK` in alternate/custom maps. The resulting public-call mean is **157.552684 cycles** on the 107,396-vector corpus, with the same <=0.3621 degree / <=202-LSB contract as all other profiles.
