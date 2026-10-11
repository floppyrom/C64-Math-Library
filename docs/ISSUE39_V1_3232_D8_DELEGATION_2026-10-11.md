# Issue #39 — V1 Balanced guarded 32/32 division by an 8-bit divisor

**Date:** 2026-10-11. **Status:** V1-only candidate with bounded trade-off. Overall unsigned DIV/MOD family remains OPEN.

## Algorithm / ABI and ownership

The existing shared UDIV32/32 and UMOD32/32 entry has already tested D!=0 and N>D. The bounded high-quotient selectors reach the D3=0 path only after that proof. A new **23-byte source-backed gate** at `REG_LOW+$0D80` (reference $1D80) reads D2 OR D1. If both are zero then **0<D<256**: the existing V1 UDIV32/16 public core computes an identical full 32-bit quotient and low 16-bit remainder. The delegate clears R2/R3 and carry and returns. Otherwise execution rejoins the original `REG_GAME` core. This is intentionally **not** the earlier rejected unconditional 16-bit-divisor transplant: the historical 16-bit route regressed by up to **429 cycles** on sampled inputs (other screens around 403–413 cycles). The D8 guard avoids that worst-case class.

The new path occupies a previously empty island $1D80–$1D96, adjacent to but not overlapping V1's $1D00 24÷8 helper. The existing V1 32/16 engine remains unmodified and keeps its source-backed loop unrolling. No added normal ZP, new stack commitment, public relocation or ABI change; the 49,042-byte reference resident span remains unchanged. Both reference and alternate V1 symbolic builds pass.

V5 retains its separate faster imported V2 32/16 specialization for **D3=D2=0**. Because V5 is built from V1 source, the hybrid builder recognizes and scrubs the entire V1-only 32/32 D8 island, restores the inherited D3=0 fallback and then installs its original V5 32/32 D16 selector. Reference V5 resident SHA-256 remains exactly `9f59d7f8eb8d5cd78d0f01867418e77db5e867e06b9b43afe34df36ccea82dc2`; V5 alternate build is also unchanged.

## Paired public machine-code measurements

The historical V1 PR #61 parent resident is reconstructed byte-for-byte with its **SHA-256 `67d709a3006e5529d49b579be20747b292f466679ea42ac24fd5384e4d71879e`**. The new permanent audit compares **51,812 old/new complete machine-code calls** for both APIs on canonical shared inputs, random full-width numerators with 8/16/24/32-bit divisor classes, two special numerator widths, 4,080 quota edge pairs, and divide-by-zero. It validates Q (for UDIV), full R, carry and N/D preservation, and enforces a **strict maximum +14-cycle regression** outside D8. On every sampled D8 input the candidate must be faster or equal.

| Operation and workload | Previous V1 | New V1 | Change |
|---|---:|---:|---:|
| UDIV32/32 common, 2,729 cases | 358.009161 | **335.825577** | −6.2% |
| UMOD32/32 common, 1,705 cases | 435.224633 | **399.676833** | −8.2% |
| UDIV32/32 uniform D8, 1,024 cases | 1943.200 | **1643.726** | −15.4%, all faster |
| UMOD32/32 uniform D8, 1,024 cases | 1942.482 | **1643.277** | −15.4%, all faster |
| UDIV32/32 uniform D16, 1,024 cases | 1665.698 | 1678.477 | **+12.8**, 1,020 slower |
| UDIV32/32 uniform D24, 1,024 cases | 1549.240 | 1563.240 | **+14.0**, all slower |
| UDIV32/32 uniform D32, 1,024 cases | 236.433 | 236.487 | effectively unchanged |

**Performance trade-off is real:** D8 sees a very large improvement, but unqualified D3=0 denominators (D9–D24) take a 14-cycle guard penalty. This must not be described as unconditionally dominating the prior code. Like V5's D16 shortcut introduced in PR #59, it is useful for narrow-divisor-dominated workloads, not a universal profile winner. Worst-case tail of the earlier unrestricted 16-bit candidate is avoided.

## Verification and history

V1 full-profile unsigned validation **164,410 public calls** passed locally, plus reference/alternate source assemblies. Genuine VICE x64sc execution used complete old/new 49,042-byte residents, 80 calls per version across both APIs, independent quotient/remainder/carry oracle, and passed **160 native calls**. Emulator reported version **VICE 3.10** despite the saved bundle name referring to 3.13.2.

Historical tests are insulated from this improvement by `tools/issue39_v1_3232_d8_parent.py`: it reconstitutes the exact merged PR #61 image before replaying the frozen earlier PR #57 bypass, PR #60 negative V1 24-bit selector, or PR #61 24÷8 positive certificate. This prevents accidental false attribution or breakage of old tests. The V5 PR #59 old/new narrow-denominator certificate continues to use its separately reconstructed V5 parent.

The implementation is a **manual architecture synthesis** informed by previous OptiSearch/loaned 32-bit division research. Private OptiSearch artifacts are not committed, and no native OptiSearch record is misleadingly represented as this public optimization.

Further issue #39 work remains: architecture/no-gain conclusions across UDIV8/16 and UMOD8/16, surviving 24-bit width/profile classes, and 32/16/32/32 alternatives under stock-C64 and REU resource contracts. Do not check off the family prematurely.
