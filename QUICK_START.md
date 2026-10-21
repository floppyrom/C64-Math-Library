# Quick start — build your own C64 math library

**V1–V5 are retired as new-project installation choices.** For a stock
C64, use the operation-first builder to link precisely the math operations,
RAM footprint, zero-page allocation and qualified speed variants your
application needs. All 56 public operations can be selected independently.

## 1. Interactive setup (recommended)

```sh
make builder-setup
```


Choose the operations and one of `balanced`, `speed`, `size` or
`zp`, then give the usable RAM and ZP budgets. The builder outputs:

- `my_math.json`: a reusable, editable project configuration.
- `build_my_math/math_selective.prg`: actual linked C64 load image.
- `build_my_math/math_api.inc`: the generated public ABI addresses.
- `build_my_math/selective_manifest.json`: exact source variants,
  physical RAM/ZP usage, code placement and SHA verification.

A project config or directory is never silently overwritten.

## 2. Noninteractive / automated setup

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --operation UDIV16 --operation ISQRT16 \
  --objective balanced --zp-budget 8 --ram-budget 4096 \
  --config-out project-math.json --build-dir build_project_math
```


Later, change `project-math.json` and run:

```sh
make builder CONFIG=project-math.json OUT=build_rebuilt
make builder-measure CONFIG=project-math.json
make builder-list
```


Speed selection requires real positive per-operation call weights and
optimizes comparable CPU-model mean cycles; it does not guess a workload:

```sh
python3 tools/configure_math.py \
  --operation UMUL8 --operation UMUL16 \
  --objective speed --calls UMUL8=1000 --calls UMUL16=1 \
  --zp-budget 4 --ram-budget 1400 \
  --config-out speed-math.json --build-dir build_speed
```


For strict memory maps, use `--memory-config game-layout.json`
to reserve application code and zero page. For an expert-certified source
override, use `--pin UMUL8=link:compact-zerozp`. The resulting
physical image must still fit all configured resource constraints.

## 3. Link into your 6502 program

Use the **generated** `math_api.inc`—never old profile address
constants—place operands in the exported 32-byte math I/O block, call the
required `MATH_*` symbol, and read the documented result/Carry.
Check the manifest for the actual chosen source, memory layout and init
requirements. The library is **not reentrant**.

## 4. Verify the distribution

```sh
make all                    # alias for the default operation-first build
make builder-validate       # operation-first qualification suite
make package-audit          # source hash/package integrity
make legacy-validate        # optional frozen V1–V5 reproductions
```


The [release acceptance matrix](docs/BUILDER_RELEASE_ACCEPTANCE.md) verifies
the four objectives and a custom reserved-memory build from real PRG output.
Read [setup details](docs/OPERATION_FIRST_USER_SETUP.md),
[public ABI](docs/API_COMPATIBILITY.md), and [performance scope](PERFORMANCE.md).

## Historical compatibility only

Source snapshots, binaries, the old Pareto wizard, historic benchmarks and
legacy regression targets have **not been deleted**. They are frozen
compatibility/research references, **not alternate recommended installers**.
The archive includes the original README's extensive optimization history:
[pre-cutover research notes](docs/README_RESEARCH_ARCHIVE_2026-10-21.md).

An **experimental native Turbo16 REU add-on** can now be selected through
the operation-first configuration, while keeping a normal UMUL16 fallback:

```sh
python3 tools/configure_math.py --operation UMUL16 --objective size \
  --zp-budget 200 --ram-budget 25000 --reu-turbo16 --reu-kib 512 \
  --config-out reu-math.json --build-dir build_reu_math
```

This produces a **separate source-built** REU PRG as well as the stock
PRG, with global memory reservations and a combined manifest. It is not
automatically accelerated: use the REU lifecycle only after INSTALL
succeeds. See the [opt-in REU guide](docs/OPERATION_FIRST_REU_TURBO16.md).
IRQ/VIC contention and timing remain unqualified.

The historical V3/V4 Turbo16/Turbo32 and V4 QS16 resident services are
still preserved as [REU compatibility exports](docs/REU_COMPAT_EXPORT.md),
not mixed into the selective PRG. 1541/1571/1581 operation-first
backends and complete historical fastest-kernel parity remain unfinished.
