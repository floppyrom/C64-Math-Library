# Issue #144 B — all-domain dual 32/16 quotient tail, direct divisor dispatch

16 October 2026 · **Source-only research, not a normal-resident/default release**

## Mechanism

The V2/V3/V4 public `MATH_UDIV32_16` and `MATH_UMOD32_16` first examine the high divisor byte. In the research candidate, the existing entry classifier sends `$0100 <= D16 <= $7FFF` to a dedicated no-17th-bit-overflow 16-step low-word producer; `$8000 <= D16 <= $FFFF` retains the canonical shared-take unrolled producer. `D8` and `D=0` continue through their original arithmetic and zero-divisor implementations. The high-divisor branch incurs no additional dispatch instruction, although relocation/page-alignment differences sometimes add one modeled cycle. Low-divisor calls pay a short direct dispatcher overhead but eliminate the overflow checks within their 16 quotient steps.

The independent low-divisor fragment uses **461 executable bytes in caller-owned $0800 RAM**. It does **not** allocate additional zero-page, data tables or REU banks. **This application-RAM dependency is not safe as a library-wide default.** The implementation is public-source independent research; private OptiSearch files and implementation details are excluded.

## Same-input assembled 6502 / public ABI comparison

[Reproduce the complete CPU-model test](../tools/issue144_u3216_dualtail_direct_dispatch_screen.py): 2,304 deterministic `N32,D16` vectors (corpus SHA256 `cbe48c6d091a03c7c6dafee47406a96b7e1b7ef093516c99fccd8d0f657f8a3c`), each executed against current canonical-source original and candidate for both public APIs, three profiles and two relocated source layouts. **27,648 matched public-call pairs / 55,296 ordinary calls**, all Q32/R16/C and N32/D16 preserved with balanced stack. Initial [native/model CI run #38823827633](https://github.com/floppyrom/C64-Math-Library/actions/runs/38823827633) passed.

| Domain | Pairs per API/profile/layout | Mean modeled cycles saved | Worst saved |
|---|---:|---:|---:|
| Nonzero `$0100..$7FFF` | 970 | **27.02990** | +26 |
| High `$8000..$FFFF` | 981 | **−0.48522** | −1 |
| D8 `$0001..$00FF` | 305 | **−1.96393** | −2 |
| D=0 | 48 | **−2** | −2 |
| Complete mixed corpus | 2,304 | **10.87153** | −2 |

Across each full mixed corpus, 831 cases are slower and 501 are equal; the remaining 972 improve. Overall p05 saved is −2 cycles, p95 +28. This is a real positive mixed-corpus CPU-model result, **not** proof of a 5% ordinary full-width public speedup.

## Native x64sc and geometry gates

[Native qualification](../tools/native_issue144_u3216_dualtail_direct_dispatch.py) ran **576 real original/candidate public calls**: V2/V3/V4, both relocated layouts, both DIV/MOD entries, with D=0, D8, lowD and highD cases. All quotient/remainder/carry, preserved numerator/divisor and stack snapshots matched the independent oracle. No native processor-status differences were seen on the 24 native vectors per group. The test uses checksum-pinned x64sc 3.10+r46274 with deterministic 6510 RAM state. Real VIC/REU bus timing was **not** measured.

[Normal-resident geometry test](../tools/issue144_u3216_dualtail_resident_geometry.py) found **zero unoccupied contiguous bytes** in the current source-owned `U3216_MAIN_END` to `U3216_D8_BASE` gap on **all six V2–V4 source layouts**. The source maps fill this region. Consequently, the extra 461-byte tail cannot simply be placed there. Unowned seemingly blank C64 RAM elsewhere is **not** free library code space.

## Decision

**Do not merge the candidate into production, replace shipped reference PRGs/REUs, update production `PERFORMANCE.md`, or check off issue #144 B.** The architecture is better than a public-call wrapper because the high-divisor fallback penalty is at most one modeled cycle and D8/D0 just two, but the optional code does not meet the normal-resident ownership test. Before a release, prove a size-compatible private placement or an explicit builder-selected code owner; then run all-sign signed DIV/MOD, full 56-entry mixed ABI, interrupt/reentrancy tests, V5 integration, source-build maps, actual native VICE, reproducible checksums and library CI. These gates remain open.

[Reproducible research workflow](../.github/workflows/issue144-b-u3216-dualtail-directdispatch.yml).

## Signed 32/16 DIV/MOD qualification (16 October 2026)

The V2/V3/V4 native signed `SDIV32_16` and `SMOD32_16` entry points use the unsigned `U3216_ENTRY` magnitude producer. Changing its low-divisor branch must therefore preserve every sign quadrant and both signed public results, not just unsigned division.

The [separate same-input signed regression](../tools/issue144_dualtail_signed_public_regression.py) passed **23,604 baseline/candidate public-call pairs** (1,967 boundary, sign-quadrant, random, signed-overflow and divide-by-zero operands × 2 signed APIs × 3 profiles × 2 maps). Full Q32/R16, C, preserved N32/D16, stack and CPU status were identical. The recorded sign-enriched corpus mean saving was **19.991865785460092 modeled cycles/call**, p05 = −2 saved cycles, best +28 and worst −2, no processor-status differences.

The [independent native x64sc harness](../tools/native_issue144_dualtail_signed32_public.py) passed **576 pinned VICE original/candidate signed public calls**, 24 input vectors per API/profile/map. Exact quotient, remainder, carry, N/D, SP and captured accumulator/X/Y/processor status matched; zero volatile register/status differences. [Signed native/model CI evidence](https://github.com/floppyrom/C64-Math-Library/actions/runs/38849380207). The native harness deliberately uses 24-byte output columns to keep its capture buffer below $0800; the original 64-byte columns overlapped the optional executable at $0800 and invalidated the first native trial.

This extends **functional qualification of the optional 461-byte caller-owned program** only. It does not establish a normal-resident 461-byte code owner, V5 extension, cross-API interrupt/reentrancy safety, physical VIC/REU bus timing or any production-default speedup. The immutable five resident PRGs, two REUs and PERFORMANCE.md are not altered.
