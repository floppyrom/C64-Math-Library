# C64 Math Library V1–V5 + Custom Pareto Builder — Complete User Manual

**Release:** Consolidated source-backed V1–V5  
**Manual revision:** 2026-09-20  
**Target CPU:** NMOS 6502/6510, Commodore 64  
**Profiles:** V1 Balanced, V2 Pareto-Fast, V3 REU 512K, V4 REU 16M, V5 Hybrid Low-ZP

This manual explains how to integrate, configure, initialize, call, relocate, and validate the C64 Math Library. The library exposes a common 46-entry stable API across V1–V5 and custom generated stock-C64 profiles. It covers signed and unsigned arithmetic, game/fixed-point helpers, the V5 low-ZP hybrid, the budget-driven Custom Pareto Builder, V3/V4 REU operation, build-time-relocatable Turbo16/Turbo32 overlays, and the V4 QS16 small-batch mode.

The short version is:

1. Pick a fixed profile, or use `tools/pareto_wizard.py` for a stock-C64 budget-generated profile.
2. Build V1–V4 from `relocatable_source/<profile>/math_relocatable.asm`; build V5 with `tools/build_hybrid.py`; build custom stock-C64 profiles with `tools/build_pareto.py`.
3. Include the generated `math_api.inc` in your application.
4. Call `MATH_INIT` once when required: mandatory on V2–V4 and on generated Pareto profiles whose manifest requires it; optional/recommended on V1 and V5.
5. Put operands in the 32-byte public I/O block.
6. `JSR` the desired math entry.
7. Read the result from the documented output vector and check Carry where required.
8. On V3/V4, make sure the matching generated REU image is present before `MATH_INIT`.
9. For Turbo16/Turbo32, obey the strict `BEGIN -> repeated CALL -> END` lifecycle.

---

## Finding performance and source code

- Human-readable speed overview: `PERFORMANCE.md`.
- All shipped profile results with direct source paths: `benchmarks/PUBLIC_PROFILE_RESULTS.csv`.
- Standalone record/Pareto alternatives: `benchmarks/STANDALONE_RESULTS.csv`.
- Complete public source index: `routines/SOURCE_CATALOG.csv`.
- Typed naming rules: `docs/NAMING_STANDARD.md`.

Every published benchmark is source-backed and checked by `tools/validate_public_catalog.py`.


## Consolidated cycles and memory index

For one cross-profile table covering every stable routine plus the REU Turbo/QS16 surfaces, see [`docs/CONSOLIDATED_ROUTINE_TABLE.md`](docs/CONSOLIDATED_ROUTINE_TABLE.md) or the machine-readable [`docs/CONSOLIDATED_ROUTINE_TABLE.csv`](docs/CONSOLIDATED_ROUTINE_TABLE.csv). It reports public cycles, reachable executable bytes, concrete ZP use/ranges, and persistent hardware-stack-page reservation.


## 1. Which profile should I use?

| Profile | Hardware | Main reason to choose it | Important cost |
|---|---|---|---|
| **V1 Balanced** | Stock C64 | Lowest zero-page integration pressure | Slower than V2 on many resident routines |
| **V2 Pareto-Fast** | Stock C64 | Best general no-REU speed/space profile | Larger ZP commitment; `MATH_INIT` required |
| **V3 REU 512K** | C64 + 512 KiB REU | Fast REU-backed 8-bit services, reciprocal, and Turbo modes | Requires matching 512 KiB REU image and ownership discipline |
| **V4 REU 16M** | C64 + 16 MiB REU-compatible device/emulator | Fastest feature set; exact REU atan2/ISQRT16, QS16, Turbo | Requires modern/VICE-style 16 MiB REU; 512 extra C64 table bytes for fast ISQRT32 |
| **V5 Hybrid Low-ZP** | Stock C64 | V1 31-byte ZP footprint with selected V2-speed division/modulo/trig paths | Uses a configurable 7,680-byte hybrid code block plus private division/table islands; exact extra private RAM vs V1 is 9,633 B |
| **Custom Pareto Builder** | Stock C64 | Fastest certified V1/V2 combination for your ZP/RAM/workload budget | Generated profile; resource use and `MATH_INIT` requirement depend on selection |

Recommended default choices:

- No REU and ZP is tight: **V1**.
- No REU and speed matters more: **V2**.
- Standard 512 KiB REU: **V3**.
- VICE or modern 16 MiB REU-compatible implementation: **V4**.
- Stock C64, V1-sized ZP budget but faster division/modulo/COS/SINCOS: **V5**.
- New stock-C64 game/demo where you know your available ZP/RAM: **Custom Pareto Builder** (recommended flexible path).

All five resident profiles and generated Pareto profiles expose the same **46-entry stable API**. V3/V4 additionally expose six stateful Turbo lifecycle entries. V4 also contains the specialized QS16 small-batch mode. V5 and custom Pareto builds add no new public calls.

---

## 2. CPU and calling assumptions

The library is written for **NMOS 6502/6510 semantics**.

### Required CPU state

The decimal flag must be clear:

```asm
        cld
```

The safest application convention is to execute `CLD` during startup and never leave decimal mode enabled when calling the library.

### Registers

Unless a routine explicitly says otherwise:

- **A, X, Y are volatile** and may be destroyed.
- Do not expect N, Z, V status flags to survive.
- Carry is part of the public status contract and must be checked for division-like operations.

### Input preservation

The stable public API preserves the documented input bytes in the public I/O vectors. This allows the caller to inspect or reuse operands after the call.

### Reentrancy

The library is **not reentrant**, but **sequential calls—including repeated calls inside ordinary game/demo loops—are fully supported**. A second math call must not begin while a previous math call is still executing. The optimized kernels use shared ZP, RAM scratch, tables, self-modifying state, and—on REU profiles—the REU controller.

This is safe:

```asm
.loop:
        jsr MATH_UMUL16
        ; consume/store the result, set the next operands
        bne .loop
```

Do not invoke the library from an IRQ/NMI that interrupts an active foreground math call, and do not let IRQ/NMI code overwrite library-owned ZP or REU state during Turbo mode. If interrupt code also needs the library, serialize access.

---

## 3. Public I/O layout

Every stable routine communicates through one 32-byte public memory block. In the reference map it starts at `$C000`; in a relocatable build the location is `MATH_IO` from `math_config.inc`.

The generated caller include exports these group bases:

```asm
MATH_X      ; 4 bytes
MATH_Y      ; 4 bytes
MATH_Z      ; 8 bytes
MATH_N      ; 4 bytes
MATH_D      ; 4 bytes
MATH_Q      ; 4 bytes
MATH_R      ; 4 bytes
```

All multi-byte values are **little-endian**: byte 0 is least significant.

| Offset from `MATH_IO` | Group | Meaning |
|---:|---|---|
| `+$00..+$03` | `MATH_X` | multiplication / geometry input X |
| `+$04..+$07` | `MATH_Y` | multiplication / geometry input Y |
| `+$08..+$0F` | `MATH_Z` | multiplication / game-math result |
| `+$10..+$13` | `MATH_N` | dividend / radicand |
| `+$14..+$17` | `MATH_D` | divisor |
| `+$18..+$1B` | `MATH_Q` | quotient / reciprocal |
| `+$1C..+$1F` | `MATH_R` | remainder |

### Convenient byte aliases

The old fixed-reference includes define aliases such as `math_x0`, `math_q2`, etc. The generated relocatable include intentionally exports the group bases. You can add these aliases in your own project:

```asm
math_x0 = MATH_X+0
math_x1 = MATH_X+1
math_x2 = MATH_X+2
math_x3 = MATH_X+3

math_y0 = MATH_Y+0
math_y1 = MATH_Y+1
math_y2 = MATH_Y+2
math_y3 = MATH_Y+3

math_z0 = MATH_Z+0
math_z1 = MATH_Z+1
math_z2 = MATH_Z+2
math_z3 = MATH_Z+3
math_z4 = MATH_Z+4
math_z5 = MATH_Z+5
math_z6 = MATH_Z+6
math_z7 = MATH_Z+7

math_n0 = MATH_N+0
math_n1 = MATH_N+1
math_n2 = MATH_N+2
math_n3 = MATH_N+3

math_d0 = MATH_D+0
math_d1 = MATH_D+1
math_d2 = MATH_D+2
math_d3 = MATH_D+3

math_q0 = MATH_Q+0
math_q1 = MATH_Q+1
math_q2 = MATH_Q+2
math_q3 = MATH_Q+3

math_r0 = MATH_R+0
math_r1 = MATH_R+1
math_r2 = MATH_R+2
math_r3 = MATH_R+3
```

---

## 4. Initialization

### Recommended universal startup

Even though ordinary V1 calls do not require initialization, the simplest application rule is:

```asm
        cld
        jsr MATH_INIT
```

Call it once after the library—and on V3/V4, the REU image—has been installed.

### V1

`MATH_INIT` is not required for the ordinary safe entry points, but it prepares persistent state used by `MATH_UMUL32_READY`. Calling it once is recommended.

### V5

Like V1, `MATH_INIT` is not required for ordinary safe entries. The hybrid validator explicitly exercises imported and untouched V1 paths from a cold load without calling `MATH_INIT`. Calling it once is still recommended if your program may use `MATH_UMUL32_READY`.

### Custom Pareto builds

Read `math_init_required` in the generated `selection_manifest.json` (or `MATH_PROFILE_INIT_REQUIRED` in the generated include). If true, call `MATH_INIT` once before any math routine. `--init-policy optional` forbids selections that would make initialization mandatory.

### V2

`MATH_INIT` is **mandatory**. It initializes persistent table-page state and installs the native SMUL16 executable-ZP core.

### V3/V4

`MATH_INIT` is **mandatory** and must be called after the matching REU contents are available. It initializes resident multiplier state and programs the normal REU one-byte lookup transport.

`MATH_INIT` does **not** fill physical REU RAM with the library tables. The required REU image must already have been attached/preloaded or copied to the REU by your loader.

---

## 5. Building the library

Python 3 is sufficient. The package includes a deterministic 6502 assembler. ACME 0.97 is optional as an independent verification assembler.

From the release root:

```sh
# Generate canonical symbolic source/configuration templates
python3 tools/generate_sources.py

# Build the four canonical V1-V4 reference configurations
python3 tools/assemble_sources.py --profile all --config-kind reference

# Build the four canonical V1-V4 alternate proof configurations
python3 tools/assemble_sources.py --profile all --config-kind alternate
```

Equivalent Makefile targets:

```sh
make reference
make alternate

# Build the V5 Hybrid Low-ZP reference + alternate maps
make hybrid

# Build and run all V5-specific validation
make hybrid-validate
```

A reference source build produces, for example:

```text
build_source/reference/v2_pareto_fast/
    math_v2_pareto_fast_source_built.prg
    math_api.inc
    source_build_manifest.json
```

V3/V4 additionally produce the matching REU image:

```text
build_source/reference/v3_reu_512k/
    c64_math_v3_reu_512k_source_built.reu

build_source/reference/v4_reu_16m/
    c64_math_v4_reu_16m_source_built.reu
```

Use the `math_api.inc` generated in the **same output directory as the binary you are actually using**.

---

## 5A. Building an optimized stock-C64 profile from a resource budget

For games and demos, the Custom Pareto Builder can choose implementations instead of forcing a fixed V1/V2/V5 decision.

Interactive:

```sh
python3 tools/pareto_wizard.py
```

Direct:

```sh
python3 tools/build_pareto.py --zp-budget 60
```

The ZP budget is the **total number of zero-page bytes** the generated library may own. The minimum is 31 bytes, matching V1. You can also constrain exact additional private RAM:

```sh
python3 tools/build_pareto.py --zp-budget 60 --ram-budget 6000
```

Or forbid selections that make startup initialization mandatory:

```sh
python3 tools/build_pareto.py --zp-budget 31 --init-policy optional
```

Hot-routine weights change the optimization objective without changing the ABI:

```sh
python3 tools/build_pareto.py --zp-budget 55 --weight MATH_UMUL24=100
```

The generated `selection_manifest.json` records every implementation pack, exact ZP ranges, exact private RAM bytes/ranges, `MATH_INIT` requirement, addresses and SHA-256. Selection is performed entirely at build time; **there is no runtime dispatch overhead**.

Current equal-weight breakpoints are:

| ZP | Default selection | Exact extra RAM vs V1 |
|---:|---|---:|
| 31 | `atan2_fast` + V5 zero-ZP imports | 9633 B |
| 36 | above + UMUL8 pack | 10206 B |
| 60 | above + record UMUL16/UMUL24 pack | 11149 B |
| 147 | `atan2_fast` + V5 imports + native SMUL16 | 9837 B |
| 176 | all active certified hybrid packs, including `atan2_fast` | 11335 B |
| 221 | complete V2 | 208 B resident increase |

The optimizer maximizes weighted cycle savings, so resource use is not required to be monotonic across those points. At 31 ZP + `--ram-budget 0`, the generated PRG is byte-identical to V1. At the default 31-ZP point (and with `--init-policy optional`), it is byte-identical to V5. At 221 ZP the builder selects complete V2.

See **`docs/PARETO_BUILDER.md`** for pack geometry, workload weighting, RAM-under-ROM details and validation.

---

## 6. Building a custom memory map

Start by copying the reference configuration:

```sh
cp relocatable_source/v2_pareto_fast/math_config_reference.inc my_math_config.inc
```

Edit the addresses, then build:

```sh
python3 tools/assemble_sources.py \
    --profile v2_pareto_fast \
    --config my_math_config.inc \
    --out my_math_build
```

The output will be under the selected output directory. For V3/V4, the build automatically generates a **matching REU image** with the selected REU bank roles and freshly assembled Turbo overlays.

### Configurable C64 symbols

| Symbol | Purpose | Reference value |
|---|---|---:|
| `REG_LOW` | low resident code/data region | `$1000` |
| `REG_API` | integer API and associated code | `$3000` |
| `REG_KERNEL` | resident kernels | `$4000` |
| `REG_GAME_API` | independent 57-byte game-math JMP block | `$5E00` |
| `REG_TABLE` | resident tables | `$6000` |
| `REG_GAME` | game/fixed-point code/data | `$C100` |
| `MATH_IO` | 32-byte caller I/O block | `$C000` |
| `REU_SCRATCH` | C64-side REU transfer buffer | `$C020` |
| `V1_SCRATCH` | V1 ordinary-RAM game scratch | `$C040` |
| `ZP_MAIN` | normal library ZP origin | `$02` |
| `ZP_SMUL` | V2–V4 native SMUL16 executable-ZP origin | `$80` |
| `HYBRID_CODE` | V5/custom-Pareto zero-ZP import region | `$A000` |
| `PARETO_AUX` | custom-Pareto generated code/data base | `$B200` |
| `TURBO16_ZP_BASE` | V3/V4 113-byte Turbo16 overlay origin | `$3E` |
| `TURBO32_ZP_BASE` | V3/V4 135-byte stack-free Turbo32 overlay origin | `$0A` |

V3/V4 configurations additionally assign each REU service to a bank. V4's QS16 table uses eight consecutive 64 KiB banks beginning at `REU_QS16_BASE_BANK`. V5 configures `HYBRID_CODE`; custom Pareto maps configure both `HYBRID_CODE` and `PARETO_AUX`. The builders reject overflow, I/O crossings and collisions with selected resident/private regions.

### Build-time safety checks

The builder rejects, among other things:

- regions outside the 16-bit C64 address space;
- ZP allocations beyond `$FF`;
- use of `$00/$01`, which belong to the 6510 processor port;
- overlapping claimed resident regions;
- overlapping normal ZP allocations;
- use of the REU register page `$DF00-$DFFF`;
- invalid page alignment for page-sensitive regions;
- illegal/colliding REU bank assignments;
- V3 REU banks outside `0..7`;
- a V4 QS16 region that is not eight-bank aligned or exceeds 16 MiB;
- Turbo origins that do not fit completely in page zero.

Legal Turbo origins are therefore:

```text
Turbo16: $02 .. $8F     ; 113 bytes
Turbo32: $02 .. $79     ; 135 bytes
```

### Important C64 banking caveat

The source validator models CPU address space and library collisions; it does not manage your application's 6510 ROM/I/O banking policy for you.

If you deliberately place executable/data regions under BASIC ROM, KERNAL ROM, or the `$D000-$DFFF` I/O/character-ROM area, your application must configure `$01` so the intended RAM is visible at the time it is accessed. The safest custom maps use ordinary always-visible RAM unless you explicitly know you want RAM-under-ROM.

The supplied alternate validation map is a relocation proof, not a recommendation for a normal game memory layout.

---

## 7. Using the prebuilt reference binaries

Each profile contains a fixed-map reference PRG under its `resident/` directory. These are useful for direct testing and reproduce the validated reference layout.

```text
v1_balanced/resident/math_v1_balanced_game_math.prg
v2_pareto_fast/resident/math_v2_pareto_fast_game_math.prg
v3_reu_512k/resident/math_v3_reu_512k_game_math.prg
v4_reu_16m/resident/math_v4_reu_16m_game_math.prg
v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg
```

For new development, prefer the source-relocatable build system rather than hardcoding the reference addresses. V5 is generated by `tools/build_hybrid.py`; its reference `$A000-$BDFF` hybrid block is RAM under BASIC ROM, so BASIC must be banked out while imported V5 code executes, or `HYBRID_CODE` must be relocated to a suitable visible RAM region.

The PRGs contain padding between sparse resident regions. If you integrate the library into a larger linker/build system, use the source or documented segment map rather than assuming the entire contiguous PRG span must remain exclusively allocated.

---

## 8. Your first call: unsigned 16×16 multiplication

Using a generated relocatable include:

```asm
!cpu 6510
!source "build_source/reference/v2_pareto_fast/math_api.inc"

math_x0 = MATH_X+0
math_x1 = MATH_X+1
math_y0 = MATH_Y+0
math_y1 = MATH_Y+1
math_z0 = MATH_Z+0
math_z1 = MATH_Z+1
math_z2 = MATH_Z+2
math_z3 = MATH_Z+3

init_math:
        cld
        jsr MATH_INIT
        rts

multiply_example:
        ; $1234 * $0020 = $00024680
        lda #$34
        sta math_x0
        lda #$12
        sta math_x1
        lda #$20
        sta math_y0
        lda #$00
        sta math_y1

        jsr MATH_UMUL16

        ; result is little-endian in z0..z3:
        ; $80,$46,$02,$00
        rts
```

For multiply entries, Carry returns clear.

---

# Part II — Stable 46-entry API reference

## 9. Unsigned multiplication

| Entry | Input | Output | Carry | Meaning |
|---|---|---|---|---|
| `MATH_UMUL8` | `X[0]`, `Y[0]` | `Z[0..1]` | `C=0` | unsigned 8×8 → 16 |
| `MATH_UMUL16` | `X[0..1]`, `Y[0..1]` | `Z[0..3]` | `C=0` | unsigned 16×16 → 32 |
| `MATH_UMUL24` | `X[0..2]`, `Y[0..2]` | `Z[0..5]` | `C=0` | unsigned 24×24 → 48 |
| `MATH_UMUL32` | `X[0..3]`, `Y[0..3]` | `Z[0..7]` | `C=0` | unsigned 32×32 → 64 |
| `MATH_UMUL32_READY` | same as UMUL32 | `Z[0..7]` | `C=0` | faster initialized-state entry |

`MATH_UMUL32_READY` is a workload-specific entry. Use it only after `MATH_INIT` and only while the library-owned persistent state has not been overwritten by external code. If in doubt, call `MATH_UMUL32`.

---

## 10. Signed multiplication

Signed values use two's-complement representation.

| Entry | Input | Output | Carry | Meaning |
|---|---|---|---|---|
| `MATH_SMUL8` | signed `X[0]`, `Y[0]` | signed `Z[0..1]` | `C=0` | signed 8×8 → 16 |
| `MATH_SMUL16` | signed `X[0..1]`, `Y[0..1]` | signed `Z[0..3]` | `C=0` | signed 16×16 → 32 |
| `MATH_SMUL24` | signed `X[0..2]`, `Y[0..2]` | signed `Z[0..5]` | `C=0` | signed 24×24 → 48 |
| `MATH_SMUL32` | signed `X[0..3]`, `Y[0..3]` | signed `Z[0..7]` | `C=0` | signed 32×32 → 64 |
| `MATH_SMUL32_READY` | same as SMUL32 | `Z[0..7]` | `C=0` | initialized-state signed entry |

Because the result width is doubled, the full mathematical signed product fits in the destination width.


### Implementation provenance

The signed API is uniform and all shipped `MATH_SMUL*`/`MATH_SDIV*` paths now own **native signed executable kernels**. Native here means a signed entry never enters the corresponding unsigned executable engine; immutable lookup tables may still be shared. V2–V4 `MATH_SMUL16` keeps its signed-specific quarter-square kernel in executable ZP, while V1/V5 preserve the 31-byte low-ZP contract with private signed executable arithmetic paths.

See `docs/SIGNED_IMPLEMENTATIONS.md` for the exact per-profile taxonomy and resource trade-offs.

---


### Division refresh 2026-09-20

The current fixed profiles apply Repose-derived UDIV24 and follow-on direct-output optimizations profile-by-profile. V1/V2/V5 use the refreshed CPU UDIV8 path; V3/V4 retain their faster REU UDIV8/UMOD8 planes. Native signed division owns signed-specific executable paths, and the same-corpus pre/post audit reports zero timing regressions across 23 measured public division-family entries in every profile. See `docs/DIVISION_REFRESH_2026-09-20.md`.

## 11. Unsigned division and modulo

Unsigned division uses `N` for numerator/dividend and `D` for divisor.

| Entry | Input | Quotient | Remainder | Divide by zero |
|---|---|---|---|---|
| `MATH_UDIV8` | `N8 / D8` | `Q[0]` | `R[0]` | `C=1`, Q/R = 0 |
| `MATH_UDIV16` | `N16 / D16` | `Q[0..1]` | `R[0..1]` | `C=1`, Q/R = 0 |
| `MATH_UDIV24` | `N24 / D24` | `Q[0..2]` | `R[0..2]` | `C=1`, Q/R = 0 |
| `MATH_UDIV32_16` | `N32 / D16` | `Q[0..3]` | `R[0..1]` | `C=1`, Q/R = 0 |

Successful division returns `C=0`.

The modulo entries are:

| Entry | Contract |
|---|---|
| `MATH_UMOD8` | computes the unsigned 8-bit remainder in `R[0]`; `C=1` and `R[0]=0` when divisor is zero |
| `MATH_UMOD16` | alias of UDIV16; both quotient and remainder are produced |
| `MATH_UMOD24` | alias of UDIV24; both quotient and remainder are produced |
| `MATH_UMOD32_16` | alias of UDIV32_16; both quotient and remainder are produced |

### Example

```asm
        ; 1000 / 24
        lda #<$03E8
        sta MATH_N+0
        lda #>$03E8
        sta MATH_N+1

        lda #24
        sta MATH_D+0
        lda #0
        sta MATH_D+1

        jsr MATH_UDIV16
        bcs .divide_by_zero

        ; Q16 = 41, R16 = 16
        rts
.divide_by_zero:
        ; handle error
        rts
```

---

## 12. Signed division and remainder

Signed division uses two's-complement inputs and **truncates toward zero**, matching the normal C integer-division rule.

For nonzero divisor:

```text
Q = trunc(N / D)
R = N - Q*D
```

The remainder therefore follows the sign of the dividend when nonzero.

| Entry | Input | Quotient | Remainder |
|---|---|---|---|
| `MATH_SDIV8` | signed N8 / D8 | signed Q8 | signed R8 |
| `MATH_SDIV16` | signed N16 / D16 | signed Q16 | signed R16 |
| `MATH_SDIV24` | signed N24 / D24 | signed Q24 | signed R24 |
| `MATH_SDIV32_16` | signed N32 / D16 | signed Q32 | signed R16 |

Signed modulo aliases:

```text
MATH_SMOD8
MATH_SMOD16
MATH_SMOD24
MATH_SMOD32_16
```

They use the same signed division kernels and therefore return both Q and R.

Divide by zero returns `C=1` and zero Q/R. Success returns `C=0`.

There is no separate signed-overflow flag. If the mathematical quotient is outside the destination two's-complement width—for example minimum signed integer divided by `-1`—the stored result is the natural width-truncated two's-complement value.

---

## 13. Exact 32/32 division and modulo

The game-math extension adds full-width division:

| Entry | Contract |
|---|---|
| `MATH_UDIV32_32` | unsigned N32 / D32 → Q32,R32 |
| `MATH_UMOD32_32` | alias of UDIV32_32; Q and R both returned |
| `MATH_SDIV32_32` | signed N32 / D32 → signed Q32,R32, truncation toward zero |
| `MATH_SMOD32_32` | alias of SDIV32_32; Q and R both returned |

The same Carry convention applies:

```text
C=0  success
C=1  divisor zero, Q=0, R=0
```

---

## 14. Fixed-point multiply helpers

These routines perform a full multiply and discard low fractional bytes.

### `MATH_UMUL16_SHR8`

```text
input:   unsigned X16, Y16
output:  Z24 = (X * Y) >> 8
```

### `MATH_SMUL16_SHR8`

```text
input:   signed X16, Y16
output:  signed Z24 = arithmetic ((X * Y) >> 8)
```

This is particularly useful for Q8.8-style arithmetic.

Example: 1.5 × 2.0 in Q8.8:

```asm
        lda #$80
        sta MATH_X+0
        lda #$01
        sta MATH_X+1       ; $0180 = 1.5 Q8.8

        lda #$00
        sta MATH_Y+0
        lda #$02
        sta MATH_Y+1       ; $0200 = 2.0 Q8.8

        jsr MATH_SMUL16_SHR8
        ; Z24 = $000300, representing 3.0 in Q8.8
```

### `MATH_UMUL32_SHR16`

```text
input:   unsigned X32,Y32
output:  Z48 = (X*Y) >> 16
```

### `MATH_SMUL32_SHR16`

```text
input:   signed X32,Y32
output:  signed Z48 = arithmetic ((X*Y) >> 16)
```

All multiply-shift entries return `C=0`.

---

## 15. Fixed-point division helpers

### `MATH_UDIV16_SHL8`

```text
Q24,R16 = (N16 << 8) / D16
```

### `MATH_SDIV16_SHL8`

```text
Q24,R16 = (signed N16 << 8) / signed D16
```

Signed division truncates toward zero.

These are useful when you want to form a fractional quotient without manually widening the numerator.

Status:

```text
C=0  success
C=1  divisor zero; Q=0,R=0
```

---

## 16. Exact Q16 reciprocal

`MATH_URECIP16_Q16` computes:

```text
Q24 = floor(65536 / D16)
```

Input is `D[0..1]`; output is `Q[0..2]`.

The output is 24 bits because `D=1` produces `65536 = $010000`.

```text
C=0  success
C=1  D=0 and Q=0
```

---

## 17. Trigonometry

The phase domain is one unsigned byte:

```text
$00 =   0 degrees
$40 =  90 degrees
$80 = 180 degrees
$C0 = 270 degrees
```

### Sine

```text
MATH_SIN8
input:  X[0] = phase
output: Z[0] = signed s8 amplitude approximately -127..+127
```

### Cosine

```text
MATH_COS8
input:  X[0] = phase
output: Z[0] = signed s8 amplitude approximately -127..+127
```

### Sine + cosine

```text
MATH_SINCOS8
input:  X[0] = phase
output: Z[0] = sine, Z[1] = cosine
```

The bytes are two's-complement signed values. All three routines return `C=0`.

---

## 18. `atan2`

```text
MATH_ATAN2_8
input:   X[0] = dx as signed 8-bit
         Y[0] = dy as signed 8-bit
output:  Z[0] = unsigned phase byte
```

It follows the mathematical orientation:

```text
phase = atan2(dy, dx)
```

with the same `$00/$40/$80/$C0` phase convention as the trig functions.

`dx=0,dy=0` returns zero.

V1–V3 use the compact approximation and are within one phase unit of the rounded mathematical reference over the signed-byte plane. V4 uses its exact REU lookup reference.

---

## 19. Integer square root

### `MATH_ISQRT16`

```text
input:   N16
output:  Z16 = floor(sqrt(N))
```

### `MATH_ISQRT32`

```text
input:   N32
output:  Z16 = floor(sqrt(N))
```

Both are exact integer square roots and return `C=0`.

The active ISQRT32 implementation is the fast independently derived hybrid used by this FINAL release: it seeds the upper root byte through the exact ISQRT16 path and performs the remaining eight restoring base-4 refinement steps.

The input radicand is preserved.

---

## 20. Distance approximations

Inputs are signed 8-bit coordinate deltas:

```text
X[0] = dx
Y[0] = dy
```

### Fast

```text
MATH_DIST8_FAST
Z[0] = max(|dx|,|dy|) + floor(min(|dx|,|dy|)/2)
```

### More accurate

```text
MATH_DIST8_ACCURATE
Z[0] = rounded 243/256 * max + rounded 107/256 * min
```

The accurate coefficient pair was selected exhaustively for the documented integer form. Both routines return an unsigned byte in `Z[0]` and `C=0`.

---

## 20A. 2D Q8.8 vector normalization

```text
MATH_VEC2_NORMALIZE_Q8_8
input:   X[0..1] = signed Q8.8 x
         Y[0..1] = signed Q8.8 y
output:  Z[0..1] = signed Q1.15 normalized x
         Z[2..3] = signed Q1.15 normalized y
status:  C=0 for a non-zero vector
         C=1 for (0,0), with Z[0..3]=0
```

The input vector is preserved. A/X/Y are volatile. The routine is approximate but uses the same certified error contract in every fixed profile and generated Custom Pareto build: angular error <=0.3621 degrees and component error <=202 Q1.15 LSB. The current full-domain certificate is tighter at <=0.360856382 degrees / <=200 LSB.

The implementation is profile-selected. V1/V5 keep the 31-byte low-ZP integration contract, V2 uses the Pareto-fast stock-C64 path, and V3/V4 use a 32 KiB direct ratio-index table in the upper half of the configured `REU_TURBO16_BANK`. See `docs/VEC2_NORMALIZE_Q8_8.md`.

### Standalone normalization source

The implementation can be taken directly from the profile-specific native source:

- `v1_balanced/resident/vector/native/vec2_normalize_q8_8.asm`
- `v2_pareto_fast/resident/vector/native/vec2_normalize_q8_8.asm`
- `v3_reu_512k/resident/vector/native/vec2_normalize_q8_8.asm`
- `v4_reu_16m/resident/vector/native/vec2_normalize_q8_8.asm`
- `v5_hybrid_lowzp/resident/vector/native/vec2_normalize_q8_8.asm`

These are executable build inputs, not pseudocode or post-build listings. The adjacent
README in each directory lists the scratch/table/REU dependencies needed when lifting
the routine out of the full library.

---

# Part III — REU profiles


## 21. V3 512 KiB REU setup

For the fixed reference build, use:

```text
v3_reu_512k/reu/c64_math_v3_512k_game_math.reu
```

For a source-built/custom map, use the `.reu` generated next to that build's PRG.

### VICE example

From the release root, with the reference image:

```sh
x64sc -reu -reusize 512 \
  -reuimage v3_reu_512k/reu/c64_math_v3_512k_game_math.reu \
  your_program.prg
```

Then your program should call:

```asm
        cld
        jsr MATH_INIT
```

### Reference bank roles

```text
bank 0  UMUL8 product low
bank 1  UMUL8 product high
bank 2  UDIV8 quotient
bank 3  UDIV8 remainder / UMOD8
bank 4  Turbo16 overlay
bank 5  Turbo32 overlay + metadata page
bank 6  reciprocal low
bank 7  reciprocal high
```

Custom builds may relocate these roles while remaining inside banks 0–7.

---

## 22. V4 16 MiB REU setup

For the fixed reference build, use:

```text
v4_reu_16m/reu/c64_math_v4_16m_game_math.reu
```

VICE example:

```sh
x64sc -reu -reusize 16384 \
  -reuimage v4_reu_16m/reu/c64_math_v4_16m_game_math.reu \
  your_program.prg
```

Then call `MATH_INIT` once.

V4 adds:

- exact REU-backed `ATAN2_8` table;
- exact REU-backed `ISQRT16` table;
- the large QS16 quarter-square region;
- the same relocatable Turbo modes as V3;
- two resident 256-byte square planes used by the fast ISQRT32 setup.

The 16 MiB profile targets VICE and compatible modern REU implementations. It should not be interpreted as a claim that a stock historical 17xx REU provides 16 MiB.

---

## 23. Physical REU hardware

A `.reu` file in this release is an image of REU memory. VICE can attach it directly.

On real hardware, `MATH_INIT` does not magically upload this file. Your loader must arrange for the same data to exist at the documented REU addresses before the API uses it. The exact mechanism depends on your REU/clone/cartridge environment.

Do not call an REU-backed profile with uninitialized or mismatched REU contents; arithmetic results will be wrong even though the resident PRG itself is correct.

---

# Part IV — Turbo16 / Turbo32

## 24. What Turbo mode is

Turbo16 and Turbo32 are V3/V4 **batch modes**. They achieve higher throughput by swapping executable code into zero page.

Unlike an ordinary API call, Turbo has state:

```text
BEGIN
  CALL
  CALL
  CALL
  ...
END
```

`BEGIN` swaps the configured overlay from REU into the configured ZP range. `END` restores the caller's original ZP contents and saves the modified/self-patched overlay back to REU so another batch can be started later.

The overlay is assembled directly for the chosen ZP origin. There is no runtime relocation step and therefore no relocation cycle penalty.

### Turbo modes in plain English

Think of the REU as a storage cupboard and zero page as the C64's fastest workbench. The Turbo multiplier normally lives in the REU so it does not permanently occupy precious zero page. When you have a batch of multiplications to do, `BEGIN` temporarily puts that specialized multiplier onto the zero-page workbench. You then use `CALL` repeatedly. `END` removes the accelerator and gives your original zero-page bytes back exactly as they were.

```text
                 BEGIN
REU overlay  ─────────────►  ZERO PAGE
                              Turbo multiplier
                                  CALL
                                  CALL
                                  CALL
                                   ...
                                    │
                 END                │
REU overlay  ◄──────────────────────┘
                              original ZP restored
```

So Turbo16/Turbo32 are **not different mathematical operations**. They are batch execution modes for the same unsigned multiplication jobs:

- **Turbo16:** repeated 16-bit × 16-bit → 32-bit products.
- **Turbo32:** repeated 32-bit × 32-bit → 64-bit products.

The reason the REU helps is not that the REU itself performs multiplication. Its DMA engine lets the library install and remove the highly optimized executable-ZP overlay cheaply enough that the setup cost can be amortized across a batch.

A useful mental model is:

```text
one or a few products  -> normal API call
many products in a row -> BEGIN, repeated Turbo CALL, END
```

For V4 16-bit multiplication there is also the QS16 middle tier documented in Part V, so the measured default rule is 1 product = normal `MATH_UMUL16`, 2–8 products = QS16, 9+ products = Turbo16.

The important ownership rule follows directly from the workbench analogy: **between `BEGIN` and `END`, the configured Turbo ZP range belongs to the overlay, not to the rest of your program.** Do not let normal math calls, another Turbo mode, or an IRQ/NMI overwrite it during that interval.

---

## 25. Turbo16 lifecycle

Entries:

```text
MATH_REU_UMUL16_BEGIN
MATH_REU_UMUL16
MATH_REU_UMUL16_END
```

Input/output of each `MATH_REU_UMUL16` call:

```text
input:   X16 in MATH_X+0..1
         Y16 in MATH_Y+0..1
output:  Z32 in MATH_Z+0..3
```

Unsigned multiplication only.

Reference geometry:

```text
TURBO16_ZP_BASE = $3E
owned range      = $3E-$AE
```

Legal source-configurable origins are `$02-$8F`.

### Example

```asm
        jsr MATH_INIT

        jsr MATH_REU_UMUL16_BEGIN

        ; product 1
        lda #$34
        sta MATH_X+0
        lda #$12
        sta MATH_X+1
        lda #$78
        sta MATH_Y+0
        lda #$56
        sta MATH_Y+1
        jsr MATH_REU_UMUL16
        ; consume/copy MATH_Z+0..3 here

        ; product 2, 3, ...
        ; write new X/Y then call again

        jsr MATH_REU_UMUL16_END
```

After `END`, the bytes that occupied the Turbo16 ZP range before `BEGIN` are restored exactly.

Reference benchmark model:

```text
BEGIN ≈ 282 cycles
CALL  ≈ 215.54 cycles mean
END   ≈ 327 cycles
```

For V3, the measured break-even versus ordinary UMUL16 is around five products per batch. On V4, use the dispatch guidance below because QS16 gives a better middle tier.

---

## 26. Turbo32 lifecycle

Entries:

```text
MATH_REU_UMUL32_BEGIN
MATH_REU_UMUL32
MATH_REU_UMUL32_END
```

Input/output:

```text
input:   X32 in MATH_X+0..3
         Y32 in MATH_Y+0..3
output:  Z64 in MATH_Z+0..7
```

Reference geometry:

```text
TURBO32_ZP_BASE = $0A
owned range      = $0A-$90
```

Legal source-configurable origins are `$02-$79`.

Reference benchmark model:

```text
BEGIN ≈ 538 cycles
CALL  ≈ 731.41 cycles mean
END   ≈ 583 cycles
```

The measured break-even is approximately 43 products per batch versus the normal 32-bit multiplication path under the release timing model.

---

## 27. Turbo ownership rules

The safest and officially supported rule is simple:

> **Do not call any normal, signed, game-math, QS16, or other Turbo mode between a Turbo BEGIN and its matching END.**

During the active interval, the overlay owns its complete configured ZP range. Turbo32 is still an exclusive mode, but the stack-free 135-byte overlay is substantially less invasive than the former 241-byte overlay.

Also do not:

- nest Turbo16 and Turbo32;
- call `BEGIN` twice without `END`;
- call `CALL` before `BEGIN`;
- call `END` for the wrong mode;
- let an IRQ/NMI overwrite the active overlay range;
- let another subsystem operate the REU while the Turbo lifecycle is active unless you have explicitly coordinated the controller state.

`END` restores the caller ZP bytes and makes the normal math API safe again.

---

## 28. Relocating Turbo overlays

For a V3/V4 custom configuration, edit:

```asm
TURBO16_ZP_BASE = $40
TURBO32_ZP_BASE = $06
REU_TURBO16_BANK = $00
REU_TURBO32_BANK = $01
```

or any other legal non-colliding REU bank assignment.

Then build normally:

```sh
python3 tools/assemble_sources.py \
    --profile v3_reu_512k \
    --config my_math_config.inc \
    --out my_math_build
```

The builder:

1. assembles Turbo16 for the selected Turbo16 ZP origin;
2. assembles Turbo32 for the selected Turbo32 ZP origin;
3. creates the matching REU image;
4. installs the overlays into the selected REU banks;
5. generates caller symbols for the resulting resident lifecycle addresses.

You must use the generated PRG, generated `math_api.inc`, and generated REU image as one matched set.

---

# Part V — V4 QS16 small-batch mode

## 29. What QS16 is for

V4 has an additional unsigned 16×16 multiplication tier using its 16 MiB quarter-square table.

Recommended V4 dispatch under the measured model:

```text
1 product     MATH_UMUL16
2-8 products QS16 BEGIN / repeated QS16 CALL / END
9+ products  Turbo16 BEGIN / repeated Turbo16 CALL / END
```

Reference-map symbols in `v4_reu_16m/resident/math_api.inc` are:

```text
MATH_REU_QS16_BEGIN = $3A80
MATH_REU_QS16       = $3A8B
MATH_REU_QS16_END   = $3B5C
```

For a source-relocated build these locations move with `REG_API`. If your generated include does not explicitly export the QS16 convenience names, they can be expressed relative to `MATH_UMUL8` (`MATH_UMUL8` is the `REG_API` base):

```asm
MATH_REU_QS16_BEGIN = MATH_UMUL8+$0A80
MATH_REU_QS16       = MATH_UMUL8+$0A8B
MATH_REU_QS16_END   = MATH_UMUL8+$0B5C
```

Usage:

```asm
        jsr MATH_REU_QS16_BEGIN

        ; X16/Y16 -> Z32
        jsr MATH_REU_QS16
        ; copy/consume Z

        ; next X/Y
        jsr MATH_REU_QS16

        jsr MATH_REU_QS16_END
```

Do not mix QS16 and Turbo lifecycles.

---

# Part VI — Optional composition helpers

## 30. Reference compatibility helper entries

The historical/reference includes also expose several convenience helpers that are not counted among the common 46 stable API entries:

```text
MATH_Z16_TO_N32
MATH_Z32_TO_N32
MATH_Q32_TO_X32
MATH_R16_TO_X16

MATH_CHAIN_UMUL16_UDIV32_16
MATH_CHAIN_UDIV16_UMUL16
MATH_CHAIN_UDIV24_UMUL24
MATH_CHAIN_UDIV32_16_UMUL32
```

Their reference offsets from the integer API base are:

```text
MATH_Z16_TO_N32                  REG_API + $0230
MATH_Z32_TO_N32                  REG_API + $0250
MATH_Q32_TO_X32                  REG_API + $0260
MATH_R16_TO_X16                  REG_API + $0270
MATH_CHAIN_UMUL16_UDIV32_16      REG_API + $0300
MATH_CHAIN_UDIV16_UMUL16         REG_API + $0330
MATH_CHAIN_UDIV24_UMUL24         REG_API + $0360
MATH_CHAIN_UDIV32_16_UMUL32      REG_API + $03A0
```

For relocatable callers you can derive them from `MATH_UMUL8`, which equals the selected `REG_API` base:

```asm
MATH_Z16_TO_N32 = MATH_UMUL8+$0230
; etc.
```

These helpers are useful for zero-host-marshalling composition, but the compatibility guarantee of the release is centered on the 46 stable API entries plus the explicitly documented V3/V4 Turbo lifecycle surface.

---

# Part VII — Practical integration patterns

## 31. Signed 32/16 division example

```asm
        ; N = -100000 as signed 32-bit
        ; D = 300 as signed 16-bit
        ; write two's-complement bytes into MATH_N/MATH_D

        jsr MATH_SDIV32_16
        bcs .zero_divisor

        ; signed Q32 at MATH_Q+0..3
        ; signed R16 at MATH_R+0..1
        rts
.zero_divisor:
        rts
```

---

## 32. Angle and movement example

```asm
        ; dx = +1, dy = +1
        lda #1
        sta MATH_X+0
        sta MATH_Y+0
        jsr MATH_ATAN2_8
        ; MATH_Z+0 ~= $20 (45 degrees)

        ; get sine for that direction
        lda MATH_Z+0
        sta MATH_X+0
        jsr MATH_SIN8
        ; MATH_Z+0 is signed amplitude
```

If chaining in application code, copy values before a later call overwrites the same output block.

---

## 33. Integer distance example

```asm
        lda #10
        sta MATH_X+0            ; dx = +10
        lda #$FB
        sta MATH_Y+0            ; dy = -5
        jsr MATH_DIST8_ACCURATE
        ; unsigned approximate distance in MATH_Z+0
```

---

## 33A. Normalize a Q8.8 direction

```asm
        ; vector (3.0, 4.0) in Q8.8
        lda #$00
        sta MATH_X+0
        lda #$03
        sta MATH_X+1
        lda #$00
        sta MATH_Y+0
        lda #$04
        sta MATH_Y+1

        jsr MATH_VEC2_NORMALIZE_Q8_8
        bcs .zero_vector
        ; Z[0..1] ~= +0.6 Q1.15
        ; Z[2..3] ~= +0.8 Q1.15
```

---

## 34. Exact square root example

```asm
        ; N32 = 1,000,000 = $000F4240
        lda #$40
        sta MATH_N+0
        lda #$42
        sta MATH_N+1
        lda #$0F
        sta MATH_N+2
        lda #$00
        sta MATH_N+3

        jsr MATH_ISQRT32
        ; Z16 = 1000 = $03E8
```

---

# Part VIII — Performance-oriented selection

## 35. Selected normal-call means

The exact benchmark CSV files in `docs/` remain authoritative. A few useful headline means are shown here to help with dispatch decisions.

| Routine | V1 | V2 | V3 | V4 |
|---|---:|---:|---:|---:|
| UMUL8 | 90.49 | 78.49 | 69.00 | 69.00 |
| UMUL16 | 273.84 | 225.84 | 225.84 | 225.84 |
| UMUL24 | 489.99 | 448.29 | 448.29 | 448.29 |
| UMUL32 | 712.24 | 712.24 | 712.24 | 712.24 |
| UDIV8 | 87.45 | 87.45 | 70.86 | 70.86 |
| UDIV16 | 160.06 | 137.28 | 137.28 | 137.28 |
| UDIV32/16 | 857.37 | 759.73 | 759.73 | 759.73 |
| URECIP16_Q16 | 126.18 | 119.58 | 66.23 | 66.23 |
| ATAN2_8 | **50.44** | **46.95** | **46.95** | **48.00** |
| ISQRT16 | 219.74 | 205.76 | 204.99 | 54.00 |
| ISQRT32 | 1378.90 | 1198.62 | 1197.86 | 1046.62 |
| VEC2_NORMALIZE_Q8_8 | **198.77** | **189.26** | **170.06** | **170.06** |

These are CPU-model benchmark figures for the release's documented corpus/timing model. REU DMA interacts with real VIC-II bus activity, so raster-critical software should remeasure on its target configuration.

V5 is intentionally V1-based, so unchanged routines retain V1 behavior/timing. Its certified direct V2 imports are:

| Routine | V1 mean | V5 mean | Gain |
|---|---:|---:|---:|
| UDIV16 | 160.064966 | **137.282268** | 14.23% |
| UDIV24 | 224.668396 | **203.612991** | 9.37% |
| UDIV32/16 | 857.373105 | **759.730823** | 11.39% |
| UMOD8 | 65.285156 | **64.819153** | 0.71% |
| UMOD16 | 163.064966 | **140.282268** | 13.97% |
| UMOD24 | 227.668396 | **206.612991** | 9.25% |
| UMOD32/16 | 860.373105 | **762.730823** | 11.35% |
| COS8 | 29 | **23** | 20.69% |
| SINCOS8 | 39 | **31** | 20.51% |
| ATAN2_8 | 50.441345 | **46.953064** | 6.92% |

`MATH_VEC2_NORMALIZE_Q8_8` is also available in V5 at **198.770271 cycles mean**, using the V1-compatible 31-ZP backend.

These direct paths were validated against V2 with cycle-vector equality. `ATAN2_8` is exhaustive across all 65,536 signed-byte vectors and independently checked for a maximum one-phase-unit approximation error; UMOD8 uses exhaustive correctness plus sampled cycle parity. `UDIV16_SHL8` and `URECIP16_Q16` benefit indirectly through imported division but retain V1 outer code. See `docs/HYBRID_PROFILE.md`.

---

## 36. Turbo timing guidance

Validated Turbo call means are approximately:

```text
Turbo16 CALL: 215.54 cycles
Turbo32 CALL: 731.41 cycles
```

But batch selection must include BEGIN/END overhead. Do not compare only the steady-state CALL number against a normal one-shot routine.

For V4 16-bit batches, follow the 1 / 2–8 / 9+ dispatch rule unless your own workload measurements indicate otherwise.

---

# Part IX — Loading and linking advice

## 37. Source integration is preferred

For a new assembly project, the cleanest approach is to keep the library as an independently built memory-resident component and include its generated symbol file in your application.

Do not hardcode `$3000`, `$5E00`, `$C000`, etc. if you intend to relocate the library later.

Instead write:

```asm
        sta MATH_X+0
        jsr MATH_UMUL16
```

and let the generated include supply the selected addresses.

---

## 38. Keep a matched build set

For V1/V2/V5, the pair is:

```text
PRG + generated math_api.inc
```

For V3/V4, the set is:

```text
PRG + generated math_api.inc + generated REU image
```

Never mix:

- a PRG from one configuration with an include from another;
- a V3/V4 PRG with a different map's REU image;
- a relocated Turbo PRG with the reference overlay REU image.

The generated `source_build_manifest.json` records the exact output hashes and map.

---

# Part X — Error handling and common mistakes

## 39. Forgetting Carry after division

Wrong:

```asm
        jsr MATH_UDIV16
        lda MATH_Q+0
```

Correct:

```asm
        jsr MATH_UDIV16
        bcs .divide_by_zero
        lda MATH_Q+0
```

---

## 40. Forgetting `MATH_INIT`

On V2–V4, symptoms can include incorrect fast multiplication, signed multiplication, or REU behavior. V1/V5 ordinary safe calls are cold-load safe, but `MATH_UMUL32_READY` retains its documented initialized-state requirement.

Universal safe startup rule:

```asm
        cld
        jsr MATH_INIT
```

once during startup.

---

## 41. Wrong endianness

The API is little-endian. `$1234` must be stored as:

```text
byte 0 = $34
byte 1 = $12
```

---

## 42. Calling normal math during Turbo mode

Do not do this:

```asm
        jsr MATH_REU_UMUL32_BEGIN
        jsr MATH_UDIV16             ; unsupported while Turbo32 owns ZP
        jsr MATH_REU_UMUL32_END
```

Finish the Turbo lifecycle first.

---

## 43. Attaching the wrong REU image

A relocated V3/V4 build can move bank roles and Turbo storage. The reference `.reu` file will no longer match that layout.

Use the `.reu` emitted by the same source build.

---

## 44. Application IRQs corrupting library state

If an interrupt routine uses ZP or REU controller registers that overlap the library, it can corrupt a foreground call even if both routines are individually correct.

Coordinate or serialize access.

---

## 45. Assuming the alternate proof map is a drop-in C64 layout

The alternate map exists to demonstrate relocation. Some addresses can fall under C64 ROM banking. Use your own application-aware map for production and manage `$01` deliberately if you place RAM under ROM.

---

# Part XI — Validation and release confidence

## 46. Run the supplied test suite

Full built-in validation:

```sh
make all
```

This covers reference/alternate source builds, stable public execution, Turbo relocation, Turbo boundary origins, ISQRT32 correctness/performance, invalid configurations, deterministic rebuilds, and the release audit.

Optional independent ACME verification:

```sh
make acme ACME=/path/to/acme
```

or:

```sh
python3 tools/verify_with_acme.py --acme /path/to/acme --kind all
```

---

## 47. What the FINAL release has validated

The frozen Turbo FINAL release records:

- 46 stable entries in all four original V1–V4 profiles, plus the same 46-entry surface in V5;
- V1–V4 alternate proof: 184/184 relocated stable entry executions and 18,356 machine calls;
- V5 reference + alternate: 46/46 entries and 4,589 machine calls per map;
- V5 hybrid direct-import validation: **144,246 cases**, including exhaustive 65,536-vector `ATAN2_8` result/cycle parity, plus 2,000 cold-load calls without `MATH_INIT`;
- V5 ZP confinement: 31-byte normal window, all 225 outside page-zero bytes unchanged in stress on both maps;
- Custom Pareto matrix: six ZP breakpoints on reference + alternate maps, 12 generated builds, 46/46 entries and 4,589 calls each (**55,068 common-API calls**);
- Custom Pareto direct V2 cycle parity: **75,644 cases**, including exhaustive 65,536-vector `ATAN2_8`, plus exhaustive 65,536-case UMOD8;
- Custom Pareto stress: 50,144 SMUL16 cycle-parity cases, 25,000 mixed-workload iterations and 10,000 ZP-guard iterations;
- Custom Pareto endpoint identity: 31 ZP + zero extra RAM is byte-identical to V1; 31 ZP + optional-init policy is byte-identical to V5;
- Custom Pareto resource/configuration validation: 12/12 cases;
- six relocatable Turbo lifecycle entries on V3/V4;
- 17,196 Turbo API calls in the main reference/alternate regression;
- 3,556 additional Turbo products at endpoint ZP/bank configurations;
- Turbo16 at minimum `$02` and maximum `$8F` origin;
- Turbo32 at minimum `$02` and maximum `$79` origin;
- exact ZP restoration after Turbo END;
- second-batch Turbo overlay reuse;
- 20,388 fast-ISQRT32 correctness executions;
- 27/27 configuration validation cases;
- 204/204 consolidated release-audit checks in the current environment;
- deterministic source rebuild identity;
- current release audit status `PASS_WITH_ACME_NOT_RUN` because ACME is not installed in this execution environment; historical ACME 0.97 identity evidence is retained for the earlier source baseline.

These tests are extensive, but they do not replace application-level testing of your particular memory banking, IRQ design, raster timing, REU hardware, and surrounding code.

---

# Part XII — Complete stable API cheat sheet

## 48. All 46 entries at a glance

| Entry | Inputs | Outputs | Status / note |
|---|---|---|---|
| `MATH_UMUL8` | X8,Y8 | Z16 | C=0 |
| `MATH_UMUL16` | X16,Y16 | Z32 | C=0 |
| `MATH_UMUL24` | X24,Y24 | Z48 | C=0 |
| `MATH_UMUL32` | X32,Y32 | Z64 | C=0 |
| `MATH_UMUL32_READY` | X32,Y32 | Z64 | initialized-state entry |
| `MATH_SMUL8` | signed X8,Y8 | signed Z16 | C=0 |
| `MATH_SMUL16` | signed X16,Y16 | signed Z32 | C=0 |
| `MATH_SMUL24` | signed X24,Y24 | signed Z48 | C=0 |
| `MATH_SMUL32` | signed X32,Y32 | signed Z64 | C=0 |
| `MATH_SMUL32_READY` | signed X32,Y32 | signed Z64 | initialized-state entry |
| `MATH_UDIV8` | N8,D8 | Q8,R8 | C=1 on D=0 |
| `MATH_UDIV16` | N16,D16 | Q16,R16 | C=1 on D=0 |
| `MATH_UDIV24` | N24,D24 | Q24,R24 | C=1 on D=0 |
| `MATH_UDIV32_16` | N32,D16 | Q32,R16 | C=1 on D=0 |
| `MATH_UMOD8` | N8,D8 | R8 | independent modulo; C=1 on D=0 |
| `MATH_UMOD16` | N16,D16 | Q16,R16 | aliases UDIV16 |
| `MATH_UMOD24` | N24,D24 | Q24,R24 | aliases UDIV24 |
| `MATH_UMOD32_16` | N32,D16 | Q32,R16 | aliases UDIV32_16 |
| `MATH_SDIV8` | signed N8,D8 | signed Q8,R8 | trunc toward zero |
| `MATH_SDIV16` | signed N16,D16 | signed Q16,R16 | trunc toward zero |
| `MATH_SDIV24` | signed N24,D24 | signed Q24,R24 | trunc toward zero |
| `MATH_SDIV32_16` | signed N32,D16 | signed Q32,R16 | trunc toward zero |
| `MATH_SMOD8` | signed N8,D8 | signed Q8,R8 | signed-div alias |
| `MATH_SMOD16` | signed N16,D16 | signed Q16,R16 | signed-div alias |
| `MATH_SMOD24` | signed N24,D24 | signed Q24,R24 | signed-div alias |
| `MATH_SMOD32_16` | signed N32,D16 | signed Q32,R16 | signed-div alias |
| `MATH_UDIV32_32` | N32,D32 | Q32,R32 | exact unsigned divmod |
| `MATH_UMOD32_32` | N32,D32 | Q32,R32 | alias of UDIV32_32 |
| `MATH_SDIV32_32` | signed N32,D32 | signed Q32,R32 | trunc toward zero |
| `MATH_SMOD32_32` | signed N32,D32 | signed Q32,R32 | alias of SDIV32_32 |
| `MATH_UMUL16_SHR8` | X16,Y16 | Z24 | `(X*Y)>>8` |
| `MATH_SMUL16_SHR8` | signed X16,Y16 | signed Z24 | arithmetic shift |
| `MATH_UMUL32_SHR16` | X32,Y32 | Z48 | `(X*Y)>>16` |
| `MATH_SMUL32_SHR16` | signed X32,Y32 | signed Z48 | arithmetic shift |
| `MATH_UDIV16_SHL8` | N16,D16 | Q24,R16 | `(N<<8)/D` |
| `MATH_SDIV16_SHL8` | signed N16,D16 | signed Q24,R16 | signed `(N<<8)/D` |
| `MATH_URECIP16_Q16` | D16 | Q24 | `floor(65536/D)` |
| `MATH_SIN8` | phase X8 | signed Z8 | phase byte |
| `MATH_COS8` | phase X8 | signed Z8 | phase byte |
| `MATH_SINCOS8` | phase X8 | signed Z8,Z8 | sine then cosine |
| `MATH_ATAN2_8` | signed dx=X8,dy=Y8 | phase Z8 | `(0,0)->0` |
| `MATH_ISQRT16` | N16 | Z16 | exact floor sqrt |
| `MATH_ISQRT32` | N32 | Z16 | exact floor sqrt |
| `MATH_DIST8_FAST` | signed dx=X8,dy=Y8 | unsigned Z8 | fast approximation |
| `MATH_DIST8_ACCURATE` | signed dx=X8,dy=Y8 | unsigned Z8 | lower-error approximation |
| `MATH_VEC2_NORMALIZE_Q8_8` | signed X16,Y16 Q8.8 | signed Z16,Z16 Q1.15 | C=1 only for zero vector |

## 48A. Reference-map entry addresses

These addresses are provided for diagnostics and fixed-reference builds. **Relocatable applications should use the generated `math_api.inc` instead of hardcoding them.**

| Entry | Reference address |
|---|---:|
| `MATH_UMUL8` | `$3000` |
| `MATH_UMUL16` | `$3020` |
| `MATH_UMUL24` | `$3060` |
| `MATH_UMUL32` | `$30B0` |
| `MATH_UMUL32_READY` | `$30C0` |
| `MATH_SMUL8` | `$3B80` |
| `MATH_SMUL16` | `$3BB0` |
| `MATH_SMUL24` | `$3BF0` |
| `MATH_SMUL32` | `$3C40` |
| `MATH_SMUL32_READY` | `$3FE0` |
| `MATH_UDIV8` | `$3120` |
| `MATH_UDIV16` | `$3140` |
| `MATH_UDIV24` | `$3170` |
| `MATH_UDIV32_16` | `$31B0` |
| `MATH_UMOD8` | `$3200` |
| `MATH_UMOD16` | `$3220` |
| `MATH_UMOD24` | `$3223` |
| `MATH_UMOD32_16` | `$3226` |
| `MATH_SDIV8` | `$3CA0` |
| `MATH_SDIV16` | `$3D20` |
| `MATH_SDIV24` | `$3DE0` |
| `MATH_SDIV32_16` | `$3EE0` |
| `MATH_SMOD8` | `$3FD4` |
| `MATH_SMOD16` | `$3FD7` |
| `MATH_SMOD24` | `$3FDA` |
| `MATH_SMOD32_16` | `$3FDD` |
| `MATH_UDIV32_32` | `$5E00` |
| `MATH_UMOD32_32` | `$5E03` |
| `MATH_SDIV32_32` | `$5E06` |
| `MATH_SMOD32_32` | `$5E09` |
| `MATH_UMUL16_SHR8` | `$5E0C` |
| `MATH_SMUL16_SHR8` | `$5E0F` |
| `MATH_UMUL32_SHR16` | `$5E12` |
| `MATH_SMUL32_SHR16` | `$5E15` |
| `MATH_UDIV16_SHL8` | `$5E18` |
| `MATH_SDIV16_SHL8` | `$5E1B` |
| `MATH_URECIP16_Q16` | `$5E1E` |
| `MATH_SIN8` | `$5E21` |
| `MATH_COS8` | `$5E24` |
| `MATH_SINCOS8` | `$5E27` |
| `MATH_ATAN2_8` | `$5E2A` |
| `MATH_ISQRT16` | `$5E2D` |
| `MATH_ISQRT32` | `$5E30` |
| `MATH_DIST8_FAST` | `$5E33` |
| `MATH_DIST8_ACCURATE` | `$5E36` |
| `MATH_VEC2_NORMALIZE_Q8_8` | `$5E39` |

---

# Part XIII — Project files to consult

## 49. Documentation map

| File | Use it for |
|---|---|
| `USER_MANUAL.md` | complete integration/user guide |
| `QUICK_START.md` | minimal build commands |
| `docs/VERSION_SELECTION.md` | fixed profile vs custom-builder choice |
| `docs/PARETO_BUILDER.md` | ZP/RAM budget-driven stock-C64 profile generation |
| `docs/PUBLIC_API_COMPLETE.csv` | authoritative 46-entry stable surface |
| `docs/PERFORMANCE_COMPARISON.csv` | common arithmetic performance |
| `docs/PERFORMANCE_GAME_MATH_FINAL.csv` | game/fixed-point performance |
| `docs/SOURCE_RELOCATION.md` | memory-map relocation contract |
| `docs/REU_GUIDE.md` | V3/V4 REU details |
| `docs/TURBO_RELOCATION.md` | Turbo lifecycle/relocation evidence |
| `docs/TURBO_API.csv` | six Turbo lifecycle entries |
| `docs/GAME_MATH_MEMORY_MAP.md` | resident/table/scratch placement |
| `CHANGELOG.md` | release history and major fixes |
| `RELEASE_STATUS.json` | frozen validation status and hashes |

---

## 50. Recommended integration checklist

Before shipping a game/demo/tool that uses this API:

- [ ] Choose V1/V2/V3/V4/V5 intentionally, or generate a stock-C64 profile with the Pareto Builder.
- [ ] Use a source-built memory map that does not collide with your application.
- [ ] Keep the generated PRG/include/REU image together.
- [ ] Ensure your C64 banking exposes every selected region when used.
- [ ] `CLD` before math calls or guarantee decimal mode is always clear.
- [ ] Call `MATH_INIT` once when required; mandatory V2–V4, optional/recommended V1/V5, and manifest-controlled for custom Pareto builds.
- [ ] Store all operands little-endian.
- [ ] Treat A/X/Y as clobbered.
- [ ] Check Carry after division, modulo where relevant, shifted division, and reciprocal.
- [ ] Do not call the library reentrantly.
- [ ] Do not let IRQ/NMI code corrupt shared ZP/REU state.
- [ ] On V3/V4, initialize/attach the matching REU image before use.
- [ ] On V5/custom-Pareto reference maps, bank BASIC ROM out while selected `$A000-$BFFF` private regions execute/read data, or relocate `HYBRID_CODE`/`PARETO_AUX`.
- [ ] Never mix ordinary math with an active Turbo lifecycle.
- [ ] Always pair Turbo BEGIN and END.
- [ ] For V4 16-bit batches, consider normal / QS16 / Turbo16 based on batch size.
- [ ] Run the supplied validation after changing the library configuration.
- [ ] Benchmark on real target hardware if raster-exact timing matters.

---

## 51. Minimal production template

```asm
!cpu 6510
!source "build_source/reference/v2_pareto_fast/math_api.inc"

math_start:
        cld
        jsr MATH_INIT

        ; Example operation
        lda #$34
        sta MATH_X+0
        lda #$12
        sta MATH_X+1
        lda #$20
        sta MATH_Y+0
        lda #$00
        sta MATH_Y+1
        jsr MATH_UMUL16

        ; MATH_Z+0..3 now contain the 32-bit product.
        rts
```

For a V3/V4 program, the code pattern is the same after the correct REU image is installed. For V5/custom Pareto builds, use the generated include, obey its initialization flag, and ensure its selected private regions are CPU-visible.

---

# 52. Final rule of thumb

Use the stable API for ordinary composable math. Use QS16 or Turbo only when a measured batch actually justifies their lifecycle overhead. Keep all addresses symbolic, keep the REU image matched to the build, and treat the generated `math_api.inc` as the caller's source of truth.

That gives you the intended property of this release: **one logical math interface across five fixed profiles plus budget-generated stock-C64 builds, with implementation selection and relocation done at build time rather than paid for at runtime.**

## Standalone ASM pickup surface and canonical naming

The library publishes one readable ASM file for every callable profile routine in `<profile>/standalone/`. These are exact executable source mirrors of the shipped profile after `MATH_INIT`, with address/byte annotations for mechanical verification. Shared immutable lookup tables and REU payload data remain profile resources rather than being duplicated into every file.

For binary arithmetic, the canonical source-facing name records operand signedness/width and result geometry. Examples: `mul_u16_u16_u32`, `mul_s8_s8_s16`, `div_u8_u8_u8_8`, and `div_s32_s16_s32_16`. Division names include the remainder width when the public call returns a remainder. The existing `MATH_*` names remain stable aliases at the same addresses, so no existing caller must change. Full rules and mappings are in `docs/NAMING_STANDARD.md`.
