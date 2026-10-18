# Biased quarter-square tables and carry-neutral partial products

**Retained research technique — do not discard during operation-first migration.**

This note preserves the exact source-backed idea highlighted in Repose's
October 2026 CSDB discussion: quarter-square tables need not store the
unbiased floor of a square divided by four. Carefully chosen table offsets
can encode arithmetic corrections *before* partial products are combined,
reducing explicit carry/borrow handling later. Repose has independently
experimented with n²/4+k. His CSDB feedback recognizes the usefulness of
this particular application. This note records the implementation without
making a claim of priority or suggesting that every offset is safe.

## Mathematical invariants

For an 8-bit operand pair, define the quarter-square lookup

    Q_k(n) = floor(n*n/4) + k * (n & 1),  0 <= n <= 510

For any unsigned bytes a and b, a+b and |a-b| have the same parity,
so the extra parity-dependent offset cancels:

    Q_k(a+b) - Q_k(|a-b|) = a*b.

The existing shifted UMUL16 candidate sources use k = 202 ($CA).
For all 511 possible square-table indices, Q_202(n) mod 256 is
**never $FF**. Consequently, Q_202(n)+1 never carries into the next
byte. A table holding the low byte of Q_202(n)+1 can therefore reuse
the *unmodified* high-byte plane of Q_202(n). This is a table-layout
invariant, not a general guarantee about arbitrary biased tables.

Their second idea is an algebraic redistribution of adjacent partials:

    (x0*b + 256) + 256*(x1*b - 1) = (x0 + 256*x1)*b.

The first partial's +256 is counterbalanced by the next partial's -1.
This lets selected cross-byte carries/borrows be pre-accounted for in
the table representation. An implementation must still prove its
6502 carry state at each instruction and how the signed/negative
prefixes compose; the identity alone does not prove an ASM routine.

## Concrete certified historical sources

- `routines/multiply/mul_u16_u16_u32_shifted99.asm`
- `routines/multiply/mul_u16_u16_u32_shifted106.asm`
- `routines/multiply/mul_u16_u16_u32_shifted116.asm`
- `routines/multiply/mul_u16_u16_u32_shifted134.asm`

Each retains the same PARITY_BIAS=$CA, tables for sqr_lo, sqr_hi,
neg_sqr_lo, neg_sqr_hi, sqr_hi_plus1 and neg_sqr_lo_plus1, and
reported standalone validation. The two additional table planes
implement high-byte +256 and low-byte +1 changes without changing
the arithmetic result. These are **specialized native 6502 ABI**
UMUL16 kernels, not already qualified as full operation-first public
ABI producers. Their large writable zero-page code footprints and
3,066-byte tables are real costs and must be charged to the installer.

Run `python3 -m unittest discover -s tools -p
'test_biased_quartersquare_offsets.py' -v` to check the 511 table indices,
all 65,536 byte-pair products, the no-low-wrap condition, and the
adjacent-product redistribution (plus lock the source constants).

## Transplant / speed promotion gate

1. Preserve the exact four historical sources and standalone benchmark
   records. No modification of fixed V1–V5 reference images.
2. Relocate source and code/table ownership, account for writable
   executable ZP, scratch, alignment, table sharing, illegal opcodes,
   initialization, non-reentrancy, and any fast READY entry preconditions.
3. Qualify complete `MATH_UMUL16` public I/O and its 32-bit output
   semantics under at least two code/data/ZP placements in CPU-model
   **and native VICE**.
4. Compare against every currently selectable UMUL16 alternative on
   **the same public-call input corpus**. Record mean, max, p95,
   memory/ZP, all slow-call regressions and real frame-budget impact.
   The historical standalone fresh-X mean of about 154 cycles is
   **not** an interchangeable builder public-call number.
5. Retain this donor as a Pareto alternative if it offers a true
   speed/resource benefit; select it automatically only when qualified,
   genuinely faster on the specified workload and within budget.

**Never replace a previously faster qualified builder kernel solely
because a new one is simpler to relocate.** A size/ZP fallback has
value, but it must not be described or selected as a speed upgrade.
