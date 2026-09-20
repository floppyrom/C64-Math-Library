# C64 Math Library — V1–V5 + Custom Pareto Builder

High-performance signed, unsigned and game/fixed-point math for the Commodore 64 / NMOS 6502/6510.

The **C64 Math Library** exposes one stable **46-entry public API** across its resident profiles. V3/V4 additionally provide six stateful Turbo16/Turbo32 lifecycle entries, V4 provides QS16, and V5 combines selected V2-speed paths with the V1 low-ZP contract.

For stock-C64 games and demos, the repository now also includes a **Custom Pareto Builder**: tell it how many zero-page bytes (and optionally how much extra RAM) you can spare, and it generates the fastest certified V1/V2 combination that fits. Selection happens at build time, so there is no runtime dispatcher.

## Profiles

| Profile | Hardware | Why choose it? |
|---|---|---|
| **V1 Balanced** | Stock C64 | Lowest integration pressure; 31-byte normal ZP |
| **V2 Pareto-Fast** | Stock C64 | Faster general resident profile when larger ZP use is acceptable |
| **V3 REU 512K** | C64 + 512 KiB REU | REU-backed services plus Turbo16/Turbo32 |
| **V4 REU 16M** | C64 + 16 MiB REU-compatible device/emulator | Fastest feature set: exact REU atan2/ISQRT16, QS16, Turbo |
| **V5 Hybrid Low-ZP** | Stock C64 | V1's 31-byte normal ZP plus selected V2-speed division/modulo/trig/ATAN2 paths |

V5 is intended particularly for games and demos. It is **one build**, not two complete libraries loaded side-by-side. The stable caller ABI remains unchanged.

## Vector normalization headline

The stable API now includes `MATH_VEC2_NORMALIZE_Q8_8`, an arbitrary-runtime signed Q8.8 2D normalizer returning signed Q1.15 components. The same contract is available in every profile and generated Custom Pareto build; the reference address is `$5E39`.

The normalization kernels are also published as **canonical standalone native sources** under each profile's `resident/vector/native/` directory. V1-V4 include those files directly in the relocatable build; the V5 copy is byte-identical to the V1 backend it inherits. Each directory includes extraction/dependency notes for using the routine independently.

| Profile | Mean cycles | Normal ZP policy | Backend |
|---|---:|---|---|
| V1 Balanced | **198.77** | 31-byte V1 contract | stock-C64 low-ZP backend |
| V2 Pareto-Fast | **189.26** | V2 resident ZP | Pareto-fast stock-C64 backend |
| V3 REU 512K | **170.06** | no added normal ZP | direct REU ratio-index lookup |
| V4 REU 16M | **170.06** | no added normal ZP | direct REU ratio-index lookup |
| V5 Hybrid Low-ZP | **198.77** | 31-byte V1 contract | V1-compatible low-ZP backend |

The common precision contract is <=0.3621 degrees angular error and <=202 Q1.15 LSB component error; the current full-domain proof is tighter at <=0.360856382 degrees / <=200 LSB. See `docs/VEC2_NORMALIZE_Q8_8.md`.


## Signed implementation taxonomy

All shipped signed multiply and divide entries now own **native signed executable kernels**. In this release, “native signed” means the signed entry never executes the corresponding unsigned multiply/divide engine; immutable lookup tables may still be shared.

- V1/V5 preserve the 31-byte normal-ZP contract while using private signed executable arithmetic paths.
- V2/V3/V4 retain the signed-specific `smul16_practical_116zp` executable-ZP kernel.
- Wider signed multiply cores and `SDIV32_32` use signed-owned private executable cores. Public API addresses remain unchanged; the multiplication refresh extends the resident payload to `$CF96` to house the private multiply cores. The cores may reuse the same arithmetic identities/tables, but they do not execute the corresponding unsigned routine.
- `tools/validate_signed_layout.py` mechanically requires zero signed/unsigned executable overlap for 13 API pairs in all five profiles.
- Every signed API now has a directly browsable exact executable source mirror under each profile's `resident/signed/multiply/native/` or `resident/signed/division/native/` directory; `tools/validate_published_signed_sources.py` verifies those mirrors byte-for-byte against the initialized resident image.

See `docs/SIGNED_IMPLEMENTATIONS.md` and each profile's `resident/signed/README.md`.


### 2026-09-20 multiplication refresh

The fixed profiles now apply the latest multiplier research profile-by-profile rather than forcing one kernel everywhere. Direct signed `SMUL8`, FAST24 signed composition and mixed-call-safe FAST31/V29 `SMUL32` are selected across V1–V5; V1/V5 use the low-ZP FAST17 `SMUL16`, while V2/V3/V4 retain their faster 116-ZP practical signed kernel. `UMUL32` is refreshed across all five profiles, V1/V5 also gain the FAST24 `UMUL24`, and `UMUL8`/`UMUL16` are intentionally retained after resource-aware comparison. The refreshed arithmetic is exposed as independent canonical includes in the V1–V4 `relocatable_source/` trees; V5 inherits the V1 low-ZP arithmetic through the hybrid build and publishes its own exact signed executable mirrors under `resident/signed/multiply/native/`. See `docs/MULTIPLY_REFRESH_2026-09-20.md`.

### 2026-09-20 division refresh

The complete `UDIV`/`SDIV` family has now been re-evaluated across V1–V5 using Repose’s new UDIV24 q0-counter work plus follow-on direct-output and early-gate optimizations. V1/V2/V5 adopt the faster CPU UDIV8 path while V3/V4 deliberately retain their faster REU 8-bit quotient/remainder planes. Repose-derived UDIV24 is integrated profile-by-profile; native signed 8/16/24/32-bit paths are refreshed without entering the corresponding unsigned executable engines; and 32/32 division gains an early q=0 gate. A deterministic old-vs-new corpus reports **zero public division-family timing regressions** across all five profiles. See `docs/DIVISION_REFRESH_2026-09-20.md`.

## Custom Pareto Builder

Interactive use:

```sh
python3 tools/pareto_wizard.py
```

Or directly:

```sh
python3 tools/build_pareto.py --zp-budget 60
```

Examples:

```sh
# 31 ZP bytes and no extra RAM -> byte-identical V1
python3 tools/build_pareto.py --zp-budget 31 --ram-budget 0

# 31 ZP bytes, but MATH_INIT must remain optional -> byte-identical V5
python3 tools/build_pareto.py --zp-budget 31 --init-policy optional

# Weight a hot routine more heavily
python3 tools/build_pareto.py --zp-budget 55 --weight MATH_UMUL24=100
```

The generated `selection_manifest.json` records the exact selected packs, ZP ranges, private RAM ranges, initialization requirement and output SHA-256. See `docs/PARETO_BUILDER.md`.

## V5 headline

V5 keeps V1's `$02-$20` 31-byte normal ZP window while using the refreshed low-ZP division selection. Final resident validation means include:

- `MATH_UDIV8`: **59.383 cycles**
- `MATH_UDIV16`: **126.386**
- `MATH_UDIV24`: **187.122**
- `MATH_UDIV32_16`: **756.639**
- `MATH_SDIV16`: **171.905**
- `MATH_SDIV24`: **253.487**
- `MATH_COS8`: **23**
- `MATH_SINCOS8`: **31**
- `MATH_ATAN2_8`: **46.953** (65,536-vector exhaustive parity; max error 1 phase unit)

The reference V5 `HYBRID_CODE` block now occupies `$A000-$BDFF` (**7,680 bytes**) under BASIC ROM. Additional profile-private division/table islands and the three fast-ATAN2 pages bring the exact current private-RAM increase versus V1 to **9,377 bytes**. BASIC ROM must be banked out while code in the reference hybrid block executes, or `HYBRID_CODE` can be relocated at build time.

See `docs/HYBRID_PROFILE.md`.

## Start here

1. Read **`USER_MANUAL.md`**.
2. Read `docs/VERSION_SELECTION.md`.
3. For V1–V4 source relocation, read `docs/SOURCE_RELOCATION.md`.
4. For V5, read `docs/HYBRID_PROFILE.md`.
5. For a budget-generated stock-C64 build, read `docs/PARETO_BUILDER.md`.
6. Include the generated/profile `math_api.inc` rather than hardcoding entry addresses.

### Build V1–V4

```sh
make reference
make alternate
```

### Build and validate V5

```sh
make hybrid
make hybrid-validate
```

or explicitly:

```sh
python3 tools/build_hybrid.py --config-kind reference
python3 tools/build_hybrid.py --config-kind alternate
python3 tools/validate_hybrid.py
python3 tools/test_hybrid_config.py
python3 tools/verify_hybrid_deterministic.py
```

### Build and validate custom Pareto profiles

```sh
make pareto-validate
```

Validate the cross-profile vector-normalization implementation and full-domain precision proof:

```sh
make normalize
```

## Calling model

The library is **not reentrant**, but ordinary sequential game/demo loops are fully supported. You may call routines repeatedly in loops; a second math call simply must not begin before the first has returned. In particular, do not invoke the same shared library state from an IRQ/NMI while a foreground math call is active.

## Validation headline

V1–V4 retain the previously reviewed validation evidence, including byte-exact source rebuilds, 184/184 alternate-map stable entries, Turbo relocation/boundary testing, fast exact ISQRT32 validation and configuration rejection tests.

The signed-implementation cleanup adds a repository-layout audit and a dedicated **264,999-call V1–V5 signed-multiplication regression**, including exhaustive 8×8 validation on the distinct resident implementation families.

V5 adds:

- **46/46 stable entries** on both reference and alternate maps, **4,589 machine calls per map**;
- **144,246 direct-import test cases**, including exhaustive 65,536-vector `ATAN2_8` result/cycle parity;
- exhaustive **65,536-case `UMOD8`** correctness;
- exhaustive full-domain `COS8` / `SINCOS8` validation;
- thousands of wide-division cases with **exact V2 cycle-vector parity**;
- dynamic proof that all **225 ZP bytes outside the configured 31-byte window remain untouched** on both maps;
- mixed V1/V2 state stress;
- **2,000 cold-load calls without `MATH_INIT`** across reference/alternate maps;
- deterministic reference/alternate rebuild identity;
- invalid hybrid map rejection for overlap, I/O, alignment and overflow.

See `validation/hybrid/` for V5 evidence and `validation/pareto/` for the Custom Pareto Builder. The Pareto validation includes a 12-build / 55,068-call API matrix, **75,644 direct V2 cycle-parity cases** including exhaustive `ATAN2_8`, exhaustive UMOD8, resource-map rejection tests, deterministic rebuilds, endpoint identity with V1/V5, and additional mixed/ZP stress.

## Project terminology

The project was originally called an API because it was designed around a stable common calling interface across multiple optimized implementations. As it grew to include the implementations, tables, REU images, build tools, tests and documentation, **C64 Math Library** became the more accurate project name; the 46-entry interface is its public API.

- **[Consolidated routine table](docs/CONSOLIDATED_ROUTINE_TABLE.md)** — cycles, reachable code, ZP, hardware-stack reservation and profile footprint for every shipped routine/profile.

## Standalone routine sources and typed names

Every callable routine is now exposed as a readable ASM source mirror under each profile's `standalone/` directory. Coverage is V1 46, V2 46, V3 52, V4 55, and V5 46 routines, including the REU Turbo lifecycle and V4 QS16 profile-specific entries.

New source-facing aliases use operand/result geometry, for example `mul_u8_u8_u16`, `mul_s16_s16_s32`, `div_u8_u8_u8_8`, and `div_u32_u16_u32_16`. The historical `MATH_*` symbols and fixed addresses remain fully compatible. See `docs/NAMING_STANDARD.md`, `docs/PUBLIC_API_COMPLETE.csv`, and each profile's `standalone/MANIFEST.csv`.
