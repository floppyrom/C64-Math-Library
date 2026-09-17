# Wolf64 projection gate — 2026-09-17

**Status:** exhaustive standalone call-site evidence over Wolf64's accepted visible projection domain. This is not a patched Wolf64 build certification.

The purpose of this test was to challenge the synthetic `game8` result rather than confirm it. The V2 width-knee exact MUL_DIV candidate had averaged about 198 cycles on a synthetic byte-sized corpus, but the implementation plan requires comparison against the **real fake** already used by a game.

## Audited call site

Wolf64 computes sprite/item horizontal screen position as:

```text
e_col_cx = 20 +/- min(30, |side|*20 / perp_mid)
```

The caller culls before `project_col_from_side`, so accepted inputs satisfy:

```text
|side| <= perp_mid
```

and therefore:

```text
floor(|side|*20/perp_mid) <= 20
```

Wolf64's TechNotes describe this path as using the 8/8 or 16/8 `div_q40` cases. The denominator is therefore the 8-bit `perp_mid`; the numerator after the constant `*20` may be 8 or 16 bits.

This gives the game three pieces of semantic information that a general MUL_DIV routine must not ignore:

1. the multiplier is the compile-time constant 20;
2. the denominator is 8-bit;
3. the quotient is provably <=20 for every accepted visible sprite.

## Exhaustive domain

`benchmark_wolf64_project_col.py` now tests every accepted signed pair:

```text
perp_mid = 1..255
side     = -perp_mid .. +perp_mid
```

Total:

```text
65,535 cases
```

The Wolf side is a literal standalone transcription of the audited `project_col_from_side`, `mul_8x8`, and `div_q40` arithmetic, with the square tables generated exactly as in Wolf64's `tools/gen_sqtab.py`.

The library side uses the current V2 `pareto_width_hybrid` exact MUL_DIV research routine with multiplier 20, including sign/absolute-value and final screen-column handling.

## Provenance

```text
Wolf64 source commit   d606a14bbfb9fb17059c24824e0d921f23fd6860
GitHub Actions run     35247963510
head commit            f4028cb11dcc137a678e105b92dd8ec4391d01d5
artifact id            10508004258
artifact digest        sha256:3ff98676bfc463e7d3799162fe486ff03abab32c1a0d33e60e9adf13f7cac34e
benchmark exit         0
errors                  0 / 65,535 on both implementations
```

## Result

| Implementation | Mean cycles | Min | Max | Errors |
|---|---:|---:|---:|---:|
| **Wolf64 current specialized path** | **577.181** | 175 | 649 | 0 |
| V2 width-knee exact MUL_DIV | **1048.155** | 252 | 1156 | 0 |

The library candidate is therefore about **81.60% slower** than Wolf64's existing specialized implementation on the complete accepted domain.

Equivalently, the Wolf64 path uses only about 55% of the cycles of the width-knee general helper on this workload.

The quotient distribution is not dominated by q=0/q=1 as the synthetic `game8` corpus was. It is spread across q=0..20. That removes the condition that made the ~198-cycle synthetic result look so strong.

## Why this is a useful negative result

This is exactly what the implementation-plan rules were intended to catch.

The synthetic `game8` benchmark said:

```text
width-knee exact MUL_DIV ~= 197.8 cycles
```

but that corpus had:

```text
q == 0   74.30%
q <= 1   86.58%
```

Wolf64's real projection domain has a very different quotient distribution and a much stronger semantic specialization. Its constant multiplier and bounded 8-bit divisor make the operation easy to fake efficiently with game-specific code.

So the correct conclusion is **not** to optimize the generic width-knee routine until it beats Wolf64 at its own special case. The correct conclusion is:

> This call site does not justify a public general MUL_DIV routine.

A library replacement would have to expose the same useful semantic constraints, for example a bounded projection helper, and that would need broader reuse before it deserved its own API entry.

## Promotion decision

The ~198-cycle synthetic small-width exact candidate **fails this real-game promotion gate**.

It remains valid research and may still help a workload whose operands and quotient distribution really resemble the synthetic corpus, but it should not be promoted based on `game8` alone.

The M2 evidence now separates very cleanly:

```text
Wolf64 projection:
    easy to specialize/fake -> keep game-specific path

Quake64 near clipping:
    dynamic reused ratio, existing workaround expensive/approximate
    -> prepared strict-fraction ratio passes the hard-to-fake gate
```

This strengthens, rather than weakens, the prepared-ratio direction. The implementation plan is successfully filtering out a routine that looked impressive in isolation but did not improve a realistic game alternative.

Machine-readable evidence: `WOLF64_PROJECT_COL_V2_EXHAUSTIVE.json`.
