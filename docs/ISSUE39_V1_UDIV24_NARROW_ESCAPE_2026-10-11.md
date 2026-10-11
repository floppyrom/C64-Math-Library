# Issue #39: V1 Balanced 24-bit high-quotient latency escape (2026-10-11)

**Scope:** V1 24-bit unsigned division and its shared modulo alias only. This is a **latency/Pareto trade-off**, not a strictly no-regression micro-optimization, not an OptiSearch-discovered faster whole engine, and not closure of the unsigned DIV/MOD campaign.

## Why V1 was slower

The main previous V1 delay was **not merely the V1 q0counter t19/k9 source having fewer unrolled stages than V2's t13/k13**. V2 has an additional `division_latency_escape.inc` that diverts sufficiently large 24-bit quotients to its already-fast 32/16 engine. V1 lacked that shortcut. On identical operands, the old V1 tail ran a 24-round alignment/restoring path, whereas the V2 path delegated to optimized 32/16.

V1 uses a smaller Balanced implementation (1,123 original 24-bit core bytes versus ~2,490 in the selected V2 24-bit core), and V1 32/16 is itself slower than V2. **Full V2 transplantation is therefore not resource- or Pareto-equivalent.**

## Conservative implementation

The original high-dividend fast front end preserves `X=N2` from its LAX. It branches to `DU24B_low_d2` when `N2>0` and `D2=0`. Only this path receives one extra absolute JMP to the private gate; the `N2=0` small-quotient path retains its original exact instruction sequence and cycle timing.

From the gate, if `D1==0` and `X>=D0`, then `N>=D<<16` (nonzero narrow D), establishing `Q>=65536`. The code preserves original `N3` across a `JSR MATH_UDIV32_16`, then clears `R2`. All other cases jump to the old UDIV24 tail unchanged. The normal V1 31-byte zero-page ownership and all 56 public ABI addresses are preserved.

A private helper is placed at `REG_TABLE+$1FA0` (reference `$7FA0`), outside V5's relocated SDIV24 private islands (which occupy `$7678–$7F78`). Both V1 and V5 source-generated residents still occupy the same 49,042-byte PRG length. V5 inherits the now-unused private helper bytes, while its public UDIV24/UMOD24 use the V2 donor and retain the same cycle vectors.

## Independent paired old/new results (same exact inputs)

A **4,753-call UDIV24** / **1,553-call UMOD24** deterministic matched-input corpus, old merged source versus candidate:

| V1 public routine | Old mean | New mean | Faster calls | Slower calls | Largest slowdown |
|---|---:|---:|---:|---:|---:|
| UDIV24 | 189.741847 | **179.964654** | 84 | 56 | +19 cycles |
| UMOD24 | 306.577592 | **276.590470** | 78 | 35 | +19 cycles |

The paired old/new run has **6,306 calls, zero arithmetic/carry/input changes**. The 91 slower cases are mostly additional classifier instructions on N2>0 but moderate-quotient tails. This is an explicit acceptance criterion: average performance and hard-case latency improve, but **not all calls are faster**. On `$FFFFFF / $000001`, **3235 → 1986 cycles** (−1249). On `$FFFFFF / $000002`, 3097 → 1976. Any change in the balanced-profile resource policy would require re-evaluating this selection.

The authoritative **cross-profile** ranking uses the issue #39 common-input comparator (136,335 calls across all 11 unsigned APIs, all V1–V5), not the historically different-seed profile validator.

## Qualification

Locally proved: exact V1 symbolic reference and alternate builds; 56 public entries / 21,678 calls in V1 alternate map; **164,410 V1 unsigned + 97,329 V1 signed** and **164,410 V5 unsigned + 36,273 V5 signed** machine-code calls; all pass. Real VICE x64sc 3.13.2 paired old/new spot checks exercised **16 UDIV24/UMOD24 calls each on V1 and V5** (64 total), including zero divisor and max dividend; outputs/carry identical and correct. V5 source-generated reference and alternate hybrid builds pass. The release workflow must still qualify all profiles, public source mirrors, common-input ranking evidence, hashes, complete packaging and CI before merging.

Source-generated candidate reference resident SHA-256:
- V1 `1a81ec4f8ded86353c919e531bf4e8030a48cf86cac2f3758fff2878f3ae83b7`.
- V5 `d3b654f56f7ddfe26ce7130d5e925fdde85e41875e7da4bcd5aafe62440483a7`.

**OptiSearch provenance:** The optimization is a **manual architectural transplant** inspired by comparing the Repose/OptiSearch-derived V2 architecture against the V1 selected footprint and constrained 31-byte ZP budget. The private optimizer project is not published. This does not constitute a globally exhaustive OptiSearch certification of V1.

**Open:** Additional V1 low-ZP tail refinements, complete other unsigned resource-class manual/OptiSearch screens, no-gain conclusions, and later issue #39 campaign families. Leave the unsigned DIV/MOD issue checkbox unchecked.
