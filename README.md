# C64 Math Library

**Build the math your Commodore 64 actually needs.** Choose from **56 independently linkable 6502/6510 operations**, optimize for speed or memory, and generate a source-built PRG with the actual entry points and resource map. **Turbo16, Turbo32 and QS16 REU acceleration** are available as optional companions through the *same* operation-first installer.

**Start here:** [Browse all 56 operations](routines/PUBLIC_OPERATIONS.csv) · [Cycles / RAM / ZP / stack per routine](docs/OPERATION_FIRST_ROUTINE_METRICS.md) · [Try the quick start](QUICK_START.md) · [Use an individual routine](docs/INDIVIDUAL_ROUTINE_PICKUP.md)

## What can it do?

Unsigned and signed multiplication, division and modulo (including 24-/32-bit and mixed-width arithmetic), integer square roots, trigonometry, ATAN2, distances, fixed-point/vector helpers, and movement/target-seeking operations.

The normal installation model is **operation-first**, not the historical V1–V5 profile system. Select individual APIs, not a preset resident or an entire release. The builder can share qualified implementation code and tables where beneficial, while checking exact physical RAM, zero-page, I/O and application reservations.

## Build a project

**Requirements:** Python 3.12+ and Make. The normal build uses the repository's own assembler.

```sh
make builder-setup
```

The guided installer asks for operations, optimization goal, RAM/ZP budgets and optional REU acceleration. For the optimization goal choose:

| Goal | Selection behavior |
| --- | --- |
| `balanced` | Balance memory and measured speed under your limits |
| `speed` | Optimize measured CPU-model cycles using your **per-operation call counts** |
| `size` | Minimize main RAM use |
| `zp` | Minimize zero-page use |

All four respect resource constraints. No goal silently enables REU hardware, and a speed-optimal **isolated** kernel is not necessarily the best kernel for a combined project.

For noninteractive builds, for example:

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --operation UDIV16 --operation ISQRT16 \
  --objective balanced --zp-budget 8 --ram-budget 4096 \
  --config-out project-math.json --build-dir build_project_math
```

Edit the saved JSON and rebuild into a *new* output directory:

```sh
make builder CONFIG=project-math.json OUT=build_new_math
make builder-measure CONFIG=project-math.json
make builder-list
```

The installer refuses to overwrite an existing configuration or output directory. For `speed`, provide positive `--calls OP=COUNT` values for **every** selected operation. To reserve application code/ZP or pin a qualified source variant, see the [configuration guide](docs/OPERATION_FIRST_USER_SETUP.md).

## What do I load, and where are the numbers?

| File / resource | What it tells you |
| --- | --- |
| `math_selective.prg` | Independently assembled stock-C64 library for your selected APIs |
| `math_api.inc` | Actual public symbols, operand locations and call addresses |
| `selective_manifest.json` | Selected source variants, **actual combined RAM/ZP use**, physical placements and hashes |
| [56-operation metric table](docs/OPERATION_FIRST_ROUTINE_METRICS.md) | Per-call mean cycles, code/tables, **isolated RAM**, ZP and persistent stack-page bytes |
| [Complete variant CSV](benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv) | Every measured linkable alternative, source path and speed/memory trade-offs |
| [Performance comparisons](PERFORMANCE.md) | Comparable examples and limits of cycle measurements |

**Read the measurements correctly:** individual routine footprints cannot simply be added together; the linker can share memory and tables. The manifest of *your build* is authoritative for total RAM/ZP. Cycle means are measured under a CPU model, not guaranteed PAL frame times. “Persistent stack-page bytes” does **not** measure transient JSR/RTS or interrupt stack high-water.

Load the generated PRG, include its *matching* `math_api.inc`, write operands to its exported I/O block, call a `MATH_*` entry and read its documented result/Carry. Do not hardcode historical V1–V5 addresses. The library is **non-reentrant**; consult the [ABI and calling conventions](docs/API_COMPATIBILITY.md).

## Optional REU acceleration

The same guided installer, or an explicit CLI flag, can add **one** independently loadable REU service alongside its required stock fallback:

| Option | Stock fallback operation | REU capacity | Service ZP ownership |
| --- | --- | --- | ---: |
| `--reu-turbo16` | `UMUL16` | 512KiB or 16MiB | 122 B executable overlay |
| `--reu-turbo32` | `UMUL32` | 512KiB or 16MiB | 135 B executable overlay |
| `--reu-qs16` | `UMUL16` | 16MiB | 16 B scratch |

Example: build a Turbo32 project with a normal 32-bit multiplication fallback:

```sh
python3 tools/configure_math.py \
  --operation UMUL32 --objective size \
  --ram-budget 30000 --zp-budget 210 \
  --reu-turbo32 --reu-kib 512 \
  --config-out reu-math.json --build-dir build_reu_math
```

In addition to the three stock files, REU builds generate `<service>_reu.prg`, `math_reu_<service>.inc`, `<service>_reu_manifest.json` and `math_project_manifest.json`. The latter accounts for **combined** C64 RAM, ZP and REU bank ownership.

Load both PRGs in their assigned regions. **Call REU INSTALL and check success before BEGIN → CALL → END; fall back to stock math if INSTALL fails.** Do not access the service-owned ZP from an IRQ or another routine during an active batch. Selecting multiple REU services in one project, REU/IRQ/VIC/SID concurrent timing safety, and automatic DMA-inclusive speed comparisons are **not qualified**. See the [REU integration and memory guide](docs/REU_OPERATION_FIRST_CONSOLIDATION.md).

## Need just one routine—or want the source?

Select a single operation with the normal installer to get a self-contained one-operation PRG plus its API and dependencies. Or look up its `source_path` in the [variant CSV](benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv) and follow the [standalone source pickup guide](docs/INDIVIDUAL_ROUTINE_PICKUP.md). Not every raw `.asm` file is drop-in: some depend on shared tables, generated symbols, scratch memory or initialization.

## Verify and understand the project

```sh
make builder-validate       # qualified stock/builder regression suite
make package-audit          # source and distribution integrity
make legacy-validate        # optional historical V1–V5 regression tests
```

See the [quick-start commands](QUICK_START.md), [full setup/manual memory placement](docs/OPERATION_FIRST_USER_SETUP.md), [API guide](docs/API_COMPATIBILITY.md), [acceptance criteria](docs/BUILDER_RELEASE_ACCEPTANCE.md), and [changelog](CHANGELOG.md).

**Historical V1–V5 releases are preserved as immutable reference and compatibility assets, not installation profiles.** New Turbo16/Turbo32/QS16 projects do **not** need a frozen V3/V4 REU image or whole-resident legacy bundle. The [legacy exporter](docs/REU_COMPAT_EXPORT.md) remains for existing software and reproducible comparisons. Full historical speed parity and operation-first drive-side (1541/1571/1581) backends are not claimed.

**License:** [MIT](LICENSE).
