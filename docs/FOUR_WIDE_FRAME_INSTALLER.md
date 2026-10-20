# Replayed mixed signed and unsigned four-API 32-bit DIV/MOD installer

The opt-in `math_builder.py --objective frame` can now recognize a
**fourth explicitly registered deterministic linked-image workload**:
public unsigned and signed full 32/32 quotient and remainder operations
in one complete project source image.

The four plans independently choose restoring 0-ZP or V2 hybrid 12-ZP
source families for unsigned and signed Q/R calls. The physical
zero-page scratch allocation may be **reused sequentially across
unrelated sign-domain producers**, rather than incorrectly added as
24 bytes; nonreentrant use is required.

```sh
mkdir -p build/mixed-four-frame
python3 tools/mixed_four_divmod_frame_parity.py --out build/mixed-four-frame/frames.json
python3 tools/frame_evidence_replay.py --report build/mixed-four-frame/frames.json
python3 tools/math_builder.py \
  --config examples/operation-first-four-wide-frame.json \
  --objective frame --frame-report build/mixed-four-frame/frames.json \
  --build --out build/mixed-four-frame/selected/selection_manifest.json
```

The standard builder reexecutes all four linked candidates on identical
150-call/24-synthetic-frame full public input histories at two qualified
code/I/O/ZP relocations before accepting timing evidence. It checks
Q32/R32/carry, signed quotient truncation, input preservation, stack,
source hashes, PRG SHA256 and actual physical RAM/ZP. The best eligible
**whole-image** measured peak is selected subject to explicit resource
limits; altered cycle peaks or unsupported histories fail closed.

The other three registered workloads remain available independently.
These *do not* qualify arbitrary 56-operation mixed projects.
Measurements count model 6510 math instructions plus caller JSR; they
do not model actual PAL VIC-II bus steals, badline interference,
IRQ/SID work, REU DMA or full application frame budget. Legacy
V1–V5 and independent V3/V4 REU compatibility remain unchanged.
