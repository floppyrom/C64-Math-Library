# Game Math Memory Map

| Profile | Public stubs | Tables | Code | Scratch | Additional integration state |
|---|---|---|---|---|---|
| V1 | `$5E00-$5E3B` | `$9400-$94FF`, `$9600-$9BFF` | `$C100-$CB20`, `$CB40-$CBA3` | `$C040-$C057` RAM | none; original 31-byte ZP unchanged |
| V2 | `$5E00-$5E3B` | `$9400-$9BFF` | `$C100-$CA31`, `$CB40-$CB98` | `$53-$6A` ZP | init patch `$32B8-$32BA`, loader `$32C0-$32CB`, SMUL16 source `$CC00-$CC73` |
| V3 | `$5E00-$5E3B` | `$9400-$9BFF` | `$C100-$CA3C`, `$CB40-$CB98` | `$53-$6A` ZP | init patch `$32B0-$32B2`, loader `$32C0-$32CD`, SMUL16 source `$CC00-$CC73` |
| V4 | `$5E00-$5E3B` | `$9400-$95FF`, `$9800-$9BFF` | `$C100-$C7CD`, `$C830-$C8FB`, `$CB40-$CB98` | `$53-$6A` ZP | same installer geometry as V3 |

The extension intentionally leaves `$A000-$BFFF` free of executable/table content. Validation PRGs are contiguous files and therefore contain padding across gaps; linkers should use the documented sparse segments rather than treating every byte in the PRG span as active resident content.

## REU

V3 game image:

- the configured `REU_TURBO16_BANK` reserves `$8000-$FFFF` for the 32 KiB `VEC2_NORMALIZE_Q8_8` ratio-index table; the Turbo16 overlay remains in the low part of the same bank and does not overlap it;
- banks 0–5 preserve the established direct lookup/turbo content;
- bank 6 = reciprocal low byte table;
- bank 7 = reciprocal high byte table (the old bank-7 metadata signature is replaced);
- game-image signature is moved to bank 5 offset `$FF00`.

V4 game image:

- the configured `REU_TURBO16_BANK` reserves `$8000-$FFFF` for the same 32 KiB `VEC2_NORMALIZE_Q8_8` ratio-index table; no additional REU bank is required;
- preserves existing operational content in banks 0–5;
- bank 6 = reciprocal low; bank 7 = reciprocal high;
- bank 8 = exact signed-byte atan2 plane;
- bank 9 = exact ISQRT16 table;
- C64 `$9800-$99FF` = two 256-byte square planes used by the fast ISQRT32 residual setup;
- the existing QS16 region `$100000-$17FFFB` is byte-for-byte unchanged;
- game-image signature is at bank 5 offset `$FF00`.

The former V4 documentation statement that the entire first 512 KiB is byte-for-byte identical to V3 is **not applicable to the game-math image**, because previously reserved banks 6–7 now have defined content.

## Current vector-normalization placement

The 2026-09-21 normalization refresh adds stock code/tables below $2000 and moves V1/V2/V5 PRG loads to $1000. The historic game-extension spans above are only part of the resident image. Current normalizer code, tables and scratch are listed in `VEC2_NORMALIZE_Q8_8.md` and each profile's `resident/SEGMENTS.csv`; `CONSOLIDATED_ROUTINE_TABLE.csv` gives current PRG spans. V3/V4 use the existing REU ratio bank without enlarging either REU image.
