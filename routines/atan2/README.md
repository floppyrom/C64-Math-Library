# ATAN2 kernels

This directory is the **readable, reusable source of truth** for the stock-C64
`MATH_ATAN2_8` implementations. The profile `math_relocatable.asm` files and
resident PRGs contain the installed/generated forms; developers should start
here when studying or reusing the algorithm.

Each shipped V1-V5 profile publishes its installed executable source under
`standalone/atan2_s8_s8_u8.asm`. The optional optimized kernels below additionally
provide self-contained ACME sources with all of their lookup tables.

## Contract

- input: signed 8-bit `x` and `y`
- output: unsigned 8-bit phase, `$00 = +X`, `$40 = +Y`, `$80 = -X`, `$C0 = -Y`
- `(0,0)` returns `$00`
- maximum error: **1 phase unit** over all 65,536 signed-byte vectors for the stock kernels
- normal zero-page usage: **0 bytes**
- inputs preserved; A/X/Y volatile; D=0 required; C=0 returned

The standalone sources use the reference internal I/O addresses `X0=$C000`,
`Y0=$C004`, `Z0=$C008`. The library build system relocates/installs the kernel
behind the stable public `MATH_ATAN2_8` entry, so callers should use the
published API include rather than these internal addresses.

## Kernels

| File | Profiles | Tables | Published public-entry timing |
|---|---|---:|---:|
| `atan2_compact.asm` | V1 | 512 B | **50.441345 mean**, 30-53 cycles |
| `atan2_fast.asm` | V2, V3, V5 | 1280 B | **46.953064 mean**, 30-48 cycles |

The fast kernel spends three additional 256-byte quadrant pages to avoid the
compact kernel's runtime quadrant-repair instructions. That is a **768-byte
incremental cost for about 6.9% lower average latency**.

V4 keeps its separate exact REU-backed ATAN2 path at a fixed 48 cycles.

## Optional optimized kernels (2026-09-20)

These are **standalone alternatives**, not installed-profile upgrades. The
existing installer still selects `compact`/`fast`; fixed profiles and Custom
Pareto resource accounting are unchanged.

| Kernel | Code | Tables | Code + tables | Mean cycles | Range | Shipped-output parity |
|---|---:|---:|---:|---:|---:|---|
| shipped `compact` | 106 B | 512 B | 618 B | 50.441345 | 30-53 | baseline |
| **`compact_opt`** | **94 B** | **512 B** | **606 B** | **48.447189** | 29-50 | exact |
| shipped `fast` | 94 B | 1280 B | 1374 B | 46.953064 | 30-48 | exact |
| **`sum_small`** | **92 B** | **768 B** | **860 B** | **45.958908** | 29-48 | 202 results differ by 1 |
| **`sum_fast`** | **89 B** | **1024 B** | **1113 B** | **44.962814** | 29-47 | exact |

All five use 0 extra ZP and satisfy the <=1 phase-unit bound against rounded
mathematical atan2. Every axis and `(0,0)` is exact. The three-page `sum_small`
clamps finite near-horizontal angles from 0 to 1; `compact_opt` and `sum_fast`
preserve all 65,536 existing results.

Cycle counts include the public JMP and RTS and exclude the caller's JSR.
Code is placed at `$8000`, lookup pages are aligned, and interrupts/VIC stalls
are not included. Add 3 bytes to the memory totals for the public JMP wrapper.
No scratch or extra hardware-stack bytes are used. A caller's usual JSR uses
two stack bytes. Other code origins can add branch page-crossing cycles.

Complete sources, ready for ACME:

- [atan2_s8_s8_u8_compact_opt.asm](standalone/atan2_s8_s8_u8_compact_opt.asm)
- [atan2_s8_s8_u8_sum_small.asm](standalone/atan2_s8_s8_u8_sum_small.asm)
- [atan2_s8_s8_u8_sum_fast.asm](standalone/atan2_s8_s8_u8_sum_fast.asm)

The [technical note](../../docs/ATAN2_OPTIMIZATION_2026-09-20.md) explains the
carry-clearing log sum and the memory/accuracy trade-offs.

## Installed profile source mirrors

| Profile | Executable source | Installed body |
|---|---|---|
| V1 Balanced | `v1_balanced/standalone/atan2_s8_s8_u8.asm` | compact body at `$C814-$C87D` |
| V2 Pareto-Fast | `v2_pareto_fast/standalone/atan2_s8_s8_u8.asm` | fast body at `$C782-$C7DF` |
| V3 REU 512K | `v3_reu_512k/standalone/atan2_s8_s8_u8.asm` | fast body at `$C78D-$C7EA` |
| V4 REU 16M | `v4_reu_16m/standalone/atan2_s8_s8_u8.asm` | exact REU lookup |
| V5 Hybrid Low-ZP | `v5_hybrid_lowzp/standalone/atan2_s8_s8_u8.asm` | fast body at `$C814-$C871`, Q3 remapped to `$5700` |

These generated profile mirrors describe the installed executable and depend
on the profile's existing tables. `tools/build_hybrid.py` remains authoritative
for the V5 transplant and table remap. Older files under `resident/modules/`
may carry historical origin comments; use the current executable mirrors above
for installed addresses.

## Files

- `atan2_compact.asm` - compact 512-byte-table kernel.
- `atan2_fast.asm` - four-quadrant speed kernel.
- `atan2_compact_opt.asm`, `atan2_sum_small.asm`, `atan2_sum_fast.asm` - optional
  optimized bodies; these are the source of truth for the complete exports.
- `export_optimized.py` - deterministic full-source publisher; `--check` detects
  stale exports without rewriting anything.
- `validate_optimized.py` - independent full-domain result/cycle/ABI validator
  and ACME byte comparison, including relocated page-crossing builds.
- `tables.py` - one shared deterministic table generator and exact reference
  model. This replaces the duplicate table-generation code that used to live
  inside `tools/upgrade_atan2.py`.
- `benchmark.py` - standalone exhaustive source benchmark/certifier. It adds a
  three-cycle JMP wrapper so reported timings match the public library entry.
- `tools/upgrade_atan2.py` - installer that consumes these sources and writes
  the certified kernels into V1/V2/V3 profile images.

## Reference table map

The standalone/reference layout is:

```text
$9600  signed-magnitude LOG page
$9700  compact table / fast Q0
$5500  fast Q1
$5F00  fast Q2
$4700  fast Q3 donor page
```

V5 remaps the donor Q3 page to `$5700` in its reference layout because `$4700`
is occupied by V1 arithmetic. Custom/relocated builds may use different physical
addresses; these are implementation pages, not public ABI locations.

## Reproduce the benchmark

```sh
python3 routines/atan2/benchmark.py
python3 routines/atan2/benchmark.py --kernel fast --json
```

The default benchmark reports all five kernels; `--kernel` can select any name
in the comparison table. No case exceeds one phase unit of error.

Reproduce the independent optimized-kernel certification:

```sh
python3 -m pip install py65==1.2.0
python3 routines/atan2/export_optimized.py --check
python3 routines/atan2/validate_optimized.py --acme /path/to/acme
```

The committed result is
[`validation/ATAN2_OPTIMIZATION_VALIDATION.json`](../../validation/ATAN2_OPTIMIZATION_VALIDATION.json).

The exhaustive installed-profile evidence remains in
`validation/ATAN2_UPGRADE_VALIDATION.json`; game-use analysis is in
`docs/ATAN2_GAME_AUDIT_2026-09-17.md`.
