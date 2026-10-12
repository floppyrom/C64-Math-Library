# Issue39: V2–V4 unsigned 32/32 modulo delayed-zero guard

**2026-10-12** · Source-qualified, native x64sc verified, complete resident-size-neutral
improvement. **Unsigned DIV/MOD campaign remains open.**

## Mechanism

Only the V2/V3/V4 source-owned remainder-only `RM3232U_ENTRY` gate in
`relocatable_source/division/remainder_fast_v2.inc` changes. The canonical
54-byte gate starts at $5472. Its existing 14-byte divisor-zero OR/test
precedes the high-to-low unsigned N/D comparison. Relocate that same
14-byte OR/test to the **N=D branch** (the only comparison outcome where
both might be zero). N<D proves divisor nonzero; N>D continues to the
original public divider with its own D=0 guard. Four branch offsets adjust
to preserve identical targets. **Exactly 50 code bytes change in each of
V2, V3, V4 and no other resident bytes change.** Total resident, normal ZP,
table/REU contents, public API, and source-relocation contract unchanged.
V1 and V5 remain byte-identical.

## Performance and verification

The candidate was compared at unchanged public entry $5E03 on identical
operand pairs, including zero divisor, equality, high quotient and random.
The same corpus also called UDIV32/32 at $5E00.

| Profile | Modulo sampled input pairs | Mean cycles saved | Faster | Tied | Slower | New official common-input mean |
|---|---:|---:|---:|---:|---:|---:|
| v2_pareto_fast | 2,491 | 13.599358 | 2,181 | 288 | 22 | 279.619941 |
| v3_reu_512k | 2,491 | 13.594540 | 2,180 | 288 | 23 | 279.619941 |
| v4_reu_16m | 2,491 | 13.599358 | 2,181 | 288 | 22 | 279.619941 |

- The **36,036** old/new public 6502 calls across V2/V3/V4 passed. For
  UDIV32/32, all **3,515 cases per profile** have exact cycle parity and
  identical quotient/remainder/flags. For UMOD32/32, all **2,491 pairs
  per profile** produce identical remainder, carry, preserved N/D, external
  sentinel, and even original Q side effects. A few D=0 cases are slower;
  aggregate means reflect the explicit corpus, not universal dominance.
- Native x64sc full-resident old/new public ABI report: **1,536 calls**;
  all Q/R/status observations match, no mathematical errors. This is not
  a native hardware cycle report. `validation/review/ISSUE39_V234_UMOD32_LATEZERO_NATIVE_VICE.json`.
- Exact reference binaries rebuilt from source and alternate relocations
  compiled successfully. The generated canonical sources reproduce the
  exact published reference residents. This change is *not* editing a
  dormant udiv32_32_early_gate.inc; that historical fragment is unused in
  the current V2–V4 source build.
- The full unsigned division validator (**822,050**
  public calls) and full signed division validator passed on all five
  profiles. All five common-input unsigned routines recomputed using the
  same benchmark specification (**136,335 calls total**).
- Repose's standalone generators have not been copied. This is a manual
  in-core rearrangement of the library's own remainder frontend.
- Results and proof: `validation/review/ISSUE39_V234_32_32_LATEZERO_PAIRED.json`. Executable check:
  `tools/screen_issue39_v234_32_32_latezero.py`.

The remainder of issue #39's entire unsigned DIV/MOD family still requires
its own production/no-gain decisions; **do not mark the campaign item complete**.
