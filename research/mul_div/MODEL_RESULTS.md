# MUL_DIV preliminary model results

**Status:** research only; not a resident-image certification.

This note records the first arithmetic/cycle-geometry pass for the bounded unsigned target:

```text
q = floor((a*b)/d)
r = (a*b) mod d

0 <= a,b <= 65535
1 <= d <= 65535
q <= 65535
```

## Correctness observation

Let the 32-bit product be:

```text
p = hi * 65536 + lo
```

Then:

```text
q <= 65535  <=>  p < d*65536  <=>  hi < d
```

So once `hi < d` is established, the upper quotient word is known to be zero. `hi` is already a legal initial remainder (`0 <= hi < d`), and exactly 16 low-product bits remain to be consumed.

That reduces the division phase to a constrained 16-step restoring tail instead of a general 32/16 quotient problem.

The recurrence used by `model.py` is:

```text
qpipe = lo
rem   = hi

repeat 16 times:
    incoming = top_bit(qpipe)
    qpipe <<= 1
    rem = 2*rem + incoming
    if rem >= d:
        rem -= d
        qpipe |= 1
```

The generated 6502 form pipelines each trial result through Carry: the subtraction decision from one step is consumed by the next step's `ROL` as the quotient bit. After the sixteenth trial, one final `ROL` inserts the last decision.

## Independent model validation

The Python model was exercised on:

- an 11-value structured edge set for all `(a,b,d)` combinations;
- 1,000,000 deterministic uniform random triples using seed `$C0FFEE` and nonzero divisors.

Random-domain classification:

```text
input triples      1,000,000
16-bit quotient      749,126
overflow              250,874
model mismatches            0
```

The recurrence matched Python's exact integer `divmod(a*b,d)` for every tested bounded case and correctly classified overflow using `hi >= d`.

## Scratch-placement cycle geometry

The table below models the unrolled 16-step divide phase. It includes scratch setup/writeback, final Carry insertion, `CLC` and `RTS`. It excludes the preceding `MATH_UMUL16` and product-range test. It also excludes branch page-cross penalties; those belong to the assembled resident-image benchmark.

| Placement | Live scratch bytes | Mean | Min | Max |
|---|---:|---:|---:|---:|
| public/absolute only | 0 | 652.820 | 492 | 948 |
| remainder low in ZP | 1 | 635.885 | 490 | 906 |
| divisor in ZP | 2 | 638.741 | 490 | 906 |
| quotient in ZP | 2 | 646.820 | 486 | 942 |
| remainder + divisor in ZP | 3 | 621.806 | 488 | 864 |
| quotient + remainder in ZP | 3 | 629.885 | 484 | 900 |
| quotient + divisor in ZP | 4 | 632.741 | 484 | 900 |
| quotient + remainder + divisor in ZP | 5 | **615.806** | **482** | **858** |

The five-byte form is selected for the first generated kernel.

Importantly, those five live bytes map to the library's existing unsigned-division ZP ABI:

```text
$12 d0
$13 d1
$14 q0
$15 q1
$16 r0
```

They therefore cost **zero incremental profile ZP** in the current library: ordinary math calls are sequential, and the resident divider already clobbers these locations as part of its normal operation.

## What remains to measure

The model deliberately does **not** claim a final speedup. The next result must come from `benchmark.py`, because only the assembled image captures:

- the selected profile's real `MATH_UMUL16` timing on the same `(a,b,d)` inputs;
- branch page crossings inside the unrolled tail;
- public-entry/adaptation costs;
- the exact composed baseline (`UMUL16 -> copy -> UDIV32_16 -> copy`) on the same corpus;
- profile differences between V1, V2 and V5.

Only after that paired benchmark should this candidate be considered for promotion or further hand optimization.
