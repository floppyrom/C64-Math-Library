# Replay-registered sixteen-choice seven-API source selection

The separate source-linked 16-way experiment is registered as an **opt-in**
synthetic arithmetic-frame evidence producer for the operation-first
`math_builder.py --objective frame` CLI. This does **not** replace the original
four-choice registered workload; both remain distinct named producer bases.

Each of the sixteen combinations links UMUL32, SMUL32, ISQRT16 and both
signed/unsigned 32/32 DIV/MOD shared families. A full **150-call,
24-synthetic-frame** run at each of two fixed RAM/ZP placements is
reexecuted on every invocation of the production frame CLI. The complete
source map, operand/carry semantics, exact binary hash, resource usage,
frame order and peak/p95/total cycles must all agree before a PRG is emitted.

The particularly useful new alternatives are:

| Peak objective, 16KB RAM | ZP | Total linked RAM | Worst-placement peak CPU math cycles |
| --- | ---: | ---: | ---: |
| Compact with radix4 root (original baseline) | 0 | 1,666 B | 63,581 |
| Compact with square-table root (new) | 0 | 2,350 B | 59,933 |
| Compact with square-table root and V2 DIV/MOD (new) | 12 | 6,737 B | 40,109 |
| Fast-everywhere (original baseline) | 31 | 8,992 B | 16,172 |

The **zero-ZP and 12-ZP** new winners are also rebuilt through the actual
production installer at the independently measured `$4123/$C040/$70`
placement. Both *exact* binary images receive independent native
x64sc r46284 public-ABI oracles for **96 calls per export**, or
**1,344 native calls** in total. The separate registration never changes
the original 4-choice source history or its compact-only RAM objective.

Run (from the repository root):

```sh
python3 tools/mixed_seven_cross_pareto.py --out build/seven-cross/frames.json
python3 -m unittest discover -s tools -p 'test_seven_cross_frame_installer.py' -v
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 tools/native_seven_frame_installer.py --cross
```

The CLI accepts only reports matching the deterministic producer reexecuted
at both original placements. It rejects altered cycle data, operand history,
sources, binary hashes, operations, choice sets and relocations. These
certificates concern **synthetic CPU-model math cycles and native correctness**.
They are *not* physical PAL timing, VIC-II badline, IRQ, SID, REU DMA, real
application busiest-frame or arbitrary 56-operation trace qualification.
All V1–V5 profile assets and V3/V4 REU images remain intact.
