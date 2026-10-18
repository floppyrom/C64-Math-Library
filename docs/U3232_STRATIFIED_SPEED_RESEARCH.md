# Full-width 32/32 DIV/MOD cycle-tail audit

This is a **non-promoting, source-qualified performance investigation**, not a
change to the 56-operation builder, the 16 current speed objectives, or any
published V1–V5 resident performance baseline.

The existing `UDIV32_32` and `UMOD32_32` selectors report means from one
384-input corpus. Those means do not show how quotient range or divisor width
affects individual complete public-call costs. Before transplanting a new fast
producer, this audit makes the per-case tradeoffs visible.

## Run

```sh
python3 tools/test_audit_u3232_cycle_frontier.py
python3 tools/audit_u3232_cycle_frontier.py \
  --cases-per-band 64 --output build/u3232_stratified_cycles.json
```

The operation-first builder workflow uploads the complete JSON as the
`u3232-stratified-cycle-tails` artifact (30-day retention). The CI console
also prints every candidate's overall mean, p95, worst, RAM and ZP costs.

The required CI run repeats the complete 64-case-per-band analysis, once at
`$8000` and once at `$7123`, for both public APIs and every available
source-qualified candidate. Its JSON report contains source SHA-256, code size,
ZP and RAM scratch, original input fingerprint, complete-call mean, median,
nearest-rank p95, best and worst cycles, and paired per-band differences
(including faster/slower/equal counts and worst regression).

## Input bands

- Divisor zero (including the required C=1 and Q/R=0)
- Quotient zero (N less than nonzero D)
- Quotient one
- Quotient 2–15
- Arbitrary 8-bit divisor
- Arbitrary 16-bit divisor
- Arbitrary 24-bit divisor
- Arbitrary full-width 32-bit divisor
- Power-of-two divisor

Every band is independently reproducible with the fixed `0x32322027` seed.
There are exactly 64 inputs per band in the CI audit, 576 inputs per
candidate and code map. Bands are intentionally *overlapping semantic
classes* (e.g. power-of-two and 8-bit divisors), so the equal-band aggregate
is a diagnostic workload, not a representation of game usage probabilities.

## Qualification gates

Every call checks the arithmetic outputs appropriate to the selected API,
the full 32-bit remainder, the success/divide-by-zero carry, original
numerator/divisor bytes, caller SP, and the expected immutable executable
image. The matched source catalog is required unchanged; any new variant
needs its own source contract and qualification before entering this screen.

**Cycle values are deterministic mini6502 model cycles through RTS.** They
exclude VIC bus contention and REU DMA, and do not establish physical C64
latency or IRQ/NMI safety. Independent native VICE gates for the source-linked
shared zero-ZP producer remain mandatory. The audit itself does not emit or
promote new production binaries.

## How to use results

Prioritize candidate kernels that reduce p95 and worst-case cycles for
unrestricted ordinary callers without significant regressions in zero-divisor,
small-divisor, or quotient-one paths. A win on the published mean alone is
not sufficient. Use same-input paired comparisons rather than historical
native-only core timings; qualify any new candidate's register ABI, RAM/ZP,
source provenance, relocation, mixed calls, and native VICE behavior.
