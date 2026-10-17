# Quick start — operation-first (preferred)

Create only the C64 routines your application calls, without selecting V1–V5:

```sh
make builder-list                         # all 56 linkable operations
make builder-measure                      # exact assembled RAM/ZP footprint
make builder                              # build example from JSON config
make builder CONFIG=my_math.json OUT=build_my_math
```

Begin by copying [`examples/operation-first.json`](examples/operation-first.json).
Set `operations` (any of 56 public APIs), `objective` (`balanced`, `size`, `zp`,
`speed`), `max_ram_bytes` and `max_zp_bytes`. Build output contains the minimal
`math_selective.prg`, callable `math_api.inc`, and selection manifest.
The output is **not** the full 56-routine library unless all 56 are selected.
The builder uses reusable scratch/shared physical producers and enforces budgets.
For explicit kernel choice use `--pin OP=link:variant`; inspect alternatives with
`python3 tools/math_builder.py --variants UMUL16`. Use `--measure` before building.

The C64 binary backend is available now; 1541/1571/1581 are planning-only.
Do not assume `--objective speed` implies historical fixed-profile speed parity:
fast V1–V5 kernels and REU services are still being transplanted and qualified.
See [`docs/PROFILE_RETIREMENT_PLAN.md`](docs/PROFILE_RETIREMENT_PLAN.md).

## Legacy profile build and validation


For speed figures, use [`PERFORMANCE.md`](PERFORMANCE.md). For the exact source behind a shipped or standalone benchmark, use [`routines/SOURCE_CATALOG.csv`](routines/SOURCE_CATALOG.csv). For **one-operation reuse**, including which files are exact audit mirrors versus independently liftable modules, use the [individual routine pickup guide](docs/INDIVIDUAL_ROUTINE_PICKUP.md).

Before publishing a new benchmark/source pair, run:

```sh
python3 tools/generate_public_indexes.py
python3 tools/validate_public_catalog.py
```

Requirements: Python 3. The repository includes its own deterministic 6502 source assembler/validator; no external assembler is required. ACME 0.97 remains an optional independent cross-check for the V1–V4 canonical source builds.

## V1–V4

```sh
python3 tools/generate_sources.py
python3 tools/assemble_sources.py --profile all --config-kind reference
python3 tools/assemble_sources.py --profile all --config-kind alternate
python3 tools/validate_source_build.py all --build build_source/alternate --out validation/source_relocation
```

V2–V4 require `MATH_INIT` once. V3/V4 also require the matching generated REU image.

## V5 Hybrid Low-ZP

V5 is built deterministically from the canonical V1 and V2 source trees:

```sh
python3 tools/build_hybrid.py --config-kind reference
python3 tools/build_hybrid.py --config-kind alternate
python3 tools/validate_hybrid.py
python3 tools/test_hybrid_config.py
python3 tools/verify_hybrid_deterministic.py
```

Or use:

```sh
make hybrid
make hybrid-validate
```

For a custom V5 map, copy `relocatable_source/v5_hybrid_lowzp/math_config_reference.inc`, edit the V1-style map symbols and `HYBRID_CODE`, then run:

```sh
python3 tools/build_hybrid.py --config path/to/math_config.inc --out build_hybrid_custom
```

The reference V5 `HYBRID_CODE=$A000` occupies `$A000-$BDFF`, so BASIC ROM must be banked out while imported V5 routines execute. Move `HYBRID_CODE` if that does not fit your application.


## Legacy Custom Pareto Builder (compatibility)

Interactive:

```sh
python3 tools/pareto_wizard.py
```

Direct:

```sh
python3 tools/build_pareto.py --zp-budget 60
```

Optional constraints:

```sh
python3 tools/build_pareto.py --zp-budget 31 --ram-budget 0
python3 tools/build_pareto.py --zp-budget 31 --init-policy optional
python3 tools/build_pareto.py --zp-budget 55 --weight MATH_UMUL24=100
```

`--ram-budget` is enforced against the **exact extra private payload** relative to V1, including the exact generated `MATH_INIT` helper when required. See `docs/PARETO_BUILDER.md`.

Validate the selector and generated profiles:

```sh
make pareto-validate
```

## Vector normalization validation

```sh
make normalize
```

This rebuilds the fixed and hybrid profiles, runs the deterministic 107,396-vector profile-parity benchmark, and regenerates the full-domain exact-ratio precision certificate.

## Other validation

```sh
python3 tools/validate_turbo_relocation.py
python3 tools/validate_isqrt32_fast.py
python3 tools/benchmark_normalize_profile_parity.py
python3 tools/certify_normalize_exact_ratio.py
python3 tools/test_config_validation.py
make package-audit
```

For V3/V4 Turbo modes, never call normal/game math between Turbo `BEGIN` and `END`; the overlay owns its configured ZP range during that lifecycle.

## Optional ACME verification

```sh
python3 tools/verify_with_acme.py --acme /path/to/acme --kind all
```

This currently covers the canonical V1–V4 resident/Turbo assembly paths. V5 and custom Pareto builds are deterministic source-derived linker builds validated by their dedicated validators.
