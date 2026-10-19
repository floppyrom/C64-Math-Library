# Source-verified frame-qualified project installer snapshot

After exporting a pinned config, run `python3 tools/native_frame_qualified_config.py` with `VICE_WRAPPER` pointing to pinned x64sc r46284 to verify the **actual, byte-identical CLI-produced PRG** in the emulator (2 layouts × 2 Pareto budgets × 3 independently checked public APIs). See [`FRAME_QUALIFIED_NATIVE_VICE.md`](FRAME_QUALIFIED_NATIVE_VICE.md). This is native correctness validation, not PAL raster-cycle timing.

This project-level export bridges the *research* mixed frame Pareto frontier
to a standard operation-first C64 Math Library configuration. It is deliberately
**not** a new 56-operation `speed` optimizer or a general physical PAL timing
certificate. It exports a source/ABI-pinned normal `math_builder.py` config
whose *specific linked binary* is reproduced and SHA-checked.

## Qualify the public call trace, then export a fixed project plan

```sh
mkdir -p build/qualified
python3 tools/mixed3_frame_parity.py \
  --out build/qualified/mixed3.json

python3 tools/frame_qualified_config.py \
  --in-report build/qualified/mixed3.json \
  --out-config build/qualified/math-config.json \
  --out-evidence build/qualified/provenance.json \
  --ram-budget 12000 --zp-budget 31 \
  --code-base 0x8000 --math-io 0xc000 \
  --zp-base 0x50 --scratch-base 0xc040

python3 tools/math_builder.py \
  --config build/qualified/math-config.json --build \
  --out build/qualified/output/selection_manifest.json
```

The resulting `math-config.json` is a **standard installer config** with
the operations, exact variant pins, RAM/ZP limits and tested code, I/O,
zero-page and scratch locations. The installer is invoked with `size`
objective *because all variant choices are explicitly pinned*, rather than
silently re-running a weighted average speed search on unrelated inputs.
The separate provenance report records the input corpus SHA256, benchmark
frame count, selected full plan and measured worst-placement memory/peak
math-cycle envelope.

**Fail-closed guarantees:**

- The raw trace must cover two or more relocations with identical public API
  sets, variant families, source hashes, and **same-input corpus digest**.
- Every variant's original code SHA must match the local current source.
- A newly assembled linked PRG at the requested **qualified** code/I/O/ZP/
  scratch placement must have **exactly** the originally measured PRG SHA256,
  selected exports, physical source count, main RAM and ZP sizes.
- A plan outside its RAM/ZP/peak limits, with a moved zero-page/scratch
  layout, or with any hash drift is rejected rather than advertised as
  performance-qualified.

**Scope:** Initial report generation exercises all eight signed/unsigned
32×32 full64 and table/tableless ISQRT16 plans at two relocations; the
exporter's evidence and selection structure can support additional
operations and frame scenarios once they are source/ABI/frame qualified.
New app call traces or memory maps require **new evidence**, not reusing
the synthetic 150-call/24-frame sample's numbers.

The math cycle envelope is produced by a Mini6502 complete public call and
caller JSR trace. It **does not** account for actual raster bus contention,
VIC-II badlines, SID player/IRQ work, REU DMA, application's other
instructions, reentrant invocation, or physical PAL/NTSC frame feasibility.
No historical V1–V5 binaries, optimized kernels, REU services or other
Pareto alternatives are removed or modified.
