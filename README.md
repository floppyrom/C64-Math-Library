# C64 Math Library

**Use only the math your Commodore 64 project needs.** Choose from **56
individually selectable 6502/6510 operations**. The builder combines your
choices into one loadable C64 library, subject to your RAM and zero-page
limits. Prefer the raw assembly? You can reuse individual sources too.

**Start here:**
[See all routines](routines/PUBLIC_OPERATIONS.csv) ·
[Compare cycles, RAM, ZP and stack](docs/OPERATION_FIRST_ROUTINE_METRICS.md) ·
[Build your selection](#build-your-own-library) ·
[Pick up a single routine](#want-only-one-routine)

## What's available?

Signed and unsigned **multiplication, division, modulo** (including wide
integers), **square roots, sine/cosine, ATAN2, distance, fixed-point/vector
helpers, and movement/target-seeking routines**.

- [Full list of 56 operations](routines/PUBLIC_OPERATIONS.csv) — names and types.
- [Consolidated performance table](docs/OPERATION_FIRST_ROUTINE_METRICS.md) — mean CPU cycles per call, code/tables, total isolated RAM, zero-page bytes, and persistent stack-page reservation.
- [All implementation variants (CSV)](benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv) — compare alternative sources for the **same operation**, including the original source file and measured trade-offs.
- [Combined-project performance charts](PERFORMANCE.md) — examples of speed/memory choices after linking.

**How to read the numbers:** per-routine RAM figures are for **isolated
builds**, not additive totals. The stack column excludes temporary
JSR/RTS/interrupt use; cycle means are CPU-model measurements, not
guaranteed PAL frame times. Your final build reports its actual linked
RAM and ZP usage.

## Build your own library

**Requirements:** Python 3.12+ and Make. The normal builder includes its
own assembler.

From the repository folder:

```sh
make builder-setup
```

The guided setup lets you:

1. **Select exactly the operations you want.**
2. **Choose an objective:** `balanced` (general trade-off), `speed`
   (measured cycles), `size` (minimum RAM), or `zp` (minimum zero page).
3. **Set your RAM/ZP budgets.** Speed mode also asks how often you expect
   to call each operation.

It produces four files:

| File | Purpose |
| --- | --- |
| `my_math.json` | Editable selection and build settings |
| `build_my_math/math_selective.prg` | Your C64 library to load |
| `build_my_math/math_api.inc` | Correct entry points and operand addresses |
| `build_my_math/selective_manifest.json` | Selected sources and **actual RAM/ZP placement** |

**To call it:** Load the generated PRG, include its matching
`math_api.inc` in your assembly project, write operands to the exported
math I/O locations, call the selected entry (for example,
`JSR MATH_UMUL16`), and read the documented
result/Carry. Do **not** hardcode addresses from old releases.
See [API instructions](docs/API_COMPATIBILITY.md).

Prefer a scripted build? This selects only multiplication, division and
integer square root:

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --operation UDIV16 --operation ISQRT16 \
  --objective balanced --zp-budget 8 --ram-budget 4096 \
  --config-out project-math.json --build-dir build_project_math
```

To edit and rebuild, change the JSON and run
`make builder CONFIG=project-math.json OUT=build_new_math`.
The guided setup won't overwrite an existing config/build directory.
See the [full configuration guide](docs/OPERATION_FIRST_USER_SETUP.md)
for custom memory maps, variant pins and speed call counts.

## Want only one routine?

**Option A — ready to use:** Run `make builder-setup` and select just
`UMUL16` (or any other operation). You get a **one-operation PRG**,
its API include and a manifest; the builder supplies required dependencies.

**Option B — lift the assembly:** Find your operation in the
[variant CSV](benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv), choose
an implementation, and open its `source_path`. The
[single-routine pickup guide](docs/INDIVIDUAL_ROUTINE_PICKUP.md) explains
how to inspect dependencies and ABI conventions. See also
[curated sources](routines/README.md) and
[portable standalone kernels](routines/standalone_lab/portable/README.md).

**Not every `.asm` file is a drop-in module.** Some require shared tables,
RAM/ZP scratch, generated symbols or initialization. For a tested,
complete one-operation build, use Option A.

## More for advanced users

[Detailed setup](docs/OPERATION_FIRST_USER_SETUP.md) ·
[API and calling conventions](docs/API_COMPATIBILITY.md) ·
[Validation](docs/BUILDER_RELEASE_ACCEPTANCE.md) ·
[Optional REU acceleration](docs/REU_OPERATION_FIRST_CONSOLIDATION.md) ·
[Historical REU compatibility archive](docs/REU_COMPAT_EXPORT.md) ·
[Historical performance archive](docs/PERFORMANCE_ARCHIVE_HISTORICAL_RESIDENTS_2026-10-21.md) ·
[Older research documentation](docs/README_RESEARCH_ARCHIVE_2026-10-21.md) ·
[Changelog](CHANGELOG.md).

## Optional REU acceleration

The same installer also supports **one optional REU service per project**:
`--reu-turbo16` (16-bit multiply), `--reu-turbo32` (32-bit multiply),
or `--reu-qs16` (16-bit quarter-square lookup; **16MiB REU required**).
Each builds an independent, source-linked REU PRG plus a normal stock-C64
fallback, API include, and combined memory manifest. No legacy V3/V4
resident is required for these new module builds.

For example:

```sh
python3 tools/configure_math.py --operation UMUL32 --objective size \
  --ram-budget 30000 --zp-budget 210 --reu-turbo32 \
  --config-out reu-math.json --build-dir build_reu_math
```

The REU service must pass runtime INSTALL before BEGIN/CALL/END.
Multiple REU services in one project, IRQ use of overlaid ZP, and
PAL/VIC/SID real-time coexistence remain **unqualified**.
See [REU setup and limits](docs/REU_OPERATION_FIRST_CONSOLIDATION.md).

**New projects use the operation-first builder, not V1–V5 installation
profiles.** Historical residents remain immutable regression archives,
not dependencies of the new modules. 1541/1571/1581 math backends
remain future work.

**License:** [MIT](LICENSE).
