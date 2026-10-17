# Operation-first builder — deterministic migration cycle baseline

After all 56 stable operations became independently source-linkable, the next
step is to **measure the real assembled standalone kernels**, rather than
mistaking legacy V1–V5 reference-profile averages for their performance.

`tools/bench_selective_migrations.py` records model-measured public-call
cycles for the last six source migrations:

- `SMUL32_SHR16`
- `SMUL32_READY` and `UMUL32_READY`
- `SMULDIV16` and `UMULDIV16`
- `VEC2_NORMALIZE_Q8_8`

Each operation is built **individually** with the operation-first selective
linker. For each it checks exact output and carry semantics, preserves
caller inputs and stack, records the assembled source SHA-256 and real code,
main-RAM and zero-page usage, and measures all 256 canonical cases on
**two** code/I/O/ZP placements. The measurement is a Mini6502 CPU model
call through RTS, not VICE wall-clock timing.

The three fixed input corpora are `mul32` (shared by all three 32-bit
multiply variants), `muldiv16` (shared by signed and unsigned fused
multiply/divide) and `vec2` (signed two-axis vectors, including zero
and domain extremes). Each corpus has a deterministic seed and serialized
SHA-256. The means, medians, p90s, maxima and corpus SHA values are printed
as a JSON document; no measurements are fabricated or committed before
the CI job actually executes.

```sh
python3 tools/bench_selective_migrations.py
```

**Interpreting the report:** comparing signed and unsigned operation means
does *not* establish a global mixed-operation speed ranking. The benchmark
basis only becomes a candidate-selection basis **within the same operation**
after a faster historical source is transplanted, proven relocatable,
measured on the **identical inputs and placements**, and charged for its
tables, scratch, normal/persistent ZP, initialization and any SMC/REU
requirements. READY candidate state lifetime and interrupt safety must
be preserved in mixed operation calls.

No reference profile code or timing data is changed by this benchmark.
The full spectrum from V1–V5 and OptiSearch remains a separate import and
qualification effort. Resource/global optimization must account for
physically shared source/table/state, not sum each operation independently.
