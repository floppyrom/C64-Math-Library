# Source-linked canonical V2 fast UMULDIV16 (research)

This research option is for stock NMOS 6510 C64s with **12 freely
available zero-page bytes** and enough main RAM. It does not delete or
replace the 288-byte zero-ZP compact reference, and does not change any
original V1–V5 profile, REU kernel, or drive-target code.

The public `MATH_UMULDIV16` operation computes the exact *unsigned*
16×16 product Z32, copies it into the documented volatile N32 buffer,
and divides it by D16. For D!=0, Q32=floor(Z32/D16), R16=Z32 % D16
and C=0. For D=0, Q32=R16=0, C=1. X16, Y16, D16, upper
remainder sentinels R2–R3 and caller stack are preserved. A/X/Y flags
are volatile except returned carry. Decimal mode is off.

| Option | Program + lookup RAM | ZP | Private ordinary RAM scratch |
|---|---:|---:|---:|
| `link:portable-zerozp` | 288 bytes | 0 | 6 bytes |
| `link:qs-v2-fused` | 3,655 bytes | 12 | 4 bytes |

The fast producer physically combines the established 233-byte
unsigned 16x16 quarter-square source, two immutable 511-byte exact
planes, and the canonical historical V2 split-tail unsigned 32/16
divider with only a 32-byte bounded product-copy/public-entry slot.
The native original 32/16 source remains unchanged, including
documented NMOS-only opcodes; only its source-level memory bindings
are relocated.

This is **not** a single newly optimized division algorithm, and it
does not yet deduplicate the shared multiplication/table resources
when other arithmetic operations are selected. Its 3,655-byte image
is intentionally a speed/RAM Pareto candidate, not a suitable default
for every demo or game.

Required qualification includes identical-input 512 full public
Q32/R16/C calls, exact source SHA hashes and resource-budget checks
at two independent origins, a 150-call/24-frame math-only busiest
frame comparison, and 192 public calls under pinned VICE r46284.
Do not compare V2 resident divider cycles with complete public
multiply+divide timing or treat CPU-model frames as physical
VIC-II/IRQ/PAL frame timing.

Automatic speed selection must choose the fastest certified feasible
source under the user's resource constraints. Any speed claim and
addition to the authenticated speed catalog remain **pending CI**.
