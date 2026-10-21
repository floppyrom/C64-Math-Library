# Explicit Turbo16 REU in the operation-first user setup (experimental)

This is the **opt-in, two-PRG** integration of the source-built Turbo16 REU module. It is not a V3/V4 profile, does not silently replace a normal math operation, and does not claim safe shared zero-page operation under active IRQ/VIC raster workloads. It requires the independently loadable Turbo16 package from PR #383. The historical profiles and REU images are still preserved.

## One configuration, global physical reservations

```sh
python3 tools/configure_math.py \
  --operation UMUL16 --operation UDIV16 \
  --objective size --zp-budget 200 --ram-budget 27000 \
  --reu-turbo16 --reu-kib 512 --reu-bank 0x4 \
  --config-out my_math_with_reu.json --build-dir build_math_with_reu
```

For a qualified **16 MiB** REU substitute `--reu-kib 16384 --reu-bank 0xC8`. Select `UMUL16` explicitly so normal stock-C64 `MATH_UMUL16` is still available as a fallback. REU is **never** chosen from a speed objective merely because its CPU-model mean is lower.

The normal global stock linker now receives these **explicit reservations before variant selection**:

| Resource | Physical reservation |
| --- | --- |
| REU service's standalone PRG staging/code/tables | $3000–$77FF (entire loadable envelope) |
| REU service's 32-byte public operand/result I/O | $C000–$C01F |
| Executable zero page exclusive while BEGIN is active | $3E–$B7 (122 bytes) |
| REU DMA registers | $DF00–$DF0A; no other I/O2 device may claim them |
| Selected REU 64KiB bank | complete exclusive bank |
| High-bank alias probe | one owned byte at bank:$FFFF in each distinct smaller-capacity mirror bank |

The stock builder defaults to `math_io=$C040` and `zp_base=$B8` in this mode, subject to the user's chosen resources and ZP budget. Both are overridable with `--memory-config`; collisions then **fail**, rather than being relocated behind the user's back. Non-REU users retain the original default placement.

**Total budgets** count all 122 REU-owned ZP bytes plus stock ZP, and the complete 18,432-byte REU PRG envelope plus 32-byte REU public I/O plus stock RAM. This is deliberately conservative. Select a small or zero-ZP stock alternative if needed. The global linker never treats the overlay as free concurrently usable zero page.

## Output and use

In addition to the original stock `math_selective.prg`, `math_api.inc`, and `selective_manifest.json`, an opt-in installation emits:

- `turbo16_reu.prg`: separately loadable, source-built, real-REU-probed Turbo16 module;
- `turbo16_reu_manifest.json`: hardware resources, source checksums and service lifecycle addresses;
- `math_reu_turbo16.inc`: optional public service entrypoints; and
- `math_project_manifest.json`: a combined, checksum-linked record of the two PRGs and globally reserved resources.

Load **both** PRGs with their included load addresses, then call the exported `MATH_T16_REU_INSTALL`. Check Carry; on failure **do not** call the REU service—use normal `MATH_UMUL16` instead. On success, use the guarded `MATH_T16_REU_BEGIN` once, `MATH_T16_REU_CALL` only within the batch, then `MATH_T16_REU_END` exactly once. Treat the 122-byte ZP overlay as exclusive throughout the active interval. Never call ordinary math routines (including the stock fallback), IRQ services or user code that touches that ZP while the overlay is active.

The source-backed REU result is in its own public 32-byte block at $C000. The stock default in REU builds is $C040; these are separate ABIs.

Saved configurations can be rebuilt *without losing the hardware option*:

```sh
python3 tools/math_builder.py --config my_math_with_reu.json --build \
  --out new_build/selection_manifest.json

python3 tools/math_builder.py --config my_math_with_reu.json --measure
```

The normal installer and all 56 stock C64 operations are unchanged when `--reu-turbo16` is absent. Ordinary V1–V5 historical profiles remain archived and never enter the mixed project.

## Qualification limits

The standalone native 512KiB/16MiB real-DMA and absent/mirrored-bank tests from PR #383 are a separate qualification. This opt-in integration adds **physical mixed stock+REU linker allocations and deterministic two-PRG rebuild evidence**, but it does **not** yet certify IRQ/VIC coexistence while the overlay is active, actual DMA bus stall cycles, all original historical V3/V4 public modes or speed parity. Real-hardware and mixed-workload qualification are required before production-grade default recommendations.
