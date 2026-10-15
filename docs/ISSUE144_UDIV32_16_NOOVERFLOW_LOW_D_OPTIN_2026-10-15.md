# Issue #144 B — UDIV32/16 no-overflow low-divisor optional producer

**15 October 2026. Source-only, V2/V3/V4 reference layouts. This is not an installed/default math routine.** Do not claim a general all-divisor Pareto improvement or universal 5% speedup.

## Core observation

For nonzero D<$8000 and already-reduced R<D, `2R+nextbit ≤ 2(D−1)+1 ≤ $FFFD`. The 17th-bit carry in every low-word restoring step is mathematically impossible. Remove that `BCS FORCE` branch and the duplicated forced-subtract lane **once the divisor is known to be in range**. This is not a trick that is safe for D≥$8000.

On **12,976 matching N32, 1≤D<$8000 pairs**, the independently assembled 16-step low quotient/remainder tail passed **all** oracle tests and saved an average **56.773 cycles** (533.666→476.893), with **zero regressions** (33–81 saved). The fragment shrank **684→444 bytes** at $2070. The high-word quotient/remainder was mathematically seeded in that *isolated tail test*, so those numbers do **not** describe the full public call.

## Actual complete public-call option

Files:
- `optional/issue144_u3216_nooverflow_lowdiv/optin_v2_v3_v4_reference.asm`: machine-assembled exact source; `OPT_U3216_LOW = $0800`; **511 bytes, $0800–$09FE**, which belongs to the *caller's* memory map.
- `tools/issue144_u3216_nooverflow_public_optional_screen.py`: constructs the same bytes, asserts absolute byte-for-byte equality to the standalone .asm, and runs public input/output and cycle comparisons.
- `tools/issue144_u3216_nooverflow_lowd_tail_screen.py`: independent isolated 6510 tail proof.
- `tools/native_issue144_u3216_nooverflow_optional.py`: actual VICE remote-monitor comparisons of the unchanged resident and the explicit source-only option.

**Dispatch:** if `$0100≤D≤$7FFF`, share the existing certified V2–V4 16/16 high-word divider at $420C then use the 16-step no-overflow tail. If `D=0`, `D<$0100` or `D≥$8000`, `JMP $31B0` to the **existing** full public 32/16 producer. This preserves complete Q32/R16/C, input N/D and SP across all D16, with no extra normal zero page. Both `MATH_UDIV32_16` and `MATH_UMOD32_16` produce Q and R, and the optional entry is callable for either use.

### Actual complete public-entry performance, 4,261 paired calls per API/profile

| Class | UDIV32_16 saved, mean | UMOD32_16 saved, mean |
|---|---:|---:|
| **Eligible D=$0100–$7FFF** (2,345 calls) | **59.725 cycles** | **62.725 cycles** |
| Identically drawn uniform N32/D16 segment (1,536 calls) | **24.324** | **27.324** |
| All 4,261 mixed test pairs | **28.064** | **31.064** |
| D≥$8000 fallback | **−11** | **−8** |
| D<$0100 fallback, including D=0 | **−10** | **−7** |

Mean gains on the eligible subset are **strictly positive** in the test: UDIV smallest 36, largest 85 cycles. The true whole-corpus p5 is **−11/−8**, proving a material fallback regression and **disqualifying it from unconditional default promotion** under Issue #144's p95/worst contract. All three V2/V3/V4 have the same paired CPU-model cycle vectors. Results include the routine entry and RTS; they exclude the caller's JSR and physical VIC/REU contention. The test corpus fingerprint is `405d0a810398fed2d47a2def2650d2e4c2c317c31bbfe3a1966035bbb3d46f76`.

### Native real x64sc proof

The pinned VICE 3.10 r46274 headless machine executed **288 baseline/candidate calls** (24 pairs × 2 implementations × 2 APIs × V2/V3/V4). Output Q/R, carry, N/D, and stack depth matched between original and optional code, including D=0/D8/eligible/wide divisor cases. Native CPU cycle timing was **not** measured; the above cycles come from the repository's placed NMOS 6502 simulator.

## Use constraints

This is a **source-only opt-in**, not a modified resident: explicitly assemble/load `optin_v2_v3_v4_reference.asm` after the normal V2/V3/V4 reference-image MATH_INIT, prove that all of **$0800–$09FE** is application-owned writable RAM (it overlaps BASIC program memory), and `JSR $0800` instead of the ordinary full producer. The hardcoded fixed reference addresses **$31B0/$420C**, normal math I/O at $C010 and ZP $10–$19 are not valid for every relocation map. It shares the resident's normal scratch and is **not IRQ/NMI/mixed-call reentrant**, so do not enable concurrent math calls.

**Not certified** on V1/V5, relocated/alternate source maps, in-place public-JMP redirection, any application with occupied $0800 memory, or native cycle/VIC contention. Five default resident binaries, both REU images, normal public entries, performance leaderboards and default builder are unchanged. No private OptiSearch source is included.

**Decision:** publish only as a separately accessible research specialist. Continue searching for an unrestricted **ordinary-call** 32/16 producer improvement without a −8/−11 cycle fallback penalty. Issue #144 B remains OPEN.
