# Replayed 32-bit DIV/MOD frame selection through the normal installer

The normal operation-first `frame` objective now recognizes a *second*
deterministic, source-authenticated complete-project workload.

The initial producer compares signed/unsigned full-64-bit multiplication
and ISQRT16. The new producer compares full-public
`MATH_UDIV32_32` and `MATH_UMOD32_32` Q32/R32/C calls using
zero-page-free, source-shared, V2 low-divisor hybrid and mixed variants
across two measured memory placements.

```sh
mkdir -p build/u3232-frame
python3 tools/u3232_joint_frame_parity.py \
  --out build/u3232-frame/frames.json
python3 tools/math_builder.py \
  --objective frame \
  --config examples/operation-first-u3232-frame.json \
  --frame-report build/u3232-frame/frames.json \
  --build --out build/u3232-frame/built/selection_manifest.json
```

Before selecting a source combination, the installer re-links and
re-executes **all** candidates at **both** reported relocations on an
identical 150-call / 24-synthetic-frame full public-call corpus. It
rejects altered peak/p95/total arithmetic cycles, changed quotient or
remainder, divisor-zero carry, operand clobber, source and PRG hashes,
physical RAM/ZP footprint, unmeasured memory maps and unregistered
producer IDs.

The selected **whole-image** peak frame math-cycle and RAM/ZP limits
are compared using complete linked project resources, not sums of
standalone kernels' average speed. The resulting normal
`math_selective.prg` retains exact source pins and an independent
provenance manifest. Existing `balanced`, `speed`, `size` and `zp`
objectives are unchanged.

**This does not certify real PAL worst-frame behavior.**
CPU-model entry-through-RTS cycles plus caller JSR exclude VIC-II
memory stealing, interrupts, SID, REU DMA, init costs and host code.
Other stock-C64 arithmetic APIs need separately qualified replay
producers before this mode can accept their frame trace.
Legacy V1–V5 PRGs and V3/V4 REU services are preserved.
