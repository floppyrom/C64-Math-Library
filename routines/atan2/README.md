# ATAN2 kernels

This directory is the **readable, reusable source of truth** for the stock-C64
`MATH_ATAN2_8` implementations. The profile `math_relocatable.asm` files and
resident PRGs contain the installed/generated forms; developers should start
here when studying or reusing the algorithm.

Each shipped V1-V5 profile now also publishes the ATAN2 implementation used by
that profile beside its other resident module sources, so a profile can be
inspected without tracing the shared installer/build tooling.

## Contract

- input: signed 8-bit `x` and `y`
- output: unsigned 8-bit phase, `$00 = +X`, `$40 = +Y`, `$80 = -X`, `$C0 = -Y`
- `(0,0)` returns `$00`
- maximum error: **1 phase unit** over all 65,536 signed-byte vectors for the stock kernels
- normal zero-page usage: **0 bytes**

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

## Profile-local resident sources

| Profile | Resident source | Installed form |
|---|---|---|
| V1 Balanced | `v1_balanced/resident/modules/resident_atan2.a` | compact body at `$C459-$C496` |
| V2 Pareto-Fast | `v2_pareto_fast/resident/modules/pareto_atan2.a` | fast body at `$C543-$C57A` |
| V3 REU 512K | `v3_reu_512k/resident/modules/pareto_atan2.a` | fast body at `$C543-$C57A` |
| V4 REU 16M | `v4_reu_16m/resident/modules/reu_atan2.a` | exact REU lookup body from `game_math_extension.asm` |
| V5 Hybrid Low-ZP | `v5_hybrid_lowzp/resident/modules/hybrid_atan2.a` | V2 fast body transplanted into the `$C814-$C871` reserved span, Q3 remapped to `$5700` |

The V1-V3 files are direct profile-local listings of the installed stock-CPU
kernels. V4 publishes its exact REU source fragment without inventing a second
fixed implementation address: the surrounding game-math source assigns that
address. V5 publishes the assembled fast-kernel semantics with the V5 physical
table map; `tools/build_hybrid.py` remains authoritative for the transplant and
address-remap operation recorded in `HYBRID_BUILD_MANIFEST.json`.

## Files

- `atan2_compact.asm` - compact 512-byte-table kernel.
- `atan2_fast.asm` - four-quadrant speed kernel.
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

Expected headline results are 50.441345 cycles for `compact` and 46.953064 for
`fast`, with zero cases exceeding one phase unit of error.

The exhaustive installed-profile evidence remains in
`validation/ATAN2_UPGRADE_VALIDATION.json`; game-use analysis is in
`docs/ATAN2_GAME_AUDIT_2026-09-17.md`.
