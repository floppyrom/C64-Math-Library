# Signed implementation validation

The native-signed release is verified at three levels.

1. `tools/validate_signed_layout.py` traces signed and unsigned executable graphs for 13 API pairs in each of V1–V5. All 65 comparisons must have **zero executable instruction overlap**. It also verifies the repository taxonomy and removal of the old `unsigned_derived` artifact tree.
2. `tools/validate_signed_multiply.py` verifies 264,999 signed multiply calls across all five profiles, including exhaustive 8x8 signed coverage for independent families plus wide edge/random and `SMUL32_READY`/fixed-point coverage.
3. `tools/validate_signed_division.py` verifies 364,533 signed divide/modulo calls across all five profiles, including exhaustive SDIV8 coverage for three independent families, wide edge/random cases, divisor-zero behavior, modulo aliases and fixed-point division.

After these focused gates, the source relocation, alternate-map, deterministic rebuild, Turbo, hybrid, Pareto and release audits exercise the integrated library.

4. `validation/multiply_refresh/MULTIPLY_REFRESH_BENCHMARK.json` is the current cross-profile multiplication benchmark (415,078 machine calls) covering refreshed unsigned/signed producers, READY entries and fixed-shift derivatives. `validation/review/NATIVE_SIGNED_DELTA_AUDIT.json` is retained as historical evidence for the earlier executable-ownership split, not as the current multiplier-performance authority.

The division validator uses the global profile index for its deterministic RNG seed even when `--profile` is used, so partitioned validation is corpus-identical to a monolithic run.
