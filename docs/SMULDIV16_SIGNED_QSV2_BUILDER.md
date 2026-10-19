# Signed compound SMULDIV16 — quarter-square and historical V2 split-tail

**Research-only dependent migration.** Depends on unsigned fast compound
PR #315, itself pending exact-head full-library qualification. Do not
merge this branch directly into main or retire any profile before
dependency qualification, package sealing and all ABI/native checks.

Public API: signed 16-bit X and Y yield exact 32-bit two's-complement
product Z; N32 is volatile and becomes that product; signed D16 yields
32-bit signed quotient (truncation toward zero) and signed remainder R16
with the product's sign. For D=0, Q32=R16=0, carry set; Z/N retain product.
X/Y/D and R2..R3, caller stack must be preserved. Decimal mode off.

| Candidate | Code and tables | ZP bytes | Ordinary scratch |
|---|---:|---:|---:|
| `link:portable-zerozp` | 439 bytes | 0 | 6 bytes |
| `link:signed-qs-v2-fused` | 4,263 bytes | 12 | 4 bytes |

The fast candidate links the **unchanged** certified signed QS16 full-width
multiply image (233-byte original unsigned producer, two immutable 511-byte
table planes, bounded signed correction), then the canonical relocated V2
unsigned split-tail divider and its already-source-qualified signed 32/16
magnitude adapter, then a 32-byte signed compound public entry.

This is *source composition*, not global shared-code/table coalescing
with other separately chosen multiply or division operations. Its resource
footprint must be counted in full until exact shared ownership exists.
No REU, SMC, INIT or changes to any of the five reference binaries.

The builder compares 512 identical X/Y/D public calls including
negative operands, zero-divisors and overflow boundaries at two code
origins. The test records mean, p95, maximum, Q32/R16/C, product and
N32, unchanged operands and high-remainder sentinels, private memory,
stack, source provenance and RAM/ZP fallback. A paired 150-call/24-frame
synthetic math-only trace compares peak workload costs. Native headless
VICE r46284 must pass both relocations independently. This is not
physical VIC-II/IRQ/PAL timing.

A speed gain is a *hypothesis* until source-model and native tests pass;
the builder must retain the small 0-ZP implementation under tight
resource budgets. No legacy profile may be removed on these results alone.
