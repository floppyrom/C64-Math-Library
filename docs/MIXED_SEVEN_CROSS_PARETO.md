# All sixteen seven-operation source-linked candidate combinations

The original seven-API source-linked `frame` benchmark qualifies four
cross-domain plan choices (all compact, fast MUL only, fast DIV only,
all fast). These four are retained unchanged and continue to be
**the only** choices in the corresponding replay-registered production
`math_builder.py --objective frame` workload.

A separate offline research sweep now tests **all sixteen** independent
two-way choices in one complete seven-operation linked C64 image:

- Unsigned and signed full64 32×32 multiplication: shared FAST31 or
  compact 0-ZP sources
- ISQRT16: square-table or tableless radix-4 source
- Shared unsigned 32/32 DIV/MOD: V2 12-ZP hybrid or aligned 0-ZP
- Shared signed 32/32 DIV/MOD: V2 12-ZP hybrid or portable 0-ZP

Instead of summing standalone mean cycles, each of 16 complete
source-pinned link plans executes an **identical 150-public-call,
24-synthetic-frame** workload at **both** measured RAM relocations.
Tests verify full product, root, quotient, remainder and carry results,
source operand preservation, stack balance, code/source hashes,
physical sharing, linked executable RAM and zero-page use, and the
worst-placement peak/p95/total arithmetic math cycles.

```sh
python3 -m unittest discover -s tools -p 'test_mixed_seven_cross_pareto.py' -v
python3 tools/mixed_seven_cross_pareto.py --out build/seven-cross/frames.json
python3 tools/mixed_frame_frontier.py \
  --in-report build/seven-cross/frames.json \
  --ram-budget 16000 --zp-budget 64 \
  --out build/seven-cross/frontier.json
```

This research can expose intermediate Pareto alternatives such as
table-root with compact MUL, fast unsigned DIV with portable signed
DIV, or FAST31 multiplication while keeping unsigned DIV at zero ZP.
It does **not** assume a combination is faster before complete
matching-input measurement. The original four candidate IDs, source
variants and benchmark history remain exactly reproducible.

**The exact sixteen-choice producer is now separately replay-registered**
for opt-in `math_builder.py --objective frame` projects. Reexecuted
source-linked evidence is required at both registered placements before
publishing a selected PRG. Its zero-ZP square-table and 12-ZP mixed
performance alternatives additionally undergo pinned native x64sc
correctness checks. The original four registered candidate IDs and
source reports remain available and unchanged. See
[production replay and independent native qualification](SEVEN_CROSS_FRAME_PRODUCTION.md).
This is math-only CPU-model arithmetic time, **not** real PAL
VIC-II/badline/IRQ/SID/REU DMA or application busiest-frame duration.
Historical profile PRGs and V3/V4 REU services remain preserved.
