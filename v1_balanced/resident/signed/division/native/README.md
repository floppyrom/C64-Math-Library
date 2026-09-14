# Native signed division: published executable sources

These files expose the **actual native signed executable paths shipped by `v1_balanced`**. They are exact generated source mirrors of the resident image after `MATH_INIT`, not placeholders. Every instruction is annotated with its resident address and bytes and is checked by `tools/validate_published_signed_sources.py`.

The canonical integrated build source remains `relocatable_source/v1_balanced/math_relocatable.asm`. These mirrors exist so a GitHub reader can inspect each signed implementation directly without hunting through the monolithic generated source. Shared immutable lookup/data tables are not duplicated; corresponding unsigned executable instructions are never entered.

| Public API | Published source |
|---|---|
| `MATH_SDIV8` | `sdiv8_native.asm` |
| `MATH_SDIV16` | `sdiv16_native.asm` |
| `MATH_SDIV24` | `sdiv24_native.asm` |
| `MATH_SDIV32_16` | `sdiv32_16_native.asm` |
| `MATH_SDIV32_32` | `sdiv32_32_native.asm` |
| `MATH_SDIV16_SHL8` | `sdiv16_shl8_native.asm` |

`SMOD*` entries are aliases of the corresponding native signed divider and therefore do not need separate executable kernels.

See `../../SIGNED_LINK_MAP.json` for placements/provenance and `validation/review/SIGNED_LAYOUT_VALIDATION.json` for the zero-overlap proof.
