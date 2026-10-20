# Replay-verified signed 32/32 DIV/MOD project selection

The operation-first `--objective frame` installer now has a **third,
explicitly registered deterministic workload**: public
`MATH_SDIV32_32` plus `MATH_SMOD32_32`.

The two linked candidates share a source that produces both quotient
and remainder: zero-ZP signed restoring and V2 signed hybrid with
12 ZP. Their RAM and peak synthetic math-frame costs are measured
for an identical **150-call, 24-frame** signed input history at two
independent code/I/O/ZP relocations. Both procedures check correct
signed truncation toward zero, numerator-signed remainder, carry
on divisor zero, caller operands and stack, as well as exact output
PRG and source hashes.

```sh
mkdir -p build/s3232-frame
python3 tools/s3232_joint_frame_parity.py --out build/s3232-frame/frames.json
python3 tools/frame_evidence_replay.py --report build/s3232-frame/frames.json
python3 tools/math_builder.py \
  --objective frame \
  --config examples/operation-first-s3232-frame.json \
  --frame-report build/s3232-frame/frames.json \
  --build --out build/s3232-frame/selected/selection_manifest.json
```

The CLI replays *every* linked candidate on both measured origins
before accepting the report's timing fields. If the evidence cannot be
reproduced, the RAM/ZP cap excludes all plans, the project APIs differ
or the resulting PRG SHA-256 changes, the build fails closed.

Unlike per-operation `speed` (matched-average) selection, `frame`
selects only among *already measured linked whole-image* configurations.
The three registered producers now cover full64 unsigned/signed MUL+
ISQRT16, unsigned 32/32 DIV/MOD, and signed 32/32 DIV/MOD. They **do
not** yet authorize arbitrary combinations of all 56 operations.

These are CPU-model public arithmetic plus caller JSR cycles, **not**
physical PAL VIC-II/IRQ/SID/REU DMA or application-level frame-timing
claims. Previously shipped V1–V5 reference images and separate
V3/V4 REU compatibility bundles are unchanged.
