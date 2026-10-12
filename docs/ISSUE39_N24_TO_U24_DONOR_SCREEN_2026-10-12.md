# Issue #39 — N24-to-UDIV24 reuse under the 32/16 public contract

12 October 2026. **Research-only no-gain finding: keep default engines.**

Manual architecture candidate: when the 32-bit numerator fits in 24 bits,
call the existing 24/24 unsigned producer ($3170) instead of the 32/16
producer. A 30-byte RAM helper saves/restores D2 and R2, zeros D2 for
the call and clears Q3. It retains full Q32/R16/carry, untouched high
remainder, dividend/divisor, sentinels and stack behavior for both public
32/16 aliases. This is a dependent helper, **not** a standalone divider.

All five exact resident images SHA-pinned against RELEASE_STATUS, two
caller RAM placements ($0800 and $0B00), 11,580 paired operand tests,
23,160 complete 6502 executions, zero observed arithmetic/ABI mismatch.
The 30-byte helper uses four temporary bytes of return/data stack and
no new persistent normal zero-page space. No native VICE claim and no
real C64 VIC/REU contention model in the cycle measurements.

| Profile | Public API | N24/D8 delta | N24/D>=256 delta | N16/D>=256 delta | Q=0 delta |
|---|---|---:|---:|---:|---:|
| v1_balanced | MATH_UDIV32_16 | -538.52 | +457.24 | -293.12 | -447.00 |
| v1_balanced | MATH_UMOD32_16 | -541.52 | +454.24 | -296.12 | -450.00 |
| v2_pareto_fast | MATH_UDIV32_16 | +146.08 | +248.08 | -174.70 | -335.00 |
| v2_pareto_fast | MATH_UMOD32_16 | +143.08 | +245.08 | -177.70 | -338.00 |
| v3_reu_512k | MATH_UDIV32_16 | +146.08 | +248.08 | -174.70 | -335.00 |
| v3_reu_512k | MATH_UMOD32_16 | +143.08 | +245.08 | -177.70 | -338.00 |
| v4_reu_16m | MATH_UDIV32_16 | +146.08 | +248.08 | -174.70 | -335.00 |
| v4_reu_16m | MATH_UMOD32_16 | +143.08 | +245.08 | -177.70 | -338.00 |
| v5_hybrid_lowzp | MATH_UDIV32_16 | +146.08 | +248.08 | -174.70 | -335.00 |
| v5_hybrid_lowzp | MATH_UMOD32_16 | +143.08 | +245.08 | -177.70 | -338.00 |

Values are mean **candidate minus current public entry** cycles;
positive means slower. Genuine 24-bit numerators with D>=256 lose
in every profile in the screened class. Some special Q=0 and N16
inputs win, but the separately released 12-byte N16 opt-in helper
already addresses the latter without using the bulkier 24-bit core.
No default or public ABI change is justified by this architecture.

Exact per-class faster/slower counts, hashes, edge/divide-zero tests
and two-map proof are in validation/review/ISSUE39_N24_U24_DONOR_SCREEN.json.
Re-run on current checked-out residents:
python3 tools/screen_issue39_n24_u24_donor.py --out /tmp/n24.json

This is one **manual architecture** rejection, not an exhaustive
OptiSearch 24-bit architecture result, proof of mathematical timing
optimality, or completion of issue #39. The family remains OPEN.
