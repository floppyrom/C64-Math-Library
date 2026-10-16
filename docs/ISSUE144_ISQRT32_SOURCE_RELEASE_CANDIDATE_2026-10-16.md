# Issue #144: ISQRT32 evaluation and five-profile source-release candidate (16 October 2026)

**Status: qualification candidate, not a shipped default release.** This independently reconstructs five current-source PRGs and V3/V4 REU images while preserving all seven historical binary files and their SHA256SUMS entries.

## Reproducible builds

From a clean checkout, with Python 3.12, run:

- `python3 tools/issue144_isqrt32_release_candidate.py --layout reference --out /tmp/c64ml-issue144-reference`
- `python3 tools/issue144_isqrt32_release_candidate.py --layout alternate --out /tmp/c64ml-issue144-alternate`

The named GitHub Actions workflow runs both commands on PRs and uploads separately versioned downloadable artifacts. Each artifact contains five canonical-source-built profile PRGs, V3/V4 regenerated REU images (existing assembler regenerates REU relocation using historical verified tables as inputs), public caller includes, source-build manifests and a new `ISSUE144_RELEASE_CANDIDATE.json` with binary hashes and provenance.

Before and after builds, seven frozen binary SHA-256s are checked against the existing package seal. For each map, all 56 public routines must execute correctly under the source 6502 model. Reference-map ISQRT32 is separately benchmarked against the historical shipped reference PRG for each profile on one identical edge, boundary-square and seeded full-width corpus. New and old outputs, carry and preserved operands are validated; per-profile mean/p95 and regression counts are emitted in the candidate JSON. The native VICE job independently requalifies the prior V1/V5, V2/V3 and V4 ISQRT32 source-built improvements, using actual emulated REU images where applicable.

## What the measurements do not certify

CPU-model instruction cycles do not include real C64 VIC bus contention, external REU DMA wall time or physical interrupt latency. Native VICE output parity is a correctness gate, **not** a physical 6510 motherboard benchmark. A further unrestricted ISQRT32 algorithmic win is not implied by packaging the already-merged highword seed and V4 fast-four/maskshift implementations.

**Do not** overwrite reference PRGs or REUs or republish historical `PERFORMANCE.md` timings from candidate source results. Releasing a new default version requires exact-head PR and postmerge CI, downloaded-artifact checksum verification, independent physical VIC/REU/IRQ evaluation or explicitly documented unsupported claims, updated versioned performance tables/changelogs, and a tagged reproducible production release.
