# MUL_DIV real-game audit — 2026-09-17

This audit applies the project's **Hard-to-Fake** and **benchmark-against-the-fake** rules before promoting `UMULDIV16` into the stable API.

Source snapshots audited:

```text
Quake64             Kweepa/Quake64 @ 7c84654946a60314568b709e7e7b97467fed69df
Steel Ranger demo   cadaver/steelranger-demo @ fa99196cb94be80df12bd295adcce7567e860e44
```

## Executive conclusion

The audit **does not justify promoting the current ~816-cycle general V2 `UMULDIV16` as a stable API yet**.

It does justify continuing the MUL_DIV family, but with a more use-case-driven split:

```text
1. Keep general bounded UMULDIV16 as an internal/fallback research primitive.

2. Prioritize prepared/shared-denominator MUL_DIV for repeated ratios.

3. Research signed mixed-width interpolation forms for clipping/geometry.

4. Let higher-level geometry kernels absorb tiny specialized MUL_DIV work
   when the arithmetic exists only as an implementation detail.
```

That is more consistent with the roadmap than publishing a generic primitive simply because it is faster than composition.

---

# 1. Quake64: ramp height

`src/world.asm` computes a walkable ramp height every floor update as:

```text
height = slope_y + (local_8.8 * sy) / run
```

The implementation forms the 24-bit product with two `umul8j` calls and divides by `run` with `div24u8`.

At first sight this looks like an ideal `MUL_DIV` replacement. It is **not** a strong general-MUL_DIV justification.

Why:

- `local` is dynamic player position;
- `sy` is slope geometry;
- `run` is `slope_sx` or `slope_sz`, also slope geometry;
- for a given map slope, `sy/run` is therefore static.

A game can precompute a fixed-point slope coefficient offline or when the map is loaded, then update height with a multiply/shift. That is exactly the kind of fixed-data specialization the Hard-to-Fake rule says we should respect.

### Decision

```text
General UMULDIV16 for ramp height: REJECT as primary library justification.
Prepared/precomputed slope coefficient: preferred.
```

The current game-specific form may still be best depending on memory/layout, but this call site does not prove the need for a general runtime MUL_DIV.

---

# 2. Quake64: perspective projection

`src/cube.asm` does **not** divide X and Y independently by Z.

For each distinct XZ column it computes a reciprocal-like projection factor once:

```text
inv = (FOCAL << 16) / (z >> k)
```

then reuses it for X and Y with a high-half multiply:

```text
proj_x = x * inv >> (16+k)
proj_y = y * inv >> (16+k)
```

It also caches the reciprocal and projected X for vertical pairs sharing the same Z.

This is an excellent example of the roadmap law in action: **two generic MUL_DIV calls would be the wrong abstraction**. Repeated denominator work wants reciprocal/prepared state.

### Decision

```text
Two UMULDIV calls per projected point: REJECT.
Prepared reciprocal / shared denominator: STRONG PASS.
```

This is direct evidence that `RECIP/PREP_DIVISOR` should remain ahead of a generic repeated `MUL_DIV` in projection workloads.

---

# 3. Quake64: near-plane interpolation

This is the strongest real MUL_DIV use case found so far.

When an edge crosses the near plane, `src/cube.asm` computes dynamic interpolation deltas for X and Y. For each component it effectively needs:

```text
delta = component_delta * (ZCLIP - z0) / (z1 - z0)
```

All three quantities are dynamic runtime values.

The current path is:

```text
scale_nd
lerp16
```

`scale_nd` arithmetic-shifts numerator and denominator together until both fit signed 8-bit. `lerp16` then multiplies a signed 16-bit component delta by the reduced signed 8-bit numerator and divides the 24-bit product by the reduced 8-bit denominator.

This is a deliberate practical approximation: scaling the ratio operands loses low bits before division.

The same `(n,d)` pair is then reused for **both X and Y**. The code explicitly saves/restores `n` and `d` around the first interpolation before applying the second.

That matters for API design. The most useful library operation is probably not:

```text
SMULDIV16(y, n, d)
SMULDIV16(x, n, d)
```

but something closer to:

```text
PREP_RATIO16(n, d)
APPLY_RATIO16(dx)
APPLY_RATIO16(dy)
```

or a fused pair form:

```text
LERP2_16(dx, dy, n, d)
```

The former is more general and naturally connects to the planned prepared-divisor/reciprocal work.

### Hard-to-Fake result

- small LUT: no, input ratio is arbitrary runtime geometry;
- shifts/adds: only by accepting approximation after dynamic normalization;
- fixed constant specialization: no;
- offline precomputation: no;
- approximation: currently used, but source comments document clipping failures from overly aggressive scaling approaches;
- game-specific trick: the current `scale_nd + lerp16` path is exactly such a trick, but it trades precision for speed.

### Decision

```text
Dynamic clipping ratio: STRONG PASS.
Single-shot generic UMULDIV16: useful but probably not the final abstraction.
Prepared/shared-denominator signed ratio: HIGHEST-PRIORITY MUL_DIV follow-up.
```

---

# 4. Quake64: segment/box intersection t

`src/util.asm` computes a face intersection parameter:

```text
t_Q7 = (plane - A) * 127 / (B - A)
```

All geometric differences are runtime signed bytes. The current `lerpdv` implementation uses log/antilog tables and clamps to ±127.

This definitely passes the dynamic-input side of the Hard-to-Fake test, but it does **not** imply that 16-bit general MUL_DIV is the correct replacement:

- multiplier `127` is fixed;
- inputs are only signed 8-bit;
- output is Q7 and bounded;
- this arithmetic is an internal step of `line_hit_box` / segment-vs-AABB.

A dedicated exact mixed-width kernel could be dramatically cheaper than full 16×16/16, and the roadmap's compound-operation rule suggests that ultimately `SEGMENT_AABB` should own this arithmetic rather than exposing a low-level helper solely for this call site.

### Decision

```text
Full UMULDIV16: too general/heavy for this site.
Specialized signed 8-bit/Q7 arithmetic: research-worthy.
Public low-level API: defer.
Higher-level SEGMENT_AABB: preferred eventual owner.
```

---

# 5. Steel Ranger demo

The current Steel Ranger demo source has general `MulU` and `DivU` helpers, but the examined gameplay uses are dominated by exactly the cases our roadmap says **not** to compete with:

- multiply by layout/constants for address calculations;
- divide by powers of two with shifts;
- fixed-size screen/world calculations;
- menu/UI arithmetic;
- weapon calculations where multiplication is followed by a fixed `/8` shift.

No compelling arbitrary-runtime `(a*b)/d` gameplay site was found in this pass that would justify replacing the existing game-specific arithmetic with the current general `UMULDIV16`.

### Decision

```text
Steel Ranger as evidence for current general UMULDIV16: NO.
Steel Ranger as evidence for future richer dynamic algorithms: still useful,
but the new capability must be demonstrated first.
```

---

# 6. What the real-game audit changes

Before the audit, the research question was largely:

> How much faster can `(a*b)/d` be than public `UMUL16 + UDIV32_16`?

The better question is now:

> Which recurring dynamic ratio patterns are currently being approximated or avoided, and what reusable state can be shared across them?

The audit identifies three distinct workload classes:

| Workload | Best direction |
|---|---|
| one arbitrary full-width exact ratio | direct-core bounded `UMULDIV16` fallback |
| several numerators / same dynamic denominator or ratio | **prepared ratio / reciprocal** |
| geometry-specific tiny bounded ratio | specialize inside compound geometry operation |

This is more useful than a single universal routine.

---

# 7. Next research target

The immediate MUL_DIV follow-up should be a **prepared signed ratio** path motivated by Quake64 near clipping.

Candidate semantic contract:

```text
RATIO16_PREP
    n : signed16
    d : signed16, nonzero
    -> prepared ratio state

RATIO16_APPLY
    y : signed16
    -> trunc_toward_zero(y*n/d), signed16/bounded result
```

Research questions:

1. Is exact division required during PREP, or can a bounded reciprocal with a correction step make APPLY much cheaper?
2. What is the break-even point versus two direct `SMULDIV16` calls?
3. Can PREP preserve enough state that two X/Y applications beat Quake64's current `scale_nd + lerp16` while improving precision?
4. What error, if any, is acceptable for clipping before the routine ceases to satisfy the library's semantic promise?
5. Can the same prepared state serve perspective, interpolation, normalization and later geometry routines?

Until those are answered, **do not promote the current general `UMULDIV16` into the stable API**.
