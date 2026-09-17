# MUL_DIV V2 profile-native results — 2026-09-17

**Status:** resident-image research evidence, not release certification and not a stable API change.

This note supersedes the earlier V2 direct/prepared cycle claims that accidentally targeted the non-installed `record_umul16_17zp.a` ABI. All results below use implementations consistent with the **shipped V2 Pareto-Fast profile**.

## Provenance

```text
GitHub Actions run     35245353355
head commit            0bf1763a25f86a61bc8679dea9d2d6763cc67804
artifact               mul-div-profile-native-results
artifact digest        sha256:f13f0679d3257a9cf3e87de829d22eff2c0c082b7d884fba6588028986f5ed95
V2 resident PRG SHA256 10af446bd1f49bcf02f9529d7944881d85f0e9b8dec2712638e306b0fab72828
seed                   $C0FFEE (+ corpus index where applicable)
```

The CI run completed all corrected profile-native benchmarks, models and independent arithmetic checks successfully.

---

# 1. Exact bounded UMULDIV16

Contract:

```text
q = floor((a*b)/d)
r = (a*b) mod d

success: d != 0 and q <= $ffff
error:   d == 0 or q > $ffff
```

All six compared paths produced **zero errors** in the 2,197-case structured edge suite and all four 5,000-case corpora after the native UDIV16 quotient handoff was corrected.

## Uniform bounded 16-bit quotient

| Candidate | Mean cycles | Min | Max | Gain vs composition |
|---|---:|---:|---:|---:|
| public composition | 1027.605 | 885 | 1189 | baseline |
| **public UMUL16 + fused bounded tail** | **859.405** | 717 | 1021 | **16.37%** |
| public small-product hybrid | 871.733 | 336 | 1033 | 15.17% |
| inlined actual-core direct | 934.248 | 808 | 1097 | 9.08% |
| inlined actual-core direct hybrid | 946.905 | 407 | 1109 | 7.85% |
| width-knee hybrid | 960.072 | 161 | 1125 | 6.57% |

The important result is negative but useful: **inlining the shipped 3xUMUL8 UMUL16 is not the best broad 16-bit route.** The simpler public-UMUL16 handoff into the constrained tail remains faster on this corpus.

So deeper fusion is not automatically beneficial. The library should keep the already selected multiply as a black-box Pareto component unless a semantic width knee provides enough information to choose a cheaper multiplication algorithm.

## Mixed unrestricted 16-bit inputs

| Candidate | Mean cycles | Gain vs composition |
|---|---:|---:|
| composition | 1055.749 | baseline |
| **fused** | **718.766** | **31.92%** |
| public hybrid | 731.481 | 30.71% |
| actual-core direct | 792.553 | 24.93% |
| actual-core direct hybrid | 805.222 | 23.73% |
| width-knee hybrid | 818.978 | 22.43% |

The fused path gains more here because bounded overflow can be rejected after the product high-word test instead of paying for a complete public 32/16 division first.

## Byte-sized `game8`

This workload is where semantic width specialization changes the result:

```text
product fits 16 bits  100.00%
q == 0                 74.30%
q <= 1                 86.58%
q <= 255               99.94%
```

| Candidate | Mean cycles | Min | Max | Gain vs composition |
|---|---:|---:|---:|---:|
| composition | 897.260 | 883 | 1193 | baseline |
| fused | 729.266 | 715 | 1027 | 18.72% |
| public hybrid | 362.085 | 334 | 1161 | 59.65% |
| actual-core direct | 819.352 | 796 | 1111 | 8.68% |
| actual-core direct hybrid | 445.084 | 395 | 1313 | 50.40% |
| **width-knee hybrid** | **197.820** | **161** | 1065 | **77.95%** |

The width-knee form is also about **45.37% below the existing public hybrid** on this corpus.

Its fast path is not a benchmark constant trick. It detects at runtime that both operands fit in bytes, performs one shipped `UMUL8`, then exploits q=0/q=1/native-UDIV16 quotient knees. If exactly one operand is byte-sized it uses a two-UMUL8 16x8 product.

This is a valid Pareto point for game-sized data, but not a universal replacement: the dispatch makes it slower on broad 16-bit inputs.

## 12-bit bounded operands

| Candidate | Mean cycles | Gain vs composition |
|---|---:|---:|
| composition | 963.851 | baseline |
| **fused** | **795.582** | **17.46%** |
| public hybrid | 797.821 | 17.23% |
| actual-core direct | 884.449 | 8.24% |
| actual-core direct hybrid | 886.437 | 8.03% |
| width-knee hybrid | 879.736 | 8.73% |

Only 2.78% of products fit in 16 bits here, so the special small-width path rarely fires. This confirms that the game8 result is workload-specific rather than a universal speedup.

### Exact-MUL_DIV decision

The current exact family therefore has a clear split:

```text
broad/full 16-bit operands:
    public UMUL16 -> constrained 16-step bounded tail

byte/small-width operands:
    runtime width knees -> 1/2 UMUL8 -> quotient-class knees

fully inlined shipped 3xUMUL8 path:
    no current performance reason to promote
```

The general exact operation still has not demonstrated enough scene-wide value to earn a stable API slot by itself. The width-knee result is compelling for small game data, but should be validated against a real call site before promotion.

---

# 2. Prepared strict fraction for Quake64-style interpolation

Real-game invariant:

```text
0 < n < d
m = Q0.16 approximation of n/d
result = signed_component * m >> 16
```

Benchmark corpus:

```text
5,000 valid near-plane crossing ratios
10,000 signed component applications
z0          [-8192, 255]
z1          [257, 8191]
component   [-8192, 8191]
```

The comparison is the literal Quake64 `scale_nd + lerp16` arithmetic pair with its ratio save/restore overhead.

| Candidate | PREP mean | APPLY mean | PREP + 2 APPLY | Gain vs Quake | Max integer error |
|---|---:|---:|---:|---:|---:|
| actual Pareto, nearest Q16 | 695.284 | 370.573 | 1436.430 | 59.08% | 1 |
| fixed-X inline, nearest Q16 | 719.284 | 290.249 | 1299.782 | 62.97% | 1 |
| **fixed-X inline, floor Q16** | **690.476** | **290.247** | **1270.970** | **63.79%** | **1** |
| Quake64 current arithmetic pair | — | — | 3510.294 | baseline | stress max 107 |

All prepared variants had **zero prepared-contract errors**.

Accuracy against exact mathematical `trunc(component*n/d)` on this deliberately broad stress corpus:

```text
nearest Q16:
    non-zero integer error  1.51%
    mean absolute error      0.0151
    max absolute error       1

floor Q16:
    non-zero integer error  3.12%
    mean absolute error      0.0312
    max absolute error       1
```

The Quake stress error distribution is not a claim about visible error frequency in normal gameplay. It exists to compare numerical behavior under broad valid crossings.

### Nearest versus floor

Floor saves about **28.81 cycles per PREP** and ~28.81 cycles for the two-value pair, while retaining the same <=1 maximum integer-error bound. Nearest roughly halves the frequency/mean magnitude of one-unit errors.

That suggests a natural Pareto distinction rather than one universal winner:

```text
accuracy-biased prepared ratio:
    nearest Q0.16

speed-biased prepared ratio:
    floor Q0.16
```

For a default public semantic contract, nearest remains easier to justify. Floor is attractive as an explicitly documented fast tier if real game integration shows the ~29-cycle saving matters.

---

# 3. What this means for the roadmap

The corrected evidence reinforces the implementation-plan laws rather than weakening them:

1. **Do not fuse just because we can.** Broad exact direct-core fusion lost to the simpler public-kernel composition boundary.
2. **Exploit semantic information that games actually have.** Runtime byte-width and quotient knees turn ~897 cycles into ~198 cycles on the synthetic game8 distribution.
3. **Share expensive dynamic state when the workload reuses it.** Prepared interpolation cuts the demonstrated Quake arithmetic pair from ~3510 to ~1271–1300 cycles with a strict <=1 error promise.
4. **Benchmark against the real fake.** The prepared-ratio case is much stronger than comparing only against `UMUL16 + UDIV32_16`.

The strongest next gate is therefore an actual Quake64 near-clip integration using the fixed-X prepared implementation, including caller marshalling and surrounding endpoint arithmetic. That integration should decide whether the eventual public abstraction is:

```text
SCALE2_FRACTION / LERP2
```

for the two-component case, with standalone PREP/APPLY reserved for 3+ applications of the same ratio.

No stable API entry or shipped profile binary was changed by this research.
