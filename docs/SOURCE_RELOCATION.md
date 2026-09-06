# Source-level assembly relocation

## Contract

The stable 45-entry API is built from `relocatable_source/<profile>/math_relocatable.asm`. `math_config.inc` supplies the selected map at assembly time. The reference PRGs are reproducibility/provenance outputs, not binary-relocation inputs.

### Configurable C64 symbols

| Symbol | Purpose | Reference | Alternate proof |
|---|---|---:|---:|
| `REG_LOW` | low resident region | `$1000` | `$9000` |
| `REG_API` | integer API/core region | `$3000` | `$B000` |
| `REG_KERNEL` | resident kernel region | `$4000` | `$2000` |
| `REG_GAME_API` | independent 57-byte game API JMP block | `$5E00` | `$7C00` |
| `REG_TABLE` | C64 table region | `$6000` | `$4000` |
| `REG_GAME` | game-math code/data region | `$C100` | `$8000` |
| `MATH_IO` | 32-byte public operand/result block | `$C000` | `$C800` |
| `REU_SCRATCH` | C64-side REU transfer buffer | `$C020` | `$C820` |
| `V1_SCRATCH` | V1 ordinary-RAM game scratch | `$C040` | `$C840` |
| `ZP_MAIN` | normal profile ZP base | `$02` | `$07` |
| `ZP_SMUL` | V2–V4 installed native SMUL16 ZP base | `$80` | `$70` |

V3/V4 additionally expose assembly-time symbols for all operational REU banks, including `REU_TURBO16_BANK` and `REU_TURBO32_BANK`. V4's eight-bank QS16 region moves as an aligned unit. Turbo16/Turbo32 also expose `TURBO16_ZP_BASE` and `TURBO32_ZP_BASE`; their executable overlays are assembled for the selected ZP origin and placed in the selected REU banks at build time.

## Safety checks

Before assembly, the build rejects:

- a region extending outside 16-bit C64 address space;
- zero-page allocation extending above `$FF`;
- use of `$00-$01` (6510 processor port);
- overlaps among claimed C64 regions or among claimed ZP ranges;
- use of the `$DF00-$DFFF` C64 I/O/REU-register page;
- invalid page alignment on page-sensitive regions;
- illegal or colliding REU bank assignments;
- V3 stable banks outside its 512 KiB range;
- V4 QS16 base not aligned to an eight-bank boundary;
- Turbo16/32 ZP origin outside the legal one-page range or overlapping `$00-$01`;
- Turbo REU banks outside the profile capacity or colliding with other active banks/QS16.

`REG_GAME_API` is deliberately not page-alignment constrained; it is a 57-byte JMP block and may move independently.

## Proof

The reference map source build reproduces the corrected resident PRG exactly for V1–V4 and reproduces the reference V3/V4 REU images byte-for-byte. The alternate proof changes all principal C64 regions and, for V3/V4, changes the REU bank geometry **and** Turbo overlay ZP origins. All 45 stable generated public addresses are invoked literally by the machine validator. A separate Turbo validator executes BEGIN/CALL/END on both maps, verifies products, exact caller-ZP restoration, second-batch reuse and cycle identity.

See `validation/source_relocation/ALTERNATE_MAP_VALIDATION.json`, `validation/turbo_relocation/TURBO_RELOCATION_VALIDATION.json`, `DETERMINISTIC_REBUILD.json`, and `../CONFIG_VALIDATION.json`. Also see `TURBO_RELOCATION.md`.
