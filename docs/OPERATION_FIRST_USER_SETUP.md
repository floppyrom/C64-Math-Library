# Operation-first C64 Math Library: configure once, build to your budget

> **Current primary user interface:** the operation-first builder is the
> sole supported stock-C64 installation path. V1–V5 are archived for
> reproduction and separate REU compatibility, not selectable installer
> profiles. All 56 public operations, four objectives and custom budgets
> passed release acceptance; see [the acceptance matrix](BUILDER_RELEASE_ACCEPTANCE.md).


This is the **normal installation path**. Do not choose V1, V2, V3, V4 or V5
first. Those releases, historical kernels and REU compatibility packages
remain as source/performance references, but are not the configuration UI.

## Quick start

From the repository root:

```sh
make builder-setup
```


You choose the public math operations needed by your program (from 56),
an optimization goal, and your **maximum total zero-page and RAM bytes**.
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

## Scope and limitations

The source-qualified operation-first stock-C64 linker covers all 56 public
operations. Every output uses source SHA checks, independently linkable
kernel contracts, actual byte placement, shared tables, scratch and ZP
accounting, and a deterministic manifest.

No user needs to run SID music, sprite, graphics, PAL deadline or REU DMA
benchmarks to install a library. Those application-specific experiments
are optional. For physical REU Turbo/QS16 functionality on V3/V4,
the separately qualified legacy REU export is still required; the stock
C64 operation-first image is **not** a mix-and-match REU service provider.
The 1541, 1571 and 1581 backends remain planning-only.

For detailed variant history and performance parity see
[profile retirement plan](PROFILE_RETIREMENT_PLAN.md).
