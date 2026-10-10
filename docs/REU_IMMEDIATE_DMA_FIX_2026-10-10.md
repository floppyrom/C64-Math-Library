# REU immediate-DMA correction (2026-10-10)

## Problem
The V3 (512 KiB) and V4 (16 MiB) resident binaries issue REU fetch/swap
commands `$81`, `$82` and, in V4, `$A1`. These commands arm a delayed DMA
operation, which requires a subsequent write to `$FF00`. A number of public
lookup and Turbo routines instead read their C64-side results immediately after
the command write. For those call sites, **bit 4 must be set** to start DMA immediately.

## Correction
Change only the commands written to `$DF01` in the affected resident paths:
`$81` => `$91` (fetch), `$82` => `$92` (swap), `$A1` => `$B1`
(autoload fetch). Keep all unrelated data bytes and any legitimately deferred
transfer unchanged. The V3 executable changes at 35 immediate-command sites;
V4 changes at 26 sites, with PRG size and public ABI unchanged. The matching
512 KiB/16 MiB REU data images are unchanged.

Canonical resident sources, relocatable generated sources, fixed-map PRGs and
standalone API source mirrors are updated together.

## Reproducibility and qualification
- Source regeneration (`tools/generate_sources.py`) and reference/alternate
  assembly reproduce the corrected fixed-map PRGs byte-for-byte.
- Both reference and alternate source-build validations: 56 public API entries
  and 21,678 calls **per profile** across V1-V4.
- Deterministic source rebuild: 8/8 checks passed.
- Standalone source validator: 1,617/1,617 checks passed.
- VICE `x64sc` native smoke probes on the corrected PRGs and original REU
  images: V3 and V4 UMUL8/UDIV8 12/12 each; Turbo16 and Turbo32 12/12 each;
  BEGIN/CALL/END zero-page restoration passed. The corresponding uncorrected
  binaries failed. See P38 native testing evidence (separate private handoff).

**Limitations:** No physical REU hardware qualification; no claim that every
public routine was exhaustively tested under VICE. Existing cycle-performance
figures should be treated as prior-model measurements pending a full
hardware/timing rebenchmark.
