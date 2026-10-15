# Issue #144 B — high-divisor sign fast-skip and full public hybrid CPU screen

**15 October 2026 — qualified model research, NOT a default/public ABI promotion.**

The high-divisor short circuit exploits a provable condition for **$8000 <= D16 <= $FFFF**. After the next remainder bit has been shifted, if the 17th-bit carry is zero and the high byte of the 16-bit tentative residual is **nonnegative in NMOS N**, then the tentative remainder is <$8000 and therefore strictly below D. It cannot produce a quotient bit of 1. Add `BPL NEXT_i` after `BCS TAKE_i` in each of 16 shared-take steps to skip the usual high/low divisor compares. This shortcut is **invalid when D<$8000**.

## Isolated tail proof

`tools/issue144_u3216_highdiv_bpl_tail_screen.py` assembles real NMOS 6502 fragments, compares stock-like duplicate subtraction, shared-take, and sign-skip on the **same 18,224 deterministic full-width N32 / high-D16 pairs**, and checks exact lower quotient and full R16 using an **oracle-derived high-word residual**.

| Tail | Assembled bytes | Mean modeled CPU cycles |
|---|---:|---:|
| Stock-like original | 684 | 469.593 |
| Shared-take | 492 | 464.249 |
| New sign-skip | 524 | 458.504 |

Mean saving vs stock-like tail **11.088 cycles**. Worst paired saving **−15 cycles**, p05 **−4**, with 2,324/18,224 slower calls. Versus shared-take, mean saving **5.745**, worst **−32 cycles**; 5,183 calls slower. Corpus SHA256 `d40b90478edfd8fbf2dc4aed7b4732a435679704ab7ed6d8f7cca9415319f83f`.

## Full public-entry hybrid

`tools/issue144_u3216_signskip_hybrid_fullcall.py` builds a **1,038-byte temporary caller-owned code block $0800–$0C0D** (inside BASIC/application RAM). For Dhigh=$00, it delegates to the original UDIV32/16 public entry, preserving its D8/zero contract. For $0100≤D≤$7FFF it reuses the previously model/native-qualified no-overflow low-divisor tail; for $8000≤D≤$FFFF it executes the new shared-take+BPL high-divisor tail. Both eligible paths call the same certified $420C high-word quotient/remainder helper and produce complete public Q32/R16/C and N/D preservation, with original stack restored. The extra normal ZP allocation is zero, but existing resident ZP is shared, so **not reentrant and not IRQ/NMI safe**.

The fully assembled **V2/V3/V4 reference-image** test passes **2,370 identical operands per profile × 2 public APIs** = **14,220 paired comparisons / 28,440 ordinary public calls**. All Q32, R16, carry, divisor-zero, inputs and SP match. Same-input modeled savings, identical on the three profiles:

| Workload | UDIV saved | UMOD saved |
|---|---:|---:|
| Uniform full-width N32/D16, n=640 | 28.923 cycles | 31.923 cycles |
| $0100–$7FFF D16, n=640 | 50.959 | 53.959 |
| $8000–$FFFF D16, n=640 | 4.445 | 7.445 |
| D8, n=256 | **−9** | **−6** |
| D=0, n=64 | **−9** | **−6** |
| Complete mixed n=2,370 | 22.502 | 25.502 |

On uniform full-width inputs, **99/640 UDIV cases slow down** (worst −17 cycles) and **66/640 UMOD** (worst −14). Mixed UDIV p05 = **−9**, worst **−20 cycles**. All-profile mixed mean is **not a universal Pareto improvement**. The new version gains only ~4.6 CPU cycles on uniform N32/D16 relative to the previous 511-byte low-divisor option, but doubles the caller-owned RAM and retains negative tails. In addition, the initial full-call test covers fixed reference maps only, not alternate relocations or real native VICE.

Reproducer: [GitHub Actions #38742928085](https://github.com/floppyrom/C64-Math-Library/actions/runs/38742928085), all tests **PASS**. Public-source study, not a released standalone ABI: no documentation of this candidate as a production routine is justified.

## Decision

**Reject default promotion.** A mean model gain alone (around 4–5% on uniform full-width inputs) is insufficient with 15% of those UDIV calls slower, zero/D8 fallback overhead, 1,038 bytes caller RAM, and missing native/map/reentrancy qualification. Preserve the source and negative/conditional result in research; leave Issue #144 B unchecked. Future candidates must eliminate fallback costs and substantial high-divisor path regressions, or restructure the quotient producer rather than stack domain guards. Five shipped PRGs, two REUs, builder, normal ZP, public API, PERFORMANCE and private OptiSearch all remain unchanged.
