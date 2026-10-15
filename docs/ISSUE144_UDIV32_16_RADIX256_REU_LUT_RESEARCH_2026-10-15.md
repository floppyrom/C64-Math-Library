# Issue #144 B — radix-256 quotient producer, mathematical and REU-table screening

**Research branch, not a release. 15 October 2026.** The existing public 32÷16 implementation remains unmodified. A cycle-efficient 6510 producer does not yet exist for these trial estimates.

## Full-domain arithmetic construction

For arbitrary nonzero 16-bit D, normalize `s=16-bit_length(D)`, `Dn=D<<s` (so $8000≤Dn≤$FFFF). Obtain high-word quotient and remainder from the ordinary `high16//D`. Then form `Rn=(remainder<<s)+((low16<<s)>>16)`, `F=(low16<<s)&$FFFF`. Invariant: `0≤Rn<Dn`, including denominators smaller than 256. Process F's two bytes with a quotient-digit estimator and correct the 16-bit remainder exactly; then undo normalization with `R=Rn>>s`. D=0 returns the normal (Q=0,R=0,C=1) mathematical contract.

The independent public-source numerical script `tools/issue144_u3216_radix256_numerical_research.py` has a deterministic **1,155,360-pair all-divisor corpus** (each D16 in 0..65535 × ten N32 boundary cases, plus 500,000 independent uniform random N32/D16). Exact Q32/R16/C matched the mathematical oracle across three independently implemented quotient estimators. Corpus SHA256: `46d1b118fbc5dd38e3430c3517031ea4a68bfab0db1f53ef06228b96ebf2ab6d`. Dedicated public GitHub Actions numerical CI [#38728754571](https://github.com/floppyrom/C64-Math-Library/actions/runs/38728754571): **PASS**.

## Three estimator architectures

1. **16/8 high-byte quotient estimate:** for normalized `Dn=256v+w` and 16-bit live remainder `R`, use `qhat=min(255,R//v)`. Correct by subtracting Dn until the trial remainder is nonnegative. Maximum **two** corrections.
2. **128-entry reciprocal seed:** replace 16÷8 with `qhat=min(255,(R*ceil(65536/v))>>16)`. A 9-bit reciprocal estimate needs up to **three** downward corrections. Multiplication cost is unmeasured on 6510.
3. **One-bank 64-KiB direct 2-byte REU lookup, strongest hardware hypothesis:** let `h=R>>8`, `l=R&255`, with `h≤v` because R<Dn. Address table record `((v-128)<<9)|(h<<1)`, storing two bytes `q0=min(255,floor(256h/v))` and `t0=256h-q0*v`. The second value fits a single byte for every reachable `h≤v`, including the clipped `h=v` case. The signed temporary remainder is
   `temp = ((t0+l)<<8)+incoming_byte-q0*w`.
   Restore with `temp+=Dn; q0--` if negative, or `temp-=Dn; q0++` if at least Dn. In the tested corpus no more than **two corrections in either direction** were needed.

### Why the table's signed correction bound is two

For `v≥128`, `w∈[0,255]`, `q0≤255`, the temporary remainder is strictly greater than `-255²=-65025`, and `Dn≥32768`, so fewer than two Dn additions suffice when negative (integer correction count at most two). When `h<v`, `t0≤v-1` and `l≤255`, giving `temp<256(v+255)+256≤3Dn`; the upward correction count is at most two. For `h=v`, `R<Dn` forces `l<w`, `q0=255` and `temp<Dn`, so the upper case is even simpler.

This is an algebraic correction bound for **exact integer arithmetic**, not a bound on CPU cycles.

## Physical resource and timing feasibility

The LUT consumes **65,536 bytes**, exactly one REU bank of 128×256 two-byte records (including unused `h>v` slots). V4's present map reserves banks $00–$09, $10–$17 and $40–$7F; **$20 is an unassigned candidate bank**, subject to explicit map ownership and independent coexistence testing. V3's 512-KiB image uses banks $00–$07 and would need an exclusive bank reassignment or additional REU. The table is not viable as a default stock-C64 RAM allocation.

Each quotient digit would need a two-byte REU lookup, an 8×8 multiply `q0*w` and bounded 16/17-bit correction arithmetic. The existing V4 REU-assisted public UMUL8 benchmark is 69.0 **modeled CPU cycles per call, excluding DMA wait**; two products alone therefore account for approximately 138 modeled cycles before lookup and correction overhead. Physical REU DMA scheduling, bank availability, scratch ownership, normalized input preparation, headword division, final output and return cost must all be measured, not guessed.

**Next genuine speed gate:** create an independently source-assembled V4 optional producer using a private-to-the-call scratch and an application-owned REU $20 lookup image, then compare fully unrestricted public Q32/R16/C/N/D/SP calls at identical inputs against current V4 (~652 modeled cycles on the documented uniform corpus; a different canonical corpus reports 617). The target is **at least 5% ordinary full-width gain**, no unacceptable p95/worst regression. Finally verify true native x64sc REU operation, mixed-call safety, alternate memory maps, absolute RAM/REU footprint and a sealed opt-in source release. Any underperformance means the experiment stays unpromoted.

**No private OptiSearch implementation is published; no source-ready fast 6510 divider, normal ABI, VICE correctness or measured DMA timing is claimed by this numerical trial.** Issue #144 remains open.
