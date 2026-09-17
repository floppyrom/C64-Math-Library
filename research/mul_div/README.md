# MUL_DIV research

This directory implements the M2 `MUL_DIV` research milestone from the implementation roadmap.

The target is deliberately **not yet a stable API entry**. The question is which multiply/divide-shaped operations are genuinely hard to fake in games, and which implementation families materially beat realistic alternatives without wasting memory, ZP, or cycles on generality the workload does not need.

> **Profile-provenance correction, 2026-09-17:** the first V2 `direct` / `direct_hybrid` and prepared-ratio experiments assumed the standalone `record_umul16_17zp.a` ABI was installed in the V2 resident image. It is not. Shipped V2 uses `pareto_umul16.a`, an integrated 3xUMUL8 kernel at `$5400`. Historical record-core cycle figures are superseded as V2 resident-image evidence. The corrected results below use the actual shipped V2 implementation. See `DIRECT_CORE_PROFILE_CORRECTION_2026-09-17.md` and `PREPARED_RATIO_PROFILE_CORRECTION_2026-09-17.md`.

## 1. Exact bounded UMULDIV16

Research contract:

```text
input:
    a = uint16
    b = uint16
    d = uint16

success:
    d != 0
    floor((a*b)/d) <= $ffff

output:
    q = floor((a*b)/d)
    r = (a*b) mod d
    C = 0

error:
    d == 0 or quotient does not fit uint16
    q = r = 0
    C = 1
```

Let the 32-bit product be `hi:lo`. Then:

```text
q fits uint16  <=>  hi < d
```

Once `hi < d` is known, `hi` is already a legal initial remainder and only the low 16 product bits need to be streamed through a constrained divider.

### Research implementations

```text
composed
    public UMUL16
    -> copy product
    -> public UDIV32_16
    -> copy q/r

fused
    public UMUL16
    -> constrained 16-step bounded tail

public hybrid
    public UMUL16
    -> native UDIV16 when product fits 16 bits
    -> constrained tail otherwise

pareto_direct
    inline the actually shipped V2 3xUMUL8 UMUL16
    -> direct live-state handoff

pareto_direct_hybrid
    same actual-core multiply
    -> q=0/q=1/native UDIV16 knees for 16-bit products

pareto_width_hybrid
    runtime operand-width knees:
        8x8   -> one UMUL8
        16x8  -> two UMUL8
        16x16 -> shipped 3xUMUL8 construction
    -> quotient-class knees
```

All corrected variants use only arithmetic scratch already owned by V2; no new persistent profile ZP allocation is required.

## 2. Corrected resident-image V2 results

Evidence:

```text
GitHub Actions run     35245353355
head                   0bf1763a25f86a61bc8679dea9d2d6763cc67804
artifact digest        sha256:f13f0679d3257a9cf3e87de829d22eff2c0c082b7d884fba6588028986f5ed95
V2 PRG SHA256          10af446bd1f49bcf02f9529d7944881d85f0e9b8dec2712638e306b0fab72828
edge suite             2,197 cases
random corpus          5,000 cases per workload
all corrected errors   0
```

### Exact MUL_DIV

| Workload | Composed | Fused | Public hybrid | Pareto direct | Pareto direct hybrid | Width hybrid |
|---|---:|---:|---:|---:|---:|---:|
| bounded uniform 16-bit | 1027.605 | **859.405** | 871.733 | 934.248 | 946.905 | 960.072 |
| mixed uniform | 1055.749 | **718.766** | 731.481 | 792.553 | 805.222 | 818.978 |
| byte-sized `game8` | 897.260 | 729.266 | 362.085 | 819.352 | 445.084 | **197.820** |
| 12-bit bounded | 963.851 | **795.582** | 797.821 | 884.449 | 886.437 | 879.736 |

The result is a genuine Pareto split, not one universal winner.

For broad 16-bit work, **public UMUL16 + the constrained tail is still the best current exact path**. Inlining the shipped 3xUMUL8 construction is slower, so the research rule is explicit: deeper fusion must earn its cost; crossing an internal boundary is not automatically an optimization.

The synthetic byte-sized `game8` corpus initially made the width-knee hybrid look exceptional at **197.820 cycles**, because its quotient distribution was dominated by q=0/q=1. That result remains valid for that distribution, but it has now failed a real-game promotion gate. See the Wolf64 result below.

Full profile-native details: `PROFILE_NATIVE_RESULTS_2026-09-17.md`.

## 3. Independent arithmetic model

`model.py` validates the bounded restoring recurrence independently of the 6502 image. On one million deterministic random nonzero-divisor triples it classified 749,126 cases as 16-bit quotient and produced zero recurrence mismatches against Python integer arithmetic.

Its scratch-placement model predicted the best first tail when quotient, remainder-low and divisor reuse the library's existing division ZP:

| Scratch placement | Live scratch | Mean modeled divide-stage cycles |
|---|---:|---:|
| all absolute | 0 | 652.82 |
| remainder low in ZP | 1 | 635.89 |
| remainder + divisor in ZP | 3 | 621.81 |
| quotient + remainder + divisor in ZP | 5 | **615.81** |

Those remain model numbers. Resident-image measurements are authoritative for profile timing.

## 4. Real-game audit changed the target

The exact routine is useful, but the audits show that `(a*b)/d` syntax alone is not enough to justify a public routine.

### Quake64

- Ramp height has geometry-static `sy/run`; precomputation or a fixed-point slope coefficient is a better fit than general MUL_DIV.
- Perspective already prepares/reuses a reciprocal-like Z factor; two independent MUL_DIV calls would be the wrong abstraction.
- Near-plane clipping has the strongest hard-to-fake case: a genuinely dynamic ratio is reused for X and Y.
- Segment/AABB intersection has a tiny Q7 ratio with fixed multiplier 127; that likely belongs inside a future compound `SEGMENT_AABB` routine rather than full general MUL_DIV.

### Wolf64

Wolf64 repeatedly exploits constants, bounded quotients, LUTs and DDA/prepared state. Its sprite projection is now an explicit negative promotion test for general MUL_DIV.

The audited call site computes:

```text
e_col_cx = 20 +/- floor(|side|*20/perp_mid)
```

with the caller already guaranteeing `|side|<=perp_mid`, an 8-bit denominator and therefore quotient <=20.

An exhaustive test over **all 65,535 accepted signed side/perp pairs** produced zero errors for both implementations:

| Projection path | Mean | Min | Max |
|---|---:|---:|---:|
| **Wolf64 current specialized path** | **577.181** | 175 | 649 |
| V2 width-knee exact MUL_DIV | 1048.155 | 252 | 1156 |

The library candidate is **81.60% slower**. The synthetic ~198-cycle `game8` point therefore does **not** earn a public API slot: Wolf64's fixed multiplier, bounded quotient and 8-bit denominator are easy to exploit more efficiently in game-specific code.

See `WOLF64_PROJECT_COL_RESULTS_2026-09-17.md` and `WOLF64_PROJECT_COL_V2_EXHAUSTIVE.json`.

### Steel Ranger

No compelling arbitrary-runtime general `(a*b)/d` gameplay site was found in the audited demo. Existing arithmetic is mostly constants, shifts and bounded special cases.

See `REAL_GAME_AUDIT_2026-09-17.md` and `WOLF64_AUDIT_2026-09-17.md`.

## 5. Prepared strict-fraction ratio

The strongest demonstrated workload is interpolation/clipping with the semantic invariant:

```text
0 < n < d
m = Q0.16 approximation of n/d
result = signed_component * m >> 16
```

For signed16 applied values, both nearest and floor Q0.16 preparation can be given an explicit **maximum integer error <= 1** against exact `trunc(component*n/d)`.

Corrected V2 implementations use the actually shipped Pareto quarter-square geometry rather than the non-installed record-core ABI:

```text
generate_prepared_fraction_pareto.py
    calls actual installed V2 UMUL8

generate_prepared_fraction_pareto_inline.py
    PREP patches fixed-X quarter-square products
    supports nearest and floor Q0.16

benchmark_prepared_fraction_pareto.py
    compares resident-image candidates against literal Quake64 arithmetic
```

### Arithmetic-level resident results

5,000 valid near-plane ratios, two signed component applications each:

| Candidate | PREP | APPLY | Pair | Gain vs Quake | Max error |
|---|---:|---:|---:|---:|---:|
| Pareto current, nearest | 695.284 | 370.573 | 1436.430 | 59.08% | 1 |
| fixed-X inline, nearest | 719.284 | 290.249 | 1299.782 | 62.97% | 1 |
| **fixed-X inline, floor** | **690.476** | **290.247** | **1270.970** | **63.79%** | **1** |
| Quake64 current arithmetic pair | — | — | 3510.294 | baseline | stress max 107 |

Nearest Q0.16 has 1.51% one-unit errors on the broad stress corpus; floor has 3.12%. Both remain bounded at one integer unit. The Quake error percentages are stress-test diagnostics, not claims about visible error frequency in normal gameplay.

### Integrated Quake64 near-clip result

The next gate includes the surrounding work that differs between Quake64's `.near0` implementation and the prepared path: n/d formation, ratio save/restore on the Quake path, X/Y delta formation, two ratio applications, endpoint accumulation and near-Z writeback.

GitHub Actions run `35246007285` measured 5,000 valid crossings:

| Integrated path | Mean | Min | Max | Gain vs Quake | Max endpoint error |
|---|---:|---:|---:|---:|---:|
| fixed-X prepared, nearest | 1487.351 | 1311 | 1670 | **59.83%** | **1** |
| **fixed-X prepared, floor** | **1458.712** | **1288** | **1644** | **60.61%** | **1** |
| Quake64 current | 3703.020 | 2220 | 4104 | baseline | stress max 120 |

Both prepared variants had **zero prepared-contract errors**. This is still a standalone integration harness rather than a complete Quake64 build, but it clears the implementation plan's most important realistic-alternative gate: the prepared operation remains decisively useful after caller marshalling and surrounding clipping arithmetic are included.

See `QUAKE64_NEARCLIP_INTEGRATION_RESULTS_2026-09-17.md` and `QUAKE64_NEARCLIP_INTEGRATION_V2_5000.json`.

## 6. Current API direction

The evidence now suggests an API family based on semantic reuse count rather than arithmetic width alone:

```text
one arbitrary exact value
    -> exact MUL_DIV fallback / specialized path

two signed values sharing 0<t<1
    -> SCALE2_FRACTION / LERP2 candidate

three or more values sharing one dynamic ratio
    -> PREP_RATIO + repeated APPLY

static/fixed ratio
    -> precompute / LUT / shifts, not library runtime division
```

The leading demonstrated M2 capability is therefore **prepared/fused strict-fraction interpolation**, not generic MUL_DIV. General exact `UMULDIV16` remains useful research/fallback machinery, while the small-width exact helper has explicitly failed one real-game promotion test.

A profile-native fused two-component SCALE2/LERP2 implementation is still worth researching because it can remove the prepared-state lifecycle for the two-value case. Any earlier record-core SCALE2 timings remain historical until reimplemented against the shipped Pareto geometry.

## 7. Key files

- `generate_umuldiv16.py` — composed/fused/public-hybrid generators; historical record-core direct experiments remain for provenance only.
- `generate_umuldiv16_pareto.py` — corrected actual V2 3xUMUL8 direct/direct-hybrid generators.
- `generate_umuldiv16_pareto_width.py` — runtime operand-width hybrid.
- `benchmark_pareto_direct.py` — corrected exact resident-image benchmark.
- `benchmark_wolf64_project_col.py` — exhaustive real-domain Wolf64 projection gate.
- `WOLF64_PROJECT_COL_RESULTS_2026-09-17.md` — interpretation of the exhaustive negative gate.
- `WOLF64_PROJECT_COL_V2_EXHAUSTIVE.json` — machine-readable Wolf64 evidence.
- `model.py` — independent bounded-tail arithmetic validator.
- `PROFILE_NATIVE_RESULTS_2026-09-17.md` — corrected resident results and interpretation.
- `DIRECT_CORE_PROFILE_CORRECTION_2026-09-17.md` — exact direct-core provenance correction.
- `PREPARED_RATIO_PROFILE_CORRECTION_2026-09-17.md` — prepared-ratio provenance correction.
- `generate_prepared_fraction_pareto.py` — installed-core prepared fraction candidate.
- `generate_prepared_fraction_pareto_inline.py` — fixed-X inline prepared ratio candidate.
- `prepared_fraction_pareto_model.py` — instruction model calibrated to shipped V2 UMUL8.
- `benchmark_prepared_fraction_pareto.py` — resident-image Quake arithmetic comparison.
- `benchmark_quake64_nearclip_integration.py` — surrounding-path Quake near-clip integration benchmark.
- `QUAKE64_NEARCLIP_INTEGRATION_RESULTS_2026-09-17.md` / `QUAKE64_NEARCLIP_INTEGRATION_V2_5000.json` — integrated evidence.
- `REAL_GAME_AUDIT_2026-09-17.md` / `WOLF64_AUDIT_2026-09-17.md` — workload audits.

## 8. Promotion gates

Before any stable MUL_DIV/ratio API is added:

1. **Passed at standalone-integration level:** the leading prepared interpolation path includes caller marshalling and surrounding Quake `.near0` arithmetic and remains about 60% below the current workaround. A real patched Quake64 build is still required for coexistence/gameplay certification.
2. decide nearest versus floor Q0.16 under an explicit accuracy/performance contract;
3. implement/measure the corrected profile-native two-value `SCALE2_FRACTION` / `LERP2` candidate and decide whether that or standalone PREP/APPLY is the better public abstraction;
4. **Negative gate completed:** the ~198-cycle synthetic small-width exact path loses badly to Wolf64's real constant/bounded specialization and should not be promoted from `game8` evidence alone;
5. establish V1/V5 profile-native implementations instead of copying V2-private assumptions;
6. research signed exact semantics only where a real use case demands them;
7. promote only operations that continue to satisfy the implementation-plan **hard-to-fake** rule.

No stable API entry or shipped profile binary has been changed by this research work.
