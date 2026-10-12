# Issue #39: 68-byte RAM self-modifying 24÷8 specialist vs the released 61-byte core

**2026-10-12 — SCREENING-ONLY, not a resident replacement.** Rebuilt the
merged V1 PR #81 source-backed resident at SHA256 cdc2ca502d664055f896d7ad1601e8dd994b61be33e24bde3e25fc0dcbee1cdd and compared an
in-memory copy replacing *only* the original $1D00 84-byte code island
with the optional 68-byte self-modifying candidate. The shipped 61-byte
non-self-modifying source, every profile PRG and public ABI remain unchanged.

The specialist caches D0 in two instruction operands (\`CMP #imm\` and
\`SBC #imm\`) once per call. Its loop then avoids repeated absolute D0 reads.
This is attractive for a C64 game/demo that controls **writable executable
RAM**, but **unsafe from ROM, non-reentrant, and dependent on caller ownership**.
Its precondition is exactly N2>0, D1=D2=0 and 0<D0<256; this code alone is
**not** a generic 24÷24 division/modulo routine and does not guard D=0.

| Full public-entry corpus | Released 61-byte code | RAM-only 68-byte | Cases |
|---|---:|---:|---:|
| UDIV24 canonical | 166.190196 | 165.228277 | 4753 |
| UMOD24 canonical | 234.433355 | 231.489375 | 1553 |
| 24/8 N2>0 stress (each API) | 976.350000 | 927.934314 | 4,080 |

The paired research screen ran **48,388 full public-entry 6502 executions**,
checking Q/R/C, unchanged N/D, Q3/R3 sentinels and stack, with **no incorrect
or slower comparisons**, including all seven fixed workload classes and
controls for wide divisors and N2=0. The narrow-divisor stress improves by
48.415686 cycles per input in that specific distribution. These are
**emulated CPU cycle counts**, not VIC-bus-inclusive native measurements.
Earlier separate native x64sc verification covered 128 *isolated core calls*;
no full-resident native validation or native cycle timing of the 68-byte
self-modifying alternative is claimed.

**Independently liftable source:** \`routines/standalone_lab/portable/div_u24_by_u8_selfmod.asm\`.
Its \`KERNEL_CODE\`, \`MATH_N\`, \`MATH_D\`, \`MATH_Q\`, \`MATH_R\` origins
are source constants you can change to disjoint writable RAM. The portable
proof checks **6,344 complete calls at $8000 and unaligned $830F**, including
two self-patched instruction operands and absence of other code writes, with
no normal ZP and no additional stack frame. The 68-byte routine is an optional
specialist; no 24/24 caller can invoke it unconditionally.

**Source/evidence:** \`tools/candidates/issue39_v1_24by8_accumulator_selfmod.asm\`,
\`tools/screen_issue39_v1_24by8_accumulator_selfmod.py\`,
\`tools/verify_issue39_v1_24by8_accumulator_selfmod_portable.py\`,
\`validation/review/ISSUE39_V1_24BY8_SMC_VS_61_PAIRED.json\`, and \`validation/review/ISSUE39_V1_24BY8_SMC_PORTABLE.json\`.

**Decision:** preserve BOTH the shipping 61-byte non-SMC routine and
liftable 68-byte SMC alternative. Do not call this a universal replacement,
misrepresent the number of code bytes, or close the unsigned DIV/MOD stage
of issue #39. Attribution: a manual C64ML optimization of the shared
short-divisor architecture from Repose-derived code; does not redistribute
private OptiSearch software.
