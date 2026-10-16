# Issue #144 F: Versioned, reproducible dual-map C64 Math Library distribution

**Status:** candidate promotion mechanism. This is **not** permission to overwrite the seven SHA-pinned historical PRG/REU files, rewrite historical performance figures, or declare physical hardware timing qualified.

## Build and verify

From a clean checkout of the desired source commit with Python 3.12:

```sh
python3 tools/issue144_versioned_distribution.py --version issue144-2026.10.16-source-rc1 --out /tmp/c64ml-versioned
cd /tmp/c64ml-versioned
sha256sum -c C64-Math-Library-issue144-2026.10.16-source-rc1.zip.sha256
python3 /path/to/C64-Math-Library/tools/issue144_versioned_distribution.py --verify C64-Math-Library-issue144-2026.10.16-source-rc1.zip
```

The builder regenerates the canonical V1, V2, V3, V4, and V5 **reference and alternate** PRGs: 10 PRGs in total. It also builds both relocated V3 512-KiB and V4 16-MiB REU images: **4** images across the two layouts. Every map/profile includes a caller `math_api.inc`, full assembly source manifest, public 56-entry source-model verification and exact package hashes. Reference-map ISQRT32 outputs are benchmarked against the **original sealed binary** on the **same 438 radicands** per profile (root, carry, preserved input, mean, p95, minimum/maximum improvement and slower-call count). The packaged V4 current-source comparison must include the PR #192 direct-ZP improvement (approximately 135.2055 CPU-model cycles on the common 438-case corpus); otherwise the builder rejects a stale image.

The top-level ZIP contains `MANIFEST_SHA256.json`, `QUALIFICATION_SUMMARY.json`, `README.md`, two per-map qualification JSON reports, `benchmarks/ISQRT32_MATCHED_INPUTS.csv`, and each profile's PRG, REU (where required), generated public API include and build manifest. An external `.sha256` file seals the whole archive. ZIP file timestamps and ordering are stable; the source commit ID is recorded explicitly. `--verify` checks complete archive inventory, every byte digest, REU size, package path safety, presence of all profiles/maps, public headers and PRG digests independently of the builder.

## Repository automation and release controls

The [Issue144 reproducible versioned dual-map candidate distribution](../.github/workflows/issue144-versioned-distribution.yml) workflow builds the archive on PRs and on the first relevant merge to `main`, uploading the result as a GitHub Actions artifact for **90 days**. Validation has **no ability to create a public release**. An actual GitHub **prerelease** requires manually dispatching the workflow on `main` with an explicit version and `publish_prerelease=true`. That publish job additionally checks that `main` has not changed, that the exact commit has green full-library validation and comparable unsigned-performance checks, that its output ZIP and SHA-256 match, and that the requested GitHub release tag does **not** already exist. It creates a **prerelease**, not the latest/default release. Future releases must use new version identifiers; neither existing tags nor historical binaries are overwritten.

No new production-default images are placed inside the tracked `v*/resident/` or `v*/reu/` paths. Existing `PERFORMANCE.md` still describes the frozen reference binary performance. The newly built version's exact ISQRT32 matched-input CSV lives **inside the versioned archive**; do not substitute it for historical mixed-corpus figures.

## Hardware limitations and outstanding work

VICE native functional tests, full public API source-model validation and 6502 instruction-cycle accounting **do not** establish physical PAL/NTSC VIC bus contention, real REU DMA elapsed latency, IRQ/NMI reentrancy or interruptible shared-ZP safety. A permanent, hardware-qualified default release requires those tests or an explicit scoped declaration of unsupported safety guarantees. Other Issue #144 unrestricted divide/multiply optimization targets remain open.

The new bundle is intended to make the first *reproducible versioned release candidate* possible without falsely changing the certification basis of the old fixed-profile binaries.
