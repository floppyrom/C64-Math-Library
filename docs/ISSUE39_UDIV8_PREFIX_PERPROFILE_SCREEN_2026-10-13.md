# Issue 39 — UDIV8 manual 8/12/16/20/24/28 prefix-source screen

13 October 2026 — reproducible full public-ABI resource and workload screen.

Manual source synthesis reproduces the existing **quotient-prefix
compare/SBC** followed by **aligned shifted-divisor tail** architecture,
used by V1/V2 (and inherited relatives). This is NOT a direct
transplant of private OptiSearch source; the private package is
kept private, and earlier OptiSearch small-quotient observations
informed the manual source analysis.

All six prefix-length variants are assembled at two caller-owned
RAM addresses ($0800 and $0851), using exactly one extra ZP
scratch byte ($70) outside the resident default resource contracts.
They execute alongside each current SHA256-pinned V1–V5 public
resident. Complete Q8, R8, carry (including D=0), preserved N/D,
unchanged high Q/R buffer sentinels and balanced stack verified.
The resident binaries, normal ZP windows and public entry addresses
are NOT changed; native VICE was not used for candidate validation.

**357,720 identical input pairs, 715,440 6502 executions**,
for the official common corpus and eight additional independent
input classes (random, tiny and large divisors, q=0/1, powers of 2,
divisor zero and structured edges). All input and cycle vectors
are SHA-pinned in the JSON. Cycle values include public-entry
execution through RTS, but do not model REU DMA/VIC bus stalls.

| Profile | Prefix K | Code bytes (RAM) | Official delta cycles | Faster / slower | Uniform delta | Tiny-D delta |
|---|---:|---:|---:|---:|---:|---:|
| v1_balanced | 8 | 229 | -0.371 | 111 / 62 | -0.109 | -3.393 |
| v1_balanced | 12 | 297 | +0.000 | 0 / 0 | +0.000 | +0.000 |
| v1_balanced | 16 | 365 | -0.350 | 73 / 67 | +0.117 | -1.121 |
| v1_balanced | 20 | 433 | +0.113 | 63 / 77 | +0.223 | +2.180 |
| v1_balanced | 24 | 501 | +0.809 | 65 / 75 | -0.059 | +5.541 |
| v1_balanced | 28 | 569 | +1.535 | 67 / 73 | +0.230 | +7.932 |
| v2_pareto_fast | 8 | 229 | -0.484 | 82 / 91 | -0.332 | -5.572 |
| v2_pareto_fast | 12 | 297 | -0.113 | 77 / 63 | -0.223 | -2.180 |
| v2_pareto_fast | 16 | 365 | -0.463 | 73 / 25 | -0.105 | -3.301 |
| v2_pareto_fast | 20 | 433 | +0.000 | 0 / 0 | +0.000 | +0.000 |
| v2_pareto_fast | 24 | 501 | +0.697 | 11 / 64 | -0.281 | +3.361 |
| v2_pareto_fast | 28 | 569 | +1.422 | 20 / 64 | +0.008 | +5.752 |
| v3_reu_512k | 8 | 229 | +12.495 | 2182 / 195 | +7.408 | +161.834 |
| v3_reu_512k | 12 | 297 | +12.865 | 2182 / 195 | +7.518 | +165.227 |
| v3_reu_512k | 16 | 365 | +12.515 | 2182 / 195 | +7.635 | +164.105 |
| v3_reu_512k | 20 | 433 | +12.978 | 2182 / 195 | +7.740 | +167.406 |
| v3_reu_512k | 24 | 501 | +13.675 | 2182 / 195 | +7.459 | +170.768 |
| v3_reu_512k | 28 | 569 | +14.400 | 2182 / 195 | +7.748 | +173.158 |
| v4_reu_16m | 8 | 229 | +12.495 | 2182 / 195 | +7.408 | +161.834 |
| v4_reu_16m | 12 | 297 | +12.865 | 2182 / 195 | +7.518 | +165.227 |
| v4_reu_16m | 16 | 365 | +12.515 | 2182 / 195 | +7.635 | +164.105 |
| v4_reu_16m | 20 | 433 | +12.978 | 2182 / 195 | +7.740 | +167.406 |
| v4_reu_16m | 24 | 501 | +13.675 | 2182 / 195 | +7.459 | +170.768 |
| v4_reu_16m | 28 | 569 | +14.400 | 2182 / 195 | +7.748 | +173.158 |
| v5_hybrid_lowzp | 8 | 229 | -0.484 | 82 / 91 | -0.332 | -5.572 |
| v5_hybrid_lowzp | 12 | 297 | -0.113 | 77 / 63 | -0.223 | -2.180 |
| v5_hybrid_lowzp | 16 | 365 | -0.463 | 73 / 25 | -0.105 | -3.301 |
| v5_hybrid_lowzp | 20 | 433 | +0.000 | 0 / 0 | +0.000 | +0.000 |
| v5_hybrid_lowzp | 24 | 501 | +0.697 | 11 / 64 | -0.281 | +3.361 |
| v5_hybrid_lowzp | 28 | 569 | +1.422 | 20 / 64 | +0.008 | +5.752 |

**Negative candidate-minus-current-resident means faster** for
that particular class only. Do not treat weighted benchmark means
as a workload-neutral optimization; also compare extra code and
scratch byte versus the resident normal-ZP budgets.

Best K by this corpus within the six SOURCE-GENERATED variants:
- v1_balanced: K=8, candidate 64.723 cycles vs current public 65.093 cycles.
- v2_pareto_fast: K=8, candidate 64.723 cycles vs current public 65.206 cycles.
- v3_reu_512k: K=8, candidate 64.723 cycles vs current public 52.228 cycles.
- v4_reu_16m: K=8, candidate 64.723 cycles vs current public 52.228 cycles.
- v5_hybrid_lowzp: K=8, candidate 64.723 cycles vs current public 65.206 cycles.

The experiment does not prove the current source byte arrangement
could be replaced in its present library-reserved slot without
affecting REU, V5 hybrid, alternate-map or other routines. Public
default replacement is therefore NOT made by this audit. A
qualifying improvement would require real resident-source packing,
zero additional normal ZP, exhaustive 65,536-case each profile,
native VICE and reference/alternate ownership checks.

Reproducer: tools/screen_issue39_u8_prefix_source_sweep.py
Evidence: validation/review/ISSUE39_UDIV8_PREFIX_PUBLIC_ABI_SWEEP.json
Published resident source anchors:
relocatable_source/v1_balanced/udiv8_direct_public.inc and
relocatable_source/v2_pareto_fast/udiv8_direct_public.inc.
The private Repose OptiSearch engine is not published.

**Issue #39 remains OPEN; unsigned DIV/MOD family not complete.**
