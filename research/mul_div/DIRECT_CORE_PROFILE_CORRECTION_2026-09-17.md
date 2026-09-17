# V2 direct MUL_DIV profile provenance correction

**Date:** 2026-09-17  
**Scope:** M2 MUL_DIV research only. No shipped binary or stable API is changed.

A fresh source/provenance audit found that the first V2 `direct` and
`direct_hybrid` MUL_DIV experiments targeted the wrong internal multiply ABI.

## Actual shipped V2 multiply layout

`v2_pareto_fast/resident/math_pareto_fast.asm` defines:

```text
I_UMUL8  = $5300
I_UMUL16 = $5400
```

The implementation installed at `$5400` is
`resident/modules/pareto_umul16.a`: a practical integrated **3xUMUL8**
difference-product construction using the selected Pareto UMUL8 at `$5300`.

The repository also contains `resident/modules/record_umul16_17zp.a`, but that
is a separate record/research source. Its `generic` / `same_x` entry geometry is
not the implementation installed at `$5400` in the shipped V2 resident image.

## What the historical direct experiment assumed

`generate_umuldiv16.py` encoded a record-core contract around:

```text
core entry   $53EC
same_x       $5400
X low bind   $21
X high bind  $29
Y high SMC   $541A
```

and the old `benchmark.py` patched those generated wrappers into the shipped V2
image.

Because `$5400` in that image is actually `pareto_umul16`, the historical
`direct` / `direct_hybrid` variants did not execute the intended record-core
handoff. Their zero-error reports and cycle figures therefore **must not be used
as shipped-V2 evidence**.

This supersedes the old direct columns in `BENCHMARK_RESULTS.md`, including the
previously quoted figures such as:

```text
815.893 cycles  bounded_uniform direct
675.137 cycles  mixed_uniform direct
294.563 cycles  game8 direct_hybrid
752.297 cycles  game12_bounded direct
```

Those numbers are retained only as historical research output until the old
artifacts are regenerated or archived.

## What remains valid from the original benchmark

The following variants enter through interfaces that really exist in the
shipped image and are not affected by the record-core provenance error:

```text
composed
    public MATH_UMUL16 + public MATH_UDIV32_16

fused
    public MATH_UMUL16 + constrained 16-step bounded tail

hybrid
    public MATH_UMUL16 + native V2 UDIV16 small-product path
    + constrained tail otherwise
```

Their existing same-input arithmetic/timing evidence remains relevant.

The mathematical bounded-tail result also remains valid:

```text
for product = hi:lo and uint16 divisor d,
quotient fits uint16 iff hi < d;
when hi < d, hi is already a valid initial remainder and only 16 low product
bits need to be streamed through the restoring tail.
```

## Corrected actual-core direct path

The replacement generator is:

```text
research/mul_div/generate_umuldiv16_pareto.py
```

It inlines the actual shipped V2 3xUMUL8 algorithm and keeps the resulting
32-bit product live:

```text
mq0 = product byte0
mq1 = product byte1
mr0 = product byte2
A   = product byte3
```

The direct candidate then enters the constrained 16-step divider without
publishing/reloading the product through the public Z vector.

The corrected hybrid additionally uses real small-product geometry:

```text
high16 == 0:
    direct q=0
    direct q=1
    otherwise native V2 UDIV16 ($420C)

high16 != 0:
    bounded-fit test
    constrained 16-step tail
```

All research scratch stays inside the V2 normal transient arithmetic window;
no new persistent ZP allocation is introduced.

## New benchmark gate

`benchmark_pareto_direct.py` compares only source/profile-consistent variants:

```text
composed
fused
hybrid
pareto_direct
pareto_direct_hybrid
```

on the existing structured edge suite and the same deterministic corpora:

```text
bounded_uniform
mixed_uniform
game8
game12_bounded
```

It explicitly excludes the historical record-core `direct` names.

At the time of this note, the new harness and actual-core generators have been
committed but **have not yet been executed in this environment**. Therefore no
new direct cycle number is promoted here.

## Rule going forward

For profile-specific fused research, an internal routine may only be called
"resident-image evidence" when the benchmarked entry point is traced to the
implementation actually installed in that profile. Standalone record sources
remain valuable optimization references, but their addresses or lifecycle
contracts must not be inferred to be active profile ABIs without build/source
provenance confirming that fact.
