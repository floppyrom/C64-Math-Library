# Issue #144 D — V1/V5 SEEK16 normal-resident accumulator batching

**Status: qualification in progress; not a default-binary release.** This candidate is
isolated to the canonical V1/V5 source-builder and is not yet merged.

## Motivation and placement

The V1/V5 `SEEK16_INIT` occupies 311 bytes out of its 312-byte normal
`REG_API+$0723` to `REG_API+$085B` island, so naively inlining the 42-byte
`s16_addmin` helper does not fit. The separate ordinary resident range
`REG_API+$0599..+$05FF` (reference addresses `$3599..$35FF`) contains
103 zero bytes in the pinned historical V1 PRG and lies directly after
the existing SEEK8 initializer.

A separate 45-byte loop body, `s16_addmin_batch`, is placed at
`REG_API+$0599..+$05C5`. It repeats the identical remainder/high-word
carry/compare/subtract/whole-increment arithmetic, but executes `DEY/BNE`
**inside the helper** and returns once after all `k0` integer increments.
The original one-shot `s16_addmin` helper remains available for fractional
`k0+1` plane construction. The original INIT source shrinks by three bytes
to 308 bytes and remains within its established resident island.

The new code claims **45 resident ROM/RAM image bytes**, but **no additional
normal zero page, dynamically allocated application RAM, stack scratch or REU**.
Its scratch and eight-slot state are identical to the established SEEK kernel.
The helper is not independently reentrant: it shares the same ordinary
init scratch and constraints as the original library code.

## Cycle hypothesis, not a measurement

The integer loop previously paid JSR/RTS on each of `k0` iterations.
Batching should remove approximately `12 × (k0−1)` modeled 6510 cycles for
`k0 >= 1`, and should be neutral at `k0=0`. The exact public-call
improvement, including branches and the Euclidean preprocessing, **must be
measured** on paired, source-built corpus inputs before promotion.
The ordinary fractional path has not been modified.

## Required gates

1. `python3 tools/generate_seek_sources.py --check` must reproduce both
   V1/V5 generated resident includes and resource READMEs.
2. Reference and alternate-map source assembly must prove collision-free
   placement and the preserved public entry/ABI contract.
3. `python3 tools/issue144_seek16_v15_normal_batch_qualify.py --moves 64`
   independently compares frozen PRG to source-built V1/V5 public INIT,
   carry/X/SP, all 248 SEEK16 state bytes, and subsequent STEP,
   STEP_INT, STEP1 over interleaved slots.
4. With a real `VICE_WRAPPER`,
   `python3 tools/issue144_seek16_v15_normal_batch_qualify.py --moves 24 --native`
   must show byte-identical native output and flags.
5. Full cross-profile builds, mixed calls, package sealing, both changelogs,
   production benchmarks and release binaries are **not replaced** by this
   research evidence; certify each gate independently.

V2/V3/V4 retain the already-merged, different in-resident source acceleration
from Issue144 PR #171. The standalone general SEEK16 example retains its
own unchanged implementation and calling convention.
