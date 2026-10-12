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
