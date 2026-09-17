# MUL_DIV research

This directory starts the M2 `MUL_DIV` research milestone from the implementation roadmap.

The first target is deliberately **not** a new stable API entry. The goal is to determine whether a fused 16-bit multiply/divide kernel can materially beat the obvious composition of the existing public routines while preserving exact integer semantics.

## Initial operation under study

```text
UMULDIV16_BOUNDED

input:
    X[0..1] = unsigned a
    Y[0..1] = unsigned b
    D[0..1] = unsigned d

success condition:
    d != 0
    floor((a*b)/d) <= $ffff

output on success:
    Z[0..1] = floor((a*b)/d)
    Z[2..3] = (a*b) mod d
    C = 0

error:
    d == 0 or quotient does not fit in 16 bits
    Z[0..3] = 0
    C = 1
```

This bounded form is the practical game/geometry case. It is mathematically equivalent to testing the high word of the 32-bit product before a 16-step restoring tail:

```text
product = hi:lo
quotient fits 16 bits  <=>  hi < d
```

When that condition is true, `hi` is already the initial remainder and only the low 16 product bits need to be streamed through the divider. A general 32/16 divider has to support the wider-quotient cases as well.

## Why this is a real fusion target

The existing public composition is conceptually:

```text
UMUL16
copy Z32 -> N32
UDIV32_16
copy Q/R -> desired output
```

Current public headline averages are:

```text
V1: UMUL16 273.8372 + UDIV32_16 857.373105 = 1131.210305 cycles before glue
V2: UMUL16 225.8372 + UDIV32_16 759.730823 =  985.568023 cycles before glue
```

Those two averages come from their own canonical corpora, so they are only a target-setting reference. `benchmark.py` measures the composed wrapper and fused candidate on the **same MUL_DIV corpus** before we make any performance claim.

## Candidate 1: product-aware 16-step tail

`generate_umuldiv16.py` emits an unrolled candidate that:

1. calls the selected profile's current `MATH_UMUL16`;
2. copies the divisor and product working bytes into the library's already-owned division ZP scratch;
3. rejects divide-by-zero and `hi >= d` overflow;
4. performs only the 16 constrained low-word divide steps;
5. returns quotient and remainder directly in `Z[0..3]`.

The tail is derived from the same carry-pipeline idea used by the resident 32/16 divider: each trial subtraction leaves the next quotient bit in Carry, and the next `ROL` consumes it. The 17th-remainder-bit path is handled separately and is known to require a quotient bit of one.

### Zero-page accounting

The fast research form uses:

```text
$12-$13  divisor copy
$14-$15  quotient pipeline
$16      remainder low byte
```

These are **not new library ZP bytes**. They are the existing resident unsigned-division ABI/scratch locations already owned by V1/V2 and inherited by the later profiles. Because the multiply has returned before the fused divide tail starts, the same bytes can be reused sequentially.

So the candidate is five live ZP bytes internally but **zero incremental profile ZP** if integrated into the current library layout.

## Preliminary arithmetic/cycle-geometry model

`model.py` validates the bounded restoring recurrence independently of the 6502 image and models the unrolled tail's instruction-path costs. On 1,000,000 deterministic uniform random `(a,b,d)` triples with nonzero `d`, 749,126 cases had a 16-bit quotient.

For those bounded cases, the modeled divide stage (including scratch copies/final writeback, but excluding `MATH_UMUL16` and the range precheck) was:

| Scratch placement | Incremental ZP if standalone | Mean modeled cycles | Min | Max |
|---|---:|---:|---:|---:|
| all public/absolute | 0 | 652.82 | 492 | 948 |
| remainder low in ZP | 1 | 635.89 | 490 | 906 |
| remainder + divisor in ZP | 3 | 621.81 | 488 | 864 |
| quotient + remainder + divisor in ZP | 5 | **615.81** | 482 | 858 |

Because the current library already owns the five selected bytes, the 5-byte live-scratch form is the correct first implementation candidate: it gets the fastest modeled tail without increasing the profile ZP footprint.

These are **model numbers, not certified resident-image timings**. Page-crossing penalties, public multiply cost on the same corpus, and wrapper effects are measured by `benchmark.py`.

## Files

- `generate_umuldiv16.py` - deterministic source generator for the unrolled bounded candidate and composed baseline wrapper.
- `model.py` - independent mathematical validator and cycle-geometry model.
- `benchmark.py` - patches generated research wrappers into a loaded V1/V2 resident image and measures both on identical deterministic corpora using `tools/mini6502.py`.

No public API, profile binary, or shipped validation result is changed by this research commit.

## Research gates before promotion

The routine should not enter the stable API until all of these are true:

1. exact correctness is validated for structured edge cases and a large deterministic corpus;
2. composed and fused paths are measured on the same inputs;
3. V1/V2/V5 integration is checked for zero additional ZP and code-region fit;
4. signed semantics are investigated separately rather than added as a wrapper by default;
5. the full-range 32-bit quotient form is compared against the bounded form;
6. prepared-divisor/reciprocal variants are benchmarked for repeated-denominator workloads.

The bounded kernel is therefore the first Pareto experiment, not yet the final `MATH_UMULDIV16` contract.
