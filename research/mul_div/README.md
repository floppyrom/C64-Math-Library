# MUL_DIV research

This directory implements the M2 `MUL_DIV` research milestone from the implementation roadmap.

The target is deliberately **not yet a stable API entry**. The question is whether a multiply/divide family can materially beat composition of the existing public routines while preserving useful game/geometry semantics and the library's resource constraints.

> **2026-09-17 provenance correction:** the first V2 `direct` / `direct_hybrid` experiments assumed the standalone `record_umul16_17zp.a` ABI was installed in the V2 resident image. It is not. Shipped V2 uses `pareto_umul16.a`, an integrated 3xUMUL8 kernel at `$5400`. Historical direct-core cycle figures are therefore superseded as resident-image evidence. See `DIRECT_CORE_PROFILE_CORRECTION_2026-09-17.md`. The public `composed`, `fused`, and `hybrid` paths remain source/profile-consistent.

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

The profile-independent research points are:

```text
composed
    public multiply + public 32/16 divide

fused
    public multiply + product-aware constrained 16-step divide tail

hybrid
    public multiply + native 16/16 divide when product fits 16 bits
    otherwise constrained tail
```

The corrected V2-specific research now adds:

```text
pareto_direct
    inline the actual shipped 3xUMUL8 UMUL16 construction
    + hand live product directly to the constrained tail

pareto_direct_hybrid
    same actual-core multiply
    + q=0/q=1 direct exits for 16-bit products
    + native UDIV16 fallback
    + constrained tail otherwise
```

## Zero-page accounting

The constrained tail uses existing resident arithmetic scratch. The corrected V2 direct generator also keeps its multiplication and divide state inside the profile's already-owned normal transient arithmetic window. It introduces **no new persistent profile ZP allocation**.

## Actual V2 multiply provenance

Shipped V2 Pareto-Fast defines:

```text
I_UMUL8  = $5300
I_UMUL16 = $5400
```

`I_UMUL16` is `resident/modules/pareto_umul16.a`, a three-UMUL8 difference-product construction. The separate `record_umul16_17zp.a` remains a useful optimization/reference source, but its `generic` / `same_x` entry geometry is not the active V2 resident UMUL16 ABI.

The replacement `generate_umuldiv16_pareto.py` consumes the actual implementation directly. After the inlined multiply it keeps:

```text
mq0 = product byte0
mq1 = product byte1
mr0 = product byte2
A   = product byte3
```

and enters the bounded tail without publishing/reloading the product through the public vector.

## Current source/profile-consistent measured V2 baseline

The following same-input results from the earlier resident benchmark enter only through interfaces that are genuinely present in shipped V2. They remain useful baselines while the corrected actual-core direct harness is pending.

| Workload | Composed | Fused | Public hybrid |
|---|---:|---:|---:|
| uniform bounded 16-bit | 1027.605 | **859.405** | 871.733 |
| mixed uniform | 1055.749 | **718.766** | 731.481 |
| byte-sized `game8` | 897.260 | 729.266 | **362.085** |
| 12-bit bounded | 963.851 | **795.582** | 797.821 |

For `game8`, 74.30% of cases have `q=0` and 86.58% have `q<=1`. This remains strong evidence that quotient-class knees matter for small-coordinate/game workloads, even though the old record-core direct-hybrid timing is no longer used.

The corrected `pareto_direct` and `pareto_direct_hybrid` cycle figures are deliberately **not filled in yet**. `benchmark_pareto_direct.py` is now the resident-image gate for those implementations.

## Independent arithmetic model

`model.py` validates the bounded restoring recurrence independently of the 6502 image. On 1,000,000 deterministic random nonzero-divisor triples it classified 749,126 cases as 16-bit quotient and produced zero mismatches against Python integer arithmetic.

Its scratch-placement model predicted the fastest first tail when quotient, remainder-low and divisor all live in already-owned division ZP:

| Scratch placement | Live scratch | Mean modeled divide-stage cycles |
|---|---:|---:|
| all absolute | 0 | 652.82 |
| remainder low in ZP | 1 | 635.89 |
| remainder + divisor in ZP | 3 | 621.81 |
| quotient + remainder + divisor in ZP | 5 | **615.81** |

Those are model numbers only. Resident-image harnesses are authoritative for profile timing.

## Prepared-ratio branch

The real-game audit also found a stronger semantic family for repeated ratios, especially clipping/interpolation:

```text
0 < n < d
m = Q0.16 approximation of n/d
result = signed_component * m >> 16
```

The first prepared-ratio experiments also used the non-installed record-core lifecycle, so their V2 cycle figures are superseded by `PREPARED_RATIO_PROFILE_CORRECTION_2026-09-17.md`.

The corrected V2 path uses the shipped Pareto UMUL8 geometry directly:

```text
generate_prepared_fraction_pareto.py
    actual installed UMUL8 calls

generate_prepared_fraction_pareto_inline.py
    PREP-patched fixed-X quarter-square products
    nearest and floor Q0.16 modes

benchmark_prepared_fraction_pareto.py
    resident-image comparison against literal Quake64 arithmetic
```

The <=1 integer-error proof for signed16 applied values remains valid; the new cycle points remain model-only until that harness is run.

## Files

- `generate_umuldiv16.py` — original composed/fused/public-hybrid generators plus historical record-core direct experiments.
- `generate_umuldiv16_pareto.py` — corrected V2 actual-core direct and direct-hybrid generators.
- `benchmark.py` — historical same-input benchmark; its record-core direct columns are superseded.
- `benchmark_pareto_direct.py` — corrected V2 direct resident-image gate.
- `model.py` — independent bounded-tail mathematical validator.
- `BENCHMARK_RESULTS.md` / `BENCHMARK_V2_5000.json` — historical benchmark evidence; see provenance correction before using direct columns.
- `DIRECT_CORE_PROFILE_CORRECTION_2026-09-17.md` — direct-core correction and replacement path.
- `REAL_GAME_AUDIT_2026-09-17.md` / `WOLF64_AUDIT_2026-09-17.md` — real-game workload audits.
- `PREPARED_RATIO_PROFILE_CORRECTION_2026-09-17.md` — prepared-ratio core-provenance correction.
- `generate_prepared_fraction_pareto.py` — actual-core prepared fraction candidate.
- `generate_prepared_fraction_pareto_inline.py` — fixed-X inline prepared fraction candidate.
- `prepared_fraction_pareto_model.py` — actual-core instruction model calibrated to shipped V2 UMUL8.
- `benchmark_prepared_fraction_pareto.py` — corrected prepared-ratio resident-image gate.

No stable API entry or shipped profile binary is changed by this research work.

## Promotion gates

Before any stable MUL_DIV/ratio API is added, we still need to:

1. run the corrected actual-core resident-image harnesses and preserve machine-readable evidence;
2. patch at least one real game path and include caller marshalling/surrounding arithmetic;
3. determine the workload split between general exact MUL_DIV, two-value fused interpolation, and 3+ value prepared ratios;
4. establish V1/V5 profile-native implementations rather than copying V2-private assumptions;
5. compare nearest versus floor prepared Q0.16 only under explicit accuracy contracts;
6. research signed exact semantics separately instead of assuming unsigned wrappers are optimal;
7. promote only operations that continue to satisfy the implementation-plan "hard to fake" rule.

The current result is therefore a **research family under corrected profile provenance**, not a final public routine.
