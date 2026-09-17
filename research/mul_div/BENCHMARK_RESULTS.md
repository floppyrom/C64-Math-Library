# MUL_DIV resident-image benchmark results

**Status:** research evidence, not yet a stable API certification.

These results use the shipped **V2 Pareto-Fast** resident image, initialized once outside timing, and the cycle-accurate `tools/mini6502.py` model. Every implementation was run on the **same inputs** and checked against exact Python integer `divmod(a*b,d)` semantics with the bounded 16-bit quotient contract.

Resident PRG SHA-256:

```text
10af446bd1f49bcf02f9529d7944881d85f0e9b8dec2712638e306b0fab72828
```

## Candidates

```text
composed
    public UMUL16 -> copy -> public UDIV32_16 -> copy

fused
    public UMUL16 -> constrained 16-step bounded tail

hybrid
    public UMUL16 -> native UDIV16 if product fits 16 bits
    otherwise constrained tail

direct
    native V2 UMUL16 -> consume live product directly in constrained tail

direct_hybrid
    native V2 UMUL16
    -> direct q=0/q=1 exits for 16-bit products
    -> native UDIV16 for remaining 16-bit-product cases
    -> constrained tail when product.high16 != 0
```

The direct variants rely on the initialized V2 native UMUL16 contract:

```text
entry       $53EC
X low bind  $21
X high bind $29
Y high SMC  $541A
product     low=$31, byte1=X, byte2=A, byte3=Y
```

## Structured edge suite

Cartesian product of 13 edge values for `a`, `b`, `d`: **2,197 cases**.

| Candidate | Mean cycles | Min | Max | Errors |
|---|---:|---:|---:|---:|
| composed | 1117.352 | 462 | 2092 | 0 |
| fused | 731.599 | 265 | 1189 | 0 |
| hybrid | 639.455 | 279 | 1206 | 0 |
| direct | 672.844 | **48** | 1141 | 0 |
| direct_hybrid | **565.961** | **48** | 1206 | 0 |

The 48-cycle minimum is the early divide-by-zero exit, now checked before multiplication.

## 5,000-case deterministic corpora

Seed family starts at `$C0FFEE`.

### Uniform bounded 16-bit quotient

Only **0.06%** of products fit in 16 bits.

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 1027.605 | 885 | 1189 | 0 | baseline |
| fused | 859.405 | 717 | 1021 | 0 | 16.37% |
| hybrid | 871.733 | 336 | 1033 | 0 | 15.17% |
| direct | **815.893** | 674 | 977 | 0 | **20.60%** |
| direct_hybrid | 823.931 | 256 | 985 | 0 | 19.82% |

The direct handoff saves about **43.5 cycles** beyond the first fused version. The hybrid remains slightly slower here because the small-product branch almost never fires.

### Mixed unrestricted uniform 16-bit operands

**74.16%** of cases satisfy the bounded 16-bit quotient contract.

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 1055.749 | 891 | 2095 | 0 | baseline |
| fused | 718.766 | 299 | 1029 | 0 | 31.92% |
| hybrid | 731.481 | 313 | 1041 | 0 | 30.71% |
| direct | **675.137** | 255 | 985 | 0 | **36.05%** |
| direct_hybrid | 683.086 | 262 | 994 | 0 | 35.30% |

The large win partly comes from rejecting quotient overflow after the product high-word test instead of paying for a full public 32/16 division first.

### `game8`: byte-sized multiplicands

All products fit in 16 bits, and the quotient distribution is strongly biased toward the tiny classes:

```text
q == 0     74.30%
q <= 1     86.58%
q <= 255   99.94%
```

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 897.260 | 883 | 1193 | 0 | baseline |
| fused | 729.266 | 715 | 1027 | 0 | 18.72% |
| hybrid | 362.085 | 334 | 1161 | 0 | 59.65% |
| direct | 686.076 | 672 | 979 | 0 | 23.54% |
| direct_hybrid | **294.563** | 254 | 1161 | 0 | **67.17%** |

The direct q=0/q=1 exits matter substantially here: the earlier direct-hybrid version averaged 336.085 cycles; specializing those two dominant quotient classes removes another **41.5 cycles**.

### `game12_bounded`: 12-bit multiplicands

Only **2.78%** of products fit in 16 bits, though **74.60%** of quotients are <=255.

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 963.851 | 883 | 1205 | 0 | baseline |
| fused | 795.582 | 715 | 1039 | 0 | 17.46% |
| hybrid | 797.821 | 334 | 1054 | 0 | 17.23% |
| direct | 752.297 | 672 | 992 | 0 | 21.95% |
| direct_hybrid | **749.629** | 254 | 998 | 0 | **22.23%** |

The hybrid is nearly neutral on the broad path and only slightly better overall because few products fit in 16 bits.

## Current interpretation

The Pareto split is clearer now:

```text
broad/full 16-bit workloads
    -> direct native UMUL16 + constrained 16-step tail

byte/small-product workloads
    -> direct native UMUL16
       + q=0/q=1 direct exits
       + native UDIV16 fallback
       + constrained-tail fallback
```

The main architectural finding is that **intermediate representation matters**. A public-call composition is not a fair lower bound for a fused routine: keeping the native UMUL16 product live removes another ~43 cycles on broad inputs, and exploiting the quotient distribution can remove hundreds more on small-coordinate workloads.

## Not yet proven

- No stable ABI has been selected.
- No V1/V5 direct-core equivalent is certified.
- The V2 direct forms require initialized native UMUL16 state.
- These 5,000-case runs are development evidence, not final canonical certification.
- Signed and prepared-divisor variants are separate research tasks.
- No claim is made that the current kernels are globally optimal 6502 MUL_DIV implementations.

Next research should attack the general path itself: deeper multiply/divide state sharing and a width/quotient-class strategy that can beat the fixed 16-step tail without hurting full-width workloads.
