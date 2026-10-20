# Operation-first builder: explicit measured-frame selection

`math_builder.py` now offers an **opt-in** `frame` objective that selects,
pins and builds a *whole* stock C64 combination directly from an
existing **qualified source-linked mixed public-call frame report**. It
does not infer per-frame performance from independent average call times.

The ordinary operation-first objectives (`balanced`, `size`, `zp`,
`speed`) are **unchanged**. Frame selection is never enabled implicitly.

## Reproduce the qualified example

```sh
python3 tools/mixed3_frame_parity.py --out build_selective/mixed3.json
python3 tools/math_builder.py \
  --config examples/operation-first-frame.json \
  --objective frame --frame-report build_selective/mixed3.json \
  --build --out build_selective/selection_manifest.json

# Equivalent after first generating the measured report:
make builder-frame FRAME_REPORT=build_selective/mixed3.json
```

The example provides all three operations (`UMUL32`, `SMUL32`,
`ISQRT16`), **exact** code, I/O, zero-page and scratch addresses, and
explicit 12,000-byte RAM / 31-byte zero-page upper bounds. The optional
`--frame-max-cycles N` is a **hard measured math-only worst-frame**
limit, rather than an estimate of physical frame time. Use
`--frame-optimize peak|ram|zp` to choose between measured combined
project plans within all budgets.

On success the builder writes the normal `math_selective.prg`,
`math_api.inc`, `selective_manifest.json`, plus
`frame_qualified_config.json` (fixed normal resource-mode pins) and
`frame_qualified_evidence.json` (public input SHA, source/PRG hashes,
selected plan and measured worst-of-all-relocations resources and cycles).

On an ineligible source, budget, public operation set, memory layout,
mismatched input corpus or unexpectedly rebuilt PRG, it **fails closed**
and does not publish an executable. Calling `--objective frame`
without a measured report is an error; manual pins and inferred call
weights are rejected. It is not a user-project source analyzer.

This first integration supports the **specific measured candidate plans
in the report**, currently eight source-linked three-API variants
across two relocations. A future generalized measurement producer and
whole-library trace-dependent branch-and-bound selector may extend
coverage. It is **not** a claim of an optimized or fastest selectable
combination for every possible subset of the 56 operations.

**Imported timing provenance is reverified, not merely checksum-checked.** The `frame` objective first re-executes the exact registered three-operation source-linked benchmark at every declared origin. It rejects altered cycle peaks, p95, RAM/ZP, input corpus and source/PRG hashes even if the original binary still matches. Unsupported benchmark producers fail closed; see [FRAME_EVIDENCE_REPLAY.md](FRAME_EVIDENCE_REPLAY.md).

**Physical timing limitation:** this gate uses Mini6502 complete
public-call cycles plus caller JSR charges from synthetic frames.
Actual PAL/VIC-II bus contention, badlines, IRQ/SID, REU DMA,
initialization, reentrancy and application frame work are unmeasured.
Prior native x64sc qualification verifies functional correctness
of four representative pinned binaries, *not* physical worst-frame
elapsed cycles. Preserve and separately distribute all historical
V1–V5 reference images and REU compatibility services.
