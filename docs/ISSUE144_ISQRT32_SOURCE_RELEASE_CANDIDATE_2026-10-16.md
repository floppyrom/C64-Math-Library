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

## Qualified candidate measurements and publication (PR #188)

[PR #188](https://github.com/floppyrom/C64-Math-Library/pull/188) merged as `338a3df2` after **29/29 PR checks passed**, including source-build reference and alternate map outputs and native VICE root checks. Both downloadable GitHub Actions artifacts were generated in [run #38852903249](https://github.com/floppyrom/C64-Math-Library/actions/runs/38852903249). Their 30-day retention is separate from this persistent research record.

The persistent **438-identical-input** source-binary comparison is [`benchmarks/ISSUE144_ISQRT32_SOURCE_CANDIDATE_2026-10-16.csv`](../benchmarks/ISSUE144_ISQRT32_SOURCE_CANDIDATE_2026-10-16.csv), with full binary SHA-256 provenance in [`validation/review/ISSUE144_SOURCE_RELEASE_CANDIDATE_2026-10-16.json`](../validation/review/ISSUE144_SOURCE_RELEASE_CANDIDATE_2026-10-16.json). V1/V5 saved 51 model cycles each, V2/V3 saved 47 each, V4 saved 119.2055 on average (101–137 range), with **no slower calls** on this corpus. V4 went from 924.0822 to 804.8767 cycles. A separate 16-call emulator-only CIA Timer A experiment on V4 measured 749–1,018 ticks (median 810.5), with JSR/read overhead; no claims about physical PAL/NTSC VIC/REU/DMA hardware are warranted.

These findings benchmark the **already-integrated root source**, not a new algorithm. Historical production `PERFORMANCE.md` retains its former PRG measurement basis. More aggressive all-domain ISQRT32 research, physical REU timing, IRQ/NMI qualification and tagged default-binary publication remain OPEN.
