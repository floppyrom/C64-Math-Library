# Issue #39 — V2 D>=24 guarded remainder-only UMOD8

Date: 2026-10-12. Status: validated candidate for PR #65; unsigned DIV/MOD campaign remains open.

The stable V2 \`MATH_UMOD8\` address stays $3200. A 3-byte JMP reaches a
**101-byte** independently symbolic V2 helper at \`REG_KERNEL+$1323\`
(reference $5323..$5387); under D<24 it falls back into the *original*
public V2 wrapper at \`MATH_UMOD8+3\`, including the certified private core
and its self-modifying small-divisor tail. For D>=24, ten compare/subtract
stages calculate remainder without allocating extra ZP, writing Q, or
modifying N/D. The helper reuses verified former zero bytes between UMUL8
and UMUL16; resident length and API do not change.

### Full-domain paired results

On exactly 65,536 N/D pairs, 131,072 complete resident 6502 executions:
- Original V2 **64.819153** cycles, optimized **52.204453** (-19.46%).
- 58,290 faster, 504 identical, 6,742 slower; worst +15 cycles.
- All remainder, divide-by-zero carry, all Q bytes, N/D/high-R
  sentinel and historical parent-hash checks passed.
- A separate native VICE x64sc (reported 3.10) test executed **4,096**
  complete old/new V2-resident calls, including MATH_INIT, with no errors.
- Original resident SHA-256: \`e1e828a2748099b6f05b224b98ca26960d120f8ba886c4906e8b52bdb8b4fbcd\`.
- New resident SHA-256: \`28fc6e653a05b170a80cd7eb50636d755895c5ebb7aab133262ed560fa465dd6\`.
- Exact guard helper SHA-256:
  \`6a733be6ca05992b46585c8443ae6ce7b21a075bfdfdfe34cf844e748b8f6f29\`.

Reference and alternate relocations pass. V5's hybrid builder normalizes
the first V2 donor entry instruction **in its transient import image only**,
before reachability tracing; V5's shipped source and final resident remain
byte-identical (SHA-256 \`bed1ee986857d045d452036d78d0d6cbdc078dbc3407f8a860a8fd54f8395fa2\`).
Custom Pareto inherits this builder and must retain the normal validation.

### Proper use and qualification

Use the entire V2 resident for a fully supported stable API, including
\`MATH_INIT\` and matching \`math_api.inc\`. The exact individually named
\`v2_pareto_fast/standalone/mod_u8_u8_u8.asm\` is an executable *audit mirror*,
not a dependency-free drop-in: the V2 fallback wrapper and
\`REG_KERNEL+$1200\` remainder engine plus scratch ZP are required below D=24.
The symbolic \`relocatable_source/v2_pareto_fast/v2_umod8_guard_d24.inc\`
is the liftable overlay in a matching resident/source layout.

The 52.204 figure uses exhaustive 8x8 inputs; the separate common-corpus
performance rank uses the exact same operands for all profiles. No new stable
API, ordinary ZP bytes, stack reservation, REU payload or PRG span were added.
OptiSearch native records are not attributed as public-entry gains without
their own transplant and ABI/placement qualification.

Evidence: \`validation/review/ISSUE39_V2_UMOD8_D24_CANDIDATE.json\`, \`validation/review/UNSIGNED_DIVISION_VALIDATION.json\`,
\`validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json\`, native VICE
handoff on issue #39, and independent PR/main CI checks.
