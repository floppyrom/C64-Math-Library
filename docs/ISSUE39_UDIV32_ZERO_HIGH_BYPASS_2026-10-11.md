# Issue #39: V1/V5 32/32 divisor-high-zero direct fallback
**Date:** 2026-10-11. **Scope:** post-PR #56 follow-up; unsigned DIV/MOD campaign remains open.

## Architecture and proof
The public 32/32 divider's early gate has proved N>D and D!=0 before it enters the bounded quotient-one filter. When divisor high byte D3=0, the old filter jumps to the quotient-two/three prefilter, which itself requires D3>=$40 and must jump to REG_GAME. Redirecting D3=0 straight to REG_GAME therefore removes a redundant guard without changing any arithmetic behavior. The only changed bytes in V1/V5 reference PRGs are $6814 (branch displacement), $6859 (JMP opcode), and $685B (JMP high target). The newly occupied $6859-$685B lies below the next source island at $6860. The relocation decoder's executable-span exclusion was extended accordingly. No new ZP, API changes, resident-size growth, REU tables, or stack-page reservations.

## Same-operand V1/V5 public measurements
| Routine | PR #56 mean | New mean | Mean saved | Faster / equal / slower |
|---|---:|---:|---:|---:|
| UDIV32_32 (2,729 pairs/profile) | 359.077684 | 358.009161 | 1.068523 cycles | 243 / 2,486 / 0 |
| UMOD32_32 (1,705 pairs/profile) | 436.899707 | 435.224633 | 1.675073 cycles | 238 / 1,467 / 0 |

Every affected case saves 12 cycles; all other cases tie. This bypass adds **no new regressions relative to PR #56**. The q2/q3 optimization's previously documented narrow-divisor tradeoff still exists. V2, V3 and V4 public cycle vectors remain unchanged.

## Verification and provenance
The permanent `tools/audit_issue39_zero_high_bypass.py` restores the three parent bytes in memory and performs 8,868 paired old/new public machine-code calls, comparing quotient, remainder, carry, input preservation and precise instruction cycles on identical operands. New V1/V5 PRGs pass 164,410 unsigned calls each and 97,329 / 36,273 signed calls respectively. Five-profile published reports cover 822,050 unsigned, 364,533 signed, 136,335 common-operand and 30,720 workload calls. V1 and V5 source/reference/alternate and hybrid builds reproduce the shipped images. Native VICE x64sc full-resident comparisons of old and new binaries passed 80 calls per profile per version, or 320 executed calls. Source and reproducibility evidence are separate from private OptiSearch; this is a manual control-flow improvement, not an OptiSearch record.

The library-wide issue #39 unsigned DIV/MOD family audit is still incomplete, and this change does not authorize moving to the next family.
