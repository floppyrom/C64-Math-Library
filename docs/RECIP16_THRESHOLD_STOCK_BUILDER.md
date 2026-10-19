# Stock-C64 Q16 reciprocal — V3/V4 threshold-strategy migration

This work targets `MATH_URECIP16_Q16` without selecting an old V1–V5
profile or requiring a RAM expansion unit. It does **not** transplant the
historical V3/V4 REU binary: it adopts the source-documented integer
threshold strategy and provides independent no-REU producers.

## Exact public API

For unsigned D16, output Q24 = floor(65536 / D) on D != 0 and clear C.
For D=0, Q24=0 and set C. Preserve D0/D1, public numerator N0..N3,
Q3, all remainder bytes, caller stack depth and unrelated memory.
A/X/Y are volatile and the routine expects decimal mode off.

## Resource/algorithm choices

| Candidate | Executable+tables | ZP | Ordinary scratch | Hardware |
|---|---:|---:|---:|---|
| `link:compact-zerozp` | 99 B | 0 | 1 B | Stock |
| `link:threshold-zerozp` | 448 B | 0 | 1 B | Stock |
| `link:threshold-tables-zerozp` | 1,544 B | 0 | 0 B | Stock |

The first is the original portable 24-step exact restoring routine.
The second applies the historical V3/V4 quotient 1..15 threshold ladder
to D>=4097 and calls the **unchanged** compact routine below that boundary.
On an identical 512-input, small-divisor-heavy complete public corpus,
its mean is 556.11 rather than the compact source's 1134.56 CPU-model
cycles at both tested origins. It **has a higher slow-call maximum**,
1716 vs 1634 cycles, and must not be represented as a worst-case speed win.

The table variant uses exact Q24 byte tables for D=1..255, a constant for
D=256, a 1..4 historical threshold shortcut for common large divisors,
and eight exact quotient-bound comparisons for the remaining D>=257.
It reserves five fixed 256-byte tables (Q0/Q1/Q2 and threshold high/low)
plus eight single-bit masks. Tables are private immutable ROM-compatible
bytes; no REU, mutable executable code, preload, INIT, or ZP dependency.
The full emitted code+table image is fixed at 1,544 bytes, independent of
its two tested origins. Worst-frame model performance, exact source
relocations and native VICE must pass before release.

## Qualification, comparability and remaining work

- `tools/test_recip16_threshold_builder.py` checks full public ABI and
  512 identical divisors at two code origins, speed selection and exact RAM
  limits. Initial source model and native VICE tests passed for the
  threshold-only fast path.
- `tools/test_recip16_table_builder.py` additionally checks all **65,536**
  divisors through the exact public CPU-model implementation, both linked
  relocations, resource constraints and three-way matched cycle results.
- Native VICE r46284 runs both new source-linked candidates from genuine
  PRGs at both memory placements with the established independent oracle.
- Do **not** compare these public-call averages to historic REU resident
  instruction timings or interpret their CPU-model frame estimates as
  physical VIC-II/IRQ/REU frame timing. True profile-retirement parity
  requires re-running the identical public corpus against each feasible
  historical source and measuring combined workloads.
- The historical V3/V4 REU reciprocal remains a separate
  hardware-specific performance baseline and is not removed.

Use `python3 tools/math_builder.py --variants URECIP16_Q16` to list
the options. Under `objective=speed`, supply a positive call count and
realistic RAM/ZP budgets. The builder must choose the fastest qualified
candidate **within** those constraints; it must never silently call a
size fallback a speed improvement.
