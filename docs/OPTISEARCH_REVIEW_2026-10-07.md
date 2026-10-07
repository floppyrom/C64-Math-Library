# Repose OptiSearchV2 review — 2026-10-07

Two ideas from Repose's completed OptiSearchV2 project improve the existing
library without expanding its ZP, table or persistent-stack contracts:
carry-primed signed 24-bit multiplication and negative-X-first ATAN2 dispatch.
The implementation preserves the subsequent upstream SMUL16, SMUL24, SMUL32
and SDIV16 changes in baseline `ff1b602f9ecff43724ca507f692beaa2aed89651`.

## Scope and provenance

The supplied `OptiSearchV2-2026-10-06(1).zip` has SHA-256
`f5a6a9f0e8728186f91a95c1112a70488cf943fc99b2380c52272424e44455eb`.
Its product frontier reports 3,247 generatable candidates, 3,245 active.
This review screens frontier metadata, inspects eleven leading generated
sources, and measures selected candidates. It is not an exhaustive benchmark
of all 3,245 active candidates or a proof of global optimality.

Credit for the imported optimization ideas belongs to Repose. The library
adaptations keep the existing public ABI, resident placement and table sharing.
Normal library builds and CI do not depend on OptiSearchV2.

| Candidate or family | Decision | Reason |
|---|---|---|
| `smul24-carry-prime-dead-zp-v2` | Adapted | Carry-seeded sign dispatch and dead pointer-low scratch fit the existing FAST24 kernel. One shared binder avoids the donor's duplicated binding code. |
| `atan2.1k.xy_a_c0` | Branch order adapted | Testing negative X before zero improves the full-domain mean while preserving every result and table. |
| `sweep-00292b82583455fd6ad3` (UMUL16) | Sampled; no replacement | 166.718580 native cycles uses a different register ABI and 21 initialized ZP bytes. The same operands cost 216.829580 at the existing V2 public entry; that difference includes public marshalling and does not establish a compatible speedup. |
| `mul141-umul24-17caf38763dbd90c` (UMUL24) | Sampled; no replacement | Closely related quarter-square family; 360.872929 native versus 429.872929 public cycles on the same sample, with 27 versus 24 ZP bytes. No measured public-ABI transplant was established. |
| `smul32-recovered-carry-prime-zp-temp-v5` | Inspected; no replacement | The library already has resource-specific compact126 and FAST31 variants, with newer public-path refinements. No additional compatible SMUL32 win was verified in this review. |
| `div-promotion-r48/r50/r52/r54/r55/r56` | Inspected; r48/r55 sampled | The fastest sampled division points trade substantial memory for native latency and need ABI/placement work. They are not installed. |

The sampled 16-bit divider `r55` averages 64.204242 native cycles, occupying
13,460 non-ZP bytes plus 9 ZP bytes. The 24-bit `r48` averages 100.617108 cycles,
occupying 15,224 non-ZP bytes plus 24 ZP bytes. Each sample contains 10,042
edge/random pairs with nonzero divisors; these figures do not certify the
library's divide-by-zero contract. See the [candidate screen](../validation/records/OPTISEARCH_CANDIDATE_SCREEN.json).

Rebuilding V5 from the current donors also brings in the upstream SDIV16
late-copy update that its previously bundled PRG had not incorporated. Its
signed division/modulo results and source mirrors were refreshed, with the
364,533-call signed division suite passing. This is an upstream synchronization,
not an additional optimization credited to OptiSearch. The code-delta proof
uses rebuilt baseline images so this difference is accounted for.

## Measured changes

Public SMUL24 uses identical 10,676-case signed edge/random inputs in every
profile and both memory maps. Means include the public entry through RTS,
excluding caller JSR and input stores. These paired values deliberately replace
older public rows that used different profile-specific samples.

| Routine | Before | After | Difference |
|---|---:|---:|---:|
| Public SMUL24, V1/V5 | 516.095822 | 511.342357 | −4.753466 cycles |
| Public SMUL24, V2/V3/V4 | 472.095822 | 467.342357 | −4.753466 cycles |
| Native standalone SMUL24 FAST24, 30,000 identical pairs | 400.301600 | 395.756600 | −4.545000 cycles |
| ATAN2 V1, all 65,536 vectors | 48.447189 | 47.462814 | −0.984375 cycles |
| ATAN2 V2/V3/V5, all 65,536 vectors | 44.962814 | 43.970627 | −0.992188 cycles |

Public SMUL24 saves exactly 4 cycles when both operands are negative and 5 in
the other quadrants on the measured corpus. Reachable code shrinks by six bytes,
with 24 ZP bytes and no persistent stack-page reservation. The native standalone
kernel shrinks from 411 to 405 code bytes; its occupied total falls from 2,512 to
2,506 bytes, including 33 initialization bytes and 2,044 table bytes. Native
placement gives per-case savings of 3–5 cycles on its separate uniform corpus.

`CPY #0` both tests Y's sign and establishes carry. Loads, stores and EOR in the
shared binder preserve it for the first product. Mixed-sign correction reuses
the dead low byte of pointer p2. The NN path uses the carry bound from negating
negative Y to start negating X. Public inputs remain stable; the upstream q2
optimization still reads original Y2 directly from `MATH_IO+$06`.

ATAN2 has a real timing trade-off: X<0 saves 2 cycles, X>0 is unchanged, and
X=0 costs 4 extra cycles in V1 or 2 in V2/V3/V5. Code and tables are unchanged in
size. All 65,536 stock outputs match the original compact kernel exactly; the
existing maximum error remains one phase unit. V4's exact 48-cycle REU path is
unchanged. Axis-heavy callers should account for the stated extra cycles.

## Verification and reproduction

- [Paired profile comparison](../validation/records/OPTISEARCH_PROFILE_COMPARISON.json): 213,520 SMUL24 calls; 24-ZP and zero-persistent-stack checks; every changed initialized-image byte belongs to SMUL24 or ATAN2 code in all ten rebuilt profile/maps.
- [SMUL24 ABI and interference checks](../validation/multiply_refresh/SMUL24_DIRECTOUT_VALIDATION.json): 106,760 edge/random calls plus 25,600 interleaved signed/unsigned multiply calls; preserved inputs, both incoming carry states, C=0 return, balanced stack and guarded writes.
- [Installed ATAN2](../validation/ATAN2_DISPATCH_VALIDATION.json): 655,360 calls covering all five profiles and both maps, exact stock-output digest, precision and ABI checks, identical relocation timing vectors.
- [Standalone ATAN2](../validation/ATAN2_STANDALONE_DISPATCH.json): both incoming carry states for both changed kernels, 262,144 calls.
- [Native FAST24 independent oracle](../validation/records/SMUL24_OPTISEARCH_ORACLE.json): 30,000 primary cases and 4,265 independent edge/random cases using OptiSearchV2 Reduced6502 with the C64 RAM model; zero result or cycle mismatches against mini6502 and Python arithmetic.

The full 54-entry reference/alternate smoke suites, signed ownership and
publication checks, deterministic rebuilds and V5 validation are also rerun
after integrating the current upstream baseline. The earlier ACME certification
is retained as historical evidence; these new sources were not rerun through
the external ACME executable in this environment.

```sh
make reference alternate hybrid
python3 tools/validate_smul24_directout.py
python3 tools/validate_atan2_dispatch.py
python3 tools/validate_signed_layout.py
python3 tools/verify_deterministic_rebuild.py

# Optional independent native oracle, using the supplied extracted project:
git show ff1b602:routines/multiply/mul_s24_s24_s48_fast24.asm > /tmp/fast24-before.asm
python3 tools/validate_fast24_optisearch.py --optisearch /path/to/OptiSearchV2 \
  --baseline /tmp/fast24-before.asm

# Build ff1b602 in a separate checkout first, then compare its outputs:
python3 tools/compare_optisearch_profiles.py \
  --baseline-source /path/to/baseline/build_source \
  --baseline-hybrid /path/to/baseline/build_hybrid \
  --baseline-commit ff1b602f9ecff43724ca507f692beaa2aed89651
```
