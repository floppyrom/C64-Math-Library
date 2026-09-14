# Custom Pareto source/build configuration

`tools/build_pareto.py` generates one stock-C64 library from certified V1/V2 implementation packs. It takes a **total zero-page budget**, optionally an **exact extra private-RAM budget**, an initialization policy and workload weights, then selects the highest-scoring compatible implementation set at build time. There is no runtime dispatcher.

For interactive use:

```sh
python3 tools/pareto_wizard.py
```

The generated build retains the common 45-entry API. `selection_manifest.json` records every selected pack, exact ZP ranges, exact private RAM bytes/ranges, whether `MATH_INIT` is mandatory, public addresses and the resulting binary hash.

Reference custom-Pareto private regions use RAM under BASIC ROM (`HYBRID_CODE=$A000`, `PARETO_AUX=$B200`). Bank BASIC out while selected private code/data are accessed, or relocate these symbols in a custom map.

See `docs/PARETO_BUILDER.md`.

## Signed 8-bit multiply

Custom Pareto builds inherit the direct signed-domain `SMUL8` from the V1 base. The legacy internal pack name `umul8_16` now upgrades only unsigned `UMUL8`; it does not replace `SMUL8`. This keeps the exhaustive 67.992188-cycle, 0-ZP signed kernel at every custom Pareto breakpoint.
