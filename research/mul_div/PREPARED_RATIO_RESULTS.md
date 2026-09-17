# Prepared signed-ratio research — first model

**Status:** arithmetic/accuracy research only. No 6502 cycle certification yet.

This work follows the real-game audit of `MUL_DIV`. The strongest call site found in Quake64 is near-plane interpolation, where the same dynamic ratio is applied to both X and Y:

```text
delta = component_delta * (ZCLIP - z0) / (z1 - z0)
```

The current Quake64 path first arithmetic-shifts the numerator and denominator together until both fit signed 8-bit (`scale_nd`), then performs the reduced multiply/divide. That is a practical way to make the operation cheaper, but it deliberately discards low ratio bits before interpolation.

## Candidate semantic split

Rather than make every application pay for a full signed multiply/divide, prepare a bounded ratio once:

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

`|n| == |d|` is represented as an identity/negate flag because the exact Q0.16 magnitude is 65536.

This is **not exact MUL_DIV**. It is a deliberately bounded approximation designed for interpolation and clipping.

## Error guarantee

Let:

```text
r = |n| / |d|
m = round(r * 65536)
```

Nearest rounding gives:

```text
|m/65536 - r| <= 1 / (2*65536)
```

For any signed 16-bit `y`:

```text
|y| <= 32768
```

so the real-valued product error is at most:

```text
32768 / (2*65536) = 0.25
```

After truncation toward zero, the integer result can therefore differ from exact `trunc(y*n/d)` by **at most one**.

That is the useful semantic promise of this candidate:

```text
prepared Q16 ratio apply:
    max integer error <= 1
```

for signed16 `y` and bounded `|n|<=|d|`.

## Deterministic synthetic near-clip model

`prepared_ratio_model.py` uses valid near-plane crossings with:

```text
ZCLIP = $0100

z0 in [-8192, 255]     ; behind the near plane
z1 in [256, 8191]      ; in front

n = ZCLIP - z0
d = z1 - z0
```

These are deliberately broad stress ranges. They are **not claimed to be the measured runtime distribution of Quake64**.

Two one-million-case corpora were run.

### Full signed-16 component stress

```text
y in [-32768, 32767]
seed = $C0FFEE
cases = 1,000,000
```

| Method | Non-zero error | Mean absolute error | Maximum absolute error |
|---|---:|---:|---:|
| Quake-style `scale_nd` reduced ratio | 98.1766% | 64.513702 | 485 |
| Rounded prepared Q16 ratio | **6.2308%** | **0.062308** | **1** |

### ±32 world-unit 8.8 component stress

```text
y in [-8192, 8191]
seed = $C0FFEF
cases = 1,000,000
```

| Method | Non-zero error | Mean absolute error | Maximum absolute error |
|---|---:|---:|---:|
| Quake-style `scale_nd` reduced ratio | 94.4709% | 16.115774 | 123 |
| Rounded prepared Q16 ratio | **1.5783%** | **0.015783** | **1** |

The large `scale_nd` errors are not a claim that Quake64 is visibly wrong in normal play. The corpus intentionally stresses broad depth/component ranges, and the game has other clipping constraints. The result shows something narrower and useful: reducing a 16-bit dynamic ratio to signed 8-bit can discard much more precision than a prepared Q16 representation.

## Why this is interesting for the roadmap

This candidate passes the Hard-to-Fake test more cleanly than the current general `UMULDIV16`:

- both ratio inputs are dynamic;
- the same ratio is reused for multiple dynamic values;
- a small LUT cannot encode all cases;
- fixed-constant specialization does not apply;
- offline precomputation does not apply;
- the existing game uses approximation specifically to avoid the full operation.

It also gives us a meaningful semantic trade:

```text
general UMULDIV16
    exact, expensive per application

prepared Q16 ratio
    one prepare cost
    much cheaper apply target
    guaranteed <= 1 integer error
```

## Performance target

No cycle result is claimed yet.

The current V2 direct bounded `UMULDIV16` research path is about 816 cycles on its broad corpus. Two independent applications therefore cost roughly 1632 cycles before any ratio sharing.

For a prepared ratio to be worthwhile on a two-component interpolation, a useful target is:

```text
PREP + 2*APPLY < ~1632 cycles
```

The existing V2 signed 16x16 multiply is about 252 cycles on its canonical corpus, so an APPLY based on a profile-native high-half multiply looks plausible. A dedicated high-half signed×unsigned kernel may do better, but this must be measured rather than assumed.

The more important comparison is **not** against two general MUL_DIV calls. It is against Quake64's existing `scale_nd + lerp16` implementation on real clipping inputs. That is the next benchmark gate.

## Next implementation pass

1. Implement a 16-step fractional `RATIO16_PREP` prototype that generates rounded Q0.16 state directly from `|n|/|d|`.
2. Implement a V2 direct-core signed16 × unsigned-Q16 high-half APPLY path.
3. Measure PREP once + APPLY twice.
4. Build a Quake64-derived clipping corpus and compare:
   - current `scale_nd + lerp16`,
   - exact direct signed MUL_DIV,
   - prepared Q16 approximate,
   - optionally an exact-corrected prepared form.
5. Keep this out of the stable API until the realistic-alternative benchmark passes.

The important result is therefore not that generic MUL_DIV is ready. It is that the real-game audit has exposed a **more promising prepared-ratio primitive with a strong, explicit error bound**.
