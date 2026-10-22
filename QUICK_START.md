# Quick start — C64 Math Library

**Use the [README](README.md) as the main entry point.** This page is the short build recipe; the [configuration guide](docs/OPERATION_FIRST_USER_SETUP.md) covers budgets, variant pins, reserved-memory maps and speed call counts.

## 1. Choose and build

```sh
make builder-setup
```

Select any of the [56 independently linkable operations](routines/PUBLIC_OPERATIONS.csv), one goal (`balanced` / `speed` / `size` / `zp`), RAM/ZP budgets, and optionally **one** REU module (Turbo16, Turbo32 or QS16). Stock C64 is the default.

To automate a stock build:

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --operation UDIV16 --operation ISQRT16 \
  --objective balanced --zp-budget 8 --ram-budget 4096 \
  --config-out project-math.json --build-dir build_project_math
```

Edit the saved configuration and rebuild in a **new** directory:

```sh
make builder CONFIG=project-math.json OUT=build_new_math
make builder-measure CONFIG=project-math.json
```

No existing config or output directory is silently overwritten.

## 2. Use the generated files

- `math_selective.prg` — assembled stock-C64 operations
- `math_api.inc` — exact public call and operand addresses
- `selective_manifest.json` — linked variants, shared code, physical memory map and total RAM/ZP
- With REU selected: `<service>_reu.prg`, `math_reu_<service>.inc`, `<service>_reu_manifest.json` and `math_project_manifest.json`

Load the stock PRG and use the *generated* API include; don't hardcode V1–V5 addresses. For REU, load the companion as well and require successful **INSTALL** before **BEGIN → CALL → END**. The selected stock operation remains the fallback.

## 3. Inspect performance and validate

[Cycles, RAM, ZP and persistent stack-page bytes for all 56 operations](docs/OPERATION_FIRST_ROUTINE_METRICS.md) · [Every measured implementation variant](benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv) · [Combined-project comparisons](PERFORMANCE.md)

Individual footprints are not additive; use your generated manifest for real combined memory. CPU-model cycle counts are not a hardware PAL deadline guarantee.

```sh
make builder-list
make builder-validate
make package-audit
```

Optional math-only frame qualification (not a physical 25/50 fps promise):

```sh
make builder-frame OUT=build_frame_example
```

On a fresh checkout the example generates its own source-qualified
three-operation report in `build_frame_example/mixed3.json` before building.
For a different application, supply a previously qualified
`FRAME_REPORT=path/to/report.json` and the matching `FRAME_CONFIG=...`;
unknown or missing reports are rejected rather than fabricated.

For REU flags, bank reservations, compatibility and limits, read the [REU guide](docs/REU_OPERATION_FIRST_CONSOLIDATION.md). For individual assembly sources, use the [routine pickup guide](docs/INDIVIDUAL_ROUTINE_PICKUP.md). Historical V1–V5 packages remain reproducible archives, **not** new-project installation choices.
