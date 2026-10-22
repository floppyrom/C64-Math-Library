# Operation-first setup: advanced configuration

**Start with the [README](../README.md) or [Quick Start](../QUICK_START.md).**
This guide explains scripting, per-operation speed weights, variants,
physical RAM/zero-page reservations and reproducible builds. All 56
stock-C64 public operations use the operation-first builder. Historical
V1–V5 profiles are preserved for regression, not installation.

## Quick start

From the repository root:

```sh
make builder-setup
```


You choose the public math operations needed by your program (from 56),
an optimization goal, and your **maximum total zero-page and RAM bytes**.
The guided installer also offers optional Turbo16, Turbo32 or QS16
REU acceleration, defaulting to no REU.
The installer makes a source-verified physical PRG using the established
exact global optimizer, including shared producer code/tables, 32 public
I/O bytes, call-exclusive scratch and any persistent SEEK object state.
Nothing is estimated by adding individual per-operation sizes.

Output:

* `my_math.json`: editable and reusable choices, limitations, optional
  source pins and memory reservations.
* `build_my_math/math_selective.prg`: only the requested operations'
  linked code, tables and no full historic resident image.
* `build_my_math/math_api.inc`: exports the *actual* chosen call
  addresses, aliases and shared math operand locations.
* `build_my_math/selective_manifest.json`: actual entry points,
  source hashes, selected variants, RAM/ZP use and physical memory map.

The installer **refuses to overwrite an existing config or directory**.
Choose a different output pair for another configuration or backup/move
the previous project yourself. It assembles and fully checks the complete
image in a temporary folder *before* publishing either artifact.

## Noninteractive commands for builds and CI

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --operation UDIV16 --operation ISQRT16 \
  --objective size --zp-budget 0 --ram-budget 4096 \
  --config-out project-math.json --build-dir build_project_math
```


For a workload where one operation dominates, specify **realistic calls**:

```sh
python3 tools/configure_math.py --operation UMUL8 --operation UMUL16 \
  --objective speed --calls UMUL8=1000 --calls UMUL16=1 \
  --zp-budget 4 --ram-budget 1400 \
  --config-out speed-math.json --build-dir build_speed_math
```


The `speed` mode refuses to guess call frequencies: each requested
operation needs its own count. Cycle choices use source-qualified
*matched-input CPU-model means*, not production SID/game PAL measurements,
and the full physical RAM/ZP constraints still apply.

Other goals are `balanced` (trade off RAM and ZP), `size`
(minimize resident RAM), and `zp` (minimize zero page).
They do **not** pretend to select the fastest routine automatically.
As budgets narrow the solution can choose a slower alternative; an
expert can inspect or explicitly pin the `link:...` variant.

## Protect the memory already occupied by your game

The optional `--memory-config placements.json` imports exactly the
linker-accepted `memory` object. Example:

```json
{
  "code_base": "$7123",
  "math_io": "$C040",
  "zp_base": "$60",
  "scratch_base": "$C060",
  "reserved": [
    {"name": "game_code", "start": "$8000", "end": "$9FFF"}
  ],
  "zp_reserved": [
    {"name": "game_zp", "start": "$02", "end": "$4F"}
  ]
}
```


All ranges are inclusive; `reserved`/`zp_reserved`
block memory regions the linker must never occupy. Check the generated
manifest rather than assuming that memory is allocated at old V1–V5
fixed addresses. Incompatible placements, oversized selected operations
and collisions cause a nonzero exit without publishing a partial setup.

Once you have an editable config, you may change operations, variants or
memory manually and use the original documented build command:

```sh
make builder CONFIG=project-math.json OUT=build_rebuilt_math
# Or check exact assembled resource use without retaining a new image:
python3 tools/math_builder.py --config project-math.json --measure
```


The generated include is essential: public entry addresses can move
when another operation or a different optimization goal is selected.

## Optional REU acceleration with the same installer

The guided installer offers **none, Turbo16, Turbo32 or QS16**. The CLI
uses `--reu-turbo16`, `--reu-turbo32` or `--reu-qs16`, with
`--reu-kib`, `--reu-bank` and repeatable `--reu-reserved-bank`
when needed. Select **exactly one** REU service and include its
required stock multiplication fallback (UMUL16 or UMUL32).

The linker reserves the companion's code, public I/O, exclusive
ZP scratch/overlay and REU banks, and counts them toward the global
RAM/ZP limits. Each result contains a separate REU PRG, its API include
and a combined `math_project_manifest.json`.

You must load and successfully INSTALL the companion before using
BEGIN/CALL/END. If detection fails, use the stock math call. No
concurrent REU modules or live IRQ/VIC/SID timing safety is claimed.

For the hardware matrix, worked Turbo32/QS16 commands, lifecycle
and precise resource ownership, consult the
[REU integration guide](REU_OPERATION_FIRST_CONSOLIDATION.md).

## Scope and limitations

The source-qualified operation-first stock-C64 linker covers all 56 public
operations. Every output uses source SHA checks, independently linkable
kernel contracts, actual byte placement, shared tables, scratch and ZP
accounting, and a deterministic manifest.

No user needs to run SID music, sprite, graphics or PAL deadline
benchmarks to install a library. Those experiments are optional
application-level qualification. The modern REU modules do **not** require
a legacy V3/V4 exported resident. Original V3/V4 REU images remain
checksum-locked [archives](REU_COMPAT_EXPORT.md) for old applications
and reproducible regression tests; never mix the original resident
with `math_selective.prg`.
The 1541, 1571 and 1581 backends remain planning-only.

For detailed variant history and performance parity see
[profile retirement plan](PROFILE_RETIREMENT_PLAN.md).
