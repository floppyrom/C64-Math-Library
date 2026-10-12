# Issue 39 — 24-by-8 writable-RAM specialist vs current V1–V5

13 October 2026. **Caller-opt-in source replay; no default public replacement.**

This test invokes the already-published manually refined, Repose-derived
div_u24_by_u8_selfmod.asm directly as a bounded library-dependent
24-bit unsigned division and modulo producer. Unlike unrestricted
UDIV24/UMOD24, this routine is correct **ONLY IF** the 24-bit
dividend has N2>0 (N>=65536) and the divisor is exactly one
nonzero byte (D1=D2=0, D0=1..255). Zero division is NOT handled;
the caller must use the resident public entry on ineligible values.

The source is assembled to two **caller-owned writable code RAM**
origins ($0800 and $0851), with self-modified compare/subtract
immediates refreshed every call. It is not ROM-safe or reentrant;
interrupt users must ensure the code cannot be reentered. Extra
normal ZP = 0. It uses existing N24/D24/Q24/R24 buffers.


**65,080 same-input pairs / 130,160 complete 6502 CPU executions**.
Five current SHA-256-pinned V1–V5 full residents, two RAM maps,
both public quotient and remainder entries, and six explicit
numerator/divisor classes. Q24, R24, carry, preserved N/D,
out-of-range remainder bytes, unrelated sentinels and stack
all pass. The public UDIV24 extra Q3 buffer byte can differ;
that non-promised extra-byte behavior is reported, not erased.
Modulo Q24 side effects are recorded separately on V2–V5.
All input and cycle vectors are hash-identified in the JSON.

| Profile | Compared API | RAM code bytes | Eligible random delta cycles | Faster / slower | Tiny D delta | Edge delta | Q3 differences | Modulo Q24 differences |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v1_balanced | UDIV24 | 68 | -46.000 | 2048 / 0 | -46.000 | -46.000 | 0 | 0 |
| v1_balanced | UMOD24 | 68 | -46.000 | 2048 / 0 | -46.000 | -46.000 | 0 | 0 |
| v2_pareto_fast | UDIV24 | 68 | -17.713 | 1937 / 71 | -17.789 | -26.242 | 2048 | 0 |
| v2_pareto_fast | UMOD24 | 68 | -22.713 | 2024 / 24 | -22.789 | -31.242 | 2048 | 0 |
| v3_reu_512k | UDIV24 | 68 | -17.713 | 1937 / 71 | -17.789 | -26.242 | 2048 | 0 |
| v3_reu_512k | UMOD24 | 68 | -22.713 | 2024 / 24 | -22.789 | -31.242 | 2048 | 0 |
| v4_reu_16m | UDIV24 | 68 | -17.713 | 1937 / 71 | -17.789 | -26.242 | 2048 | 0 |
| v4_reu_16m | UMOD24 | 68 | -22.713 | 2024 / 24 | -22.789 | -31.242 | 2048 | 0 |
| v5_hybrid_lowzp | UDIV24 | 68 | -17.713 | 1937 / 71 | -17.789 | -26.242 | 2048 | 0 |
| v5_hybrid_lowzp | UMOD24 | 68 | -22.713 | 2024 / 24 | -22.789 | -31.242 | 2048 | 0 |

**Cycle delta is standalone specialist minus current resident public
entry, so negative is faster.** The eligible 24/8 sample is NOT
representative of arbitrary 24/24 division, and direct entry skips
general-purpose divisor/width dispatch overhead. V1 already uses
a related helper under its narrower in-resident guard; the direct
V1 mean saving must not be advertised as an algorithmic breakthrough.
For V2–V5 the direct specialist saves approximately 18–23 cycles
for the tested eligible inputs, without paying any new guard cost
because the **caller** asserts the exact precondition.

**No default promotion.** Adding an in-resident guard would tax
all unqualified inputs; that potential integration is NOT proven
faster under the public benchmark, and needs another source/alternate
layout and mixed-call/nonnarrow screen. The Q3 side-effect differences
must also be understood before any transparent in-place replacement.
The published standalone source is ready for callers willing to
provide writable RAM and their own precondition guarantees.

Reproducer: tools/screen_issue39_u24_d8_smc_current.py
Evidence: validation/review/ISSUE39_U24_D8_SMC_CURRENT_PUBLIC_SCREEN.json
Source: routines/standalone_lab/portable/div_u24_by_u8_selfmod.asm
No private OptiSearch source published; original provenance retained.
Cycles are NMOS instruction counts, NOT native VIC/REU bus timing.
No new native VICE executions are claimed.

Issue #39 remains OPEN. This is a bounded U24/D8 specialist
qualification, not completion of all unsigned DIV/MOD profiles.
