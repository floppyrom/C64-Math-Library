# Issue #39: generic U24 high-quotient live-X substitution

13 October 2026. Source-backed research, not production promotion.

Both V1 and V2 24-bit quotient paths first execute illegal NMOS LAX N2,
putting N2 into A and X. On the N2>D2 high_gt path X remains unchanged
until the high-byte subtract. Replace LDA N2 (4 cycles, 3 bytes) with
TXA (2 cycles, 1 byte) immediately before SBC D2. This is a generic
operand class, not a small-divisor caller-specialist. No new scratch.

The existing V1 and V2 full monolithic sources were expanded and assembled
before and after the single source mutation. The original source-built
memory exactly matched current SHA-pinned V1/V2 resident program bytes.
The candidate retained all stable public API addresses.

**34,088 identical-input pairs, 68,176 emulated 6502 executions**,
zero promised Q/R/carry/operand/high-R/scratch/stack discrepancies.
Tests included official same-input pairs, N2>D2, N2=D2, N2<D2,
nonzero D8/high N2, uniform operands, structured edges, zero divisor.
Uncontracted Q3 side effects were counted separately.

| Profile | Public API | Official cases | Delta mean cycles | Faster / slower | N2>D2 delta |
|---|---|---:|---:|---:|---:|
| v1_balanced | UDIV24 | 4753 | -0.858616 | 2035 / 0 | -1.998047 |
| v1_balanced | UMOD24 | 1553 | -0.684482 | 530 / 0 | -1.983398 |
| v2_pareto_fast | UDIV24 | 4753 | -0.855039 | 2035 / 0 | -1.989258 |
| v2_pareto_fast | UMOD24 | 1553 | +0.003220 | 13 / 18 | +0.007812 |

Negative candidate-minus-original delta means faster. V1 UDIV24 and
UMOD24 both gained without an observed slower official input; V2 UDIV24
also gained without a slower input. V2 dedicated remainder-only UMOD24
had a small layout/branch-phase tradeoff (13 faster, 18 slower), not
an unconditional no-regression proof.

**No default promotion yet.** Integration requires reference/alternate
symbolic source rebuilds, V3/V4 inherited-source updates, V5 imported
V2 donor repacking, resource-island integrity, native VICE correctness
and full post-merge release CI. All resident binaries stay unchanged.

Reproducer: tools/screen_issue39_u24_highgt_txa.py
Evidence: validation/review/ISSUE39_U24_HIGHGT_LIVE_X_SCREEN.json
Source roots: relocatable_source/v1_balanced/udiv24_direct_repose_balanced.inc
and relocatable_source/v2_pareto_fast/udiv24_direct_repose.inc.
Private OptiSearch tools and data are not published.
Cycle figures exclude VIC/REU DMA bus contention.

Issue #39 remains OPEN; unsigned DIV/MOD family not complete.
