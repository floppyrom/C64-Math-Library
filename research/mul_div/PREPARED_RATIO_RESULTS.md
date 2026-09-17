# Prepared signed-ratio research

**Status:** validated research Pareto family; not yet a stable API.

The real-game MUL_DIV audit identified Quake64 near-plane interpolation as the strongest current use case. A crossing edge needs the same dynamic ratio for both X and Y:

```text
delta = component_delta * (ZCLIP - z0) / (z1 - z0)
```

The current game path uses `scale_nd + lerp16`: numerator and denominator are arithmetic-shifted together until they fit signed 8-bit, then a 16x8 product is divided by an 8-bit denominator. In the actual near-clip path the original ratio is saved/restored and **`scale_nd` is run again for the second component**.

That makes this a natural prepared-state problem rather than two independent generic MUL_DIV calls.

## Candidate contract

```text
RATIO16_PREP_APPROX
    n : signed16
    d : signed16, nonzero
    requires |n| <= |d|

    sign = sign(n/d)
    m = round(|n| * 65536 / |d|)

RATIO16_APPLY_APPROX
    y : signed16

    result = trunc_toward_zero(y * sign * m / 65536)
```

`|n| == |d|` is represented as an identity/negate mode because exact Q0.16 magnitude would be 65536.

The V2 APPLY prototype binds `m` as the persistent X operand of the existing record UMUL16 core, then uses its `same_x` entry for each new `y`. That is the important fusion: the ratio multiplier stays prepared across X/Y applications instead of being rebound for every multiply.

This is a stateful research contract. Another call that rebinds the native V2 UMUL16 X operand invalidates the prepared state.

## Accuracy guarantee

Nearest Q0.16 preparation gives:

```text
|m/65536 - |n/d|| <= 1 / 131072
```

For signed16 `y`, `|y| <= 32768`, so the real-valued product error is at most 0.25. After truncation toward zero, the integer result can differ from exact `trunc(y*n/d)` by **at most one**.

So the semantic promise is explicit:

```text
signed16 y, |n|<=|d|:
    max integer error <= 1
```

This is deliberately approximate. It should not be confused with the exact general `UMULDIV16` research path.

## 6502 implementations

`generate_prepared_ratio.py` emits two V2 research points:

| Variant | PREP code | APPLY code | Total code | Strategy |
|---|---:|---:|---:|---|
| compact | 221 B | 130 B | **351 B** | 16-step loop |
| unrolled | 889 B | 130 B | **1019 B** | unrolled carry-pipelined fractional divide |

Both reuse existing division ZP `$10-$15` during PREP and the existing V2 UMUL16 state at `$21-$31`. The retained sign/mode bytes are ordinary private RAM. No new profile ZP allocation is required by the prototype.

The unrolled PREP treats `(n<<16)/d` as the same constrained 16-step geometry discovered during MUL_DIV research: because `|n|<|d|`, `n` is already a legal initial remainder and only 16 fractional quotient bits remain to be generated.

## Cycle-accurate Quake64-derived benchmark

The first paired cycle run uses:

```text
cases       5,000 edge crossings
seed        $C0FFEE
ZCLIP       $0100
z0          [-8192, 255]   ; behind
z1          [256, 8191]    ; in front
X/Y delta   [-8192, 8191]  ; ±32 world units in 8.8

n = ZCLIP-z0
d = z1-z0
```

These are valid near-plane crossings but deliberately broad stress ranges. They are **not claimed to reproduce Quake64's runtime frequency distribution**.

The prepared path is measured against the actual Quake64 arithmetic structure from commit `7c84654946a60314568b709e7e7b97467fed69df`: `scale_nd + lerp16` for X, restore the original ratio, then `scale_nd + lerp16` again for Y. The 28-cycle four-PHA/four-PLA ratio save/restore is included in the Quake pair.

The V2 APPLY uses the exact current `record_umul16_17zp.a` native core (`git blob de86a12f116e85ab8b94c3d0167b33479e9c867c`).

### Cycles excluding the external caller JSR

| Path | PREP | APPLY mean | Pair mean | Pair min | Pair max |
|---|---:|---:|---:|---:|---:|
| prepared compact | 952.231 | 216.144 | **1384.519** | 1199 | 1608 |
| prepared unrolled | **744.538** | **216.144** | **1176.827** | 1022 | 1380 |
| Quake64 current X+Y | — | — | **3510.286** | 1863 | 3896 |

The unrolled prepared pair is **66.47% lower** in this stress corpus than the current Quake arithmetic pair. The compact 351-byte point is **60.56% lower**.

Including only the external JSRs changes the means to:

```text
compact prepared   1402.519 cycles
unrolled prepared  1194.827 cycles
Quake current      3522.286 cycles
```

The result remains about **66.08% lower** for the unrolled point. Caller operand marshalling is excluded for both sides; a real integration benchmark is still required.

## Accuracy on the same 5,000 edge-pair corpus

There are 10,000 component outputs.

| Method | Non-zero error | Mean absolute error | Maximum absolute error |
|---|---:|---:|---:|
| prepared rounded Q16 | **1.57%** | **0.0157** | **1** |
| Quake `scale_nd + lerp16` | 94.33% | 16.1613 | 107 |

This does **not** mean Quake64 visibly produces large clipping errors 94% of the time in normal play. The stress corpus is intentionally broad, and the game has additional scene constraints. It shows that when broad valid crossings are exercised, reducing the dynamic ratio to signed 8-bit can lose much more precision than Q0.16 preparation.

The independent million-case arithmetic model remains useful as a wider accuracy check. For ±32 world-unit deltas it found prepared Q16 max error 1 versus max 123 for the reduced-ratio model.

## Why this passes the implementation-plan laws better

The prepared ratio now has a much stronger case than the ~816-cycle general exact `UMULDIV16` fallback:

- **dynamic:** `n`, `d`, X delta and Y delta are all runtime values;
- **reused state:** one ratio is applied to multiple values;
- **not a LUT problem:** the ratio is not fixed or enumerable cheaply;
- **not a constant-specialization problem:** numerator and denominator both vary;
- **realistic fake exists:** Quake64 uses `scale_nd + lerp16`, so we can benchmark against an actual game workaround rather than only against our own library primitives;
- **compound semantic value:** PREP moves expensive denominator/ratio work out of repeated APPLY calls;
- **explicit approximation contract:** <=1 integer error rather than an undocumented precision trade.

Wolf64 independently shows the same architectural pattern in its sprite scaling: prepare a ratio once, then advance it incrementally instead of repeatedly dividing.

## What is still missing

This is strong research evidence, but promotion would still be premature.

1. Run a corpus derived from actual Quake64 captured near-clip events, not only valid synthetic crossings.
2. Include exact caller marshalling/integration costs in a patched game build.
3. Investigate a safe prepared-state form that does not conflict with an intervening UMUL16 call, and quantify the cost versus the fast `same_x` lifecycle.
4. Test whether a fused `APPLY2` for X/Y can remove another layer of dispatch/sign overhead.
5. Decide whether the public semantic name should be ratio/interpolation-oriented rather than exposing implementation detail.
6. Investigate an exact-corrected prepared form, but only if correction remains cheaper than the current <=1 approximation and a game use actually requires exactness.

## Current decision

The research direction has changed materially:

```text
general exact UMULDIV16
    -> keep as internal/fallback research

prepared Q16 signed ratio
    -> now the leading M2 candidate for repeated dynamic ratios

small fixed/bounded ratios
    -> leave to specialized game or compound geometry kernels
```

The important result is not just a lower cycle count. We now have a candidate that beats a real game workaround **and** improves its numerical behavior on the same stress inputs, while exploiting reusable runtime state that ordinary MUL + DIV composition cannot preserve.

Machine-readable evidence: `PREPARED_RATIO_V2_5000.json`.
