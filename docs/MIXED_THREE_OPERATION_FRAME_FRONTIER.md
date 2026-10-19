# Project-level frame parity across three stock C64 operations

This research expands the [two-operation multiplication frontier](MUL32_JOINT_SHARED_VS_SEPARATE.md)
without modifying any arithmetic kernel or historical V1–V5 profile.

The independently linked test now mixes three public entrypoints:

- `MATH_UMUL32` (unsigned 32×32 → full 64-bit)
- `MATH_SMUL32` (signed 32×32 → full 64-bit)
- `MATH_ISQRT16` (unsigned integer square root)

It builds **eight actual source configurations**: independent compact,
unified-375, independent FAST31 or shared FAST31 multiplication, crossed
with the original square-table or the tableless radix-4 ISQRT16. This
is a true three-operation linked-image comparison: occupied code/tables,
alignment, RAM, zero page and shared producer count come from each
build manifest, not from adding standalone source estimates.

Each candidate runs the *same* deterministic 150 complete-public-call,
24-synthetic-frame input/caller-state corpus at both `$8000/$C000`
and `$7123/$C040`. Tests check the exact unsigned/signed full result,
input preservation, signed corner values, ISQRT16 output and unchanged N,
carry and stack. Per-operation and full-frame cycle measurements come
from a linked Mini6502 call-through-RTS trace, with the scorer adding
six caller-JSR cycles per call.

`tools/mixed_frame_frontier.py` is a generic, **offline** plan evaluator.
It fails closed on missing operations, unequal input-corpus checksums,
source/variant changes between relocations, missing call coverage, malformed
PRG/source provenance, or insufficient RAM/ZP/peak-frame headroom. It
computes the nondominated frontier across memory, zero page, peak/p95
math-only frame cycles and total cycles. It considers *complete linked
plans*: no automatic extrapolation from isolated routine averages.

Run:

```sh
python3 -m unittest discover -s tools -p 'test_mixed_frame_frontier.py' -v
python3 -m unittest discover -s tools -p 'test_mixed3_frame_parity.py' -v
python3 tools/mixed3_frame_parity.py --out build/mixed3_frame_parity.json
python3 tools/mixed_frame_frontier.py \
  --in-report build/mixed3_frame_parity.json \
  --ram-budget 12000 --zp-budget 31 \
  --out build/mixed3_frame_frontier.json
```

These are **synthetic 6510 CPU-model arithmetic timings**, not actual PAL
frame timing. They exclude VIC-II bus stealing/badlines, IRQ/NMI, SID,
sprite DMA, REU transfers, application code and init amortization.
The workflow is *research qualification*, not an automatic performance
claim for all 56 operations, a production installer objective or a
V1–V5 hardware replacement. Preserve the existing historical sources,
reference PRGs, REUs and compact Pareto alternatives.

Future work: reuse this generic offline frontier on additional
certified mixed workloads, then implement a bounded/trace-certified
peak-frame constraint in the production operation-first selector,
without weakening the existing source/ABI and resource checks.
