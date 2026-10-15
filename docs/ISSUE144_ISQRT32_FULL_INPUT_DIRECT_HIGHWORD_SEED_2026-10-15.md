# Issue144 — unrestricted ISQRT32 direct high-word seed opt-ins

**Four non-REU producer profiles qualified: V1/V2/V3/V5; V4 REU path unchanged.**

Original ISQRT32 writes the source low word to resident scratch,
copies the input high word to the low-word slot, uses the existing
exact ISQRT16 lookup to obtain its initial high root byte, then
restores the low word before eight base-4 refinement steps.
This opt-in source separately assembles the same high-root seed
to address **$C012/$C013 directly**, bypassing redundant input
copy/save/restore. Refinement uses the original initialized resident
radix-4 helper, normal zero-page scratch and square tables.
All 32-bit radicands are valid, no narrow-input precondition.

## Canonical 4,130 case identical-input public entry comparisons

| Profile | Stock CPU cycles | Source opt-in | Saved | Program bytes |
|---|---:|---:|---:|---:|
| v1_balanced | 1219.261 | 1168.261 | 51 | 102 |
| v2_pareto_fast | 1053.285 | 1006.285 | 47 | 95 |
| v3_reu_512k | 1053.326 | 1006.326 | 47 | 95 |
| v5_hybrid_lowzp | 1219.261 | 1168.261 | 51 | 102 |

All **16,520 matched CPU-model calls PASS** with root equality to
Python math.isqrt(), low-level carry=0, X, Y, stack, preserved input,
ordinary ISQRT16 interleaved and restoration of normal public JMP.
Every paired call saves **exactly 47 cycles (V2/V3)** or **51 cycles
(V1/V5)**, with no tail regressions in the measured corpus.

Native VICE x64sc: **192 baseline/direct-entry opt-in calls** passed
correct 16-bit result and carry on the four changed profiles.
Native V4 control: 24 additional original calls with the actual
**16 MiB REU image loaded** PASS. **No V4 replacement is claimed**.
The CPU-model includes the preserved public $5E30 JMP entry, while
the native opt-in harness calls the separate $0C00 entry directly.
Native cycle timing is NOT measured; REU wall/bus cycles are not
inferred from the CPU model.

### ABI, resources and safe use

- Original public MATH_ISQRT32 entry remains $5E30; call the
  separate $0C00 entry directly, or redirect only the original
  two-byte in-memory JMP target ($5E31/$5E32) under exclusive
  access. No shipped PRG or resident source is modified.
- Source islands occupy $0C00..$0CB5 including gaps; program
  requires 95 bytes V2/V3 or 102 bytes V1/V5.
- This address range is **example caller-owned RAM**, not reserved
  by the library; check application/loader/IRQ/stack maps.
- Exact resident MATH_INIT and precomputed square lookup tables
  must remain accessible and unchanged.
- Uses the resident shared zero page and original radix-4 helper;
  safe for sequential mixed calls, **not** interrupt-reentrant.
- Source is per-profile, relocations need fresh validation.
- V4 uses an unrelated REU table architecture; this alternative
  is **not** compatible with V4 and leaves it unchanged.
- Default resident PRGs, both REU images, ordinary API symbols,
  default zero-page budgets and PERFORMANCE leaderboard unchanged.

Assembly sources: optional/issue144_isqrt32_highword_direct/<profile>.asm
Source generator: tools/issue144_isqrt32_highword_direct_experiment.py
Canonical public-entry benchmark: tools/issue144_isqrt32_direct_seed_canonical.py
Real native VICE: tools/native_issue144_isqrt32_highword_direct.py
CPU proof: validation/review/ISSUE144_ISQRT32_DIRECT_HIGHWORD_SEED_MODEL.json
VICE proof: validation/review/ISSUE144_ISQRT32_DIRECT_HIGHWORD_SEED_NATIVE_VICE.json
No private OptiSearch code or archive is redistributed.
