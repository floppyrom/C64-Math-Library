# Benchmarks — operation-first system

**Current chart and measurement interpretation:** [Performance — operation-first](../PERFORMANCE.md). It compares actual source-linked **whole-library plans**, RAM/ZP budgets and matched trace outcomes, not profile columns. Individual source variant CPU-model means for a chosen operation are **recomputed by the normal speed installer** and published in `selective_manifest.json` with the original corpus hash; see [operation-first setup](../docs/OPERATION_FIRST_USER_SETUP.md).

## Preserved historical data (not current installation choices)

- [`PUBLIC_PROFILE_RESULTS.csv`](PUBLIC_PROFILE_RESULTS.csv): 245 archived callable rows across V1–V5, original public resident benchmark samples, resources and SHA references.
- [`BEST_PROFILE_RESULTS.csv`](BEST_PROFILE_RESULTS.csv): archived fastest-profile ranking, **not** today's optimizer ranking. Different benchmark bases must not be mixed.
- [`UNSIGNED_COMMON_PROFILE_RESULTS.csv`](UNSIGNED_COMMON_PROFILE_RESULTS.csv): 55 matched-input observations (11 APIs × 5 legacy residents), including p95/worst-case and corpus hashes, reproducible historical comparability only.
- [`STANDALONE_RESULTS.csv`](STANDALONE_RESULTS.csv): independent Pareto and record kernels; may have distinct ABI, corpus or memory state and are **not necessarily selectable** by the current source linker.

The original historical Markdown table is retained [unchanged in the performance archive](../docs/PERFORMANCE_ARCHIVE_HISTORICAL_RESIDENTS_2026-10-21.md).

## Never mix measurement bases

CPU-model entry-through-RTS means, whole-project math-only CPU+JSR frame peaks, and native VICE PAL/CIA **elapsed slots** measure different things. External REU DMA/bus delay is absent from historical CPU-model-only REU timings. Source-only record means on different corpora cannot prove one variant is faster than another. Quote the specific source, input corpus, selected `link:...` variant, physical RAM/ZP budget and measured scope.
