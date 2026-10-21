# Complete REU migration — operation-first acceptance contract

## Target architecture

**One operation-first setup, no V1–V5 resident required for a new project.**
A user chooses stock math operations and optional REU services, RAM/ZP and
REU-bank reservations, then obtains independently loadable, source-built PRGs,
matching includes and one combined physical-resource manifest.

The original resident PRGs and REU images remain *immutable test fixtures*.
Do not use them as a hidden runtime dependency or embed them into the new
selective PRG. A complete migration does not require deleting reference code.

## Current qualified user-facing implementation

- 56/56 ordinary C64 public operations: current operation-first builder.
- REU Turbo16: opt-in independent PRG, real DMA presence/alias preflight,
  global RAM/ZP reservations and fallback, as qualified by #383/#384.
  It still has explicit IRQ/VIC/DMA timing limits.
- REU Turbo32 and V4 QS16: **not yet installed or qualified** in the
  operation-first runtime. The original compatibility exporter remains
  available until replacements prove the same functional contracts.
- 1541/1571/1581 operation-first backends: future work; no claim of usable
  drive-side math binaries in this migration.

## Independent source proof for the two remaining REU services

The new `tools/reu_remaining_source_modules.py` assembles the original
relocatable Turbo32 135-byte executable-ZP producer, separate public binder
and normal-RAM summation from checksum-locked symbolic sources. Its
quarter-square lookup bytes are materialized from matched V3/V4 source,
never extracted from a historical resident PRG.

For QS16, the tool independently *derives* the full 524,284-byte exact
quarter-square data set in little-endian 32-bit records:
`Q(v) = floor(v*v/4)` for `v = 0..131070`.
It also source-assembles the relocatable V4 BEGIN/CALL/END entry family.
This table occupies eight aligned 64KiB REU banks (with four unfilled bytes
in the last bank). It is a *resource ownership requirement*, not stock C64
RAM. The legacy QS16 source uses a 16-byte span of zero-page state,
with ten distinct scratch locations within that span.

The dedicated CPU-model suite checks distinct source placements and
identical mathematical results. **This does not provide a safe INSTALL,
hardware detection or native DMA REU service.**

## Gates before exposing Turbo32 and QS16 in configure_math.py

1. **Hardware install:** create standalone source-built PRGs for Turbo32
   and QS16, with explicit success/failure reporting and no execution before
   hardware detection. Handle 512KiB/16MiB distinction and high-bank mirror
   probes, reserving any destructive probe locations.
2. **Data initialization:** Turbo32 must upload/restore its exact executable
   overlay with repeatable DMA SWAP and preserve its four quarter-square
   C64 tables. QS16 must populate and verify its complete 524,284-byte table
   on a 16MiB REU without relying on an externally preloaded legacy `.reu`
   image. Mark ready only after verification; fail closed otherwise.
3. **Lifecycle safety:** independent BEGIN/CALL/END, no nested batches,
   precise 135-byte Turbo32 ZP restore, QS16 scratch ownership,
   caller inputs/outputs/Carry/stack invariants, sequential reuse,
   no unsafe mixing with stock or other live overlays.
4. **Global physical placement:** reserve every service's C64 code,
   public I/O, scratch, ZP and REU banks *before* selecting stock routines.
   Reject collisions across multiple selected services, user REU banks,
   IRQ ZP and VIC/device I/O. Apply entire-project RAM/ZP limits, not
   isolated routine estimates.
5. **Native validation:** use pinned VICE x64sc on actual packaged PRGs
   for absent and aliased REUs; both real capacity tiers; 16MiB QS16;
   native DMA and products; repeated batches and exact ZP restoration.
   Verify distinct source/maps, no historical resident PRG, separate exports,
   deterministic reproducible builds and manifest/checksum integrity.
6. **Single user interface:** add independently selectable
   `--reu-turbo32` and `--reu-qs16` to the same guided/CLI installer,
   with qualified defaults, explicit stock fallback and no historical
   `--profile` option. Update docs and tests *after* those modes work.

A build failing any of these gates must not publish PRGs or claim a REU
backend. Performance recommendations require independently measured
DMA-inclusive latency; lower historical CPU-only cycles do not imply a
higher 50Hz application frame rate.

## Evidence and command

Run:

```sh
python3 -m unittest discover -s tools -p 'test_reu_remaining_source_modules.py' -v
```

This source qualification is deliberately a **staging deliverable**, not a
completed REU consolidation. Once every gate above passes, normal users
should never need `tools/export_reu_compat.py`; the immutable exporter
may remain in the repository for regression reproduction only.
