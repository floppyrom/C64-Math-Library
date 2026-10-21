# Pick up a single C64 math routine

**For a new stock-C64 project, start with the operation-first builder.**
All **56 public math operations** can be selected individually without
installing a whole historical V1–V5 resident profile.

There are **two ways** to take just what you need:

| What you want | Recommended approach |
| --- | --- |
| **One working routine, already linked** | Select one operation with `make builder-setup`. The generated PRG contains its code and necessary dependencies, with a matching `math_api.inc` and resource manifest. |
| **Assembly source to transplant or modify** | Compare source-backed variants in the [current variant table](../benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv), follow each row's `source_path`, and read its memory, I/O and dependency contract. |

## Option 1: build just one operation

The guided command lets you choose **only one operation**:

```sh
make builder-setup
```

Or build a single unsigned 16-bit multiplication routine with a reproducible
configuration:

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --objective balanced \
  --zp-budget 8 --ram-budget 4096 \
  --config-out just-umul16.json --build-dir build_just_umul16
```

Use the generated `math_selective.prg` and `math_api.inc` together.
Consult `selective_manifest.json` for the actual linked variant, code location,
ZP allocation, public I/O and any initialization requirements.
**Do not use a V1–V5 fixed address with this PRG.**

For other selected operations, replace `UMUL16` with a name from the
[public catalog](../routines/PUBLIC_OPERATIONS.csv). To compare available
qualified implementations before selecting one:

```sh
python3 tools/math_builder.py --variants UMUL16
```

[Full configuration instructions](OPERATION_FIRST_USER_SETUP.md) ·
[Current cycles/RAM/ZP/stack reference](OPERATION_FIRST_ROUTINE_METRICS.md).

## Option 2: lift or adapt the assembly source

1. Open the [current per-variant CSV](../benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv).
   Filter on `operation`, e.g. `MATH_UMUL16`. Compare variants on the
   **same operation and input corpus**.
2. Follow the chosen row's `source_path` to its assembly file and check
   any related documentation and linked dependencies.
3. Check the **operand/result ABI, tables, scratch RAM, ZP reservations,
   initialization, relocations and self-modifying code** before including
   the source in a different project. Validate it at your actual addresses.

Useful starting points: [curated symbolic sources](../routines/README.md),
[portable standalone kernels with configurable addresses](../routines/standalone_lab/portable/README.md),
and [source relocation notes](SOURCE_RELOCATION.md).

**Source-linkable does not automatically mean one-file, copy-and-paste
portable.** Some source files are bound by the builder into an executable
module using generated symbols, dedicated tables and scratch. For the simplest
integration, choose **Option 1** instead.

## Historical source mirrors (reference only)

The old V1–V5 `standalone/` directories and
[routine source catalog](../routines/SOURCE_CATALOG.csv) remain useful for
investigating exact shipped implementations. **They are not the new-project
installer** and individual mirror files are not necessarily self-contained:
shared data and hard-coded profile addresses may be missing or unsuitable.
The following sections retain their historical examples for developers
studying or reproducing those releases.

## Direct links to the recent issue #39 unsigned improvements

The 2026-10-11 changes optimize **existing public operations**, not additional public API addresses. The optimized entrypoint remains stable in its selected profile:

| Operation | Exact shipped V1 source mirror | Exact shipped V5 source mirror | Canonical modified symbolic code / comment |
|---|---|---|---|
| `MATH_UMOD8` | [mod_u8_u8_u8.asm](../v1_balanced/standalone/mod_u8_u8_u8.asm) | [mod_u8_u8_u8.asm](../v5_hybrid_lowzp/standalone/mod_u8_u8_u8.asm) | [77-byte guarded source](../relocatable_source/v1_balanced/umod8_relocatable_public.inc), [V5 import/patch logic](../tools/build_hybrid.py) |
| `MATH_UDIV24` | [div_u24_u24_u24_24.asm](../v1_balanced/standalone/div_u24_u24_u24_24.asm) | [div_u24_u24_u24_24.asm](../v5_hybrid_lowzp/standalone/div_u24_u24_u24_24.asm) | [V1 exact 24÷8 fast path](../relocatable_source/v1_balanced/udiv24_latency_escape_balanced.inc) |
| `MATH_UMOD24` | [mod_u24_u24_u24.asm](../v1_balanced/standalone/mod_u24_u24_u24__math_umod24.asm) | [mod_u24_u24_u24.asm](../v5_hybrid_lowzp/standalone/mod_u24_u24_u24__math_umod24.asm) | Shared V1 24÷8 path, with the optimized V5 remainder-only path retained |
| `MATH_UDIV32_16` | [div_u32_u16_u32_16.asm](../v1_balanced/standalone/div_u32_u16_u32_16.asm) | [div_u32_u16_u32_16.asm](../v5_hybrid_lowzp/standalone/div_u32_u16_u32_16.asm) | [V1 loop unroll](../relocatable_source/v1_balanced/udiv32_16_loop_unrolled.inc) |
| `MATH_UMOD32_16` | [mod_u32_u16_u16.asm](../v1_balanced/standalone/mod_u32_u16_u16__math_umod32_16.asm) | [mod_u32_u16_u16.asm](../v5_hybrid_lowzp/standalone/mod_u32_u16_u16__math_umod32_16.asm) | Shared 32/16 divider, modulo front ends are profile-selected |
| `MATH_UDIV32_32` | [div_u32_u32_u32_32.asm](../v1_balanced/standalone/div_u32_u32_u32_32.asm) | [div_u32_u32_u32_32.asm](../v5_hybrid_lowzp/standalone/div_u32_u32_u32_32.asm) | [V1 bounded 8-bit-divisor shortcut](../relocatable_source/v1_balanced/udiv32_32_d8_delegate.inc); [high quotient filters](../relocatable_source/v1_balanced/udiv32_32_high_qone.inc), [V5 16-bit-divisor route](../tools/build_hybrid.py) |
| `MATH_UMOD32_32` | [mod_u32_u32_u32.asm](../v1_balanced/standalone/mod_u32_u32_u32__math_umod32_32.asm) | [mod_u32_u32_u32.asm](../v5_hybrid_lowzp/standalone/mod_u32_u32_u32__math_umod32_32.asm) | Shared 32/32 quotient/remainder core: same optimized path as UDIV32/32 |

Source mirrors include dependencies reachable through code, but **not all** shared data; callers should use the matching `math_api.inc`, storage conventions and memory/zero-page map. For V2/V3/V4, substitute that exact profile directory. V2–V4 require an initial `MATH_INIT`; REU profiles also require the matching REU image. V1/V5 have optional `MATH_INIT`.

## Other independently useful modules

- **MULDIV16:** [portable composed source](../routines/muldiv16/muldiv16_composed.inc), [optimized fused source](../routines/muldiv16/muldiv16_fast_v2v4.inc), and [dependency/ABI guide](../routines/muldiv16/README.md).
- **Seek / DDA movement:** [8-bit source](../routines/movement/seek_u8_u8_dda.asm), [16-bit X source](../routines/movement/seek_u16_u8_dda.asm), and [guide](../routines/movement/README.md).
- **Multiply alternatives:** [record/compact sources](../routines/multiply/), including signed FAST24 and signed FAST31, with their own resource contracts.
- **Every other public API, including ISQRT16/32, ATAN2, normalization and trig:** use the [typed catalog](../routines/SOURCE_CATALOG.csv) to locate the **profile-specific** mirror and its SHA-qualified benchmark.

## Minimal use from an existing V1/V5 resident

With a matching resident PRG loaded and caller-visible memory set aside according to the manual:

```asm
!source "math_api.inc"   ; from the *same* profile's resident directory
    lda #$C8
    sta $C010            ; MATH_N = 200, low byte
    lda #$25
    sta $C014            ; MATH_D = 37, low byte
    jsr MATH_UMOD8       ; output remainder in $C01C, carry clear
    lda $C01C            ; 15
```

This **uses the resident**, not the extracted one-file graph. The `$C010/$C014/$C01C` locations above are reference-map examples; use the generated symbolic map when relocating. Consult [quick start](../QUICK_START.md) and [user manual](../USER_MANUAL.md) for memory ownership and exact ABI details.

## Verifying a copied file really corresponds to the benchmark

```sh
python3 tools/generate_public_indexes.py
python3 tools/validate_public_catalog.py
python3 tools/validate_standalone_sources.py
```

Read [the machine-readable source catalog](../routines/SOURCE_CATALOG.csv) before comparing cycle means across profiles. Same-input statistics and per-workload tradeoffs matter; faster-average dispatches can add a few cycles to unqualified cases. **An exact source mirror is available separately; a guaranteed one-file, location-independent plug-in for every public entry is not yet claimed.**

## Experimental standalone math kernels

The [standalone fast-kernel lab](../routines/standalone_lab/README.md) preserves three OptiSearch-derived NMOS 6510 division/modulo candidates with independent source, fixed-map entrypoints, reproducible 7,163-case emulator tests and a backlog of screened alternatives. These are not yet certified as arbitrarily relocatable or usable alongside BASIC.

For independently callable UDIV16, UMOD16 and specialist UDIV32 kernels with **editable assembly origins, operand buffers and zero-page allocation**, start at the [standalone portable pickup guide](../routines/standalone_lab/portable/README.md). It includes tested layouts, arithmetic and carry semantics, and native VICE correctness proof. These isolated variants are not general-purpose BASIC-resident add-ons.

An additional [carry-corrected 32-bit modulo module with zero ZP usage](../routines/standalone_lab/portable/mod_u32_aligned_carry.asm) is available as a specialist. Its 1,024-input random subset is faster than the V2–V4 UMOD32 path, but its full-distribution mean is markedly slower; use the [standalone guide](../routines/standalone_lab/portable/README.md) before copying it.

A [zero-ZP, no-REU UDIV32 standalone module](../routines/standalone_lab/portable/div_u32_aligned_nozp.asm) is available alongside the faster 4-ZP ZP-tail variant. It requires four scratch bytes in ordinary RAM and uses 576 code bytes. Its mean is 408.012 cycles over 2,729 identical inputs (not a universal speed winner), with 8,187 source-executed calls and 192 x64sc correctness calls across multiple relocations. Follow the [standalone guide](../routines/standalone_lab/portable/README.md) for exact tradeoffs.
