# Complete technical assessment — C64 Math API Game-Math FINAL
> **V5 addendum:** This assessment originally covered V1–V4. The repository now also ships V5 Hybrid Low-ZP, which preserves the same stable API (now 54 entries, with the 2026-09-25 seek DDA addition; see `SEEK_DDA.md`) and V1 31-byte normal ZP footprint while importing a certified V2 subset. Its independent validation and performance evidence are in `HYBRID_PROFILE.md` and `../validation/hybrid/`.
> **Custom Pareto addendum:** Stock-C64 users can now generate a resource-budgeted profile instead of choosing only a fixed V1/V2/V5 point. The selector optimizes over certified dependency-compatible packs using total ZP, exact private-RAM and optional workload weights, with no runtime dispatch. See `PARETO_BUILDER.md` and `../validation/pareto/`.


## Result

The collection is now a coherent signed+unsigned integer and game/fixed-point math library rather than simply a wider integer API. Nineteen additions were retained because they address recurring hot paths in games, demos, raycasters, 3D transforms and future ports; trivial operations that should be inlined remain outside the library.

All four reviewed reference binaries pass the current source-build/relocation regression. The release also carries the prior exhaustive validation evidence for all bytes that remain unchanged, plus new dedicated validation for the optimized ISQRT32 kernel.

## 32/32 division

The magnitude core is tiered: zero/order/equality fast exits, reuse of the selected 32/16 path when the divisor fits 16 bits, and a 16-quotient-bit path for divisors ≥65536. Signed division normalizes magnitudes and repairs signs around the private core; it is not a public unsigned-wrapper implementation.

## Fixed-point operations

Multiply-shift entries reuse the selected optimized multiplication producer and extract the byte-aligned result. Shifted division reshapes the numerator and enters the profile's optimized 32/16 divider instead of maintaining a slower duplicate divider.

## Reciprocal

The final exact routine uses quotient-special thresholds q=1..15, directly covering 93.75% of the 16-bit divisor space, then falls back to selected UDIV24 (V1/V2) or exact REU lookup (V3/V4). Exhaustive means are **126.175720, 119.577560, 66.233795, 66.233795 cycles** for V1–V4.

## Trig and square root

ATAN2 is tiered. V1 uses the optimized compact 512-byte signed-log design. V2/V3 use two biased log pages and two reflected angle pages (1024 bytes total), combining the logs with a carry-clearing sum and an XOR half-turn; V4 uses an exact 64 KiB REU plane. ISQRT16 is table-search on V1–V3 and exact REU lookup on V4. ISQRT32 now uses a faster independently derived hybrid. For `N=(H<<16)+L`, `r=floor(sqrt(H))` is exactly the high byte of `floor(sqrt(N))`; the routine therefore reuses the selected exact ISQRT16 path for `H`, forms the exact residual `H-r^2`, and executes only the eight remaining base-4 refinement steps over `L`. It preserves the public radicand and returns `C=0`. On the same 4,130-case corpus as the previous table the means are **1378.900969 / 1198.619613 / 1197.859322 / 1046.622518 cycles** for V1–V4. V4 restores two 256-byte resident square planes (`$9800-$99FF`) to minimize residual-setup latency.

## Distance

The accurate distance kernel's coefficients 243/107 were chosen by exhaustive search over all 65,536 byte coefficient pairs for the stated rounded linear form. It cuts full-plane mean absolute Euclidean error from 8.47 pixels (fast form) to 2.22.

## SMUL16 correction discovered during this work

The September 5 V2–V4 package stored 116 zero bytes where the practical native SMUL16 executable-ZP image should have been, and `MATH_INIT` did not install the core. The image was reconstructed from the original independently validated source; the same reconstruction reproduced the existing 60-byte signed tail byte-for-byte. The final core is stored at `$CC00-$CC73` and installed into `$80-$F3` by `MATH_INIT`. An earlier `$CA00` working placement was rejected after integration growth created a V2/V3 collision; the independent byte-range audit now explicitly protects against regression.

## Public benchmark means

| Routine | V1 | V2 | V3 | V4 |
|---|---:|---:|---:|---:|
| UDIV32_32 | 434.110992 | 401.972551 | 401.972551 | 401.972551 |
| SDIV32_32 | 586.253917 | 541.582885 | 541.582885 | 541.582885 |
| UMUL16_SHR8 | 424.116274 | 391.840802 | 380.000000 | 358.634906 |
| SMUL16_SHR8 | 465.078538 | 294.068632 | 294.068632 | 294.068632 |
| UMUL32_SHR16 | 836.513583 | 817.513583 | 817.513583 | 817.513583 |
| SMUL32_SHR16 | 896.087739 | 874.087739 | 874.087739 | 874.087739 |
| UDIV16_SHL8 | 855.681132 | 762.606368 | 762.606368 | 762.606368 |
| SDIV16_SHL8 | 971.872406 | 872.964151 | 872.964151 | 872.964151 |
| URECIP16_Q16 | 126.175720 | 119.577560 | 66.233795 | 66.233795 |
| SIN8 | 23.000000 | 23.000000 | 23.000000 | 23.000000 |
| COS8 | 29.000000 | 23.000000 | 23.000000 | 23.000000 |
| SINCOS8 | 39.000000 | 31.000000 | 31.000000 | 31.000000 |
| ATAN2_8 | **48.447189** | **44.962814** | **44.962814** | **48.000000** |
| ISQRT16 | 219.740570 | 205.760590 | 204.992523 | 54.000000 |
| ISQRT32 | 1378.900969 | 1198.619613 | 1197.859322 | 1046.622518 |
| DIST8_FAST | 86.085602 | 79.570038 | 79.070038 | 79.070038 |
| DIST8_ACCURATE | 92.085602 | 85.570038 | 85.070038 | 85.070038 |

See `PERFORMANCE_GAME_MATH_FINAL.csv` for min/max and case counts. The ISQRT32 row uses the same 4,130-case deterministic corpus as the preceding reviewed release for a direct speed comparison; the optimized kernel additionally passes a separate 5,097-case boundary/perfect-square/random validation. Exhaustive means are exact only where the validation document says the domain is exhaustive.

## Resource/ownership rules

V1 consumes no additional ZP for game math and uses `$C040-$C057` RAM scratch. V2–V4 use `$53-$6A` game ZP, adjacent to native signed-DIV scratch `$3E-$52`; practical SMUL16 executes from `$80-$F3`. V3/V4 Turbo overlays own overlapping ZP ranges, so normal game-math calls are prohibited between Turbo BEGIN and END.

Game tables occupy selected pages in the resident table region. V1 uses `$9600/$9700` for its compact log/angle pages. V2/V3 use `$9600/$9700/$6E00/$6F00` for sum-fast LOGX/LOGY/QPOS/QNEG; V5 maps those four pages to V1-free `$6D00-$70FF`. V4 also initializes `$9800-$99FF` for the ISQRT32 square planes. Game code is at `$C100+` with the fast ISQRT32 body at `$CB40+`, and the SMUL installer image is `$CC00-$CC73` on V2–V4. V3 reserves two 64 KiB REU planes for reciprocal; V4 additionally reserves exact atan2 and ISQRT16 banks.

## Source-level relocation review

The reviewed Git/source release no longer relies on post-build binary relocation. `relocatable_source/<profile>/math_relocatable.asm` is the canonical assembly input and `math_config.inc` supplies the memory/REU map at assembly time. A reference configuration reproduces all four corrected resident PRGs byte-for-byte. A deliberately different configuration moves the API/code/table/game regions, public I/O, normal ZP, SMUL16 executable ZP, V1 scratch, C64-side REU scratch and REU data banks; all 46 stable public entries execute successfully in every profile. V3/V4 additionally assemble Turbo16/Turbo32 overlays for different ZP origins and different REU storage banks.

The alternate-map stable regression executes 4,589 machine calls per profile (18,356 total). Turbo relocation adds 17,164 product calls plus 32 BEGIN/END lifecycle calls across V3/V4 reference+alternate maps (17,196 Turbo API calls total), including exact caller-ZP restoration and second-batch reuse. A separate endpoint sweep adds 3,556 products at Turbo16 `$02/$8F` and Turbo32 `$02/$79`, including V3 banks `$06/$07` and V4 `$FE/$FF`. Reference/alternate Turbo cycle vectors are identical, proving zero runtime relocation cost. Configuration validation now includes Turbo ZP range and Turbo REU-bank safety checks. The six Turbo lifecycle calls remain a separate stateful API surface rather than being counted among the common 46 stable entries.

## Portability

Target is NMOS 6502/6510 with D=0. New extension code uses documented instructions, but some inherited fastest divider kernels use stable NMOS `LAX`/`ANC`; do not assume 65C02 portability without replacing and revalidating them.

## Scope judgment

The current scope is complete enough to publish. Vector MAC/dot and a fused perspective-projection pack remain worthwhile future optional work, but neither is required for this release to be coherent.
