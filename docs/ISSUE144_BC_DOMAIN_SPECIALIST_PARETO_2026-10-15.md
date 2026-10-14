# Issue #144 — B/C opt-in arithmetic Pareto source publication

**Separate caller-selected domain specialists; not normal API replacements.**
The regular V1–V5 PRGs, REUs, public symbol addresses, ZP and public
PERFORMANCE leaderboard remain byte-for-byte unchanged.

## B: 25-byte 32/16 unsigned remainder-only power-of-two producer

Precondition: D16 nonzero and exactly a power of two (1..32768).
N32 at $C010–$C013, D16 at $C014–$C015. Output R16 only
at $C01C–$C01D, carry clear. Q32 at $C018–$C01B is
**not computed**: this cannot be used as a drop-in replacement
for existing MATH_UMOD32_16 which also returns Q32.
No ZP, immutable tables, or init required; 25 bytes at caller-owned
$0C00 (reassemble if occupied). X,Y,SP and inputs preserved.

| Profile | Matched stock UMOD mean | R-only opt-in | Saved cycles |
|---|---:|---:|---:|
| v1_balanced | 1351.194 | 38.000 | 1313.194 |
| v2_pareto_fast | 851.142 | 38.000 | 813.142 |
| v3_reu_512k | 851.142 | 38.000 | 813.142 |
| v4_reu_16m | 851.142 | 38.000 | 813.142 |
| v5_hybrid_lowzp | 851.142 | 38.000 | 813.142 |

Each profile: 16 legal power-of-two denominators, 160 random numerators
per denominator plus structured edges: 2,752 paired CPU-model calls.
All 13,760 matched model calls correct, including carry/input and
preserved non-output quotient bytes. Native x64sc: 24 baseline plus
24 optional calls/profile. These comparisons prove remainder/carry
only, *not* quotient equivalence.

## C: exact ISQRT32 low-word-domain selector

Precondition: upper input word $C012,$C013 is zero, N32 <= $FFFF.
The stock MATH_ISQRT16 is exact over this domain, so the separately
placed three-byte JMP at $0C40 reuses it and returns exactly the
same 16-bit root, input preservation and clear carry.
Requires the resident original MATH_INIT and table data.

| Profile | Stock 32-bit sqrt on low16 workload | Low16 specialist | Saved |
|---|---:|---:|---:|
| v1_balanced | 1712.837 | 89.286 | 1623.551 |
| v2_pareto_fast | 1530.418 | 89.544 | 1440.873 |
| v3_reu_512k | 1530.418 | 89.565 | 1440.853 |
| v4_reu_16m | 971.625 | 57.000 | 914.625 |
| v5_hybrid_lowzp | 1712.837 | 89.286 | 1623.551 |

There is also an AUTO selector that checks upper input bytes. It is
exact on arbitrary 32-bit inputs, but its branch tax slows full-width
calls. **Not promoted as a default:** choose only after measuring
application inputs. Mean paired full-width regression / 10% low16
workload improvement (cycles, CPU model):

| Profile | Full32 regression | Mixed 10% low16 gain |
|---|---:|---:|
| v1_balanced | 14.000 | 152.803 |
| v2_pareto_fast | 14.000 | 134.240 |
| v3_reu_512k | 14.000 | 134.237 |
| v4_reu_16m | 14.000 | 77.649 |
| v5_hybrid_lowzp | 14.000 | 152.803 |

All five profiles pass deterministic common-input model tests
and native x64sc arithmetic/carry comparisons (240 native calls
total for both specialist families). The V4 sqrt native test
loads the actual 16-MiB REU file. VICE native cycles, VIC-II
bus effects and REU DMA time are **not** claimed.

Source B: optional/issue144_pow2_mod32_16/mod32_16_pow2_remainder_only.asm
Source C: optional/issue144_isqrt32_u16/low16_dispatch.asm
Model reproducer: tools/issue144_BC_domain_screen.py
VICE reproducer: tools/native_issue144_BC_specialists.py
Native evidence: validation/review/ISSUE144_BC_SPECIALISTS_NATIVE_VICE.json

## Wider research that has NOT been promoted

The existing 114-byte Issue39 power-of-two full-division helper
produces complete Q32/R16. A new checked dispatcher can use that
on power-of-two D and fall back to the ordinary alias for all
other denominators, preserving divide-by-zero semantics. A separate
same-input screen shows ~33.38 mean cycles gained when 10% of V2–V5
divisors are powers of two, but ~28.39 mean cycles regressed when
D16 is uniform. It is kept as source research, not a new normal API.
Source: optional/issue144_guarded_pow2_divmod/guard.asm

All specializers require independently verified caller-owned RAM;
the example addresses are not reserved and can conflict with a
loader, application screen, other opt-ins or interrupt hooks.
No private OptiSearch source is published.
