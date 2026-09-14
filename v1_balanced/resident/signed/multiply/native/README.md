# Native signed multiplication: published executable sources

These files expose the **actual native signed executable paths shipped by `v1_balanced`**. They are exact generated source mirrors of the resident image after `MATH_INIT`, not placeholders. Every instruction is annotated with its resident address and bytes and is checked by `tools/validate_published_signed_sources.py`.

The canonical integrated build source remains `relocatable_source/v1_balanced/math_relocatable.asm`. These mirrors exist so a GitHub reader can inspect each signed implementation directly without hunting through the monolithic generated source. Shared immutable lookup/data tables are not duplicated; corresponding unsigned executable instructions are never entered.

| Public API | Published source |
|---|---|
| `MATH_SMUL8` | `smul8_native.asm` |
| `MATH_SMUL16` | `smul16_native.asm` |
| `MATH_SMUL24` | `smul24_native.asm` |
| `MATH_SMUL32` | `smul32_native.asm` |
| `MATH_SMUL32_READY` | `smul32_ready_native.asm` |
| `MATH_SMUL16_SHR8` | `smul16_shr8_native.asm` |
| `MATH_SMUL32_SHR16` | `smul32_shr16_native.asm` |

See `../../SIGNED_LINK_MAP.json` for placements/provenance and `validation/review/SIGNED_LAYOUT_VALIDATION.json` for the zero-overlap proof.
