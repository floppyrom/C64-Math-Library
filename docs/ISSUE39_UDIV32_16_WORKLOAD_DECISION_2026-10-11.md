# Issue #39 — V1 32/16 division workload sensitivity and no-promotion decision (2026-10-11)

## Scope and decision

The issue #39 campaign has a reproducible **identical-input cross-profile benchmark** for all unsigned DIV/MOD entries (136,335 public-entry calls, including divisor-zero/edge/random/quotient stress). Its mean is valid for **that corpus**, but the input distribution is not representative of every C64 demo, tool or game. Rankings must therefore be treated as workload-conditioned. This report adds a second, reproducible **30,720-call six-workload audit** for the 32/16 variants on all five profiles. It preserves the original corpus, its table, and all correctness validators unchanged.

A V1-specific 92-byte quotient-0/1 public-entry shortcut was investigated and **rejected** as the default Balanced implementation. It passed full **164,410 V1 unsigned and 97,329 signed** machine-code correctness calls, and the existing weighted corpus showed mean `UDIV32_16` **896.061561→832.177354** and `UMOD32_16` **916.280352→803.818182**. However, **2,482 of 2,729 division cases and 1,458 of 1,705 modulo cases became slower**, by as much as **51 cycles**, because almost every nonqualifying call pays a dispatch cost. Only 247 calls improved for each API. Thus an apparent 7% or 12% overall win on the edge-heavy corpus cannot justify selecting it as the default arithmetic engine.

An independent pre-publication evaluation with **4,000 common inputs for each workload**, comparing the merged PR #54 V1 binary against the q0/q1 trial:
| Workload | V1 original mean | Trial mean | Trial penalty/gain |
|---|---:|---:|---:|
| Uniform full-width 32-bit numerators | 857.972 | 874.972 | +17.000 |
| 24-bit numerators | 741.201 | 756.901 | +15.700 |
| Full-width numerator / small divisor 1–255 | 1699.786 | 1716.786 | +17.000 |
| Power-of-two divisors | 1473.294 | 1490.294 | +17.000 |
| 16-bit numerators | 667.480 | 398.979 | −268.502 |

These are distinct deterministic workload corpora rather than the primary leaderboard, and every case passed arithmetic correctness, carry and input-preservation checks. In particular, **0 of 4,000** full-width-uniform calls improved, while all **4,000** became 17 cycles slower. The trial is a niche fast path, not a generally superior V1 Balanced routine. **It is not merged and the shipped V1/V5 binary stays unchanged by this audit.**

## Permanent workload-specific performance evidence

The new public source `tools/benchmark_unsigned_3216_workloads.py` runs **six independently seeded 512-pair workloads**, including uniform full-width, 24-bit, 16-bit, small divisors, power-of-two divisors and deliberately targeted q=0/1 cases. For each API and five resident profiles, it verifies unsigned quotient/remainder/carry as appropriate, N/D ownership, and exact V2/V3/V4/V5 per-case cycle parity. It emits:
- `validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json`: per-scenario means, median, p95, extrema, operand hashes, resident hashes and cycle-vector hashes.
- `benchmarks/UNSIGNED_3216_WORKLOAD_AUDIT.csv`: readable per-profile, per-scenario comparison.

On the shipped post-PR54 V1 binary, a first source-executed run of this independent 512-pair suite produced the following representative UDIV32/16 means:

| Scenario | V1 Balanced cycles | V2/V3/V4/V5 cycles |
|---|---:|---:|
| Uniform 32×16 | 861.439 | 662.461 |
| 24-bit numerator | 733.881 | 556.438 |
| 16-bit numerator | 665.225 | 487.885 |
| Small divisor 1–255 | 1698.746 | 822.969 |
| Power-of-two divisor | 1494.492 | 861.100 |
| Quotient 0 or 1 | 659.979 | 482.658 |

V2–V5 remain faster than V1 for **all six measured scenarios**, so there is no hidden profile reversal to fix with the rejected V1 fast path. This is a **32/16 resource/algorithm-selection audit, not an optimization or blanket proof of global optimality**. We must continue investigating architecture choices and best-effort no-gain cases for the remaining unsigned families.

## Methodological commitments

1. Use **identical operands within a cross-profile comparison**, and retain independent profile-specific random inputs to broaden correctness coverage.
2. Publish explicit workload mix, means and high-percentile/worst-case cycles; never describe one weighted mean as universal speed dominance.
3. Keep arithmetic operands, carry, and public ABI checks in the benchmark itself, with SHA-256 fingerprints identifying the exact programs and inputs.
4. Guard the published artifacts through comparable-performance CI without overwriting the historical single-corpus leaderboard or rewriting existing PR-verified cycle numbers.
5. Do not cross the issue #39 unsigned DIV/MOD checklist item until all relevant configurations have auditable architecture and no-gain outcomes, green validation, and docs/changelogs synchronized.

No OptiSearch source code was used or published here; the rejected shortcut arose from manual 6502 architecture analysis.
