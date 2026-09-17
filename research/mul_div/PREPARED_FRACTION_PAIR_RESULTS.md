# Fused strict-fraction SCALE2 research

**Status:** generated assembly + resident-image benchmark harness + calibrated cycle prediction. The new fused cycle point is **not yet resident-image certified**.

The strict-fraction work already reduced the demonstrated interpolation domain to:

```text
0 < n < d
m = round(n*65536/d)
result = trunc_toward_zero(component*m/65536)
```

Quake64 near clipping always applies that same ratio to **two signed components**, X and Y. That exposes another avoidable abstraction boundary.

Instead of:

```text
PREP(n,d)
APPLY(x)
APPLY(y)
```

we can express the actual compound operation:

```text
SCALE2_FRACTION(n,d,x,y)
    trusted 0<n<d

    m  = round(n*65536/d)
    zx = trunc_toward_zero(x*m/65536)
    zy = trunc_toward_zero(y*m/65536)
```

Research output mapping:

```text
X0:X1 -> signed x
Y0:Y1 -> signed y
N0:N1 -> unsigned n
D0:D1 -> unsigned d

Z0:Z1 <- scaled x
Z2:Z3 <- scaled y
```

## Why fuse the pair

The previous fast prepared state gets its speed by binding `m` into the V2 native UMUL16 X state and using `same_x`. That is fast, but a persistent PREP/APPLY API has a lifecycle problem: an unrelated multiply can rebind the native core before the next APPLY.

A fused SCALE2 call removes that problem entirely:

```text
fractional divide -> bind m -> same_x(x) -> same_x(y) -> return
```

No prepared multiplier state survives the call. The routine remains ordinary sequential/non-reentrant library code, but callers do not need a special prepared-state discipline.

This is also a better fit to the roadmap's compound-operation rule: the expensive denominator work is shared because the semantic operation actually shares it, not because the caller has to manually coordinate internal multiplier state.

## Calibrated prediction

`prepared_fraction_pair_model.py` reuses the instruction-calibrated V2 `same_x` model from `prepared_fraction_model.py`.

On the strict 5,000-edge `$C0FFEE` corpus:

```text
z0      [-8192, 255]
z1      [257, 8191]
X/Y     [-8192, 8191]
0<n<d   always
```

it predicts:

| Path | Mean cycles |
|---|---:|
| strict fraction PREP + two separate APPLY calls | **1059.7478** |
| fused strict-fraction SCALE2 | **1045.2418** |

The fused internal saving is modest, about **14.51 cycles / 1.37%**, because the important denominator sharing had already happened in PREP/APPLY.

However, the API boundary also changes from three calls to one. Including only caller JSR cost:

```text
separate: 1059.7478 + 18 = 1077.7478
fused:    1045.2418 +  6 = 1051.2418
```

So the one-call compound form saves about **26.5 cycles** at the actual call boundary while eliminating the fast-state lifecycle hazard.

Against the previously measured Quake64 stress arithmetic mean of `3510.2862` cycles, the calibrated fused prediction is about **70.22% lower** before caller marshalling. The Quake reference used the nearly identical earlier corpus whose `z1` range included `$0100`; no identity cases occurred in that measured seed, but the comparison is still kept explicitly as a reference rather than presented as a new paired measurement.

The strict APPLY model on the new corpus is:

```text
mean  182.1937 cycles
min   164
max   216
```

The first component can fall through directly into the second. Depending on its sign, that removes either 8 terminal `CLC+RTS` cycles or replaces them with a 3-cycle JMP, in addition to removing PREP's terminal return.

## Assembly candidate

`generate_prepared_fraction_pair.py` emits the actual V2 candidate. It:

1. assumes the semantic hot-path contract `0<n<d`;
2. generates rounded Q0.16 `m` with the unrolled carry-pipelined 16-step fractional divide;
3. binds `m` once into the V2 record UMUL16 state;
4. applies it to signed X and Y via `same_x`;
5. publishes both signed high-half results and returns once.

No persistent prepared state is exported.

## Resident-image gate

`benchmark_prepared_fraction_pair.py` is the authoritative next test. It compares on identical strict-fraction inputs:

```text
fraction_fast_separate
fraction_scale2_fused
quake64_current
```

and checks every output against both the rounded-Q16 prepared contract and exact mathematical `trunc(component*n/d)`.

The fused candidate must satisfy:

```text
prepared-contract errors = 0
maximum error vs exact ratio <= 1
```

before any cycle number is promoted from calibrated prediction to resident-image evidence.

## Architectural conclusion

The cycle saving over separate strict PREP/APPLY is not itself large enough to justify a new public primitive purely as a micro-optimization.

The more important benefits are:

- one semantic operation instead of a fragile prepared-state lifecycle;
- denominator work is inherently shared across the pair;
- one public call instead of three;
- the operation maps directly to clipping/interpolation workloads;
- it remains much more precise than the current reduced-ratio workaround.

That makes the fused SCALE2 form a stronger candidate for eventual **geometry/interpolation API ownership**, while standalone PREP/APPLY remains useful when a ratio is applied to three or more values or across a longer loop.

The next decision should therefore be workload-count based:

```text
1 value   -> direct/specialized ratio operation
2 values  -> fused SCALE2
3+ values -> PREP + repeated APPLY
```

This is the first MUL_DIV result that naturally produces an API family from the actual reuse count rather than from arithmetic width alone.
