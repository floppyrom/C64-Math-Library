# MUL_DIV resident-image benchmark results

**Status:** research evidence, not yet a stable API certification.

These results use the shipped **V2 Pareto-Fast** resident image, initialized once outside timing, and the cycle-accurate `tools/mini6502.py` model. Every compared implementation was run on the **same input cases** and checked against Python integer `divmod(a*b,d)` semantics with the bounded 16-bit quotient contract.

The V2 resident image used for this run has SHA-256:

```text
10af446bd1f49bcf02f9529d7944881d85f0e9b8dec2712638e306b0fab72828
```

## Candidates

```text
composed
    public MATH_UMUL16
    -> copy product Z32 -> N32
    -> public MATH_UDIV32_16
    -> copy Q/R -> Z

fused
    public MATH_UMUL16
    -> product-aware bounded 16-step divide tail

hybrid
    public MATH_UMUL16
    -> native V2 UDIV16 if product fits 16 bits
    -> otherwise bounded 16-step tail

direct
    call the native V2 UMUL16 core directly
    -> consume its live product result directly into the bounded tail
    -> avoid publishing/reloading the complete product through public Z32

direct_hybrid
    direct native V2 UMUL16
    -> native V2 UDIV16 when the product fits 16 bits
    -> otherwise direct bounded tail
```

The direct candidates rely on the current initialized V2 native UMUL16 contract:

```text
entry       $53EC
X low bind  $21
X high bind $29
Y high SMC  $541A
product     low=$31, byte1=X, byte2=A, byte3=Y
```

They are therefore profile-specific research kernels at this stage, not portable public wrappers.

## Structured edge suite

The edge suite is the Cartesian product of:

```text
0, 1, 2, 3, 127, 128, 255, 256, 257,
32767, 32768, 65534, 65535
```

for `a`, `b`, and `d`: **2,197 cases**.

| Candidate | Mean cycles | Min | Max | Errors |
|---|---:|---:|---:|---:|
| composed | 1117.352 | 462 | 2092 | 0 |
| fused | 731.599 | 265 | 1189 | 0 |
| hybrid | 639.455 | 279 | 1206 | 0 |
| direct | 689.383 | 247 | 1143 | 0 |
| direct_hybrid | **604.096** | 255 | 1180 | 0 |

## 5,000-case deterministic corpora

Seed family starts at `$C0FFEE`.

### Uniform bounded 16-bit quotient

Only **0.06%** of products fit in 16 bits, so this corpus strongly favors the general bounded path rather than the small-product shortcut.

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 1027.605 | 885 | 1189 | 0 | baseline |
| fused | 859.405 | 717 | 1021 | 0 | 16.37% |
| hybrid | 871.733 | 336 | 1033 | 0 | 15.17% |
| direct | **815.900** | 674 | 977 | 0 | **20.60%** |
| direct_hybrid | 824.427 | 310 | 986 | 0 | 19.77% |

This is the clearest evidence that consuming the native multiply result directly matters. The direct-core candidate saves about **43.5 cycles** over the first fused version before any deeper algebraic fusion has been attempted.

### Mixed unrestricted uniform 16-bit operands

This corpus includes overflow and divide-by-zero handling. **74.16%** of cases satisfy the bounded 16-bit quotient contract.

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 1055.749 | 891 | 2095 | 0 | baseline |
| fused | 718.766 | 299 | 1029 | 0 | 31.92% |
| hybrid | 731.481 | 313 | 1041 | 0 | 30.71% |
| direct | **675.142** | 255 | 985 | 0 | **36.05%** |
| direct_hybrid | 683.492 | 263 | 993 | 0 | 35.26% |

The large gain here partly comes from rejecting bounded-overflow cases after the product high-word comparison instead of paying for a complete public 32/16 division and only then discovering that the quotient is too wide.

### `game8`: byte-sized multiplicands

All products fit in 16 bits. The quotient distribution is strongly game-like for this synthetic workload:

```text
q == 0     74.30%
q <= 1     86.58%
q <= 255   99.94%
```

That distribution is exactly where the resident V2 UDIV16 kernel's q=0/q=1 specialization becomes valuable.

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 897.260 | 883 | 1193 | 0 | baseline |
| fused | 729.266 | 715 | 1027 | 0 | 18.72% |
| hybrid | 362.085 | 334 | 1161 | 0 | 59.65% |
| direct | 686.082 | 672 | 981 | 0 | 23.54% |
| direct_hybrid | **336.085** | 308 | 1135 | 0 | **62.54%** |

This is the strongest result so far: for byte/small-coordinate workloads, a single universal 16-step tail leaves a lot of performance on the table. The direct hybrid reduces the average from about **897 cycles to 336 cycles**.

### `game12_bounded`: 12-bit multiplicands

Here only **2.78%** of products fit in 16 bits, but **74.60%** of quotients are still <=255.

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 963.851 | 883 | 1205 | 0 | baseline |
| fused | 795.582 | 715 | 1039 | 0 | 17.46% |
| hybrid | 797.821 | 334 | 1054 | 0 | 17.23% |
| direct | 752.303 | 672 | 994 | 0 | 21.95% |
| direct_hybrid | **751.070** | 308 | 1002 | 0 | **22.08%** |

The small-product dispatch is almost neutral here because few products fit in 16 bits. That is useful evidence against making the hybrid the only implementation.

## Current interpretation

The first useful Pareto split is now clear:

```text
full/broad 16-bit workloads
    -> direct native UMUL16 + constrained 16-step tail

byte/small-product workloads
    -> direct native UMUL16 + native UDIV16 fast path
       with constrained-tail fallback
```

The direct-core result also changes the research target. A final `MATH_UMULDIV16` should not simply call public `MATH_UMUL16`; at least on V2 it should bind directly to the selected multiply core and keep intermediate bytes live.

## What is not yet proven

- No stable ABI has been selected.
- No V1/V5 direct-core equivalent has been certified.
- The direct V2 candidates assume initialized native UMUL16 state.
- The 5,000-case runs are strong development evidence, not final exhaustive/canonical certification.
- No claim is made that these are optimal 6502 MUL_DIV implementations.
- Signed and prepared-divisor forms remain separate research tasks.

The next optimization pass should investigate whether the multiply and divide can share still more state than the direct handoff already removes, and whether quotient-class prechecks can beat a fixed 16-step tail on the general bounded path.
