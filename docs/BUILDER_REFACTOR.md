# Builder refactor: operation-first selection (phase 1)

The future **C64 Math Library Builder** will replace user-facing V1–V5 profile
selection with a choice of mathematical **operations**, resource constraints,
and optimization goals. Historical images remain available as regression
oracles until the new linker meets the same correctness and timing contracts.

**A first real selective linker is now available for UDIV16, UMOD16, UDIV32_32 and UMOD32_32.**
These use separately qualified relocatable sources, not the historical
full-profile images or exact extracted resident mirrors. Other operations
remain selection-plan-only until their own source contracts pass qualification.
A mirror extracted from a resident image is not automatically a self-contained
or relocatable module.

## Try it

Browse the 56 stable operations without selecting a fixed profile:

```sh
python3 tools/math_builder.py --list
```

Create a plan for a new project:

```sh
python3 tools/math_builder.py \
  --operation UMUL16 --operation ATAN2_8 --operation ISQRT16 \
  --objective speed --zp-budget 20 --ram-budget 4096 \
  --out build_selective/selection_manifest.json
```

Or run interactively (a human-readable list grouped by operation).
For experienced users, an equivalent JSON configuration:

```json
{
  "target": "c64",
  "operations": ["UMUL16", "ATAN2_8", "ISQRT16"],
  "objective": "balanced",
  "constraints": {
    "max_zp_bytes": 20,
    "max_ram_bytes": 4096
  },
  "pins": {}
}
```

Use with `--config selection.json`. Both short `UMUL16`, historical
`MATH_UMUL16`, and typed `mul_u16_u16_u32` names resolve to the same
operation. Use `--preview` to print without writing.

Inspect the available *source* variants (with original provenance, SHA and
qualification status) using:

```sh
python3 tools/math_builder.py --variants UMUL16
```

An advanced selection can copy a content-derived variant ID from
`--variants UMUL16` and pin it with `--pin MATH_UMUL16=mirror:<sha-prefix>`.
Legacy source provenance remains in metadata but is **not a profile choice**.
A pin is a source preference for future linker integration, not proof of
linkability.

The plan records every source choice and explicitly sets:
`status=planning_only_not_a_loadable_binary`,
`unresolved_dependencies=true`, and `linker_status=not_implemented`.
No code size, cycle total or zero-page total is guessed by adding unrelated
routine figures. Standalone timing corpora may differ substantially.

## First compact build (experimental)

Generate a PRG containing only unsigned 16-bit division and/or remainder:

```sh
python3 tools/math_builder.py --operation UDIV16 --operation UMOD16 \
  --objective size --zp-budget 2 --ram-budget 1000 --build
```

Output in `build_selective/`:

- `math_selective.prg`: **585 code bytes**, plus the usual two-byte PRG load header.
- `math_api.inc`: only the selected callable symbols, plus shared I/O symbols.
- `selective_manifest.json`: entry addresses, source SHA, actual segments and RAM/ZP ownership.

The pair shares **2 ZP scratch bytes** (sequential, nonreentrant calls), a
**32-byte caller-owned I/O block**, and has a **617-byte total RAM claim**.
No other math operations, global lookup tables or fixed resident code are
included. For a one-routine 0-ZP modulo build, select:

```sh
python3 tools/math_builder.py --operation UMOD16 --objective zp \
  --zp-budget 0 --ram-budget 1100 --build
```

This selects the independently relocatable direct-chain engine: 976 code/table
bytes + 2 ordinary scratch bytes + 32 caller I/O bytes. It is slower than the
biased modulo source on the prior paired corpus, but uses no ZP. Pin explicitly
via `--pin UMOD16=link:direct-zerozp` or `--pin UMOD16=link:biased`.

The linker also supports full-width 32/32 division and remainder, reusing
the existing portable OptiSearch-derived C64 kernels:

```sh
python3 tools/math_builder.py --operation UDIV32_32 --operation UMOD32_32 \
  --objective size --zp-budget 4 --ram-budget 1200 --build
```

The size-oriented version selects the 544-byte UDIV32 ZP-tail and 496-byte
zero-ZP UMOD32: **1,040 code bytes, 4 shared ZP bytes, 4 ordinary scratch
bytes, and 32 public I/O bytes** (1,076 claimed RAM bytes). With
`--zp-budget 0`, it selects the 576-byte zero-ZP UDIV32 alternative
instead, for **1,072 code bytes and 1,108 total RAM bytes**. The 32-bit
operands and outputs occupy the full four-byte public I/O groups. Divisors
of zero set carry and return zero results, while modulo preserves Q.

**Performance caveat:** the portable 32-bit kernels can be slower than the
resident implementations, especially for certain small-divisor workloads.
These are the first *linkable* choices, not proven universal speed winners.
The optimizer currently enforces budgets globally and scores the few available
implementations by size/ZP trade-offs. An actual `--objective speed --build`
request is **rejected**, rather than pretending unrelated benchmark cycles are
comparable. The speed objective will be enabled after same-corpus qualification.

A JSON configuration can specify a custom, nonoverlapping memory map:

```json
{
  "operations": ["UDIV16", "UMOD16"],
  "objective": "size",
  "constraints": {"max_zp_bytes": 2, "max_ram_bytes": 1000},
  "memory": {"code_base": "$7123", "math_io": "$C040", "zp_base": "$60"}
}
```

The default code origin is `$8000`, public I/O at `$C000-$C01F`, and
shared scratch at `$50`–`$51` when needed. ROM underlay, I/O address
ranges, system stack, zero-page processor ports, address overflow, and
colliding source/data allocations are rejected. The public ABI preserves
N/D. Divide-by-zero sets C, clears Q/R for UDIV16; UMOD16 clears R while
preserving the caller's Q. `CLD` is required before calls.

**No broader optimized-variant claims yet:** fixed source variants and record
kernels with unrelated performance corpora are shown in the inventory but
cannot be silently selected for a compact build. An unsupported routine or
unsupported variant pin makes `--build` fail instead of loading 56 routines.

The compact linker is intentionally marked experimental pending native
VICE qualification; source/mixed-call CPU and native linked-image tests are
included in dedicated CI.

## Direction and acceptance criteria

1. **Inventory (implemented).** Index all 56 stable operations using
   `routines/SOURCE_CATALOG.csv`, retaining the current source, hash,
   provenance and validation distinctions. Offer interactive/JSON selection,
   variant inspection, pins and strict parameter validation. Preserve existing
   building and publication paths.
2. **Certified linkable module contracts.** Add explicit relocations,
   public input/output ABI, 6502 legality, writable-code needs, source and
   data dependencies, memory ownership, scratch lifetime, initialization,
   and benchmark-corpus identity. Deduplicate shared code and tables.
   Qualified *standalone* does not imply mixed-call or arbitrary-location safety.
3. **Real selective linker (initial UDIV16/UMOD16 implementation).** Assemble/link only the chosen operations and
   transitive dependencies; retain only necessary export stubs. Respect
   reserved ranges, code execution under ROM, stack and ZP conflicts.
   Measure actual linked byte ranges rather than summing reported footprints.
4. **Global constrained optimizer.** Choose among *certified linkable* variants
   for speed/size/ZP, obeying shared resource and hardware constraints.
   Exclude unverified or narrowly conditioned specialists from automatic
   general-purpose selection; allow explicit, checked opt-in.
5. **Full qualification before switching defaults.** Reproduce old V1–V5
   behaviors as fixtures, run exhaustive/edge/random and mixed-call tests,
   verify cycles on matching corpora and native CPU/VICE, check memory
   ownership, reproducible output, and generated-symbol correctness.
   Only then make operation-first selective builds the default.

Until step 5, existing profile binaries, REU image generation, the Pareto
builder and their published benchmark records remain untouched. The new
builder must never silently include all 56 routines when a user has selected
only a subset.

## Validation

```sh
python3 tools/test_math_builder.py
python3 tools/test_selective_linker.py
# or:
make builder-validate
```

The tests cover the real published 56-operation index, historical/typed
aliases, idempotent operation selection, pin errors, resource validation,
catalog checksum verification, deterministic plans, and hard rejection of
an unsupported selective binary.
