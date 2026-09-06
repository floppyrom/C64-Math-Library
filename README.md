# C64 Math Library

A source-relocatable integer and game-math library for the Commodore 64 / NMOS 6502/6510, available in four performance and memory profiles.

The library exposes the same **45-entry stable API** across all profiles, covering unsigned and signed multiplication, division, remainder/modulo, 32/32 division, fixed-point helpers, reciprocal, trigonometry, `atan2`, integer square roots, and distance approximations.

The REU profiles additionally provide **Turbo16** and **Turbo32** batch multiplication modes that temporarily install highly optimized executable overlays in zero page. Both the resident library and the Turbo overlays are configurable at **assembly time**—there is no runtime relocation penalty.

## Highlights

- NMOS 6502/6510 compatible
- **45-entry common API** across V1–V4
- Unsigned and signed 8/16/24/32-bit arithmetic
- Exact 32/32 signed and unsigned division/remainder
- Fixed-point multiply/divide helpers
- Exact Q16 reciprocal
- `SIN8`, `COS8`, `SINCOS8`, `ATAN2_8`
- Exact `ISQRT16` and fast exact `ISQRT32`
- Fast and higher-accuracy 8-bit distance approximations
- Fully **source-relocatable** code, tables, I/O, scratch RAM and zero page
- V3/V4 **REU acceleration**
- V3/V4 **relocatable Turbo16/Turbo32 overlays**
- V4 16 MiB **QS16 quarter-square** multiplication tier
- Deterministic Python build/validation tooling included
- Independently cross-checked with **ACME 0.97**
- Complete user manual and reproducibility evidence included

## Profiles

| Profile | Hardware | Best fit | Main trade-off |
|---|---|---|---|
| **V1 Balanced** | Stock C64 | Tight zero-page budgets | Lowest ZP integration pressure; slower resident paths |
| **V2 Pareto-Fast** | Stock C64 | General-purpose fastest practical no-REU build | Larger ZP commitment |
| **V3 REU 512K** | C64 + 512 KiB REU | REU-backed acceleration and Turbo modes | Requires matching REU image and REU ownership discipline |
| **V4 REU 16M** | C64 + 16 MiB REU-compatible device/emulator | Fastest feature set, QS16, exact REU lookup paths | Requires 16 MiB REU compatibility; 512 extra resident bytes for fast ISQRT32 |

A simple rule of thumb:

- choose **V1** if zero page is scarce;
- choose **V2** for the fastest practical stock-C64 profile;
- choose **V3** for a normal 512 KiB REU;
- choose **V4** for VICE or a modern 16 MiB REU-compatible implementation.

All four profiles expose the same stable API. V3/V4 add six stateful Turbo lifecycle entries.

## Quick start

### Requirements

- Python 3
- No external assembler is required: the repository includes its own deterministic 6502 source assembler and validators.
- ACME 0.97 is optional as an independent byte-for-byte verification path.

### Build the reference configuration

```sh
python3 tools/generate_sources.py
python3 tools/assemble_sources.py --profile all --config-kind reference
```

Generated output appears under:

```text
build_source/reference/<profile>/
```

Each profile build contains the resident PRG and generated `math_api.inc`. V3/V4 also produce the matching REU image.

### Build the deliberately relocated test configuration

```sh
python3 tools/assemble_sources.py --profile all --config-kind alternate
```

### Run the main validation suite

```sh
python3 tools/validate_source_build.py all \
    --build build_source/alternate \
    --out validation/source_relocation

python3 tools/validate_turbo_relocation.py
python3 tools/validate_isqrt32_fast.py
python3 tools/test_config_validation.py
```

Or use the Makefile targets described in [QUICK_START.md](QUICK_START.md).

## Using the API

Include the generated API symbols for the profile you built:

```asm
!source "build_source/reference/v2_pareto_fast/math_api.inc"
```

V2–V4 require `MATH_INIT` once before normal use. Calling it on V1 is also recommended for a uniform startup path.

```asm
        jsr MATH_INIT
```

Operands and results use a shared little-endian public I/O block (`MATH_X`, `MATH_Y`, `MATH_Z`, `MATH_N`, `MATH_D`, `MATH_Q`, `MATH_R`). See [USER_MANUAL.md](USER_MANUAL.md) for the exact geometry of every entry.

### Example: unsigned 16×16 → 32

```asm
        ; X = $1234
        lda #$34
        sta MATH_X+0
        lda #$12
        sta MATH_X+1

        ; Y = $5678
        lda #$78
        sta MATH_Y+0
        lda #$56
        sta MATH_Y+1

        jsr MATH_UMUL16

        ; result is now in MATH_Z+0..3
```

### Example: unsigned 16-bit division

```asm
        ; numerator / divisor
        ; write inputs as documented in USER_MANUAL.md
        jsr MATH_UDIV16
        bcs divide_by_zero

        ; quotient and remainder are now in the documented Q/R vectors
```

Division-family calls use Carry for divide-by-zero reporting according to the documented ABI.

## Stable API

The 45 common entries are:

### Multiplication

- `MATH_UMUL8`
- `MATH_UMUL16`
- `MATH_UMUL24`
- `MATH_UMUL32`
- `MATH_UMUL32_READY`
- `MATH_SMUL8`
- `MATH_SMUL16`
- `MATH_SMUL24`
- `MATH_SMUL32`
- `MATH_SMUL32_READY`

### Division and remainder/modulo

- `MATH_UDIV8`
- `MATH_UDIV16`
- `MATH_UDIV24`
- `MATH_UDIV32_16`
- `MATH_UMOD8`
- `MATH_UMOD16`
- `MATH_UMOD24`
- `MATH_UMOD32_16`
- `MATH_SDIV8`
- `MATH_SDIV16`
- `MATH_SDIV24`
- `MATH_SDIV32_16`
- `MATH_SMOD8`
- `MATH_SMOD16`
- `MATH_SMOD24`
- `MATH_SMOD32_16`
- `MATH_UDIV32_32`
- `MATH_UMOD32_32`
- `MATH_SDIV32_32`
- `MATH_SMOD32_32`

### Fixed-point helpers

- `MATH_UMUL16_SHR8`
- `MATH_SMUL16_SHR8`
- `MATH_UMUL32_SHR16`
- `MATH_SMUL32_SHR16`
- `MATH_UDIV16_SHL8`
- `MATH_SDIV16_SHL8`
- `MATH_URECIP16_Q16`

### Trig, roots and distance

- `MATH_SIN8`
- `MATH_COS8`
- `MATH_SINCOS8`
- `MATH_ATAN2_8`
- `MATH_ISQRT16`
- `MATH_ISQRT32`
- `MATH_DIST8_FAST`
- `MATH_DIST8_ACCURATE`

For exact inputs, outputs, clobbers, carry semantics and signed behavior, use the [complete user manual](USER_MANUAL.md) rather than relying on this summary.

## Turbo16 / Turbo32 on V3 and V4

Turbo mode is intended for **many multiplications in a row**.

Think of the REU as storage and zero page as the C64's fastest workbench:

```text
                 BEGIN
REU overlay -----------------> zero page
                               Turbo multiplier
                               CALL
                               CALL
                               CALL
                                   |
                 END               |
REU overlay <----------------------+ 
                               original ZP restored
```

`BEGIN` swaps a pre-assembled multiplier overlay from the REU into its configured ZP range. Repeated `CALL`s perform the products. `END` restores the caller's original ZP contents and retains the updated overlay for the next batch.

Turbo16:

```asm
        jsr MATH_REU_UMUL16_BEGIN

loop:
        ; write 16-bit X/Y
        jsr MATH_REU_UMUL16
        ; consume 32-bit Z
        ; ...
        bne loop

        jsr MATH_REU_UMUL16_END
```

Turbo32 uses the analogous:

```text
MATH_REU_UMUL32_BEGIN
MATH_REU_UMUL32
MATH_REU_UMUL32_END
```

Important: while Turbo is active, the configured overlay owns its ZP range. **Do not call normal math, game-math, QS16, or the other Turbo mode between `BEGIN` and its matching `END`.** IRQ/NMI code must also not overwrite that range or use the REU concurrently without coordination.

The Turbo ZP origins and REU banks are build-time configurable:

```asm
TURBO16_ZP_BASE    = $40
TURBO32_ZP_BASE    = $06
REU_TURBO16_BANK   = $00
REU_TURBO32_BANK   = $01
```

The builder assembles the overlays directly for those addresses, so relocation costs **zero runtime cycles**.

See [docs/TURBO_RELOCATION.md](docs/TURBO_RELOCATION.md) and [USER_MANUAL.md](USER_MANUAL.md) for the complete lifecycle and safety rules.

## V4 QS16 batch tier

V4 also exposes a quarter-square-backed 16×16 multiplication mode for small and medium batches.

Under the measured release model:

```text
1 product      normal MATH_UMUL16
2–8 products   QS16 BEGIN / repeated CALL / END
9+ products    Turbo16 BEGIN / repeated CALL / END
```

Treat these as dispatch guidance, not a universal law—measure your own workload if the crossover matters.

## Source relocation

The public API, game API, code, tables, I/O block, scratch regions, normal ZP, Turbo ZP origins and REU overlay banks are all selected at **assembly time**.

For a custom map:

1. copy the profile's reference configuration;
2. change the symbols you need;
3. build with `tools/assemble_sources.py`;
4. use the generated PRG, `math_api.inc`, and—on V3/V4—the generated REU image as one matched set.

Example:

```sh
python3 tools/assemble_sources.py \
    --profile v3_reu_512k \
    --config my_math_config.inc \
    --out my_math_build
```

The configuration validator rejects unsafe mappings, including:

- ZP ranges that wrap past `$FF`;
- use of the 6510 `$00/$01` processor-port locations;
- overlapping resident regions;
- C64/REU hardware-I/O conflicts;
- invalid page alignment;
- REU bank conflicts;
- Turbo overlays that do not fit completely in zero page.

See [docs/SOURCE_RELOCATION.md](docs/SOURCE_RELOCATION.md).

## Performance snapshot

Representative public mean cycle counts from the release evidence:

| Operation | V1 | V2 | V3 | V4 |
|---|---:|---:|---:|---:|
| `UMUL8` | 90.49 | 78.49 | **69.00** | **69.00** |
| `UMUL16` | 383.32 | 350.78 | 339.00 | **317.54** |
| `UMUL24` | 514.53 | **475.78** | **475.78** | **475.78** |
| `UMUL32` | 782.82 | **763.82** | **763.82** | **763.82** |
| `UDIV8` | 87.45 | 87.45 | **70.86** | **70.86** |
| `UDIV16` | 160.06 | **137.28** | **137.28** | **137.28** |
| `UMOD8` | 65.29 | 64.82 | **49.93** | **49.93** |
| `ISQRT32` | 1378.90 | 1198.62 | 1197.86 | **1046.62** |

Turbo steady-state means:

```text
Turbo16 CALL  ~215.54 cycles
Turbo32 CALL  ~731.41 cycles
```

Remember that Turbo batches also pay `BEGIN`/`END` setup costs.

Full measurements and provenance are in:

- [docs/PERFORMANCE_COMPARISON.csv](docs/PERFORMANCE_COMPARISON.csv)
- [docs/PERFORMANCE_GAME_MATH_FINAL.csv](docs/PERFORMANCE_GAME_MATH_FINAL.csv)
- profile-specific `PUBLIC_PERFORMANCE*.csv`

## Validation and reproducibility

The current reviewed release reports:

- **45/45** stable entries passing in each profile
- **180/180** relocated stable API entries total
- **16,688** stable-API machine calls
- **17,196** Turbo API calls across reference and alternate configurations
- **3,556** additional Turbo boundary products
- **20,388** fast-ISQRT32 correctness executions
- **27/27** configuration safety cases
- **8/8** deterministic reference/alternate rebuilds
- **145/145** release-audit checks
- reference and alternate resident builds independently reproduced byte-for-byte with ACME 0.97

The lean distribution deliberately does **not** ship generated `build_source/` trees. They are recreated deterministically on demand.

See:

- [validation/REVIEWED_RELEASE_VALIDATION.md](validation/REVIEWED_RELEASE_VALIDATION.md)
- [validation/RELEASE_AUDIT.json](validation/RELEASE_AUDIT.json)
- [validation/PACKAGE_AUDIT.json](validation/PACKAGE_AUDIT.json)
- [RELEASE_STATUS.json](RELEASE_STATUS.json)

## Repository layout

```text
.
├── README.md
├── QUICK_START.md
├── USER_MANUAL.md
├── CHANGELOG.md
├── Makefile
├── relocatable_source/       canonical source-relocatable build trees
├── v1_balanced/              V1 reference profile
├── v2_pareto_fast/           V2 reference profile
├── v3_reu_512k/              V3 reference profile + 512 KiB REU data
├── v4_reu_16m/               V4 reference profile + 16 MiB REU data
├── tools/                    build, emulator and validation tooling
├── docs/                     API, relocation, performance and provenance docs
└── validation/               reviewed validation evidence
```

Generated builds appear under `build_source/` and are intentionally not committed as part of the lean distribution.

## Documentation

Start with:

- **[USER_MANUAL.md](USER_MANUAL.md)** — complete integration and API manual
- **[QUICK_START.md](QUICK_START.md)** — build and validation commands
- [docs/VERSION_SELECTION.md](docs/VERSION_SELECTION.md) — choosing V1/V2/V3/V4
- [docs/API_COMPATIBILITY.md](docs/API_COMPATIBILITY.md) — common ABI and compatibility
- [docs/SOURCE_RELOCATION.md](docs/SOURCE_RELOCATION.md) — custom memory maps
- [docs/TURBO_RELOCATION.md](docs/TURBO_RELOCATION.md) — Turbo overlay relocation
- [docs/REU_GUIDE.md](docs/REU_GUIDE.md) — REU setup and VICE usage
- [docs/COMPLETE_TECHNICAL_ASSESSMENT.md](docs/COMPLETE_TECHNICAL_ASSESSMENT.md) — technical assessment
- [CHANGELOG.md](CHANGELOG.md) — complete release history
- [CSDB_CHANGELOG.txt](CSDB_CHANGELOG.txt) — concise CSDb-facing changes

## REU notes

`MATH_INIT` configures the library/REU controller state; it does **not** magically populate REU memory. V3/V4 must be used with the REU image generated for the same configuration as the resident PRG and `math_api.inc`.

For VICE commands and image names, see [docs/REU_GUIDE.md](docs/REU_GUIDE.md).

## Reentrancy, IRQs and banking

The library is not designed for unsynchronized recursive or concurrent use of shared math state.

In particular:

- do not invoke the library recursively;
- do not let an IRQ/NMI use library-owned ZP or REU state while a call is active unless you serialize access;
- during Turbo mode, the overlay owns its complete configured ZP range;
- custom placements must respect the C64's RAM/ROM/I/O banking state.

See the integration chapters in [USER_MANUAL.md](USER_MANUAL.md).

## License and provenance

This repository combines original integration/build/validation work with previously selected low-level C64 math kernels whose existing provenance/licensing status is retained. The integration does not purport to relicense independently sourced components.

The active `MATH_ISQRT32` implementation is independently derived and does not use the earlier Verz/Codebase64-derived recurrence.

Before redistributing or incorporating individual kernels, review:

- [docs/THIRD_PARTY_NOTICES_GAME_MATH.md](docs/THIRD_PARTY_NOTICES_GAME_MATH.md)
- `v3_reu_512k/LICENSE_NOTES.md`
- `v4_reu_16m/LICENSE_NOTES.md`
- any provenance/license notes shipped with the relevant profile/source component

## Release integrity

The canonical lean release includes `SHA256SUMS.txt` covering every shipped file except the checksum manifest itself.

To audit the package contents:

```sh
python3 tools/package_audit.py
```

To run the complete deterministic build path:

```sh
make all
```

---

**Target:** Commodore 64 / NMOS 6502/6510  
**Profiles:** V1 Balanced · V2 Pareto-Fast · V3 REU 512K · V4 REU 16M  
**Stable API:** 45 entries  
**Additional V3/V4 Turbo API:** 6 lifecycle entries
