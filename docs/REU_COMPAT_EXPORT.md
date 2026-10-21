# Immutable V3/V4 legacy REU compatibility bundles

> **Historical regression/export only, not a new-project installer.**
> The operation-first builder supports all 56 stock-C64 operations plus
> optional, independently source-built REU Turbo16, Turbo32 and QS16
> modules. See [the unified setup](REU_OPERATION_FIRST_CONSOLIDATION.md).
> The original V3/V4 resident images are preserved unchanged for historical
> API compatibility and benchmark reproduction, **not because modern
> REU modules depend on them**. Mixing a frozen resident with
> `math_selective.prg` remains unsupported.

The commands below reproduce byte-identical **old installations** for
existing projects or regression testing. For a new project, use
`make builder-setup` or the `--reu-turbo16`, `--reu-turbo32`, and
`--reu-qs16` options of `tools/configure_math.py`.

This tool produces a **separate** checksum-locked, source-identical copy of
each entire historical REU-enabled resident. Use either of these commands:

    python3 tools/export_reu_compat.py --profile v3_reu_512k --out build/reu-v3-compat
    python3 tools/export_reu_compat.py --profile v4_reu_16m --out build/reu-v4-compat

Each destination contains:

- math_legacy.prg: 49,042-byte original profile resident
- math_legacy.reu: matching original 512 KiB or 16 MiB REU image
- math_api.inc: original public address bindings and lifecycle entries
- REFERENCE_README.md and LICENSE_NOTES.md: original shipped documents
- COMPATIBILITY.txt: explicit exclusive-resident warning
- compat_manifest.json: each exact source SHA-256, byte size, original path,
  nine-or-six REU lifecycle entry ownership, and original hardware tier

The exporter checks each source file against the repository's SHA256SUMS.txt
before copying, and rechecks each staged file before publishing the bundle.
It refuses corrupted source, changed sizes or ABI, invalid profiles and
existing output directories; it never modifies legacy reference artifacts.

**Important:** This is not a REU module for a generated selective math PRG.
Do not concatenate/link these resident images, merge their MATH_* exports
with a selective include, or assume the Turbo overlay's 122/135 bytes of
zero-page executable code (or QS16's 16-byte mode) can coexist with
ordinary library scratch. Original BEGIN/CALL/END contracts still apply.

Native VICE and identical-input REU model studies already exist in the
historical V3/V4 research. This exporter preserves byte-identical access,
not physical PAL timing and not full V1–V5 retirement readiness. The source-built new REU modules have separate lifecycle/DMA/source
regressions. Mixed IRQ/VIC/SID use and concurrent REU-service
residency are not qualified; consult the new module guide.
