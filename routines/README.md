# Public routine sources

> **User installation:** use `make builder-setup`, not a source from one
> frozen V1–V5 resident directory. The source catalog and old profile mirrors
> remain essential immutable provenance records; actual linker selections
> and published implementations appear in the generated manifest.
> [Start here](../QUICK_START.md).


This directory is the public source index for the C64 Math Library.

There are two source classes:

1. **Shipped profile routines.** Every callable entry in V1-V5 has an exact typed `.asm` mirror in that profile's `standalone/` directory. These mirrors match the shipped executable after initialization and preserve the historical `MATH_*` ABI. The machine-readable index is [`SOURCE_CATALOG.csv`](SOURCE_CATALOG.csv).
2. **Liftable symbolic modules and standalone alternatives.** Human-facing source modules that are intended to be transplanted without reverse-engineering a resident disassembly live here under their operation family. `muldiv16/` is the first stable-API family whose integrated profile build now sources the same symbolic files exposed to developers. Independently benchmarked record/Pareto kernels (for example `multiply/mul_s24_s24_s48_fast24.asm`) live alongside them and are listed in [`../benchmarks/STANDALONE_RESULTS.csv`](../benchmarks/STANDALONE_RESULTS.csv).

## Publication rule

A performance number is considered publishable in this repository only when:

- the exact source is present in the repository;
- the source uses the typed naming convention from [`../docs/NAMING_STANDARD.md`](../docs/NAMING_STANDARD.md);
- the corresponding benchmark row names the source path and SHA-256;
- the validation/evidence path is present; and
- `python3 tools/validate_public_catalog.py` passes.

This prevents source-less benchmark claims and makes every published number traceable to code.

## Audit mirror versus liftable module

A file under `<profile>/standalone/` proves exactly what executable graph ships for one public entry. It is excellent for inspection and exact extraction, but shared tables/data are intentionally not duplicated, so it is not automatically a one-file drop-in module.

A curated module under `routines/` is the preferred copy/paste surface when one exists: it uses symbolic ABI/dependency names and is either sourced directly by the integrated build or independently benchmarked and validated. The project is moving stable families toward this model without weakening the exact audit mirrors.

For `MATH_UMULDIV16` / `MATH_SMULDIV16`, use [`muldiv16/README.md`](muldiv16/README.md): it documents the portable composed source and the faster V2/V3/V4 fused source plus their exact dependencies.

## Game movement

[`movement/`](movement/README.md) contains `seek_u8_u8_dda` (8-bit
coordinates, fastest) and `seek_u16_u8_dda` (16-bit x), exact Bresenham/DDA
"move toward target" steppers. It is the recommended alternative
to building target seeking on `MATH_VEC2_NORMALIZE_Q8_8`.

## Finding a routine

For the fastest overview, start with [`../PERFORMANCE.md`](../PERFORMANCE.md). For every shipped profile row, use [`../benchmarks/PUBLIC_PROFILE_RESULTS.csv`](../benchmarks/PUBLIC_PROFILE_RESULTS.csv). For standalone alternatives, use [`../benchmarks/STANDALONE_RESULTS.csv`](../benchmarks/STANDALONE_RESULTS.csv).

The source catalog currently indexes **295 shipped callable profile-entry mirrors** (including profile-specific REU extensions) plus **25 separately benchmarked standalone alternatives**. Profile-local duplication is intentional because each fixed profile remains self-contained. For direct links to recent UDIV/UMOD variants and to distinguish exact mirrors from truly liftable modules, see [the single-routine pickup guide](../docs/INDIVIDUAL_ROUTINE_PICKUP.md).

## Standalone fast-kernel collection

[The Issue #39 standalone fast-kernel lab](standalone_lab/README.md) publishes independently callable, source-backed fixed-map 6502 routines that can be useful even when they lose or cannot fit in a V1-V5 resident. Each candidate documents its ABI, memory ownership, comparable cycles and proof status. This is separate from the stable public API mirrors and fully curated standalone-results catalog.

The standalone lab also offers [individually configurable relocation modules](standalone_lab/portable/README.md), with machine-code-tested buffer/ZP remapping and native VICE result checks. These are independent alternatives, not integrated-profile replacements.

The isolated collection now also includes a [zero-ZP UMOD32 random-divisor specialist](standalone_lab/portable/mod_u32_aligned_carry.asm) with its full-spectrum performance caveat and ordinary-RAM scratch allocation.

A [zero-zero-page UDIV32 alternative](standalone_lab/portable/div_u32_aligned_nozp.asm) is included for projects that can spare four ordinary RAM bytes but have no free ZP. It is slower than the published V2-V4 resident on full and random workloads; read its [resource/performance qualifications](standalone_lab/portable/README.md) before pickup.
