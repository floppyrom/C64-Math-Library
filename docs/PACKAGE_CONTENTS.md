# Package contents and lean-distribution policy

The release ZIP is intended to be both **usable** and **reproducible** without carrying disposable build output.

## Shipped

- `v1_balanced/` … `v4_reu_16m/`: the four original reference profiles, including their validated resident PRGs and profile-local source/data required by the assembly trees.
- `v5_hybrid_lowzp/`: the validated stock-C64 hybrid reference PRG, generated API include, segment map, performance table and example.
- `v3_reu_512k/reu/` and `v4_reu_16m/reu/`: the two deployable reference REU images.
- `relocatable_source/`: canonical source-level relocation inputs and map configurations, including Turbo16/Turbo32 overlays, V5 hybrid maps, and `custom_pareto/` maps used by the budget selector.
- `v1_balanced/resident/signed/` … `v5_hybrid_lowzp/resident/signed/`: native-signed implementation/provenance artifacts under `multiply/native` and `division`, with per-profile link maps and zero-overlap validation.
- `tools/`: deterministic builders and validators, including `build_pareto.py`, the interactive `pareto_wizard.py`, Pareto configuration tests and stress validation.
- `validation/`: current validation results, including `validation/hybrid/` and `validation/pareto/`, plus the compact prior exhaustive baseline needed by the binary-delta validation argument.
- `docs/`, `USER_MANUAL.md`, `QUICK_START.md`, `README.md`, `CHANGELOG.md`, `CSDB_CHANGELOG.txt`: integration/reference documentation.

## Intentionally not shipped

- `build_source/reference/`, `build_source/alternate/`, `build_hybrid/`, `build_hybrid_repeat/`, and `build_pareto/`: generated outputs. Recreate V1–V4 with `make reference` / `make alternate`, V5 with `make hybrid`, and custom budget builds with `build_pareto.py` / `pareto_wizard.py`.
- Superseded slow-ISQRT32 candidate patch/evidence folder. The active release carries its own fast-kernel correctness, performance and delta evidence.
- Historical superseded releases, nested ZIPs, interrupted logs, Python caches, editor backups and temporary files.
- Obsolete development-only validators that depended on an external prior-release working directory, plus unreferenced legacy binary/label intermediates.

## Intentional duplication

Some small source/table/module files are identical across V1–V4. They are retained within each profile because the profile trees are designed to remain self-contained and the assembly sources reference those local files. Removing them would save little while making integration and archival use more fragile.

## Manifest hygiene

Legacy segment manifests were audited against the actual files in this distribution. Game-math segment rows now point to the integrated profile PRG rather than removed archival build directories; V4 ranges without separately shipped segment binaries are explicitly marked as integrated in the V4 PRG.
