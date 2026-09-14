# Native signed implementation map — v5_hybrid_lowzp

Every shipped `SMUL*` and `SDIV*` public path in this profile is a **native signed kernel**: the signed API owns its executable arithmetic path and does not enter the corresponding unsigned executable multiply/divide engine. Immutable lookup/data tables may still be shared.

The actual per-routine executable source is now published directly under:

- `multiply/native/` — `SMUL8`, `SMUL16`, `SMUL24`, `SMUL32`, `SMUL32_READY`, `SMUL16_SHR8`, `SMUL32_SHR16`
- `division/native/` — `SDIV8`, `SDIV16`, `SDIV24`, `SDIV32_16`, `SDIV32_32`, `SDIV16_SHL8`

These are exact generated source mirrors of the initialized resident executable, with address/byte annotations. They are verified against the shipped binary by `tools/validate_published_signed_sources.py`; they are no longer placeholder READMEs. The canonical integrated build source remains `relocatable_source/v1_balanced/math_relocatable.asm + tools/build_hybrid.py`.

`SIGNED_LINK_MAP.json` records each active entry, private-core placement/provenance, and the corresponding published source file. The zero-executable-overlap contract is independently checked by `tools/validate_signed_layout.py`.
