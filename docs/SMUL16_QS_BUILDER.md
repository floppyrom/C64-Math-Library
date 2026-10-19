# Signed 16×16 quarter-square source for the operation-first installer

Status: **research**, pending exact-head same-input CPU-model, native VICE,
paired-frame and package checks. The five historical profiles remain available.

The `MATH_SMUL16` public ABI reads signed X16 and Y16, writes full signed
Z32 modulo 2^32, preserves both operands and Z4..Z7, clears C and requires
decimal mode off. A/X/Y are volatile.

## Two independent Pareto choices

| Variant | Code + tables | ZP | Ordinary RAM scratch |
|---|---:|---:|---:|
| `link:compact-zerozp` | 161 bytes | 0 | 6 bytes |
| `link:qs-signed-public` | 1,351 bytes | 0 | 4 bytes |

The fast candidate directly reuses the established 233-byte quarter-square
unsigned 16x16 code and its two immutable 511-byte table planes. Its 96-byte
bounded signed adapter invokes the original producer and corrects the high
word by subtracting unsigned Y when X is negative, and unsigned X when Y is
negative. The identity is exact modulo 2^32:

```
signed_product = unsigned(X) * unsigned(Y)
               - (X_sign ? unsigned(Y) << 16 : 0)
               - (Y_sign ? unsigned(X) << 16 : 0)
```

The candidate is stock NMOS 6510/6502 code, requires no INIT, REU, special
hardware, reserved zero-page, self-modification, or writable executable
tables. It occupies more code/table RAM than compact but needs two fewer
bytes of scratch, and both alternatives remain independently selectable.

The builder compares **512 identical full public-call signed inputs** and
measures mean, p95, maximum, outputs, operand preservation and stack depth
at two disjoint relocations. A separate 150-call/24-frame model trace
tests peak math-frame latency; this is *not* VIC/IRQ/physical PAL frame
qualification. Pinned native VICE r46284 verifies both relocations on a
real 6510 emulation path. Final publication validation re-seals all
SHA-256 source files before speed mode can be trusted as a release option.

A project that uses both UMUL16 and SMUL16 may benefit in the future from
a shared table/code resource owner; this candidate does **not** yet claim
that the operation-first installer deduplicates their 1,022 table bytes.
