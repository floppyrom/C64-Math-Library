# Standalone fast-kernel collection

This collection preserves useful **standalone 6502/6510 math implementations**, including alternatives that lose or cannot fit in the integrated V1-V5 resident profiles. It is an addition to the existing shipped-profile mirrors and curated alternatives under `routines/` and `benchmarks/STANDALONE_RESULTS.csv`, not a replacement for them.

**Status: fixed-map experimental standalone sources, assembled and functionally qualified.** The three included ACME-style `.asm` files can be assembled independently, without loading a C64 Math Library resident, an REU, any data table or the private OptiSearch engine. Their tested code and RAM addresses are fixed, not freely relocatable. They use NMOS undocumented `LAX`/`ANC`; they are not 65C02 routines.

| Source (entry) | 6502 mean cycles on same inputs | Compared with published resident | Resources |
|---|---:|---|---|
| [UDIV16 biased](div_u16_biased.asm) (`$0610`) | **152.443**, 2,729 inputs | V1 public entry 156.088; V1 relocated attempt **156.866**, so not promoted | 323 code bytes, 2 ZP |
| [UMOD16 biased, carry-corrected](mod_u16_biased_carry.asm) (`$080F`; direct `$0800`) | **187.002**, 1,705 inputs | V2-V5 public entry 198.601; V2-V5 ZP/stack ownership not proven | 244 + 15 + 3 code bytes, 2 ZP, 2 nested-stack bytes |
| [UDIV32 ZP-tail](div_u32_zptail.asm) (`$0600`) | **380.698**, 2,729 inputs; **188.398** on random subset | V2-V4 242.549 full set, 193.660 random subset; *specialized* option | 325 + 219 code bytes, 4 ZP, 2 nested-stack bytes |

**ABI (all):** numerator at `$0300` (2 or 4 bytes); divisor `$0320` (2 or 4); quotient `$0540` for division only; remainder `$0560`. Inputs N/D are preserved. On success C=0; for D=0 C=1 and result zero (UMOD16 does not touch the quotient buffer). The caller must execute `CLD` and reserve ZP `$10-$11` (U16) or `$10-$13` (U32). Scratch is clobbered. UDIV16 code occupies `$0610-$0752`; UMOD16 occupies `$0610-$0703` and `$0800-$0811`; UDIV32 occupies `$0600-$0744` and `$2000-$20DA`. **These regions overlap C64 BASIC/KERNAL working RAM.** Use them only in machine-code programs that own those memory regions, not as BASIC-callable resident add-ons. Only load one variant at a time.

For the corrected modulo implementation, include `mod_u16_biased_carry.asm` in an ACME-style build, store `200` into `INPUT_NUM` (16-bit little-endian), store `37` into `INPUT_DIV`, and `JSR FAST_UMOD16_PUBLIC`. Afterwards `OUTPUT_REM` contains `15` and carry is clear. The faster `FAST_UMOD16_CARRYFIX` at `$0800` omits the 3-cycle trampoline. The caller itself must be placed outside the occupied regions.

**Evidence:** `python3 routines/standalone_lab/verify.py` uses only the repository's bundled `tools/mini6502.py`. It independently assembles each symbolic source, confirms original generated segment SHA-256 hashes, reproduces the exact current-main public benchmark case SHA-256 values, and validates 7,163 calls (Q/R/C/N/D and stack). Means include entry through RTS, not caller JSR or real C64 bus/DMA. Native VICE and relocation into other maps are **not** claimed for these exact standalone variants. These results are not yet qualified for the official `STANDALONE_RESULTS.csv` catalog.

See [the candidate backlog](CANDIDATE_BACKLOG.csv) for other Repose outputs and unpromoted approaches. Credit: **Repose / OptiSearch** for the generated 6502 donor strategies; the modulo carry correction and verification here are C64ML adaptations. No OptiSearch private engine source or binaries are included.

## Configurable relocation and native VICE

The new [portable standalone modules](portable/README.md) have editable code, buffer, and ZP addresses. Unlike the original fixed-map donors, they have passed 9,657 emulator calls across three disjoint memory maps and 576 native x64sc correctness calls across two maps. Cycle numbers remain specific to each compiled placement. The original fixed-map sources and segment SHA provenance are retained; a duplicate *internal* UDIV32 symbol was renamed without changing machine code.

## New 0-ZP 32-bit modulo specialist

The [configurable zero-ZP aligned UMOD32 source](portable/mod_u32_aligned_carry.asm) is independently assembled and tested. It needs four ordinary scratch-RAM bytes plus the public carry adapter. On 1,024 identical random wide-divisor inputs it averages **190.867 cycles** versus the published V2-V4 UMOD32 average **199.833**, but its full-spectrum mean is far worse (**476.938 vs 279.620**). It belongs in the isolated-specialist collection, **not** the general-purpose profile ranking. See [portable README](portable/README.md) and `portable/verify_umod32_common.py`.

## Another 0-ZP option: aligned 32-bit quotient + remainder

The [source-backed zero-ZP aligned UDIV32 alternative](portable/div_u32_aligned_nozp.asm) is individually configurable and fully arithmetic/flag-checked. It uses 576 code bytes and four ordinary scratch RAM bytes, with **no ZP allocation**. Its full 2,729-pair mean is **408.012 cycles** (V2-V4 resident 242.549), and its random 2,048-pair mean is **196.890** (resident 193.660). It is therefore a *memory-constraint specialist*, not a new global fastest divider. [Provenance, relocation and benchmarks](portable/README.md). Source-assembled verification: 8,187 current-corpus calls at three maps and 192 native VICE correctness calls at two maps.

## Sixth unique OptiSearch implementation recovered

[Direct-chain UMOD16 with zero zero-page use](portable/UMOD16_DIRECT_PICKUP.md) is preserved as a memory-specialist candidate: 976 code+data bytes, 2 ordinary scratch RAM bytes and 2 nested stack bytes. Its official full-corpus average is **209.868 cycles**, *slower* than V2-V5's 198.601; it is published for zero-ZP resource-constrained users, not as a universal fastest routine. The three-map emulator proof covers 5,115 calls and the independent native VICE campaign covers 192 correctness calls. This gives source-backed coverage of all six distinct generators from Repose's October 11 comparison bundle; individual performance and ABI qualification still apply.

Current V2–V5 UMOD16 biased public-ABI/identical-input screen: [docs/ISSUE39_UMOD16_BIASED_CURRENT_MAIN_DECISION_2026-10-12.md](../../docs/ISSUE39_UMOD16_BIASED_CURRENT_MAIN_DECISION_2026-10-12.md). The 185.826-cycle corpus mean hides 1,391/1,705 slower cases and extra RAM/ZP/stack; no resident promotion.
