# Public routine sources

This directory is the public source index for the C64 Math Library.

There are two source classes:

1. **Shipped profile routines.** Every callable entry in V1-V5 has an exact typed `.asm` mirror in that profile's `standalone/` directory. These mirrors match the shipped executable after initialization and preserve the historical `MATH_*` ABI. The machine-readable index is [`SOURCE_CATALOG.csv`](SOURCE_CATALOG.csv).
2. **Standalone alternatives / record-Pareto points.** Independently benchmarked kernels that are useful outside a fixed profile live here under their operation family, for example `multiply/mul_s24_s24_s48_fast24.asm`. These are listed in [`../benchmarks/STANDALONE_RESULTS.csv`](../benchmarks/STANDALONE_RESULTS.csv), including timing basis, ZP, stack reservation, source hash and validation evidence.

## Publication rule

A performance number is considered publishable in this repository only when:

- the exact source is present in the repository;
- the source uses the typed naming convention from [`../docs/NAMING_STANDARD.md`](../docs/NAMING_STANDARD.md);
- the corresponding benchmark row names the source path and SHA-256;
- the validation/evidence path is present; and
- `python3 tools/validate_public_catalog.py` passes.

This prevents source-less benchmark claims and makes every published number traceable to code.

## Game movement

[`movement/`](movement/README.md) contains `seek_u8_u8_dda` (8-bit
coordinates, fastest) and `seek_u16_u8_dda` (16-bit x), exact Bresenham/DDA
"move toward target" steppers. It is the recommended alternative
to building target seeking on `MATH_VEC2_NORMALIZE_Q8_8`.

## Finding a routine

For the fastest overview, start with [`../PERFORMANCE.md`](../PERFORMANCE.md). For every shipped profile row, use [`../benchmarks/PUBLIC_PROFILE_RESULTS.csv`](../benchmarks/PUBLIC_PROFILE_RESULTS.csv). For standalone alternatives, use [`../benchmarks/STANDALONE_RESULTS.csv`](../benchmarks/STANDALONE_RESULTS.csv).

The source catalog contains all **245** shipped callable profile entries plus the separately published standalone alternatives. Profile-local duplication is intentional because each fixed profile remains self-contained.
