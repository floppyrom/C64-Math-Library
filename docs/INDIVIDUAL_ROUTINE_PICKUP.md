# Pick up a single routine: public API, exact source, or portable module

This is the practical entry point for demo, game, and tool developers who want **one operation**, not necessarily the whole C64 Math Library.

**All 56 stable public calls are available in every V1–V5 resident profile.** The five profile directories also publish one named `.asm` **source mirror per stable call**. REU profiles include their additional Turbo/QS entry mirrors. The current `routines/SOURCE_CATALOG.csv` indexes **295 shipped-profile source mirrors** plus **25 standalone alternatives**, with individual file paths, source SHA-256, measured cycles, ZP budgets and evidence.

There are three distinct ways to use these sources. Do not confuse them:

| You want | Start here | What you get |
|---|---|---|
| Use a routine in an actual game/demo | [V1 resident](../v1_balanced/resident/) or [V5 resident](../v5_hybrid_lowzp/resident/), plus that profile's `math_api.inc` | Complete tested public ABI; assemble/load the **profile image**, then `JSR MATH_* `; V1/V5 work on stock C64 |
| Examine/extract **one shipped implementation** | [V1 standalone mirror index](../v1_balanced/standalone/README.md), [V5 standalone mirror index](../v5_hybrid_lowzp/standalone/README.md) and [source catalog](../routines/SOURCE_CATALOG.csv) | One auditable `.asm` per public entry with all statically reachable executable instructions and byte/address annotations |
| Integrate a **relocatable source kernel** | [V1 symbolic source tree](../relocatable_source/v1_balanced/) or [full relocation guide](SOURCE_RELOCATION.md), and curated [liftable modules](../routines/README.md) | Symbolic operands/address definitions and explicit profile dependencies; some modules are directly reusable, others depend on their host core |

**Important limitation:** a file named `<profile>/standalone/<typed-name>.asm` is an **exact extracted executable graph**, **not automatically a self-contained drop-in library**. It may require shared immutable tables, zero-page reservations, REU data or another public/private routine, and its annotated addresses belong to a chosen profile. The buildable complete profile and the separately curated `routines/` modules are different packaging products. Check dependencies before copying a mirror alone. We deliberately do not claim every `standalone/*.asm` file compiles and functions independently.

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
