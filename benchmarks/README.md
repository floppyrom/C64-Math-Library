# Benchmarks

This folder is the machine-readable performance front door.

- [`PUBLIC_PROFILE_RESULTS.csv`](PUBLIC_PROFILE_RESULTS.csv): all 245 callable rows across V1-V5, with cycles, memory/ZP information, exact public source path and source SHA-256.
- [`BEST_PROFILE_RESULTS.csv`](BEST_PROFILE_RESULTS.csv): one row per canonical routine, selecting the fastest shipped profile by measured mean cycle count.
- [`STANDALONE_RESULTS.csv`](STANDALONE_RESULTS.csv): independently useful record/Pareto kernels and optional alternatives, with timing basis and validation path.

- [`UNSIGNED_COMMON_PROFILE_RESULTS.csv`](UNSIGNED_COMMON_PROFILE_RESULTS.csv): 55 apples-to-apples cross-profile observations (11 unsigned APIs × 5 profiles), deterministic identical inputs, with p95/worst-case cycles and SHA-256 case/provenance hashes. Ranking winners for these 11 APIs in `BEST_PROFILE_RESULTS.csv` now use this comparable basis, not the old different-seed profile means.

The human-readable summary is [`../PERFORMANCE.md`](../PERFORMANCE.md).

Cycle numbers are not automatically comparable across different benchmark corpora. The `cycle_basis` column is part of the result and should be quoted with the number whenever comparing standalone alternatives.

**Important:** `PUBLIC_PROFILE_RESULTS.csv` and consolidated legacy tables retain the independent per-profile validation seeds. Their numerical differences are not proof of faster code. Workload class, call frequency, ZP, and external REU DMA costs still matter.
