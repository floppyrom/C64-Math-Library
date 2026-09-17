# MUL_DIV resident-image benchmark results

**Status:** research evidence, not yet a stable API certification.

> **2026-09-17 correction:** the historical V2 `direct` and `direct_hybrid` candidates in the original run assumed the standalone `record_umul16_17zp.a` ABI was installed at `$53EC/$5400`. Shipped V2 actually installs `pareto_umul16.a`, the integrated 3xUMUL8 kernel, at `$5400`. The old direct/direct-hybrid columns are therefore **superseded and must not be cited as shipped-V2 evidence**. See `DIRECT_CORE_PROFILE_CORRECTION_2026-09-17.md`. The `composed`, `fused`, and `hybrid` paths below use genuine shipped interfaces and remain the valid baseline set.

The original run used the shipped **V2 Pareto-Fast** resident image, initialized once outside timing, and the cycle-accurate `tools/mini6502.py` model. Every implementation was run on the same inputs and checked against exact Python integer `divmod(a*b,d)` semantics with the bounded 16-bit quotient contract.

Resident PRG SHA-256 recorded by the historical run:

```text
10af446bd1f49bcf02f9529d7944881d85f0e9b8dec2712638e306b0fab72828
```

## Source/profile-consistent candidates

```text
composed
    public UMUL16 -> copy -> public UDIV32_16 -> copy

fused
    public UMUL16 -> constrained 16-step bounded tail

hybrid
    public UMUL16 -> native UDIV16 if product fits 16 bits
    otherwise constrained tail
```

The corrected profile-native direct replacements now live in:

```text
generate_umuldiv16_pareto.py
benchmark_pareto_direct.py
```

They inline the actual shipped V2 3xUMUL8 construction. Their results are not inserted into this document until the new harness is run.

## Structured edge suite

Cartesian product of 13 edge values for `a`, `b`, `d`: **2,197 cases**.

| Candidate | Mean cycles | Min | Max | Errors |
|---|---:|---:|---:|---:|
| composed | 1117.352 | 462 | 2092 | 0 |
| fused | 731.599 | **265** | 1189 | 0 |
| hybrid | **639.455** | 279 | 1206 | 0 |

## 5,000-case deterministic corpora

Seed family starts at `$C0FFEE`.

### Uniform bounded 16-bit quotient

Only **0.06%** of products fit in 16 bits.

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 1027.605 | 885 | 1189 | 0 | baseline |
| fused | **859.405** | 717 | 1021 | 0 | **16.37%** |
| hybrid | 871.733 | 336 | 1033 | 0 | 15.17% |

The public hybrid is slightly slower than fused here because the small-product branch almost never fires.

### Mixed unrestricted uniform 16-bit operands

**74.16%** of cases satisfy the bounded 16-bit quotient contract.

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 1055.749 | 891 | 2095 | 0 | baseline |
| fused | **718.766** | 299 | 1029 | 0 | **31.92%** |
| hybrid | 731.481 | 313 | 1041 | 0 | 30.71% |

The large gain over public composition partly comes from rejecting quotient overflow after the product high-word test instead of always paying for a full public 32/16 division.

### `game8`: byte-sized multiplicands

All products fit in 16 bits, and the quotient distribution is strongly biased toward tiny classes:

```text
q == 0     74.30%
q <= 1     86.58%
q <= 255   99.94%
```

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 897.260 | 883 | 1193 | 0 | baseline |
| fused | 729.266 | 715 | 1027 | 0 | 18.72% |
| hybrid | **362.085** | **334** | 1161 | 0 | **59.65%** |

This valid result remains important: a q=0/q=1-aware profile-native direct hybrid is worth researching because the workload itself is heavily concentrated in those quotient classes.

### `game12_bounded`: 12-bit multiplicands

Only **2.78%** of products fit in 16 bits, though **74.60%** of quotients are <=255.

| Candidate | Mean | Min | Max | Errors | Gain vs composed |
|---|---:|---:|---:|---:|---:|
| composed | 963.851 | 883 | 1205 | 0 | baseline |
| fused | **795.582** | 715 | 1039 | 0 | **17.46%** |
| hybrid | 797.821 | 334 | 1054 | 0 | 17.23% |

The hybrid is nearly neutral on the broad path because few products fit in 16 bits.

## Superseded historical direct columns

For reproducibility, the original run also emitted the following values. They are retained here only so old notes/commits can be interpreted. **Do not use these as V2 resident performance claims.**

| Workload | Historical `direct` | Historical `direct_hybrid` |
|---|---:|---:|
| edge suite | 672.844 | 565.961 |
| bounded uniform | 815.893 | 823.931 |
| mixed uniform | 675.137 | 683.086 |
| `game8` | 686.076 | 294.563 |
| `game12_bounded` | 752.297 | 749.629 |

The corresponding generated wrappers targeted the wrong internal ABI for the image they were patched into. Zero arithmetic mismatches from that run do not repair the provenance mismatch.

## Corrected direct-core architecture

The new `pareto_direct` generator inlines the actual `pareto_umul16.a` construction and deliberately places final product bytes directly into divide state:

```text
$10 = product byte0 / quotient pipeline low
$11 = product byte1 / quotient pipeline high
$16 = product byte2 / initial remainder low
A   = product byte3 / initial remainder high
```

The latest optimization keeps bytes 0/1 in their existing `$10/$11` locations instead of copying them into a second quotient pair. The corrected hybrid saves byte3 only when it needs to dispatch the 16-bit-product knees, then uses the actual V2 UDIV16 ABI at `$10-$17` for the remaining small-product cases.

## Current interpretation

The profile-independent result still supports a workload split:

```text
broad/full 16-bit workloads
    -> public multiply + constrained bounded tail is already useful

small-product / tiny-quotient workloads
    -> explicit quotient-class knees can be dramatically better

profile-native direct path
    -> must be derived from the implementation actually installed in that profile
```

The architectural lesson remains that intermediate representation matters, but the amount saved by a direct handoff must now be remeasured against the real Pareto 3xUMUL8 core.

## Not yet proven

- Corrected `pareto_direct` and `pareto_direct_hybrid` have not yet been executed in the resident-image harness in this environment.
- No stable ABI has been selected.
- No V1/V5 direct-core equivalent is certified.
- These 5,000-case baseline runs are development evidence, not final canonical certification.
- Signed and prepared-divisor variants are separate research tasks.
- No claim is made that the current kernels are globally optimal 6502 MUL_DIV implementations.

Next gate: run `benchmark_pareto_direct.py`, preserve the machine-readable result, and only then repopulate the direct columns.
