# UMUL32 + SMUL32: measured source-sharing versus independent FAST31

Two-operation projects should not choose their fastest UMUL32 and SMUL32
kernels independently and simply add each one's standalone code and table
budgets: both operations can share **one** historical FAST31 full64 source,
its four aligned quarter-square table slots and 31-byte ZP scratch pool.

The paired measurement `tools/mul32_joint_frame_parity.py` builds exactly
four *two-operation* plans at each of two code/I/O origins:

| Plan | Source images | Zero-page profile |
|---|---:|---|
| Compact unsigned + compact signed | 2 | 0 ZP |
| Six-entry unified compact 375-byte code | 1 | 0 ZP |
| Standalone FAST31 unsigned + standalone FAST31 signed | 2 | 31 ZP |
| Shared FAST31 source with both public exports | 1 | 31 ZP |

The 150-call 24-frame synthetic sequence alternates unsigned and signed
32×32→64 public entrypoints, includes signed-negative corner values, and
holds complete input operands and caller A/X/Y/C/D identical across all
four *fully independently linked* source choices. Every call verifies
signed/unsigned full64 output, preserved X/Y and C=0, and balanced
hardware stack. The score compares same-call peak/p95/total math cycles,
slower individual calls, exact producer count and actual alignment-aware
RAM/ZP use.

This is *not* a physical PAL frame measurement. A shared source is not
automatically the single fastest signed call; its advantage is the
project-level RAM/table sharing when both public calls are linked. Keep
compact zero-ZP choices for projects without writable RAM or 31 free ZP
bytes. Historical V1–V5 binaries and external REU/Turbo/QS16 APIs are
unmodified and remain separately protected.

```sh
python3 -m unittest discover -s tools -p 'test_mul32_joint_frame_parity.py' -v
python3 tools/mul32_joint_frame_parity.py --out build/mul32_joint_source_parity.json
```
