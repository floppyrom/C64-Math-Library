# Repository structure

The repository is organized around three user tasks: **pick a build**, **inspect a routine**, and **check the numbers**.

| Path | Purpose |
|---|---|
| `v1_balanced/` ... `v5_hybrid_lowzp/` | Self-contained fixed profiles, deployable resident images and exact profile-local standalone routine mirrors. |
| `relocatable_source/` | Canonical relocatable integration source used by the builders. |
| `routines/` | Public source catalog plus independently benchmarked standalone/record alternatives. |
| `benchmarks/` | Machine-readable full-profile, fastest-profile and standalone performance tables with direct source paths. |
| `validation/` | Current validation evidence and record qualification data. |
| `tools/` | Builders, generators and validators. |
| `docs/` | API, naming, profile selection, relocation and technical reference. |

## What was intentionally removed

Historical exploratory research trees are not part of the replacement package. The current code, current validation evidence, benchmarked standalone sources and build tools remain. Git history is the archive for superseded experiments.

Generated build directories (`build_source/`, `build_hybrid/`, `build_pareto/`) are also omitted; rebuild them from the supplied sources.

## Source publication contract

Every shipped callable routine is indexed by `routines/SOURCE_CATALOG.csv`. Every benchmarked standalone alternative has a public source file under `routines/` and a row in `benchmarks/STANDALONE_RESULTS.csv`. `tools/validate_public_catalog.py` checks this contract mechanically.
