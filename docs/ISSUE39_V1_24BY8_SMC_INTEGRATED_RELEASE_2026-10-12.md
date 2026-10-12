# Issue #39: V1 68-byte RAM self-modifying shared 24/8 DIV/MOD release

12 October 2026. Replaces ONLY the previous 61-byte short-divisor V1
producer with a 68-byte writable-RAM-only SMC kernel within the original
84-byte fixed code island. Modifies the immediate operands of CMP and SBC.
The existing library is sequential/non-reentrant; this routine MUST execute
from writable RAM, and cannot be invoked concurrently or from ROM.
The source-only previous 61-byte fallback remains separately available.

Prior V1 binary SHA256: cdc2ca502d664055f896d7ad1601e8dd994b61be33e24bde3e25fc0dcbee1cdd; source-built current: d6e013740a8c1ac8f35fa895b69afb8bf6226cde99f491a470b4518a7c6dfa9a.
V2–V5 binaries remain byte-identical. API and zero-page/stack unchanged.
Native VICE full resident comparison 384 public calls with zero correctness,
flags, input preservation or stack errors; no native cycle timing is claimed.
Paired 48,388 old/new public calls and 6,344 independently relocatable
standalone calls pass. 822,050 unsigned, 364,533 signed multi-profile calls
and 136,335 common same-input profile calls; reference/alternate builds pass.

| API | 61-byte before | 68-byte after |
|---|---:|---:|
| UDIV24 | 166.190196 | 165.228277 |
| UMOD24 | 234.433355 | 231.489375 |
| 24/8 special stress | 976.350000 | 927.934314 |

Standalone SMC: routines/standalone_lab/portable/div_u24_by_u8_selfmod.asm
Non-SMC historical portable source: tools/candidates/issue39_v1_24by8_accumulator.asm
Native evidence: validation/review/ISSUE39_V1_24BY8_68SMC_FULL_RESIDENT_NATIVE_VICE.json
Issue #39 remains open; other DIV/MOD widths and profiles still unaudited.
