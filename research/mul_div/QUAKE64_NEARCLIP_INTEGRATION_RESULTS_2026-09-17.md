# Quake64 near-clip integration results — 2026-09-17

**Status:** standalone integration evidence derived from the actual Quake64 near-clip arithmetic shape. This is stronger than the earlier arithmetic-only comparison, but it is still not a full patched Quake64 build/runtime certification.

## Provenance

```text
GitHub Actions run      35246007285
head commit             e0e2bf9de735c3ba34ed45fe33fcfb2f9aadb7a9
artifact                mul-div-profile-native-results
artifact id             10507671590
artifact digest         sha256:d4dc8b7cb537edd7098b923cbbbbc25ef6df3af492940ef44bcb0375ae7ec4a1
V2 resident PRG SHA256  10af446bd1f49bcf02f9529d7944881d85f0e9b8dec2712638e306b0fab72828
Quake64 source          7c84654946a60314568b709e7e7b97467fed69df
seed                    $C0FFEE
cases                   5,000 edge crossings / 10,000 component outputs
```

All CI steps completed successfully.

## What the integration benchmark includes

Unlike the earlier `PREP + 2*APPLY` arithmetic-only benchmark, this wrapper includes the work that actually differs in Quake64's `.near0` clipping path:

- form `d = z1-z0`;
- form `n = ZCLIP-z0`;
- preserve/restore the ratio on the current Quake path;
- form dynamic X and Y endpoint deltas;
- apply the ratio twice;
- accumulate both deltas into the clipped endpoint;
- write the near-plane Z value.

It excludes unrelated CAM endpoint loading, edge-loop dispatch, post-clip projection, full game integration, VIC/IRQ/SID effects and other rendering work common to both paths.

The prepared implementation is the corrected V2 **profile-native fixed-X quarter-square** candidate, not the historical non-installed record-core experiment.

## Results

| Path | Mean cycles | Min | Max | Gain vs current Quake | Max endpoint error |
|---|---:|---:|---:|---:|---:|
| fixed-X prepared, nearest Q16 | 1487.351 | 1311 | 1670 | **59.83%** | **1** |
| **fixed-X prepared, floor Q16** | **1458.712** | **1288** | **1644** | **60.61%** | **1** |
| Quake64 current `scale_nd + lerp16` path | 3703.020 | 2220 | 4104 | baseline | stress max 120 |

Both prepared candidates produced **zero prepared-contract errors**.

Accuracy against exact mathematical clipped endpoints on this broad valid-crossing stress corpus:

```text
nearest Q16
    non-zero integer error   1.59%
    mean absolute error       0.0159
    max absolute error        1

floor Q16
    non-zero integer error   2.84%
    mean absolute error       0.0284
    max absolute error        1

Quake current reduced ratio
    non-zero integer error  94.60%
    mean absolute error      15.9906
    max absolute error      120
```

The Quake error distribution is deliberately a stress diagnostic, not a claim that normal gameplay visibly clips incorrectly at that frequency. The important comparison is that the prepared Q0.16 path retains an explicit `<=1` integer endpoint error bound while materially reducing the arithmetic work.

## Roadmap test

This result clears the most important **Hard-to-Fake** gate we set for M2:

1. `n` and `d` are genuinely dynamic runtime geometry, so offline precomputation does not solve the problem.
2. The same ratio is reused for two independent dynamic values, so reusable prepared state has semantic value.
3. The realistic alternative is known: Quake64 already contains a purpose-built approximation (`scale_nd + lerp16`).
4. The candidate is not merely faster than our own generic library composition; it is about **60% lower** than that real game workaround in the integrated arithmetic path.
5. It also improves numerical behavior on the same stress inputs.

That is considerably stronger evidence than the exact generic `UMULDIV16` microbenchmark.

## Nearest versus floor

The floor preparation removes the final rounding stage and is about **28.64 cycles** lower in the integrated path:

```text
nearest   1487.3514
floor     1458.7122
saving      28.6392 cycles
```

Both retain the same maximum integer error of one. Nearest roughly halves the frequency/mean magnitude of one-unit errors.

This still looks like a valid Pareto choice rather than a single mandatory implementation:

```text
nearest Q16
    accuracy-biased default candidate

floor Q16
    explicitly speed-biased candidate
```

If the API is eventually public, the approximation/rounding semantic must be named and documented rather than hidden behind a generic `MUL_DIV` label.

## API implication

The strongest current abstraction is no longer general `(a*b)/d`.

For this demonstrated workload the semantic operation is closer to:

```text
SCALE2_FRACTION
    n,d : uint16 with 0<n<d
    x,y : signed16

    t = Q0.16 approximation of n/d
    out_x = x*t
    out_y = y*t
```

or, when endpoint accumulation is part of the caller:

```text
LERP2
    p0, p1, t
    -> interpolated 2D point
```

For three or more values sharing a ratio, standalone `PREP_RATIO + APPLY` remains the more scalable abstraction.

## Decision after this gate

The M2 evidence now supports the following hierarchy:

```text
1 value, exact arbitrary ratio
    exact MUL_DIV fallback / specialized width path

2 values sharing a strict fractional ratio
    SCALE2_FRACTION / LERP2 candidate

3+ values sharing a dynamic ratio
    PREP_RATIO + repeated APPLY

static ratio
    precompute / LUT / shifts
```

The generic exact `UMULDIV16` should remain research/internal for now. The prepared interpolation family has now demonstrated the scene-level value required by the implementation plan.

## Remaining promotion gate

The next meaningful step is **not another synthetic micro-optimization**. It is to patch the leading profile-native prepared implementation into an actual Quake64 build, then verify:

- code/memory coexistence;
- caller marshalling in the real source tree;
- full path timing in context;
- no gameplay/render regressions;
- whether nearest or floor is the right public semantic point.

Until that game-build integration is complete, no stable API entry or shipped profile binary should change.

Machine-readable evidence: `QUAKE64_NEARCLIP_INTEGRATION_V2_5000.json`.
