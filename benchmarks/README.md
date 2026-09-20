# Benchmarks

This folder is the machine-readable performance front door.

- [`PUBLIC_PROFILE_RESULTS.csv`](PUBLIC_PROFILE_RESULTS.csv): all 245 callable rows across V1-V5, with cycles, memory/ZP information, exact public source path and source SHA-256.
- [`BEST_PROFILE_RESULTS.csv`](BEST_PROFILE_RESULTS.csv): one row per canonical routine, selecting the fastest shipped profile by measured mean cycle count.
- [`STANDALONE_RESULTS.csv`](STANDALONE_RESULTS.csv): independently useful record/Pareto kernels and optional alternatives, with timing basis and validation path.

The human-readable summary is [`../PERFORMANCE.md`](../PERFORMANCE.md).

Cycle numbers are not automatically comparable across different benchmark corpora. The `cycle_basis` column is part of the result and should be quoted with the number whenever comparing standalone alternatives.
