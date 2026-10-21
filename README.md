# C64 Math Library

**Pick the math routines your Commodore 64 project needs — and leave the rest out.**

The library offers **56 individually selectable 6502/6510 math operations**.
Choose only the operations you need; the builder links their code, tables and
dependencies into a C64 `.prg`, while respecting your RAM and zero-page limits.
You can also inspect and reuse the source in your own project.

**New here? Choose what you want to do:**

| I want to… | Start here |
| --- | --- |
| **See what routines are available** | [Browse all 56 operations](routines/PUBLIC_OPERATIONS.csv) or run `make builder-list` |
| **Compare speed and memory use** | [Cycles / RAM / ZP / stack table](docs/OPERATION_FIRST_ROUTINE_METRICS.md) |
| **Compare alternative implementations** | [Full per-variant CSV](benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv) |
| **Build my own selection** | [Quick start](#build-a-library-for-your-project) |
| **Take just one routine's source** | [Single-routine pickup guide](docs/INDIVIDUAL_ROUTINE_PICKUP.md) |

## What's inside?

Signed and unsigned **multiply, divide and modulo** routines (including
wide-integer variants), plus **integer square roots, trigonometry, ATAN2,
distance, fixed-point/vector helpers and target-seeking movement**.

The [full operation catalog](routines/PUBLIC_OPERATIONS.csv) lists the
exact names and types. Look up a routine in the
[performance table](docs/OPERATION_FIRST_ROUTINE_METRICS.md) to see its
measured cost before choosing it.

## Build a library for your project

**Requirements:** Python 3.12+ and Make. No external assembler is needed for
the normal installer.

From the repository folder, run:

```sh
make builder-setup
```

The guided setup asks you to:

1. **Pick operations** — one, several, or all 56.
2. **Choose a goal** — `balanced` (general trade-off), `speed` (measured
   CPU-model cycles), `size` (less RAM), or `zp` (less zero-page use).
3. **Set your available RAM and ZP** — the builder checks that the result fits.
   In `speed` mode, it also asks how frequently you expect to call each operation.

You receive:

| File | What it is |
| --- | --- |
| `my_math.json` | Your choices; edit and reuse them later |
| `build_my_math/math_selective.prg` | Your selected C64 library, ready to load |
| `build_my_math/math_api.inc` | The **actual** entry points and operand addresses for your build |
| `build_my_math/selective_manifest.json` | The selected sources, exact memory placement and RAM/ZP allocations |

**Using it:** Load the generated `.prg` at its configured address, include
the *matching* `math_api.inc` in your assembly project, write operands to
the exported math I/O symbols, `JSR` the selected `MATH_*` entry, then
read its documented result and Carry status. Entry addresses can change
when you rebuild; don't copy addresses from an old release.
See [calling conventions](docs/API_COMPATIBILITY.md) and the
[step-by-step setup guide](docs/OPERATION_FIRST_USER_SETUP.md).

### Prefer a command instead of the setup wizard?

This example builds only unsigned 16-bit multiplication, unsigned 16-bit
division and 16-bit integer square root:

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --operation UDIV16 --operation ISQRT16 \
  --objective balanced --zp-budget 8 --ram-budget 4096 \
  --config-out project-math.json --build-dir build_project_math
```

Edit `project-math.json` to change your choices, then rebuild into a
**new** output directory:

```sh
make builder CONFIG=project-math.json OUT=build_new_math
```

Existing configurations and build directories are not silently overwritten.
For custom memory maps, source pins and speed call counts, see the
[full setup guide](docs/OPERATION_FIRST_USER_SETUP.md).

## Want to reuse **one** routine in your own code?

You have two options:

**Easiest: build only that operation.** Run `make builder-setup` and select
one operation (for example, `UMUL16`). You'll get a small loadable `.prg`,
its API include and an exact footprint manifest, without taking a whole
legacy resident library. Required shared code and tables are included.

**Prefer to copy or adapt the assembly source?** Use the
[variant CSV](benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv): filter the
`operation` column (for example, `MATH_UMUL16`) and follow the
`source_path` for the implementation you're interested in.
Start with [curated routine sources](routines/README.md) and the
[single-routine pickup guide](docs/INDIVIDUAL_ROUTINE_PICKUP.md).
Some [portable standalone kernels](routines/standalone_lab/portable/README.md)
have their own documented, editable addresses and calling conventions.

**Important:** An individual source file is *not always* a drop-in module.
It may need shared tables, scratch memory, symbolic bindings or setup code.
Check its dependencies and ABI before transplanting it.
The builder is the safer route if you simply want a working one-operation
library.

## How fast? How much memory?

The [consolidated routine table](docs/OPERATION_FIRST_ROUTINE_METRICS.md)
shows **mean CPU cycles/call, code + tables, total isolated RAM, ZP and
persistent stack-page reservations** for all 56 operations.
The [full variant CSV](benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv)
lets you compare alternatives for the *same* operation.
[Performance charts](PERFORMANCE.md) show selected combined-project
trade-offs.

These are measured reference figures, **not a promise of exact PAL frame
timing**. Isolated routine footprints cannot simply be added together:
linked projects may share code, tables and scratch. Check **your own**
`selective_manifest.json` for actual combined RAM/ZP allocation.
The stack-page column does **not** measure temporary JSR/RTS or interrupt
stack depth.

## More information

- [Complete setup and memory-map options](docs/OPERATION_FIRST_USER_SETUP.md)
- [Public API and calling conventions](docs/API_COMPATIBILITY.md)
- [Source pickup and relocation notes](docs/INDIVIDUAL_ROUTINE_PICKUP.md)
- [Validation and release acceptance](docs/BUILDER_RELEASE_ACCEPTANCE.md)
- [Experimental Turbo16 REU add-on](docs/OPERATION_FIRST_REU_TURBO16.md) and [separate legacy REU services](docs/REU_COMPAT_EXPORT.md)
- [Historical V1–V5 performance archive](docs/PERFORMANCE_ARCHIVE_HISTORICAL_RESIDENTS_2026-10-21.md), [research README archive](docs/README_RESEARCH_ARCHIVE_2026-10-21.md) and [changelog](CHANGELOG.md)

**Which version should I install?** For a new stock-C64 project, use the
**operation-first builder above**, not the old V1–V5 configuration profiles.
The historic source, binaries, benchmarks and compatibility services are
preserved for reference. The optional REU service is experimental; other
historical REU services remain separate and cannot be mixed into the stock
selective `.prg`. 1541/1571/1581 math backends are not available yet.

**License:** [MIT](LICENSE) — you may use, adapt and redistribute the code,
subject to the license terms.
