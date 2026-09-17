# MUL_DIV research

This directory implements the M2 `MUL_DIV` research milestone from the implementation roadmap.

The target is deliberately **not yet a stable API entry**. The question is whether an exact 16-bit multiply/divide family can materially beat composition of the existing public routines while preserving useful game/geometry semantics and the library's resource constraints.

## Operation under study

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

Let the 32-bit product be `hi:lo`. Then:

```text
quotient fits 16 bits  <=>  hi < d
```

Once that condition is true, `hi` is already a legal initial remainder and only the low 16 product bits need to be streamed through the divider.

## Why it is hard to fake efficiently

The obvious public composition is:

```text
MATH_UMUL16
copy Z32 -> N32
MATH_UDIV32_16
copy Q/R -> output
```

That throws away useful internal state twice: first when the multiplier publishes its four-byte product, then when the divider reconstructs its own working state.

The research therefore tests progressively tighter handoffs:

```text
composed
    public multiply + public 32/16 divide

fused
    public multiply + product-aware constrained 16-step divide tail

hybrid
    public multiply + native 16/16 divide when product fits 16 bits
    otherwise constrained tail

direct (V2)
    native UMUL16 core + direct live-product handoff to constrained tail

direct_hybrid (V2)
    native UMUL16 core + native UDIV16 fast path for 16-bit products
    otherwise direct constrained tail
```

## Zero-page accounting

The constrained tail uses:

```text
$12-$13  divisor
$14-$15  quotient pipeline
$16      remainder low byte
```

These bytes already belong to the resident unsigned-division ABI. Because ordinary library calls are sequential/non-reentrant, the research kernel can reuse them after multiplication returns.

So the first fast candidates require **zero incremental profile ZP**.

## V2 direct-core handoff

V2's selected record UMUL16 kernel already leaves the product in an unusually useful form:

```text
entry       $53EC
X low bind  $21
X high bind $29
Y high SMC  $541A

result:
    byte0 = $31
    byte1 = CPU X
    byte2 = CPU A
    byte3 = CPU Y
```

The direct candidate consumes those bytes immediately instead of forcing the product through public `Z32` first. This alone removes about **43.5 additional cycles** on the 5,000-case uniform bounded corpus relative to the first fused version.

## Current measured V2 results

All numbers below are paired same-input measurements against the shipped V2 resident image, with zero arithmetic errors in the listed corpora. See `BENCHMARK_RESULTS.md` for full ranges, corpus shapes and caveats.

| Workload | Composed | Fused | Direct | Direct hybrid |
|---|---:|---:|---:|---:|
| uniform bounded 16-bit | 1027.605 | 859.405 | **815.900** | 824.427 |
| mixed uniform | 1055.749 | 718.766 | **675.142** | 683.492 |
| byte-sized `game8` | 897.260 | 729.266 | 686.082 | **336.085** |
| 12-bit bounded | 963.851 | 795.582 | 752.303 | **751.070** |

The emerging Pareto split is therefore:

```text
broad/full 16-bit workloads
    -> direct native UMUL16 + constrained 16-step tail

byte/small-product workloads
    -> direct native UMUL16 + native UDIV16 fast path
       with constrained-tail fallback
```

The hybrid is not universally faster: on uniformly distributed bounded 16-bit operands almost no products fit in 16 bits, so its dispatch is overhead. That is useful evidence against collapsing everything into one implementation.

## Independent arithmetic model

`model.py` validates the bounded restoring recurrence independently of the 6502 image. On 1,000,000 deterministic random nonzero-divisor triples it classified 749,126 cases as 16-bit quotient and produced **zero mismatches** against Python integer arithmetic.

Its scratch-placement model predicted the fastest first tail when quotient, remainder-low and divisor all live in the already-owned division ZP:

| Scratch placement | Live scratch | Mean modeled divide-stage cycles |
|---|---:|---:|
| all absolute | 0 | 652.82 |
| remainder low in ZP | 1 | 635.89 |
| remainder + divisor in ZP | 3 | 621.81 |
| quotient + remainder + divisor in ZP | 5 | **615.81** |

Those are model numbers only. `benchmark.py` is authoritative for resident-image cycle comparisons.

## Files

- `generate_umuldiv16.py` — deterministic generators for composed, bounded, public-hybrid, V2 direct and V2 direct-hybrid kernels.
- `model.py` — independent mathematical validator and tail cycle-geometry model.
- `benchmark.py` — same-input resident-image correctness/timing harness for V1/V2/V5; V2 additionally exposes the direct variants.
- `MODEL_RESULTS.md` — preliminary arithmetic and scratch-placement evidence.
- `BENCHMARK_RESULTS.md` — paired V2 resident-image results.
- `direct_core_notes.md` — V2 native handoff details and interpretation.

No stable API entry or shipped profile binary is changed by this research work.

## Promotion gates

Before a stable `MATH_UMULDIV16` is added, we still need to:

1. run a larger/canonical paired validation corpus and preserve machine-readable evidence;
2. determine whether quotient-class prechecks can beat the fixed 16-step general tail;
3. investigate deeper multiply/divide state sharing beyond the current direct handoff;
4. establish V1/V5 direct-core equivalents or decide that V2 gets a distinct implementation tier;
5. compare the bounded 16-bit-result contract with a full-range 32-bit quotient form;
6. research prepared-divisor/reciprocal versions for repeated-denominator workloads;
7. research signed semantics separately instead of assuming an unsigned wrapper is optimal.

The current result is therefore a validated **research Pareto family**, not yet the final public routine.
