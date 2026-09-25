# Package contents and lean-distribution policy

This replacement package is intended to be copied over a clean local checkout and committed as the complete repository tree.

## Included

- all five validated fixed profiles (`v1_balanced` ... `v5_hybrid_lowzp`), including deployable PRGs and the V3/V4 REU images;
- `relocatable_source/` and the build/validation tools needed to reproduce the profiles;
- all profile-local typed standalone sources (54 / 54 / 60 / 63 / 54 callable entries);
- `routines/`, including public standalone record/Pareto sources, the optimized ATAN2 family and the `movement/` seek DDA;
- `benchmarks/`, with the full profile table, a fastest-shipped-per-routine index, standalone alternatives, direct source paths and SHA-256 for every published row;
- current validation/certification evidence;
- integration, naming, profile and performance documentation.

## Intentionally excluded

- the old top-level `research/` experiment tree;
- generated build directories and Python caches;
- nested release ZIPs, temporary files, logs and editor backups;
- untracked local scratch work.

The repository's Git history remains the archive for superseded experiments. The current tree is kept focused on code that can be built, called, audited or benchmarked.

## Public-source rule

No standalone performance claim should be added without an exact public source file and validation path. Run:

```sh
python3 tools/validate_public_catalog.py
```

before release. The validator checks all 245 shipped callable entries plus every standalone alternative in the benchmark table.
