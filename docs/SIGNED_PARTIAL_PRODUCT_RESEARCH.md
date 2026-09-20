# Signed partial-product research — 2026-09-14

This note records the signed-multiply optimization pass that followed the direct
SMUL8 upgrade.  The question was whether forming signed partial products directly
can beat the conventional two's-complement identity

```
signed = unsigned
       - (x_negative ? y << W : 0)
       - (y_negative ? x << W : 0)
```

for wider practical multipliers.

## Production conclusion

**Yes at 8×8; not yet at 16×16, 16×32 or 32×32.**

`MATH_SMUL8` is now a true direct signed-domain quarter-square implementation and
is shipped in every fixed profile.  The wider experiments below are retained as
qualified negative evidence and are **not** part of the resident execution path.
The existing native SMUL16/24/32 kernels remain selected.

## 8×8: direct signed formation wins decisively

The shipped kernel evaluates the signed-domain quarter-square identity directly.
It does not form an unsigned product and repair the high byte afterwards.

| Metric | Shipped direct SMUL8 |
|---|---:|
| exhaustive cases | 65,536 |
| errors | 0 |
| mean cycles | **67.992188** |
| min / max | 66 / 70 |
| ZP | **0 B** |
| persistent stack page | **0 B** |
| reachable code | 46 B |
| new useful table bytes | 1,022 B |
| shared existing table bytes | 1,022 B |

Two lower-level mixed-sign primitives were also qualified exhaustively:

| Primitive | Mean | Range | Errors | Code |
|---|---:|---:|---:|---:|
| signed operand bound, S8×U8 | **47.992188** | 46–50 | 0 / 65,536 | 31 B |
| signed operand indexed, U8×S8 | **51.992188** | 50–54 | 0 / 65,536 | 33 B |

For both primitives the final carry has a useful exact property over the whole
input domain: **C=1 iff the mathematical product is non-negative**.

## 16×16: direct signed high-row experiment loses

The first wider candidate made the high X byte signed during partial-product
formation, so the producer represented signed-X × unsigned-Y and only the Y-sign
correction remained.

It was tested with the same large harness used for the established SMUL16 work:
2,097,152 profile products plus 267,148 signed edge cases, zero errors.

| 16×16 implementation | Mean cycles | Range | ZP | Table/data bytes |
|---|---:|---:|---:|---:|
| current fastest generic | **185.312025** | 162–224 | 171 B | 2,044 B |
| current practical | **189.562251** | 166–229 | 116 B | 2,044 B |
| compact 101-ZP reference | 190.771 | — | 101 B | ~2,044 B |
| signed-partial hybrid | **192.468827** | 173–222 | 150 B | **4,088 B** |

The hybrid is dominated.  The middle-position signed partial needs explicit sign
extension and disrupts the very efficient carry phase of the unsigned
quarter-square chain.  It is slower than both the fastest and practical baselines
while doubling table data.

## 16×32 and 32×32: the critical signed-row subproblem

Both widths reduce to the same decisive subproblem when only one top row is made
signed-aware:

* 16×32: the signed high byte of the 16-bit operand requires a **signed 32×8 row**.
* 32×32: making the final high byte of one 32-bit operand signed also requires the
  same **signed 32×8 row**.

That row was therefore implemented and measured directly in two matched forms:

1. ordinary unsigned 32×8 formation followed by the conventional sign correction;
2. direct S8/U8 mixed partial products accumulated with full sign extension.

The corpus contains all 256 signed scalar values against a dense edge set plus
100,000 deterministic random 32-bit multiplicands: **103,584 cases per routine**.
Both implementations return zero errors.

| Signed 32×8 row | Mean cycles | Range | Code | Standalone tables |
|---|---:|---:|---:|---:|
| unsigned row + correction | **360.908480** | 335–387 | 258 B | 2,044 B |
| direct signed partials | **371.857488** | 364–380 | **255 B** | 2,044 B |

The direct form is 3 code bytes smaller, but **10.949008 cycles slower on the
matched corpus**.  More importantly, in a wider multiplier the ordinary unsigned
quarter-square tables are still required by the other rows, so selecting this
direct row would add another **2,044 bytes** of mixed-sign tables.

Accordingly, this direct-partial route is worse on both practical speed and
integrated memory for 16×32 and 32×32.

## Why 8×8 succeeds but wider composition does not

At 8×8, the signed result is the whole result.  The quarter-square lookup can
absorb sign directly, and there are no higher columns that must receive sign
extension.

In a wider multiplication, a signed byte partial usually sits inside a larger
carry network.  Its two-byte two's-complement representation is not enough by
itself: negative partials must be sign-extended into higher result columns.  That
bookkeeping competes directly with the cheap post-product correction we were
trying to remove.  At 16×16 it also interferes with the existing carry-fused
quarter-square chain; at 16×32/32×32 the matched signed-row experiment shows that
the direct approach still loses even before considering the extra integrated
table family.

## What this does and does not establish

This pass **does not prove** that unsigned-product-plus-correction is globally
optimal for 16×16, 16×32 or 32×32.  It does establish that the most natural direct
quarter-square extensions of the successful SMUL8 technique do not beat the
current practical baselines.

Future work with a genuinely different carry representation, signed-digit row
encoding, or a generator that co-optimizes signed row formation and column
summation may still find a wider win.  Such a routine should be required to beat
both cycle count **and** the integrated table/ZP cost before replacing the current
library kernels.

## Preserved evidence

The qualified machine-readable result is retained in
`validation/research/SIGNED_PARTIAL_PRODUCT_RESEARCH.json`. The superseded
experimental generators and intermediate source variants were intentionally
removed from the lean replacement tree; they remain recoverable from Git
history. The production consolidated table remains
`docs/CONSOLIDATED_ROUTINE_TABLE.{md,csv}`.
