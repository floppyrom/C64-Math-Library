# C64 Math Library

High-performance integer, fixed-point and game math for the Commodore 64 / NMOS 6502/6510.

The library exposes one stable **46-entry public API** across five fixed profiles. V3/V4 add stateful Turbo16/Turbo32 calls; V4 also adds QS16. A Custom Pareto Builder can generate a stock-C64 mix for a chosen ZP/RAM budget.

## Start here

- **How fast are the routines?** [`PERFORMANCE.md`](PERFORMANCE.md)
- **Machine-readable results:** [`benchmarks/PUBLIC_PROFILE_RESULTS.csv`](benchmarks/PUBLIC_PROFILE_RESULTS.csv), [`benchmarks/BEST_PROFILE_RESULTS.csv`](benchmarks/BEST_PROFILE_RESULTS.csv), and [`benchmarks/STANDALONE_RESULTS.csv`](benchmarks/STANDALONE_RESULTS.csv)
- **Where is the exact source?** [`routines/SOURCE_CATALOG.csv`](routines/SOURCE_CATALOG.csv)
- **Calling/integration manual:** [`USER_MANUAL.md`](USER_MANUAL.md)
- **Naming convention:** [`docs/NAMING_STANDARD.md`](docs/NAMING_STANDARD.md)
- **Repository layout:** [`docs/STRUCTURE.md`](docs/STRUCTURE.md)
- **Moving an object toward a target:** use the exact DDA stepper in [`routines/movement/`](routines/movement/README.md), not vector normalization

Every published benchmark row now points to a public source file and SHA-256. Run `python3 tools/validate_public_catalog.py` to verify that contract.

## Fixed profiles

| Profile | Hardware | Main goal |
|---|---|---|
| **V1 Balanced** | Stock C64 | Low integration pressure, 31-byte normal ZP contract |
| **V2 Pareto-Fast** | Stock C64 | Faster resident choices where more ZP/private resources are acceptable |
| **V3 REU 512K** | C64 + 512 KiB REU | REU-backed services plus Turbo16/Turbo32 |
| **V4 REU 16M** | C64 + 16 MiB REU-compatible device/emulator | REU-heavy feature set, QS16, Turbo, exact REU ATAN2/ISQRT16 paths |
| **V5 Hybrid Low-ZP** | Stock C64 | V1 31-byte normal-ZP contract with selected faster V2-derived paths |

Use [`docs/VERSION_SELECTION.md`](docs/VERSION_SELECTION.md) for integration trade-offs.

## Performance snapshot

These are current public-entry means, through `RTS`; caller `JSR` and input stores are excluded unless documented otherwise.

| Routine | V1 | V2 | V3 | V4 | V5 |
|---|---:|---:|---:|---:|---:|
| `mul_u16_u16_u32` | 273.837 | 225.837 | 225.837 | 225.837 | 273.837 |
| `mul_s24_s24_s48` | 531.496 | 487.182 | 486.816 | 487.220 | 530.874 |
| `div_u16_u16_u16_16` | 132.726 | 127.774 | 125.424 | 125.626 | 126.386 |
| `div_s24_s24_s24_24` | 313.583 | 248.344 | 236.810 | 237.569 | 253.487 |
| `atan2_s8_s8_u8` | 48.447 | 44.963 | 44.963 | 48.000 | 44.963 |

For the complete table, resource use, min/max, corpora and source links, see [`PERFORMANCE.md`](PERFORMANCE.md).

The repository also publishes standalone record/Pareto alternatives, including the current 24-ZP signed 24x24 FAST24 point at **400.301600 cycles** and the stack-free 135-ZP signed 32x32 point at **665.877260 cycles**. These use their own documented benchmark bases and should not be compared blindly with public-profile means.

## Source layout and naming

The historical `MATH_*` symbols and fixed addresses remain ABI-compatible. Source-facing names encode signedness and geometry, for example:

```text
mul_u8_u8_u16
mul_s16_s16_s32
div_u8_u8_u8_8
div_u32_u16_u32_16
```

Every callable fixed-profile entry has an exact source mirror under `<profile>/standalone/`. Independently benchmarked alternatives live under `routines/`. The complete source index is [`routines/SOURCE_CATALOG.csv`](routines/SOURCE_CATALOG.csv).

## Build

Requirements: Python 3. The deterministic assembler/build path is included; ACME is optional as an independent cross-check.

```sh
# V1-V4 reference and alternate maps
make reference
make alternate

# V5
make hybrid
make hybrid-validate

# Custom stock-C64 Pareto build
python3 tools/pareto_wizard.py
# or
python3 tools/build_pareto.py --zp-budget 60
```

See [`QUICK_START.md`](QUICK_START.md) and [`docs/SOURCE_RELOCATION.md`](docs/SOURCE_RELOCATION.md).

## Current ATAN2 selection

The 2026-09-20 ATAN2 refresh is included in this tree:

- V1: `compact_opt`, **48.447189** mean, 606 B occupied, 0 ZP;
- V2/V3/V5: `sum_fast`, **44.962814** mean, 1,113 B occupied, 0 ZP;
- V4: exact REU lookup, **48 cycles fixed**.

Standalone `compact_opt`, `sum_small` and `sum_fast` sources remain available under [`routines/atan2/`](routines/atan2/).

## Validation and publication policy

The current tree keeps the buildable profiles, current validation evidence and source-backed benchmark alternatives, while removing the old top-level exploratory `research/` tree. Git history remains the archive for superseded experiments.

Useful checks:

```sh
python3 tools/generate_public_indexes.py
python3 tools/validate_public_catalog.py
python3 tools/validate_standalone_sources.py
make reference
make alternate
make package-audit
```

The library is **not reentrant**. Sequential calls in ordinary game/demo loops are supported; do not enter shared math state from an IRQ/NMI while another library call is active.
