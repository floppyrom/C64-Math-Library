# C64 Math Library — V1–V5 + Custom Pareto Builder

High-performance signed, unsigned and game/fixed-point math for the Commodore 64 / NMOS 6502/6510.

The **C64 Math Library** exposes one stable **45-entry public API** across its resident profiles. V3/V4 additionally provide six stateful Turbo16/Turbo32 lifecycle entries, V4 provides QS16, and V5 combines selected V2-speed paths with the V1 low-ZP contract.

For stock-C64 games and demos, the repository now also includes a **Custom Pareto Builder**: tell it how many zero-page bytes (and optionally how much extra RAM) you can spare, and it generates the fastest certified V1/V2 combination that fits. Selection happens at build time, so there is no runtime dispatcher.

## Profiles

| Profile | Hardware | Why choose it? |
|---|---|---|
| **V1 Balanced** | Stock C64 | Lowest integration pressure; 31-byte normal ZP |
| **V2 Pareto-Fast** | Stock C64 | Faster general resident profile when larger ZP use is acceptable |
| **V3 REU 512K** | C64 + 512 KiB REU | REU-backed services plus Turbo16/Turbo32 |
| **V4 REU 16M** | C64 + 16 MiB REU-compatible device/emulator | Fastest feature set: exact REU atan2/ISQRT16, QS16, Turbo |
| **V5 Hybrid Low-ZP** | Stock C64 | V1's 31-byte normal ZP plus selected V2-speed division/modulo/trig paths |

V5 is intended particularly for games and demos. It is **one build**, not two complete libraries loaded side-by-side. The stable caller ABI remains unchanged.


## Signed implementation taxonomy

All shipped signed multiply and divide entries now own **native signed executable kernels**. In this release, “native signed” means the signed entry never executes the corresponding unsigned multiply/divide engine; immutable lookup tables may still be shared.

- V1/V5 preserve the 31-byte normal-ZP contract while using private signed executable arithmetic paths.
- V2/V3/V4 retain the signed-specific `smul16_practical_116zp` executable-ZP kernel.
- Wider signed multiply cores and `SDIV32_32` use signed-owned private executable cores in existing reserved holes, so public ABI addresses and resident load/end ranges are unchanged. The cores may reuse the same arithmetic identities/tables, but they do not execute the corresponding unsigned routine.
- `tools/validate_signed_layout.py` mechanically requires zero signed/unsigned executable overlap for 13 API pairs in all five profiles.

See `docs/SIGNED_IMPLEMENTATIONS.md` and each profile's `resident/signed/README.md`.

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

V5 keeps V1's `$02-$20` 31-byte normal ZP window and imports certified V2 paths with no extra normal ZP:

- `MATH_UDIV16`: 160.06 → **137.28 cycles**
- `MATH_UDIV24`: 224.67 → **203.61**
- `MATH_UDIV32_16`: 857.37 → **759.73**
- wider `UMOD` aliases inherit those faster division paths
- `MATH_UMOD8`: 65.29 → **64.82**
- `MATH_COS8`: 29 → **23**
- `MATH_SINCOS8`: 39 → **31**

The reference V5 private implementation occupies `$A000-$B1FF` (4608 bytes), RAM underneath BASIC ROM. BASIC ROM must therefore be banked out while imported V5 paths execute, or `HYBRID_CODE` can be relocated at build time.

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

## Calling model

The library is **not reentrant**, but ordinary sequential game/demo loops are fully supported. You may call routines repeatedly in loops; a second math call simply must not begin before the first has returned. In particular, do not invoke the same shared library state from an IRQ/NMI while a foreground math call is active.

## Validation headline

V1–V4 retain the previously reviewed validation evidence, including byte-exact source rebuilds, 180/180 alternate-map stable entries, Turbo relocation/boundary testing, fast exact ISQRT32 validation and configuration rejection tests.

The signed-implementation cleanup adds a repository-layout audit and a dedicated **264,999-call V1–V5 signed-multiplication regression**, including exhaustive 8×8 validation on the distinct resident implementation families.

V5 adds:

- **45/45 stable entries** on both reference and alternate maps, **4,172 machine calls per map**;
- **78,710 direct-import test cases**;
- exhaustive **65,536-case `UMOD8`** correctness;
- exhaustive full-domain `COS8` / `SINCOS8` validation;
- thousands of wide-division cases with **exact V2 cycle-vector parity**;
- dynamic proof that all **225 ZP bytes outside the configured 31-byte window remain untouched** on both maps;
- mixed V1/V2 state stress;
- **2,000 cold-load calls without `MATH_INIT`** across reference/alternate maps;
- deterministic reference/alternate rebuild identity;
- invalid hybrid map rejection for overlap, I/O, alignment and overflow.

See `validation/hybrid/` for V5 evidence and `validation/pareto/` for the Custom Pareto Builder. The Pareto validation includes a 12-build / 50,064-call API matrix, exact V2 cycle parity for imported kernels, exhaustive UMOD8, resource-map rejection tests, deterministic rebuilds, endpoint identity with V1/V5, and additional mixed/ZP stress.

## Project terminology

The project was originally called an API because it was designed around a stable common calling interface across multiple optimized implementations. As it grew to include the implementations, tables, REU images, build tools, tests and documentation, **C64 Math Library** became the more accurate project name; the 45-entry interface is its public API.
