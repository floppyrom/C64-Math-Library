# M2 MUL_DIV / prepared-ratio gate decision — 2026-09-17

**Decision status:** the research has produced a credible M2 candidate, but the stable API is **not frozen yet**.

The evidence now supports a sharper conclusion than “add a fast `(a*b)/d` routine.”

> The M2 capability that best satisfies the implementation-plan laws is **prepared dynamic fractional scaling**, not a universal full-width `MUL_DIV` entry.

The exact general `UMULDIV16` work remains useful as a fallback/research primitive. The prepared strict-fraction path has the stronger case for eventual API promotion because it beats a real game workaround on the operation the game was forced to approximate.

---

## 1. What survives the gate

### A. Exact bounded `UMULDIV16`: keep, but do not promote yet

For broad V2 unsigned 16-bit inputs the best current exact general route is still:

```text
public UMUL16
    -> product-aware 16-step bounded divide tail
```

Measured on the 5,000-case bounded-uniform corpus:

```text
public UMUL16 + public UDIV32_16 composition   1027.605 cycles
fused bounded tail                              859.405 cycles
                                                  16.37% lower
```

That is a real improvement, but the real-game audits did not find a sufficiently strong broad full-width call site to justify a stable API slot by this result alone.

The attempt to inline the actually shipped V2 3xUMUL8 core was slower, which is an important negative result: **crossing an API boundary is not automatically wasteful if the selected component kernel is already the correct Pareto point.**

### B. Runtime small-width exact path: retain as a specialized Pareto point

The width-knee exact path is excellent when runtime data are genuinely small:

```text
synthetic game8 corpus
composition          897.260 cycles
width-knee hybrid    197.820 cycles
                     77.95% lower
```

The path detects byte-width operands at runtime and uses one/two UMUL8 operations plus quotient knees. It is not a constant benchmark trick.

However, Wolf64 gives us the counterexample required by the implementation plan: its real projection helper has a constant multiplier, an output known to be <=20, and a divider explicitly capped at 40. On its exhaustive visible domain:

```text
Wolf64 current bounded helper    577.181 cycles
V2 width-hybrid replacement     1048.155 cycles
```

The generic library replacement is **81.6% slower** there.

So the law is working: keep the width-knee technology, but do not claim that every small `(a*b)/d` expression should use it.

---

## 2. Prepared strict fraction passes the hard-to-fake gate

Quake64 near-plane clipping supplies the strong real workload:

```text
n = ZCLIP - z_behind
d = z_front - z_behind

0 < n < d

clipped_x = x0 + trunc((x1-x0) * n / d)
clipped_y = y0 + trunc((y1-y0) * n / d)
```

The ratio is dynamic and is reused for two independent signed values. A fixed LUT, constant specialization or offline precomputation cannot replace it.

Quake64 currently makes the operation affordable by repeatedly running `scale_nd` until numerator and denominator fit signed bytes, then using `lerp16`. That is exactly the kind of real “fake” the roadmap says to benchmark against.

### V2 library-style prepared path

On a 5,000-edge standalone integration harness that includes ratio formation, X/Y delta formation, ratio application, endpoint accumulation and near-Z writeback:

| Path | Mean cycles | Max endpoint error vs exact |
|---|---:|---:|
| Quake64 current | **3703.020** | stress max 120 |
| V2 prepared nearest Q16 | **1487.351** | **1** |
| V2 prepared floor Q16 | **1458.712** | **1** |

The nearest path is **59.83% lower** than the current Quake arithmetic integration; floor is **60.61% lower**.

The broad stress-corpus error distribution is not a claim about visible Quake64 error frequency in normal play. It demonstrates that the prepared path is both substantially cheaper and numerically much tighter on valid dynamic crossings.

This is the first M2 result that clearly satisfies all of the following simultaneously:

```text
dynamic runtime inputs          yes
ratio reused                    yes
fixed LUT inadequate            yes
constant specialization         no
real game workaround exists     yes
realistic alternative measured  yes
meaningful cycle reduction      yes
explicit accuracy contract      yes
```

---

## 3. Game-native ceiling: Quake's own table bank can do even better

A Quake-native variant reuses the game's existing `$F000-$F7FF` quarter-square tables and existing math scratch, preparing fixed multipliers directly into writable code.

On the same 5,000-edge near-clip integration corpus:

| Path | Mean cycles | Min | Max | Max error | Gain vs current |
|---|---:|---:|---:|---:|---:|
| Quake64 current | 3703.020 | 2220 | 4104 | 120 stress | baseline |
| Quake-native nearest | **1373.542** | 1209 | 1550 | **1** | **62.91%** |
| Quake-native floor | **1347.906** | 1189 | 1524 | **1** | **63.60%** |

Evidence provenance:

```text
GitHub Actions run     35254482690
head commit            c4d136be140fd906b819bc0c466cec2a46b4aa86
artifact               mul-div-profile-native-results
artifact digest        sha256:487c424dc1d5b0071b99b3eb13644e3c6e667d2732d4113ce9621c58e1aaa203
Quake64 source         7c84654946a60314568b709e7e7b97467fed69df
cases                  5,000 edges / 10,000 component outputs
prepared errors        0
```

Machine-readable copy: `QUAKE64_NEARCLIP_SMC_5000.json`.

This game-native variant is **not** proposed as the portable library implementation. Its value is to establish the achievable ceiling when the library idea is specialized to an actual engine's existing tables and memory architecture.

---

## 4. The one-call `SCALE2` abstraction currently loses

We explicitly tested the apparently cleaner compound operation:

```text
SCALE2_FRACTION(n,d,x,y)
```

against PREP once + APPLY twice.

On the profile-native V2 integration:

```text
nearest:
    PREP + APPLY + APPLY    1487.351
    fused SCALE2            1507.836
    SCALE2 is 1.38% slower

floor:
    PREP + APPLY + APPLY    1458.712
    fused SCALE2            1480.191
    SCALE2 is 1.47% slower
```

The reason is architectural rather than semantic: the shared fixed-X multiply helper and its internal call/marshalling costs outweigh the call-boundary saving.

Therefore:

> **Do not promote the current SCALE2 implementation just because it looks like the cleaner API.**

A compound API earns its place only if its implementation also wins or if it materially simplifies a broader algorithm. At present, PREP/APPLY is the better Pareto point.

---

## 5. Accuracy tier decision

Two Q0.16 preparation policies remain useful:

```text
nearest Q16
    fewer one-unit errors
    preferred default semantic tier

floor Q16
    ~26-29 cycles cheaper in current prepared implementations
    same observed/proved maximum integer error <=1
    higher frequency of one-unit errors
```

On the integrated Quake stress corpus:

```text
nearest: nonzero endpoint error 1.59%, mean abs 0.0159, max 1
floor:   nonzero endpoint error 2.84%, mean abs 0.0284, max 1
```

The default API candidate should therefore remain **nearest**, with floor retained as an explicitly speed-biased tier if later integration shows the ~2% PREP saving matters.

---

## 6. Candidate API shape

The research now supports a stateful semantic pair more strongly than a public generic MUL_DIV:

```text
MATH_FRAC16_PREP
    n : uint16
    d : uint16
    semantic hot domain: 0 < n < d

    prepares a private approximation of n/d
    default tier: nearest Q0.16

MATH_FRAC16_APPLY_S16
    y : signed16
    -> signed16 trunc-toward-zero scaled result

    accuracy contract:
        differs from exact trunc(y*n/d) by at most 1
```

For a stable public entry, the PREP wrapper should either validate the domain and return C=1 on invalid input, or the precondition must be made unambiguously part of the API contract. The internal hot entry can remain trusted.

The profile-native fixed-X implementation stores prepared information in its own writable code/state rather than relying on the transient binding of an unrelated public multiply routine. That makes it a much healthier basis for a persistent PREP/APPLY API than the superseded record-core experiment.

---

## 7. Resource / placement gate

The Quake-native kernels assemble to:

```text
nearest   1033 bytes
floor     1007 bytes
```

Quake64's current memory map places the next free GAME byte at `$9546`, with the heap ceiling at `$C000`. The documented tightest level is E1M2 with 2,980 bytes of current heap slack.

A contiguous ~1.0 KiB candidate appended to GAME therefore appears feasible, leaving roughly:

```text
nearest   ~1947 bytes tightest-level slack
floor     ~1973 bytes tightest-level slack
```

`quake64_smc_placement.py` was added to turn this arithmetic into an assembler-backed layout check. A full Quake build remains the authoritative gate.

---

## 8. M2 decision matrix

| Candidate | Hard to fake? | Beats realistic game alternative? | Current decision |
|---|---|---|---|
| Exact broad `UMULDIV16` | yes in abstract | not yet demonstrated | **retain research/fallback** |
| Exact width-knee MUL_DIV | workload-dependent | loses badly in audited Wolf64 projection | **specialized research only** |
| V2 prepared strict fraction | **yes** | **yes, ~60% in near-clip integration** | **promotion candidate** |
| Quake-native prepared fraction | **yes** | **yes, ~63.6%** | **game-integration proof / ceiling** |
| Current fused `SCALE2` | yes | yes vs Quake, but loses to PREP/APPLY | **do not promote current implementation** |
| Repeated fixed/static ratio | no | LUT/precompute wins | **do not use MUL_DIV** |

---

## 9. Remaining promotion gate

M2 should be considered **research-complete but not release-complete** when the following are done:

1. append/relocate the Quake-native prototype into a real Quake64 GAME build without violating the heap gate;
2. patch `.near0` and `.near1` and verify game behavior in the actual build;
3. measure a representative scene with normal IRQ/VIC/SID activity rather than only the arithmetic region;
4. decide stable checked PREP semantics and reserve final state/code locations in the C64 Math Library profiles;
5. reproduce the chosen library implementation on V1/V5 or explicitly make it a V2+ optional capability;
6. only then add public JMP slots and release performance rows.

Until then, **no stable API or shipped profile binary should change**.

Once that gate is passed, the roadmap should move on to M4 dynamic geometry rather than spending more time shaving generic `UMULDIV16` microbenchmarks.
