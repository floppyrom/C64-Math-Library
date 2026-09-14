# Native signed implementation map — v4_reu_16m

Every shipped `SMUL*` and `SDIV*` public path in this profile is now classified as a **native signed kernel**. Here, native means the signed API owns its executable arithmetic path and does not enter the corresponding unsigned executable multiply/divide engine. Immutable lookup tables may still be shared.

The canonical build source is `relocatable_source/v4_reu_16m/math_relocatable.asm`. `SIGNED_LINK_MAP.json` records the active signed entries and any private executable cores. `multiply/native/` retains hand-authored native-kernel reference material where available. Division reference sources remain under `division/`.

The old `multiply/unsigned_derived/` tree has been removed. Zero executable overlap is mechanically checked by `tools/validate_signed_layout.py`.
