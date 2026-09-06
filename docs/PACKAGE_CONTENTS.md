# Package contents and lean-distribution policy

The release ZIP is intended to be both **usable** and **reproducible** without carrying disposable build output.

## Shipped

- `v1_balanced/` … `v4_reu_16m/`: four reference profiles, including their validated resident PRGs and profile-local source/data required by the assembly trees.
- `v3_reu_512k/reu/` and `v4_reu_16m/reu/`: the two deployable reference REU images.
- `relocatable_source/`: canonical source-level relocatable assembly and map configurations, including Turbo16/Turbo32 overlay sources.
- `tools/`: deterministic builder, machine validator, configuration checks and independent-assembler verification scripts.
- `validation/`: current validation results plus the compact prior exhaustive baseline needed by the binary-delta validation argument.
- `docs/`, `USER_MANUAL.md`, `QUICK_START.md`, `README.md`, `CHANGELOG.md`, `CSDB_CHANGELOG.txt`: integration/reference documentation.

## Intentionally not shipped

- `build_source/reference/` and `build_source/alternate/`: generated outputs. Shipping them would duplicate the four PRGs plus generated REU images, including two additional 16 MiB V4 images. Recreate them with `make reference`, `make alternate`, or `make all`.
- Superseded slow-ISQRT32 candidate patch/evidence folder. The active release carries its own fast-kernel correctness, performance and delta evidence.
- Historical superseded releases, nested ZIPs, interrupted logs, Python caches, editor backups and temporary files.
- Obsolete development-only validators that depended on an external prior-release working directory, plus unreferenced legacy binary/label intermediates.

## Intentional duplication

Some small source/table/module files are identical across V1–V4. They are retained within each profile because the profile trees are designed to remain self-contained and the assembly sources reference those local files. Removing them would save little while making integration and archival use more fragile.

## Manifest hygiene

Legacy segment manifests were audited against the actual files in this distribution. Game-math segment rows now point to the integrated profile PRG rather than removed archival build directories; V4 ranges without separately shipped segment binaries are explicitly marked as integrated in the V4 PRG.
