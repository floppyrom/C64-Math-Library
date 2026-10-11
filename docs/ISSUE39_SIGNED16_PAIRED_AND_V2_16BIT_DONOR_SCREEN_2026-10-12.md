# Issue #39 — signed16 paired audit and rejected V2 UDIV16/UMOD16 donor gates

**Date:** 2026-10-12. **Status:** independently executable research **PASS**, no arithmetic publication or source promotion. The unsigned DIV/MOD campaign remains open.

## Why the existing 16-bit rankings seemed inconsistent

The earlier `SIGNED_DIVISION_VALIDATION.json` deliberately used a *different*
random seed per profile. Signed SMOD16/SDIV16 numbers from that file were
not a valid paired profile ranking.

`tools/audit_issue39_signed16_common.py` executes all five initialized,
real resident PRGs on **5,477 identical signed N/D operand pairs per API**:
**54,770 complete public API calls** across signed DIV16 and MOD16. It
verifies quotient, remainder, carry and preservation of N/D on every call,
including sign combinations, zero divisors and high-quotient stress.
The same operand SHA is used across all five profiles, with signed-quotient
class means and cycle-vector SHA-256 values in the machine-readable report.

For *both* signed APIs (which share the semantic signed divider):

| Profile | Measured cycles, common signed corpus |
|---|---:|
| v1_balanced | 229.477816 |
| v2_pareto_fast | 251.548475 |
| v3_reu_512k | 251.535877 |
| v4_reu_16m | 251.535877 |
| v5_hybrid_lowzp | 251.549388 |

V2 beats V1 on **4,491** individual operands, loses on
**985**, and ties on **1**;
yet V1 wins the overall mean because its q=2..31 path is much shorter:

| Absolute signed quotient class | Cases | V1 cycles | V2 cycles |
|---|---:|---:|---:|
| divisor zero | 152 | 45.000 | 54.513 |
| numerator zero | 31 | 95.419 | 83.548 |
| quotient 2 to 7 | 1,098 | 280.832 | 409.862 |
| quotient 32 plus | 274 | 1002.595 | 1024.551 |
| quotient 8 to 31 | 433 | 630.129 | 712.397 |
| quotient one | 1,172 | 147.957 | 123.529 |
| quotient zero | 2,317 | 93.973 | 78.919 |

Do **not** overwrite `PERFORMANCE.md`'s earlier signed-family
varied-seed correctness measurements with these values; the benchmarks use
distinct and explicitly labeled bases. These paired results support only the
specific deterministic sampled workload.

## Rejected V2 V1-donor 16-bit architecture

`tools/screen_issue39_v2_udiv16_donor.py` transplants the already certified
V1 323-byte UDIV16/UMOD16 core from reference $4200-$4342 to V2
$B000-$B142 in an *ephemeral CPU image*. It relocates the sole absolute
internal JMP. A 13-byte selector at $B200-$B20C selects V1 or V2 using
divisor-high thresholds. The original V2 arithmetic is preserved as fallback,
and **none of these bytes are shipped**.

The screen uses the existing exact same-input unsigned corpus, checks
Q/R/C for UDIV16 and R/C for UMOD16 (because UMOD16 does not promise
a quotient), and verifies both inputs unchanged. The complete lifted V1
core matches its original entry's cycle counts.

| Operation | Shipped V2 | Best gated V1-donor candidate | Outcome |
|---|---:|---:|---|
| UDIV16 | 161.761451 | 173.343349 (D-high >= 96) | +11.582 cycles, rejected |
| UMOD16 | 198.610557 | 216.641056 (D-high >= 64) | +18.030 cycles, rejected |

All tested threshold gates have a **slower aggregate mean**. At the
best threshold for each API, every case is slower. The lower thresholds
save a few isolated calls but lose substantially more on the remaining inputs. The theoretical zero-dispatch, per-case best-of-two *oracle*
for UDIV16 is 135.950165 cycles and for
UMOD16 158.631085; those numbers are **not
achievable measured implementations**. A productive next attempt must
optimize V2's q=2..9 *inside* its native branch or arithmetic dispatch
rather than impose an expensive new universal wrapper. Bounded
low-level mutations require live VICE, source relocation, V5-hybrid
isolation, same-input distributions, OptiSearch differential screening,
and full release qualification before adoption.

## Evidence and release status

- `validation/review/ISSUE39_SIGNED16_SAME_INPUT_AUDIT.json`
- `benchmarks/ISSUE39_SIGNED16_SAME_INPUT_AUDIT.csv`
- `validation/review/ISSUE39_V2_UDIV16_UMOD16_DONOR_SCREEN.json`
- `tools/audit_issue39_signed16_common.py`
- `tools/screen_issue39_v2_udiv16_donor.py`

All five resident PRG binaries, unsigned profile winners, signed routine
selection and published public-entry ABIs are **unchanged**. No new ZP,
table, resident RAM region, or stack depth has been committed. Private
OptiSearch remains outside the repository. Proof is restricted to the
specified input distributions and complete-resident source-executed
instruction counts.
