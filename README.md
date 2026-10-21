# C64 Math Library

**Build only the math routines your Commodore 64 application needs.** The supported
stock-C64 installation system is the **operation-first builder**, with **56
independently linkable public operations**, configurable resource budgets,
source-qualified implementation alternatives and an exact physical linker.

**V1–V5 are retired as configuration profiles.** New applications should not
choose "Balanced V1", "Fast V2", "REU V3", "REU V4" or "Low-ZP V5" as their
library build strategy. Those named historical releases are preserved,
unchanged, for source provenance, comparative benchmarks, regression
testing and certain **separate REU compatibility services**. They are *not*
deleted, and no unconditional historical speed/REU parity is claimed.

## Get started

Requirements: Python 3.12+ and Make for the Makefile shortcuts. The
repository contains its own deterministic 6502 assembler; an external
assembler is not required for normal installation.

**Interactive setup:**

```sh
make builder-setup
```


Select your operations, optimization objective and available RAM/zero page.
The setup produces:

| Output | Purpose |
|---|---|
| `my_math.json` | Editable, reusable application-specific configuration |
| `build_my_math/math_selective.prg` | Real, minimal source-linked C64 load image |
| `build_my_math/math_api.inc` | Actual exported function and operand addresses |
| `build_my_math/selective_manifest.json` | Selected variants, source hashes, physical RAM/ZP placements, link proof |

Existing configuration and build paths are **not overwritten**. Make a
new output directory for another configuration. The builder validates the
selected sources, budgets and memory reservations before publishing outputs.

**Noninteractive or CI setup:**

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --operation UDIV16 --operation ISQRT16 \
  --objective balanced --zp-budget 8 --ram-budget 4096 \
  --config-out project-math.json --build-dir build_project_math
```


To edit an existing project, modify its JSON configuration and rebuild:

```sh
make builder CONFIG=project-math.json OUT=build_new_math
# Check the actual assembled footprint without making a new image:
make builder-measure CONFIG=project-math.json
# Browse the complete public operation catalog:
make builder-list
```


No `--profile` switch is used in the supported installer. The
old reference-source targets are kept only for reproducibility and tests.

## Choose according to your application

| Objective | What it optimizes | What it does **not** promise |
|---|---|---|
| `balanced` | A trade-off across physical RAM and ZP constraints | Fastest historical or possible runtime |
| `speed` | Minimize estimated calls × matched-input mean cycles | Hardware-exact frame timing, or unmeasured donor performance |
| `size` | Smallest qualifying main RAM footprint | Fastest execution |
| `zp` | Lowest qualifying zero-page use | Smallest code or fastest execution |

A tight memory budget can legitimately select a slower but smaller
qualified routine. The global optimizer considers sharing, code and table
alignment, 32-byte public I/O, call-exclusive scratch and ZP, persistent
SEEK state and reserved memory. It does **not** independently choose a
"best" routine per API and then merely add isolated byte counts.

Speed mode requires **positive workload call counts for every requested
operation** and refuses to silently assume they run equally often:

```sh
python3 tools/configure_math.py \
  --operation UMUL8 --operation UMUL16 --objective speed \
  --calls UMUL8=1000 --calls UMUL16=1 \
  --ram-budget 1400 --zp-budget 4 \
  --config-out my_speed_math.json --build-dir build_my_speed_math
```


You may pin a certified `link:...` implementation, reserve RAM/ZP
occupied by your game with `--memory-config your-layout.json` and
inspect selectable implementations with
`python3 tools/math_builder.py --variants UMUL16`.
The installer refuses unqualified source substitutions or overlapping
allocations. See the [complete setup guide](docs/OPERATION_FIRST_USER_SETUP.md),
[public API details](docs/API_COMPATIBILITY.md) and
[resource-qualified acceptance matrix](docs/BUILDER_RELEASE_ACCEPTANCE.md).

## Use the generated library

Load `math_selective.prg` into the application's chosen legal
C64 address range, include the **generated** `math_api.inc` in the
6502 program, write operands into the exported public I/O block, call
the exported `MATH_*` entry and read the operation's documented
result/Carry. Check `selective_manifest.json` for the exact
selected module contracts, initialization requirements and memory map.
Do not hardcode old resident profile entry addresses.

The code is non-reentrant: do not call into shared math state from an
IRQ/NMI while another library call is active. Source-level public API
contracts and operation-specific caveats remain relevant regardless
of the chosen memory/speed objective.

## Release qualification

The operation-first user interface and binary-linking acceptance have
passed their exact-head CI suites:

- [Guided builder PR #370](https://github.com/floppyrom/C64-Math-Library/pull/370):
  **35/35 checks**, source-qualified config and generated PRG/include/manifest.
- [User configuration release matrix PR #372](https://github.com/floppyrom/C64-Math-Library/pull/372):
  **34/34 checks**, balanced/size/ZP/speed and a pinned reserved-memory
  configuration each rebuilding bit-for-bit; invalid reservations fail closed.
- Native VICE and source-model regressions independently validate the
  all-56 linked C64 image and many historical arithmetic implementations.
  Exact package hashes are tracked in `SHA256SUMS.txt`.

```sh
make builder                 # build from default operation-first JSON
make builder-validate        # comprehensive selective-source checks
make package-audit           # package integrity checks
make legacy-validate         # opt-in historical profile reproducibility tests
```


A successful installer test demonstrates **correctly linked configurations**;
it is not a guarantee of peak historical V1–V5 speed for every API, and
CPU-model cycle estimates are not full VIC-II/SID/REU frame measurements.
SID/music, graphics and PAL stress experiments are application-level
research and **do not gate use of the math library**.

## Archived releases and hardware-specific services

The historical `v1_balanced/`, `v2_pareto_fast/`,
`v3_reu_512k/`, `v4_reu_16m/` and
`v5_hybrid_lowzp/` directories, old custom-Pareto tools,
source tables, benchmark baselines and validation scripts remain
**unchanged and available**. They are a compatibility/reproducibility
archive, not alternative recommended installers.

**REU exception:** V3/V4 Turbo16/Turbo32 and V4 QS16 BEGIN/CALL/END
services are not implemented by the new stock-C64 selective backend.
Existing applications that specifically require those services must
use their **separate checksum-locked historical REU resident bundle**:

```sh
python3 tools/export_reu_compat.py \
  --profile v4_reu_16m --out build/reu-legacy-compat
```


That historical whole-resident bundle **cannot** be linked into
`math_selective.prg` or mixed with the generated stock ABI:
see [REU compatibility](docs/REU_COMPAT_EXPORT.md) and
[historical REU contracts](docs/REU_GUIDE.md). The 1541/1571/1581
math backends remain planning-only.

For readers reproducing the old releases, consult the
[archived historical user manual](USER_MANUAL.md),
[archived pre-cutover development README](docs/README_RESEARCH_ARCHIVE_2026-10-21.md),
[historical retirement/performance evidence](docs/PROFILE_RETIREMENT_EVIDENCE.md),
[performance results](PERFORMANCE.md) and
[changelog](CHANGELOG.md). The documented distinction is **retired
installation UX, preserved and still partially required legacy hardware
compatibility**.
