# Custom Pareto Builder

The **Custom Pareto Builder** generates one stock-C64 C64 Math Library build from certified V1/V2 implementation packs. It is intended for games and demos that know how much zero page and ordinary RAM they can dedicate to math.

There is **no runtime dispatcher**. Selection happens at build time and the generated library keeps the same 45-entry public API.

## Easiest way: interactive wizard

```sh
python3 tools/pareto_wizard.py
```

The wizard asks:

1. how many **total ZP bytes** the library may reserve;
2. an optional **extra private RAM budget** relative to V1;
3. whether one startup `MATH_INIT` call is acceptable;
4. optional hot-routine weights;
5. which memory map to use.

It shows the selected implementation packs before building.

## Direct builder

```sh
python3 tools/build_pareto.py --zp-budget 60
```

Useful options:

```text
--zp-budget N          total ZP bytes available; minimum 31
--ram-budget N         exact extra private/resident payload bytes allowed vs V1
--init-policy auto     packs requiring one MATH_INIT are allowed
--init-policy optional forbid packs that make MATH_INIT mandatory
--weight NAME=N        make one API routine more/less important
--weights-json FILE    load routine weights from JSON
--config-kind reference|alternate
--config FILE          use your own memory map
--name NAME            generated build-directory name
```

The output directory contains:

```text
math_custom_pareto_game_math.prg
math_api.inc
selection_manifest.json
source_build_manifest.json
```

`selection_manifest.json` records the selected packs, exact ZP ranges, exact extra private RAM bytes/ranges, initialization requirement, public addresses and binary SHA-256.

## What “optimal” means

For each certified pack the library records its measured cycle savings and resource requirements. The selector evaluates every compatible combination that fits the requested budgets and chooses the highest weighted cycle saving.

With no weights supplied, every affected public API routine has weight `1`. A weight is therefore a **multiplier relative to the normal equal-weight model**, not a declaration that every unspecified routine has weight zero.

For example:

```sh
python3 tools/build_pareto.py \
  --zp-budget 55 \
  --weight MATH_UMUL24=100 \
  --weight MATH_UMUL8=0 \
  --weight MATH_UMUL16=0 \
  --weight MATH_SMUL8=0 \
  --weight MATH_UMUL16_SHR8=0
```

makes the 24-bit multiplier much more important. At the same 55-byte ZP budget, this can choose the UMUL24 pack instead of the normal UMUL8/16 pack.

## Certified stock-C64 packs

| Pack | Additional ZP | Extra private RAM payload | Main accelerated public paths |
|---|---:|---:|---|
| V5 zero-ZP imports | 0 | 4608 B | UDIV16/24/32_16, matching UMOD aliases, UMOD8, COS8, SINCOS8 |
| initialized UMUL32 | 0 | 350 B | UMUL32/SMUL32 and 32-bit shifted multiply users |
| UMUL8/16 | 5 B | 714 B | UMUL8, UMUL16, SMUL8, UMUL16_SHR8 |
| UMUL24 | 24 B | 356 B | UMUL24, SMUL24 |
| native SMUL16 executable-ZP | 116 B | 176 B | SMUL16, SMUL16_SHR8 |

When any selected pack requires initialization, the builder also emits a small exact-size `MATH_INIT` helper. Its bytes are included in `--ram-budget` accounting.

At a 221-byte ZP budget, the complete V2 implementation fits and the builder selects V2 directly rather than reconstructing it from packs.

## Default equal-weight Pareto points

These are the current default selections when RAM is unrestricted and startup `MATH_INIT` is allowed:

| ZP budget | Selected result | Exact extra RAM vs V1 | Init? |
|---:|---|---:|---|
| **31 B** | V5 zero-ZP imports + initialized UMUL32 | **4976 B** | yes |
| **36 B** | above + UMUL8/16 pack | **5698 B** | yes |
| **60 B** | above + UMUL24 pack | **6086 B** | yes |
| **147 B** | V5 imports + initialized UMUL32 + native SMUL16 | **5162 B** | yes |
| **176 B** | all certified hybrid packs | **6272 B** | yes |
| **221 B** | complete V2 | **208 B resident increase vs V1** | yes |

RAM is not monotonic with ZP because the optimizer maximizes weighted speed, not “number of packs.” For example, the 147-byte point spends most of its ZP budget on the exceptionally fast SMUL16 executable-ZP implementation and omits smaller multiplier packs.

## Why V1 and V5 still matter

The builder reaches the existing fixed profiles naturally:

```sh
python3 tools/build_pareto.py --zp-budget 31 --ram-budget 0
```

produces a PRG **byte-for-byte identical to V1**.

And:

```sh
python3 tools/build_pareto.py --zp-budget 31 --init-policy optional
```

produces a PRG **byte-for-byte identical to V5**.

So V1/V2/V5 remain useful reproducible presets and validation anchors; the custom builder is the flexible stock-C64 integration path.

## ZP geometry

The ZP budget counts the number of bytes owned, not necessarily one contiguous range. In the reference map:

```text
$02-$20   31 B   V1 base window
$21-$38   24 B   optional UMUL24 pack
$39-$3D    5 B   optional UMUL8/16 pack
$80-$F3  116 B   optional native SMUL16 executable-ZP pack
```

The generated manifest lists the exact active ranges. Bytes outside those ranges are not library-owned.

For a custom map, `ZP_MAIN` relocates the low ranges and `ZP_SMUL` independently relocates the executable SMUL16 range. The configuration validator rejects overlaps, `$00/$01`, overflow and other illegal placements.

## Ordinary RAM and BASIC ROM

The reference custom-Pareto map deliberately uses RAM under BASIC ROM:

```text
HYBRID_CODE = $A000   ; V5 import area when selected
PARETO_AUX  = $B200   ; generated multiplier/data area
```

A game/demo using these selected packs must expose RAM underneath BASIC ROM while they execute, or relocate these regions in its custom configuration.

The RAM budget is enforced against the **exact private payload bytes actually selected**, not the size of a single contiguous address envelope. See `private_main_ram_ranges` in the generated manifest for exact ownership.

## Initialization

If the manifest says:

```text
"math_init_required": true
```

call `MATH_INIT` exactly as you would for V2:

```asm
        cld
        jsr MATH_INIT
```

before any math call.

`--init-policy optional` restricts the selector to implementations that retain V1/V5-style optional initialization.

## Validation

Run:

```sh
make pareto-validate
```

or individually:

```sh
python3 tools/validate_pareto.py
python3 tools/test_pareto_config.py
python3 tools/stress_pareto.py
```

The release validation covers representative budget points on both reference and alternate maps, all 45 public entries, V2 result/cycle parity for imported paths, exhaustive UMOD8, deterministic rebuilds, V1/V5 endpoint identity, ZP confinement, invalid resource maps, signed-multiply stress and mixed workloads.
