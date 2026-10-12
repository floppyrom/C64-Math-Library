# Issue #39: OptiSearch biased UMOD16 vs current V2–V5 residents

**12 October 2026. Decision: retain as a separate standalone specialist;
do not promote as the default resident.** This is an API/resource screen,
not a statement that the donor is mathematically incorrect.

The original Repose/OptiSearch `division.u16-biased-zp-stable-illegal`
donor, adapted for carry handling, is already published at
`routines/standalone_lab/portable/mod_u16_biased_carry.asm`.
This screen sources that same editable NMOS 6510 assembly, assembles
two RAM-backed copies at $E000/$E400 and $E108/$E500, allocates two
additional ZP bytes $70-$71, and compares against the actual V2,
V3, V4 and V5 `MATH_UMOD16` public entry images on **identical**
1,705 inputs per profile/placement: 27,280 complete 6502 calls.

All R16, carry including divide-by-zero, N/D input preservation and
SP oracle checks pass. **No resident binary was modified.**

| Input class | Inputs | Current resident cycles | Portable donor cycles |
|---|---:|---:|---:|
| All official pairs | 1,705 | 198.601173 | 185.826393 |
| Structured edges | 529 | 417.442344 | 316.385633 |
| Uniform random | 1024 | 80.490234 | 111.772461 |
| Stress cases | 24 | 893.958333 | 926.125000 |
| Divisor zero | 128 | 108.679688 | 99.875000 |

The weighted overall mean improves **12.774780 cycles**, but
**1,391/1,705 tested inputs become slower**, including the vast majority
of random operands (resident 80.490234 vs donor 111.772461 cycles).
The donor is faster on 314 cases and tied on none. The existing public
Q16 buffer and donor Q16 buffer have different contents on **667**
cases per profile, so byte-identical current-program behavior is not
established. Whether Q16 is formally guaranteed by each remainder-only
profile is a separate ABI decision; do not silently equate these effects.

The donor requires **262 external code-RAM bytes, 2 additional ZP bytes
and an extra nested JSR frame (2 stack bytes)**. The two chosen external
placements only work on a C64 when RAM is actually visible under
$E000. These extra resources and memory banking were not accepted
into any fixed-profile contract or source-resident layout. Mini6502
instruction cycles exclude REU DMA and native VIC bus contention.

**Verdict:** useful independent Repose-generated standalone option;
not a universal speed or Pareto-record replacement for V2–V5.
The user can select it if workload is edge/narrow-divisor heavy and
the caller owns the extra RAM/ZP/stack. Further source synthesis would
need to preserve the target Q side effect where required, reduce the
random-input penalty, verify owned code space/ZP and undergo native
full-resident, relocation, mixed-call and five-profile release gates.

Permanent evidence: `validation/review/ISSUE39_UMOD16_BIASED_CURRENT_MAIN.json`. Reproduce:
`python3 tools/screen_issue39_umod16_biased_standalone.py --out /tmp/issue39_umod16_biased.json`.
The V1 UMOD16 alias is intentionally excluded because its
quotient-producing ABI differs. **Leave issue #39 open** until the
remaining unsigned DIV/MOD no-gain and width/profile screens are done.
