# Turbo16 / Turbo32 source relocation

V3 and V4 provide two high-throughput REU batch modes. They remain lifecycle APIs, but their executable-ZP origins and REU storage banks are now selected at **assembly/build time**. There is no runtime relocation pass and no relocation cycle penalty.

## Lifecycle surface

| Entry | Reference offset from `REG_API` | Purpose |
|---|---:|---|
| `MATH_REU_UMUL16_BEGIN` | `$0800` | SWAP/install 113-byte Turbo16 overlay |
| `MATH_REU_UMUL16` | `$0840` | one 16x16->32 product |
| `MATH_REU_UMUL16_END` | `$0880` | restore caller ZP / save modified overlay |
| `MATH_REU_UMUL32_BEGIN` | `$08C0` | SWAP/install 135-byte stack-free Turbo32 overlay |
| `MATH_REU_UMUL32` | `$0900` | one 32x32->64 product |
| `MATH_REU_UMUL32_END` | `$0960` | restore caller ZP / save modified overlay |

## Configurable overlay geometry

| Symbol | Reference | Alternate proof | Size/constraint |
|---|---:|---:|---|
| `TURBO16_ZP_BASE` | `$3E` | `$40` | 113 bytes; must fit `$02-$FF` |
| `TURBO32_ZP_BASE` | `$0A` | `$06` | 135 bytes; therefore base `$02-$79` |
| `REU_TURBO16_BANK` V3 | `$04` | `$00` | bank 0..7, unique active role |
| `REU_TURBO32_BANK` V3 | `$05` | `$01` | bank 0..7, unique active role |
| `REU_TURBO16_BANK` V4 | `$04` | `$28` | unique, outside QS16 range |
| `REU_TURBO32_BANK` V4 | `$05` | `$29` | unique, outside QS16 range |

The overlay sources are `relocatable_source/turbo/turbo16_overlay.asm` and `turbo32_overlay.asm`. Their square-table references follow `REG_TABLE`, so moving the resident table region also regenerates the correct overlay operands. The Turbo32 wrapper follows `REG_LOW`.

The REU image builder assembles fresh overlay bytes for the chosen map and installs them into the configured banks. The logical metadata page historically associated with bank 5 moves with the configured Turbo32 bank so the reference build remains byte-identical while a 512 KiB alternate layout can use every bank operationally.

## Ownership contract

Turbo modes are deliberately not ordinary composable calls. Between `BEGIN` and `END`, the selected overlay owns its complete ZP range. Do not invoke normal signed/unsigned/game-math routines during that interval. `END` restores the caller's pre-overlay ZP bytes exactly. A second batch is valid: the modified/self-patched overlay saved by the prior END is correctly swapped back on the next BEGIN.

## Relocation proof

`validation/turbo_relocation/TURBO_RELOCATION_VALIDATION.json` validates V3 and V4, reference and alternate maps. It covers **17,164 product calls plus 32 BEGIN/END lifecycle calls (17,196 Turbo API calls total)**, exact products, exact ZP restoration, second-batch reuse, and verifies that reference vs alternate call/lifecycle cycle vectors are identical. Thus build-time relocation adds **zero runtime cycles**.

ACME 0.97 independently assembles all Turbo overlay sources for both maps and produces byte-identical overlays to the bundled assembler.

## Boundary proof

`TURBO_BOUNDARY_SWEEP.json` additionally executes both overlay families at the supported ZP-origin endpoints: Turbo16 `$02` and `$8F`, Turbo32 `$02` and `$79`. It also exercises V3 Turbo storage at banks `$06/$07` and V4 at `$FE/$FF`. The sweep adds **3,556 exact product calls** and preserves the same cycle vectors between minimum and maximum origins. ACME 0.97 independently reproduces the endpoint overlay bytes, including the `$8F` Turbo16 layout.
