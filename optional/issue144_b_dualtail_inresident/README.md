# In-resident dual-tail UDIV32/16 opt-in (issue #144 B)

The reproducible source-builder and machine/native qualification live in:

- `tools/build_issue144_u3216_resident_optin.py` — selected V2/V3/V4 source-built PRG/REU/API output
- `tools/issue144_u3216_inresident_dualtail_model.py` — all four DIV/MOD public entries, six relocated maps
- `tools/native_issue144_u3216_inresident_dualtail.py` — pinned x64sc exact-state tests
- `tools/issue144_u3216_inresident_fullabi_stage.py` — full 56-entry build and write guard
- `tools/issue144_u3216_inresident_v5_hybrid_probe.py` — V5 donor isolation regression
- `docs/ISSUE144_B_DUALTAIL_INRESIDENT_2026-10-16.md` — complete evidence/limits

This does not change the default canonical source or binary reference images. The 461-byte helper occupies existing `REG_LOW+$0C00` source-owned image padding **only in a specifically selected build**. V5 direct inheritance is unsafe and explicitly excluded. Private OptiSearch implementation is neither read nor published by these reproducible tests.
