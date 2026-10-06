## 2026-10-06 — SMUL32 NN X3 prebind

- Pre-bound original X3 table operands on the X<0,Y<0 dispatcher path while X3 is already live in A; common x0!=0 calls avoid a later absolute reload, while the rare carry path overwrites the speculative bindings.
- Canonical SMUL32 means improve to **711.586966 / 711.941885 / 712.136986 cycles**; min/max remain **630–838**.
- Shared 6,361-case mean improves **717.735105 → 716.802547** in all V2/V3/V4 profiles; focused NN improves **734.714806 → 730.807690**, max **837 → 833**.
- MATH_SMUL32_SHR16 is **780.756936 cycles mean (695–903)**; producer, summation, 31-ZP and zero-persistent-stack contracts are unchanged.
- Full signed-multiply, multiply-refresh, deterministic rebuild, published-source, Turbo relocation/boundary and package gates pass.

## 2026-10-06 — SMUL32 q1 bounded-carry + correction tail

- Replaced only the FAST31 q1 (X>=0, Y<0) late-column summation in V2/V3/V4 with the validated bounded-carry state machine and tail-placed its signed correction; q0/q2/NN and the four-row producer are unchanged.
- Canonical SMUL32 means improve to **712.403902 / 712.856787 / 712.948941 cycles**; min remains **630** and max remains **838**.
- On an identical 6,361-case corpus all three profiles are cycle-identical at **717.448043 cycles**, improving the PR #18 baseline by **0.332495 cycles/call**.
- Focused q1 mean improves **734.268012 → 732.785800** and worst case **839 → 830**.
- MATH_SMUL32_SHR16 is **781.620041 cycles mean (695–903)**; the 31-ZP / zero-persistent-stack contract is unchanged.
- Full signed-multiply, multiply-refresh, published-source, deterministic rebuild, Turbo relocation/boundary and package gates pass.

## 2026-10-06 — SMUL32 q2 correction tail-placement

- Tail-placed the shared FAST31 q2 signed correction after the alternate bounded-carry continuation in V2/V3/V4; the four-row producer and q0/q1/NN paths are unchanged.
- Canonical SMUL32 means improve to **712.623495 / 713.107929 / 713.133250 cycles**; min remains **630** and max improves **841 → 838**.
- On the identical 20,324-case corpus all three profiles remain cycle-identical at **720.223332 cycles**, another **0.343043 cycles/call** below the previous q2-bounded release.
- MATH_SMUL32_SHR16 is **781.884889 cycles mean (695–903)**; the 31-ZP / zero-persistent-stack contract and 291-byte q2 block are unchanged.
- Full signed-multiply, multiply-refresh, published-source, deterministic rebuild, Turbo relocation/boundary and package gates pass.

## 2026-10-06 — SMUL32 q2 bounded-carry follow-up

- Replaced only the FAST31 q2 (X<0, Y>=0) late-column summation in V2/V3/V4 with the validated bounded-carry state machine; q0/q1/NN and the four-row producer are unchanged.
- Canonical SMUL32 means improve to **712.935243 / 713.365297 / 713.431714 cycles**; min remains **630** and max improves **845 → 841**.
- On one identical 20,324-case corpus all three profiles remain cycle-identical at **720.566375 cycles**, improving the current baseline by **0.731451 cycles/call**.
- MATH_SMUL32_SHR16 is **782.219674 cycles mean (695–906)**; the 31-ZP / zero-persistent-stack contract is unchanged.
- Validation passes 264,999 signed-multiply calls, 415,078 multiply-refresh calls, published-source checks, deterministic rebuild, and Turbo relocation/boundary proofs.

## 2026-10-06 — V2–V4 SMUL32 bounded-carry summation follow-up

- Tightened the existing FAST31/V29 signed 32×32 summation without changing the four-row quarter-square producer, 31-byte ZP contract, persistent-pointer layout, public ABI, or stack usage.
- Reordered measured carry sites so the common no-carry cases fall through, and removed late-column wrap checks that are unreachable under the positive-magnitude bounds already guaranteed by the signed quadrant dispatcher.
- Exact 20,324-case V2 A/B comparison: **722.867792 → 720.762498 cycles mean** (**−2.105294**), minimum **632 → 630**, maximum unchanged at **845**, with zero errors.
- Canonical 2,409-case public `MATH_SMUL32` means are now **713.643005 / 714.019095 / 714.095475** cycles in V2/V3/V4; a shared 20,324-case corpus is cycle-identical at **720.762498** in all three profiles.
- `MATH_SMUL32_SHR16` improves to **782.934189 cycles mean (695–910)** in V2/V3/V4. Resident PRGs, standalone/native signed mirrors, consolidated tables, validation evidence, release hashes and package checksums were regenerated from canonical source.

## 2026-10-06 — all-profile 16-bit fixed-point register-return adapters

- Replaced the byte-copy tails in `MATH_UMUL16_SHR8` and `MATH_SMUL16_SHR8` with register-return adapters while preserving the stable public entries and base multiply implementations.
- Unsigned SHR8 is now exactly **UMUL16 +31 cycles** in V1/V5 and **UMUL16 +27 cycles** in V2/V3/V4, saving **10 / 14 cycles** respectively on every call.
- Signed SHR8 is now exactly **SMUL16 +31 cycles** in all five profiles, saving **10 cycles** on every call.
- Reference/alternate maps are cycle-identical; V5 matches the inherited V1 unsigned path and all inputs/results/carry contracts pass the all-profile deterministic proof.

## 2026-10-06 — all-profile SMUL24 direct-output optimization

- Applied the same low-result lifetime optimization used by UMUL24 to the private FAST24 four-quadrant signed composition in all five fixed profiles.
- Product bytes Z0-Z2 are written directly to public result RAM once their pointer-low aliases are dead; mixed-sign correction still operates only on the upper 24 bits in Y/A/X.
- V1/V5 signed validation means become **513.496472 / 512.874222** cycles; V2/V3/V4 become **469.181818 / 468.816106 / 469.220008**.
- The transformation is a constant **-18 cycles per call**: three ZP stores become absolute public stores (+3 cycles total), while three 7-cycle ZP-to-public copy pairs disappear (-21).
- 24-ZP ownership, table geometry, signed quadrant logic, ABI, and persistent stack usage are unchanged. Reference/alternate vectors and V1/V5 inheritance remain identical.

## 2026-10-06 — all-profile UMUL24 direct-output optimization

- V1/V5 private FAST24 and V2/V3/V4 resident reverse/carry UMUL24 keep their existing 24-ZP/table geometry but now write z0-z2 directly to public result RAM after the corresponding pointer-low lifetimes end.
- Same-corpus old-vs-new comparison: **exactly 18 cycles saved on all 10,324 calls** in both representative implementation families.
- Current means: **474.042329 cycles (444–530)** in V1/V5 and **429.555502 cycles (400–485)** in V2/V3/V4; reference/alternate vectors are identical and V5 matches V1 exactly.
- Signed SMUL24 executable code is unchanged; only the unsigned producers changed.
- Added permanent all-profile UMUL24 validation and regenerated V1–V5 resident/standalone/publication artifacts.

## 2026-10-06 — V2–V4 UMUL16 direct-output optimization\n\n- Optimized the existing fixed-profile 17-ZP UMUL16 family without importing a high-ZP research kernel: the public adapter now enters with **A=x1**, removing a redundant reload, and the fused quarter-square core writes **Z0 directly to MATH_Z**.\n- V2/V3/V4 `MATH_UMUL16` measures **216.980037 cycles mean, 205–240** on the 10,169-case deterministic edge+random corpus, with identical reference/alternate cycle vectors.\n- The private pointer footprint drops from **17 to 16 ZP bytes**; table geometry and persistent stack usage are unchanged.\n- `MATH_UMUL16_SHR8` inherits the producer win and remains an exact **+41-cycle** composition: **257.980037 mean, 246–281** on the same corpus.\n- Promoted V2/V3/V4 PRGs, exact standalone mirrors, resident UMUL16 binary slices, segment metadata, consolidated/public indexes, and package hashes are regenerated from canonical source.\n\n## 2026-10-06 — Turbo16 public-wrapper optimization

- Kept the 113-byte Turbo16 executable-ZP overlay **byte-for-byte unchanged** and removed one redundant 4-cycle absolute reload from the public CALL adapter by keeping `x1` live in A for the existing `umult_ax1` entry.
- Canonical Turbo16 CALL improves from **215.544111** to **211.544111 cycles mean**; the unchanged corpus range shifts from **203–240** to **199–236**.
- All **17,196 Turbo API calls** pass in reference/alternate V3/V4 builds, and the **3,556-product** minimum/maximum-origin boundary sweep remains cycle-identical.
- BEGIN/END remain **282 / 327 cycles**; versus 225.837200-cycle normal UMUL16, Turbo16 now crosses over at **43 products** per batch.

## 2026-10-06 — Turbo32 direct-I/O runtime optimization

- Reworked the V3/V4 Turbo32 resident adapter while preserving the exact 135-byte stack-free executable-ZP overlay and its legal $02-$79 origins.
- Removed Y-byte marshalling into ZP, moved high-column temporaries into public result RAM, and write final product bytes directly into MATH_Z where lifetime analysis permits.
- Canonical Turbo relocation corpus: **2,193 calls, 684.185219 cycles mean, 621–796**, down from **728.947080**; zero arithmetic errors.
- Reference/alternate maps are cycle-identical, and minimum/maximum legal ZP-origin boundary sweeps pass in both V3 and V4.
- Turbo32 now beats normal UMUL32 (690.235367) per active CALL; with 326-cycle BEGIN and 371-cycle END, the batch crossover is **116 products**.
- Corrected stale Turbo16/QS16 guidance: Turbo16 previously crossed normal UMUL16 at roughly 60 products; QS16 remains supported but has no current speed crossover.

## 2026-10-06 — V3/V4 REU UDIV8 hybrid fast path

- Replaced the V3/V4 two-DMA UDIV8 public path with a hybrid quotient ladder: q=0..3 returns on the CPU; q>=4 uses the exact existing REU quotient/remainder planes.
- Exhaustive 65,536-case validation passes with **52.852264 cycles mean (28–115)** in both profiles, down from **70.863281** and faster than V2's 59.383011-cycle current public mean.
- `UMOD8` remains the direct single-plane REU remainder lookup; REU image layout and public ABI are unchanged.
- Rechecked UDIV24: V2/V3/V4 use the same Repose q0-counter arithmetic and are identical on the existing same-corpus gate; no REU-specific UDIV24 replacement was warranted.

## 2026-10-06 — FAST31 direct public-entry follow-up

- Removed the redundant 3-cycle self-redirect at the stable V2/V3/V4 `MATH_SMUL32` entry; the fixed address now falls directly into the FAST31 dispatcher.
- Canonical SMUL32 means improve to **715.605230 / 716.033209 / 716.090079 cycles** for V2/V3/V4, with min/max **632/845** on the 2,409-case signed corpus.
- `MATH_SMUL32_SHR16` inherits the same constant reduction and now measures **784.998853 cycles** (697–910) in V2/V3/V4 on the 4,361-case refresh corpus.
- The literal FAST31 v2 `CPY #$00` carry-seeded dispatcher was transplanted and measured **exactly neutral** under the public memory ABI; it merely exchanges a 2-cycle `SEC` for a 2-cycle compare and was discarded.
- Validation passed 264,999 signed multiply calls, 415,078 multiply-refresh calls, alternate-map 54-entry public validation, and 17,196 Turbo lifecycle calls.

## 2026-10-05 — FAST31 V2–V4 persistent-pointer profile integration

- Integrated the 31-ZP FAST31/V29 32-bit multiply family more deeply into V2/V3/V4 without expanding V2 beyond its documented **221-byte ZP commitment**.
- All six FAST31 table-pointer pairs now persist in holes already owned by the V2-family normal ZP map, eliminating the ordinary mixed-call pointer repair. The per-routine footprint remains 31 touched ZP bytes and persistent stack-page reservation remains zero.
- Ordinary signed `MATH_SMUL32` and `MATH_SMUL32_SHR16` improve by exactly **25 cycles/call** in V2/V3/V4; ordinary unsigned `MATH_UMUL32` and `MATH_UMUL32_SHR16` improve by **22 cycles/call**. READY entries are unchanged.
- Canonical signed-corpus SMUL32 means become **718.605230 / 719.033209 / 719.090079 cycles** for V2/V3/V4. The regenerated stable-API ZP unions are **207 / 202 / 201 bytes** respectively.
- Validation passes **264,999 signed multiply calls**, **415,078 multiply-refresh calls**, reference/alternate mixed-call validation, and **17,196 Turbo lifecycle calls**. Turbo END restores the persistent pointer bytes exactly.
- Fixed the standalone/consolidated/source-recovery tooling to treat active Turbo executable-ZP code as a BEGIN-installed overlay rather than decoding normal-profile ZP contents.

## 2026-10-05 — SMUL32 FAST31 v2 and record-metadata alignment

- Added `mul_s32_s32_s64_fast31_native_v2.asm`: **692.825100 cycles**, 31 ZP, zero persistent stack-page bytes, 0 errors on the primary 100,000-pair corpus; **692.678520** on an independent 100,000-pair seed; 0 errors on 1,849 structured edge cases.
- FAST31 v2 transfers two compact126 ideas into the low-resource kernel: the NN common/rare x0-borrow split and `CPY #$00` carry-seeding sign dispatch. This improves the previous 697.259440 31-ZP native point by **4.434340 cycles/call**.
- A separate 31-ZP public-ABI research candidate measured **736.188510 cycles** (independent seed 736.128620). It is retained as historical evidence; the later same-day V2–V4 persistent-pointer integration supersedes it with **718.605230 / 719.033209 / 719.090079-cycle** canonical public SMUL32 means.
- Aligned compact126 with the standalone record metadata/accounting convention: executable code is **428 bytes** (302 ordinary RAM + 126 page-$01), and total occupied bytes including its 136-ZP claim are **2,608**. Added standardized `;ABI` / `;Results` metadata.

## 2026-10-05 — SMUL32 compact126 native record

- Added `routines/multiply/mul_s32_s32_s64_compact126.asm`, validated at **646.354530 cycles** on the primary 100,000-pair C0FFEE native corpus, **646.281100** on an independent 100,000-pair seed, and 0 errors on a 1,849-case structured edge suite.
- Resource point: **136 ZP bytes**, **126 persistent hardware-stack-page bytes**, **302 ordinary-RAM code bytes**, and the existing **2,044-byte** quarter-square table family.
- The fixed V1–V5 public `MATH_SMUL32` implementations are deliberately unchanged. V1/V5 cannot accept the ZP footprint; V2–V4 already use the relevant executable-ZP window for native SMUL16, and a standard-ABI compact126 transplant measures about **757.7 cycles**, slower than the shipped ~743–744-cycle public path.
- Added profile-local `optional/smul32_compact126/` source aliases for V2/V3/V4. They are explicit exclusive-overlay packages only; fixed public `MATH_SMUL32` remains unchanged. Added `docs/SMUL32_COMPACT126_PROFILE_FIT.csv` with the exact ownership ranges.
- Updated `PERFORMANCE.md`, `benchmarks/STANDALONE_RESULTS.csv`, `routines/SOURCE_CATALOG.csv`, signed/profile-selection documentation, and profile README compatibility notes. See `docs/SMUL32_COMPACT126.md`.

## 2026-09-25 — stable entries 47–54: seek movement (`MATH_SEEK8_*`, `MATH_SEEK16_*`)

- Add eight stable API entries in every fixed profile and every generated Custom Pareto build, at `REG_GAME_API+$3C..+$51` (reference `$5E3C-$5E51`). `MATH_SEEK8_INIT/STEP/STEP_INT/STEP1` handle 8-bit x/y; `MATH_SEEK16_*` handle 16-bit x with 8-bit y. The API grows from 46 to **54 entries**; no existing address, output or timing changes.
- Each family moves eight objects to a target pixel along the exact Bresenham line and lands exactly on it. Speed is Q8.8, along the major axis or (speed bit 15) along the path.
- Per frame (every profile, public entry incl. JMP): SEEK8 **87.1 / 71.0 / 66.0** cycles for STEP / STEP_INT / STEP1; SEEK16 **118.3 / 103.7 / 98.2**. Init (V2–V4 / V1–V5): SEEK8 337 / 368 at a major-axis speed, 752 / 835 at a Euclidean speed; SEEK16 478 / 530.
- Re-optimized kernels versus the 2026-09-25 standalone versions:
  - SEEK8 init −15%, code 642 → 582 bytes;
  - SEEK16 per frame −11%, init −25%;
  - one 16-bit counter for speed fraction and distance in both families;
  - Euclidean speed selected by a flag instead of a separate entry;
  - `DCP`-based 1 px/frame steppers for both families;
  - integer speeds skip the k0+1 precomputation.
- One template (`tools/seek_kernel.py`) emits the five profile installs and both standalone sources (`tools/generate_seek_sources.py --check` in CI). The SEEK8 steppers sit inside one page in every profile. V1/V5 use `V1_SCRATCH` RAM for init scratch (31-byte ZP contract kept); V2–V4 use the game-scratch ZP. No new ZP, no REU use, no `MATH_INIT` dependency.
- Placement:
  - 1,288 code bytes (1,423 in V1/V5) plus 408 bytes of object state, in islands inside existing claimed regions;
  - proven untouched by every other routine, `MATH_INIT`, Turbo overlays and REU DMA on both maps (`validation/movement/SEEK_PLACEMENT.json`);
  - only seek-owned bytes changed in the images (`SEEK_BINARY_DELTA.json`); PRG spans and REU images are unchanged.
- The common validator now checks every seek frame, interleaved with other library calls, in V1–V5 and all Pareto builds: 54/54 entries and 21,422 calls per map. The standalone mirrors add 40 files; `docs/SEEK_DDA.md` documents the API.
- The standalone-mirror publisher emits NMOS unintended opcodes as annotated `!byte` lines, like `LAX`/`ANC`. The Makefile gets a `seek` target and an `ACME ?= acme` default; `make acme` works without setting `ACME`.

## 2026-09-25 — 8-bit seek DDA and unintended opcodes in the emulator

- Add `routines/movement/seek_u8_u8_dda.asm` for 8-bit game coordinates (x, y 0..255), following Repose's point that screen coordinates are small. The error term, distance counter and positions are single bytes. The fraction accumulator and distance countdown share one 16-bit counter. Carries are pre-biased into the stored deltas, and the per-frame paths index only with X.
- Add `seek8_step1`, which uses NMOS `DCP` to count down and test arrival in one instruction at 1 px/frame.
- On 408 moves on a 256x200 screen at 0.5-4 px/frame, compared with the normalize mover with arrival bookkeeping (8-bit x):
  - setup takes 375-713 cycles instead of 4,412;
  - per frame is 63.0 (1 px/frame), 68.0 (integer speed) or 84.3 (fractional speed) cycles, vs 81.7;
  - end to end is 1.4x cheaper at the same Euclidean speed and 2x at 1 px/frame;
  - the path stays within 0.5 px and arrival is exact, vs up to 3.6 px drift and edge wrap-around.
  - The routine takes 674 bytes of code and table.
- `tools/mini6502.py` now assembles and emulates the stable NMOS unintended opcodes (SLO, RLA, SRE, RRA, SAX, LAX, DCP, ISC, ANC, ALR/ASR, ARR, SBX, SBC $EB) and ignores `!cpu` lines. Existing builds and validations are unchanged. `tools/test_mini6502_illegal.py` checks them against *No More Secrets* and runs in CI.

## 2026-09-25 — exact DDA "seek" for moving objects toward a target

- Add `routines/movement/seek_u16_u8_dda.asm`, a standalone Bresenham/DDA stepper for "move object to (tx,ty) at speed", following Repose's review on CSDb. Each frame's position is on the Bresenham line (within 0.5 px of the true line), and the object lands exactly on the target. Speed is Q8.8 px/frame along the major axis (`seek_init`) or along the path (`seek_init_euclid`, within 0.7%). Up to 8 objects are supported, with no scratch in the per-frame stepper.
- On 408 random screen moves at 0.5-4 px/frame, compared with normalize + `SMUL16_SHR8` velocity + ISQRT/divide arrival bookkeeping on V1: setup takes 967 cycles instead of 4,412; per-frame cost is 126.6 cycles vs 93.7 (109.3 for integer-speed `seek_step_int`); total per move is about even. Path error is <=0.5 px vs up to 3.2 px, with no target miss vs up to 4 px. The routine takes 754 code + table bytes, vs 3,441 for the stock normalizer alone.
- Document in `docs/VEC2_NORMALIZE_Q8_8.md` that raw 16-bit pixel deltas are valid normalize input (normalization is scale-invariant), and that the 0.36-degree bound is up to about 2 px over a full screen.
- Register the source in `benchmarks/STANDALONE_RESULTS.csv` and `routines/SOURCE_CATALOG.csv`. Evidence: `validation/movement/SEEK_DDA_BENCHMARK.json`.

## 2026-09-21 — smaller normalize and ATAN2 without timing regressions

- Reduce normalize to 881 code + 2,560 table bytes in V1/V2/V5, saving **290 bytes**. V3/V4 use 849 code + 1,024 C64 table bytes, saving **18 bytes**.
- Use four certified logarithmic ratio pages, remove redundant instructions and small-vector scratch transfers, and keep each stock quadrant within one code page.
- Normalize now averages **160.150080 cycles** in V1/V2/V5 and **156.661198 cycles** in V3/V4. No slower call among 107,396 comparison vectors per profile.
- Reduce V2/V3/V5 ATAN2 bodies from 89 to **85 bytes** by sharing carry setup. All 65,536 inputs retain identical cycles and outputs; mean remains **44.962814 cycles**.
- Preserve the existing accuracy contract. Stock normalize outputs change, with full-domain bounds of 0.361659109 degrees and 201 LSB; REU normalize outputs are unchanged. PRG spans and REU images are unchanged.
- Refresh native and standalone sources, profile/segment/result tables and validation. Correct mixed-call validation to bind multiply state before calling `UMUL32_READY`.
- Full details: `docs/SIZE_OPTIMIZATION_2026-09-21.md`.

## 2026-09-21 — faster vector normalization

- V1/V2/V5 now average **161.332256 cycles**, down 18.83% for V1/V5 and 14.76% for V2. V3/V4 average **157.552684 cycles**, down 7.35%, on the same 107,396-vector corpus.
- Dispatch the sign quadrant once and write signed components directly. Stock profiles use certified logarithmic-ratio tables; REU profiles retain their existing mapping and outputs.
- Preserve the public Q8.8-to-Q1.15 ABI, <=0.3621-degree / <=202-LSB contract, and V1/V5 31-byte shared ZP allocation. Each normalizer uses four scratch bytes.
- Trade more RAM for speed: 915 code + 2,816 table bytes for stock profiles; 867 code + 1,024 C64 table bytes for REU profiles, with unchanged REU images. V1/V2/V5 PRGs now load at $1000, adding 4 KiB to the contiguous file span including gaps.
- Update canonical code/table sources, resident PRGs, source mirrors, hybrid/Pareto builds, public performance and memory tables, and release validation. Stock outputs change within the existing error contract.

## 2026-09-20 — consolidated public source and benchmark structure

- Added `PERFORMANCE.md` as the human-readable speed front door and `benchmarks/PUBLIC_PROFILE_RESULTS.csv` / `benchmarks/STANDALONE_RESULTS.csv` as machine-readable indexes.
- Added `routines/SOURCE_CATALOG.csv`, indexing all **245** shipped callable profile sources plus source-backed standalone alternatives.
- Published exact standalone source files for the current UMUL16 shifted-row Pareto points, UMUL24 FAST24, UMUL32 bounded-carry points, SMUL24 FAST24, and the SMUL32 Turbo135 / FAST31-native research points.
- Added `tools/generate_public_indexes.py` and `tools/validate_public_catalog.py`; benchmark rows now carry an exact source path and SHA-256 and fail validation if the source/evidence is missing.
- Fixed generated V5 `math_api.inc` output so canonical typed aliases are preserved by rebuilds; the full standalone/API consistency audit again passes **1,357/1,357 checks**. No resident arithmetic bytes or public addresses changed.
- Removed the old top-level exploratory `research/` tree from the replacement distribution; Git history remains the archive for superseded experiments.
- Added a single lean CI workflow focused on source/publication consistency and deterministic reference/alternate builds.

## 2026-09-20 — smaller and faster ATAN2 kernels and profile integration

- Added `compact_opt`: 48.447189 cycles / 606 B code plus tables, preserving every shipped result.
- Added `sum_small`: 45.958908 cycles / 860 B; 40% fewer table bytes than the shipped fast tier, with the same <=1-unit error bound and exact axes. It changes 202 near-horizontal outputs by one unit.
- Added `sum_fast`: 44.962814 cycles / 1113 B, preserving every shipped result; 4.24% faster with 20% fewer table bytes than the shipped fast tier.
- Published complete ACME sources including tables, a deterministic exporter, and a reproducible dual-emulator validator. All variants use zero ZP and return C=0.
- Certified 917,504 cases against py65 and the bundled emulator, including both entry carry states and relocated page-crossing layouts; six ACME assembly comparisons are byte-identical.
- Installed `compact_opt` in V1 and `sum_fast` in V2/V3; V4 retains its exact 48-cycle REU plane and V5 imports the new V2 kernel with four private table pages.
- Regenerated resident binaries, relocatable and standalone source mirrors, hybrid/Pareto resource accounting, manifests, and all public performance/consolidated tables. Installed means are now **48.447189 / 44.962814 / 44.962814 / 48.000000 / 44.962814** for V1–V5.
- The Custom Pareto `atan2_fast` pack is now **0 ZP / 1,024 B**, and fixed V5 uses **9,633 B** of exact extra private RAM versus V1.

## 2026-09-20 — standalone routine publication and typed API names

- Published one exact readable ASM source mirror for every callable routine in every profile (46/46/52/55/46).
- Adopted canonical operand/result names such as `mul_u8_u8_u16` and `div_u8_u8_u8_8` while preserving all legacy `MATH_*` symbols and addresses.
- Added canonical-name columns to public/performance/consolidated tables without changing measured values.
- Added profile-specific typed names for REU Turbo16/Turbo32 and V4 QS16.
- Added a 1,371-check standalone/API/table consistency audit.

## 2026-09-20 — five-profile division refresh

- Re-evaluated `UDIV8/16/24/32_16/32_32`, `SDIV8/16/24/32_16/32_32`, all corresponding modulo/remainder entries, shifted divide helpers and `URECIP16_Q16` across all five fixed profiles.
- Integrated Repose’s selective-q0 UDIV24 idea as profile-local direct-public cores; V1 uses a balanced derivative, V2/V3/V4 use the fast derivative, and V5 repacks the selected core under its 31-byte normal-ZP contract.
- Selected the new CPU UDIV8 path for V1/V2/V5 while deliberately retaining V3/V4’s faster REU quotient/remainder planes.
- Added direct-output native signed 8/16/24/32-bit division paths and removed a redundant zero test from signed 32/32 magnitude handling; signed executable ownership remains disjoint from unsigned division engines.
- Added an early q=0 gate to exact 32/32 unsigned division where it wins and preserved existing 32/16/shifted paths where the new candidate did not beat the installed implementation.
- Same-corpus old-vs-new selection audit covers 23 public division-family paths per profile and reports **zero regressions** in V1–V5.
- Final resident validation covers **822,050 unsigned division/modulo calls** and **364,533 signed division/modulo calls**, zero errors.
- Regenerated exact native signed division mirrors; 65 published signed routines / 270 source checks and 279 signed-layout checks / 65 zero-overlap comparisons pass.
- Refreshed V5 and Custom Pareto accounting. Equal-weight extra-RAM points are now **9377 / 9950 / 10893 / 9581 / 11079 B** at 31 / 36 / 60 / 147 / 176 ZP before the full-V2 endpoint.
- Reference V5 `HYBRID_CODE` grows to `$A000-$BDFF` / **7,680 bytes**; exact default 31-ZP V5 private-RAM increase versus V1 is **9,377 bytes**.
- Reference/alternate source builds, V5 hybrid, Custom Pareto, deterministic rebuild, package audit and the 205-check release audit all pass; external ACME rerun was not performed for this refresh.

## 2026-09-20 — five-profile multiplication refresh

- Re-evaluated `UMUL8/16/24/32` and `SMUL8/16/24/32`, including READY and fixed-shift derivatives, across all five fixed profiles using the recent Repose/quadrant and quarter-square work.
- Selected direct signed-domain `SMUL8` in every profile at **67.992188 cycles exhaustive**.
- Selected low-ZP FAST17 `SMUL16` for V1/V5 while deliberately retaining the faster 116-ZP practical native SMUL16 in V2/V3/V4.
- Selected FAST24 signed composition in every profile; V1/V5 also adopt the FAST24 unsigned producer, while V2/V3/V4 retain their slightly faster existing record UMUL24.
- Selected mixed-call-safe FAST31/V29-derived `UMUL32` and `SMUL32` in all five profiles, with **712.235367-cycle UMUL32** and profile SMUL32 means around **743–745 cycles**.
- Preserved V3/V4 Turbo16/Turbo32 entry geometry by relocating the new unsigned q0 core away from the REU Turbo executable islands.
- Kept existing `UMUL8` and record-derived 17-ZP `UMUL16` after explicit profile-resource evaluation; the faster standalone high-ZP points do not produce a clean fixed-profile integration win.
- Broke refreshed kernels out as canonical reusable profile includes, taught source regeneration to preserve them, regenerated exact signed native mirrors, and updated consolidated/per-profile performance evidence.
- Validation includes **264,999 signed multiply calls**, **415,078 refresh benchmark calls**, **17,196 Turbo relocation calls**, reference/alternate 46-entry source builds, deterministic rebuilds, signed executable zero-overlap checks and the full release audit.
- Custom Pareto was refreshed to match the new fixed-profile baseline: the old `umul32_initialized` donor pack is retired because FAST31/V29 is already in V1; the 5-ZP legacy `umul8_16` pack now accelerates only UMUL8 because direct SMUL8 is already common; and the 24-ZP pack imports the refreshed V2 FAST24 signed core. Current equal-weight extra-RAM points are **9377 / 9950 / 10893 / 9581 / 11079 B** at 31 / 36 / 60 / 147 / 176 ZP before the full-V2 endpoint.

## 2026-09-18 — stable 46th entry: Q8.8 VEC2 normalization

- Promoted `MATH_VEC2_NORMALIZE_Q8_8` at `REG_GAME_API+$39` / reference `$5E39`, expanding the stable public API from 45 to **46 entries** across V1–V5 and generated Custom Pareto builds.
- Contract: signed Q8.8 X/Y -> signed Q1.15 normalized X/Y; inputs preserved; `C=1` only for `(0,0)`, which returns zero output.
- Final means: **V1 198.770271**, **V2 189.260317**, **V3 170.058633**, **V4 170.058633**, **V5 198.770271 cycles** on the 107,396-vector deterministic corpus.
- V1/V5 retain the 31-byte low-ZP contract; V2 uses the Pareto-fast stock backend. V3/V4 replace the reciprocal/multiply stage with a 32 KiB direct ratio-index table in `$8000-$FFFF` of relocatable `REU_TURBO16_BANK`, requiring no additional V3 REU bank.
- Corrected full-domain certification passes at **<=0.360856382 degrees / <=200 Q1.15 LSB**, inside the public <=0.3621 degrees / <=202-LSB contract.
- Fresh V1–V4 reference/alternate source builds pass **46/46 entries, 4,589 calls per map**. V5 exposes the same routine through its generated and shipped API includes. Custom Pareto validation now totals **55,068 common-API calls** across 12 builds.
- Updated canonical source regeneration, REU image generation, performance/resource tables, API includes, manual, profile-selection/REU documentation and package metadata.
- Broke the normalizer out into profile-local canonical native sources under `resident/vector/native/`; V1-V4 now include those files directly from `math_relocatable.asm`, while V5 publishes the byte-identical V1/V5 backend for standalone reuse. Added independent native-source assembly/byte-identity validation.

## 2026-09-17 — ATAN2 fast tiers + game audit

- Reworked stock-C64 `MATH_ATAN2_8` around compressed signed-magnitude log differences and generated final-angle tables. Exhaustive 65,536-vector validation keeps maximum error to one 1/256-turn phase unit.
- Final timings: **V1 50.441345 cycles mean (30–53)**; **V2/V3 46.953064 (30–48)**; **V4 remains exact at 48 fixed cycles**; **V5 imports the V2 fast tier at 46.953064**. All stock implementations use 0 extra ZP.
- V1 keeps the compact 512-byte table point. V2/V3 use 1280 bytes of ATAN2 tables. V5 adds the fast tier through three formerly unused 256-byte table pages, remapping the V2 donor's third extra page away from V1-owned data.
- Added hard V5 page-collision guards and exhaustive V5 result/cycle-vector parity against V2, including cold-load/no-`MATH_INIT` coverage. V5 now records **144,246 direct-import cases**.
- Added independent Custom Pareto pack `atan2_fast` (**0 ZP / 768 B**), so the selector accounts for the speed/RAM trade-off explicitly. At that ATAN2 revision, equal-weight extra-RAM points were **6021 / 6611 / 7371 / 6207 / 7557 B**; the 2026-09-20 multiplication refresh supersedes those selector figures.
- Pareto deep validation now covers **75,644 direct V2 cycle-parity cases**, including exhaustive ATAN2, plus exhaustive UMOD8 and the existing stress/ZP/deterministic checks.
- Added `docs/ATAN2_GAME_AUDIT_2026-09-17.md`, auditing Steel Ranger, Wolf64 and Quake64 against the project rule that an optimized general routine should not replace a cheaper discrete/direct-angle game representation without a real runtime need.

## 2026-09-14 — all-native signed kernel refresh

- Published exact per-routine native signed source mirrors under every profile's `resident/signed/multiply/native/` and `resident/signed/division/native/` trees, including V1/V5 and signed fixed-point/READY entries. These mirrors are byte-verified against the initialized resident executable by `tools/validate_published_signed_sources.py`; no resident PRG/REU payload changed.
- Converted every shipped `SMUL*` and `SDIV*` path to an independently owned signed executable kernel; immutable tables may still be shared.
- Split `SDIV32_32` and the remaining signed multipliers away from shared unsigned executable engines, without changing public ABI addresses, profile ZP budgets, or resident load/end ranges.
- Compacted safe signed multiply finalizers for a three-cycle path saving on affected entries.
- Same-corpus comparison confirms **−3 cycles** on every newly split/compacted SMUL path (V2–V4 SMUL16 was already native and is unchanged); the newly private `SDIV32_32` is also faster in all five profiles.
- Added zero-overlap executable tracing and dedicated 364,533-call signed division validation alongside the 264,999-call signed multiply validation.
- Removed the obsolete `multiply/unsigned_derived/` taxonomy.

# 2026-09-07 — Custom Pareto Builder

## 2026-09-14 — signed implementation taxonomy cleanup (superseded later the same day)

- Reorganized `resident/native_signed/` as `resident/signed/` so signed API semantics are no longer conflated with a native signed arithmetic kernel.
- Earlier in the day, signed multiplication artifacts were separated by implementation provenance. This intermediate taxonomy was superseded by the all-native signed kernel refresh above.
- Removed stale/mislabelled V2–V4 `smul16_native.*` publication artifacts; the active true-native source is now named directly as `smul16_practical_116zp.a`.
- Added `SIGNED_LINK_MAP.json`, profile-local signed READMEs, corrected segment/performance/selection documentation, and explicit division architecture terminology.
- Added `tools/validate_signed_layout.py` and `tools/validate_signed_multiply.py`; the latter currently passes 264,999 signed multiply calls across V1–V5.
- This was documentation-only at that stage; the later all-native refresh above changed signed resident internals while preserving the public ABI and profile resource contracts.

- Added a **build-time stock-C64 Pareto selector**. Give it a total ZP budget, optional exact extra-RAM budget, initialization policy and optional routine weights; it generates the fastest certified compatible V1/V2 combination that fits. There is no runtime dispatcher.
- Added `tools/pareto_wizard.py` for interactive game/demo integration and `tools/build_pareto.py` for scripted builds.
- Generated builds retain the same 45-entry stable API and emit `math_api.inc` plus `selection_manifest.json` containing exact ZP ranges, exact private-RAM ranges, initialization requirement, implementation provenance and SHA-256.
- Default equal-weight breakpoints: **31 / 36 / 60 / 147 / 176 / 221 ZP bytes**. At 31 ZP + zero extra RAM the builder reproduces V1 byte-for-byte; at 31 ZP + optional-init policy it reproduces V5 byte-for-byte; at 221 ZP it selects complete V2.
- Exact extra-RAM accounting now includes the actual emitted init helper rather than a conservative allowance. At that revision, the default points used 6021 / 6611 / 7371 / 6207 / 7557 bytes of extra private payload; the 2026-09-20 multiplication refresh supersedes those selector figures.
- At that revision, certified selectable packs included the independent 0-ZP/768-byte `atan2_fast` upgrade, V5 zero-ZP division/modulo/trig imports, initialized UMUL32, V2 UMUL8/SMUL8, the record UMUL16/UMUL24 pack, and native executable-ZP SMUL16. The 2026-09-20 refresh retires the redundant initialized-UMUL32 pack and updates the multiply packs. Workload weights can change the chosen pack at the same resource budget.
- Validation: 12 representative generated builds across reference/alternate maps, **45/45 entries and 4,172 calls each (50,064 common-API calls)**; 75,644 direct V2 cycle-parity cases including exhaustive ATAN2; exhaustive 65,536-case UMOD8; 50,144 additional SMUL16 cycle-parity cases; 25,000 mixed-workload iterations; 10,000 ZP-guard iterations; deterministic rebuilds; V1/V5 endpoint identity; and **12/12** invalid resource/configuration tests.

# 2026-09-06 — V5 Hybrid Low-ZP

- Renamed the project presentation to **C64 Math Library**; the stable 45-entry callable surface remains its public API.
- Added **V5 Hybrid Low-ZP**, a stock-C64 profile that keeps V1's 31-byte normal ZP window while importing selected faster V2 division/modulo/trigonometric paths.
- Direct gains vs V1: UDIV16 14.23%, UDIV24 9.37%, UDIV32/16 11.39%, UMOD16 13.97%, UMOD24 9.25%, UMOD32/16 11.35%, COS8 20.69%, SINCOS8 20.51%; UMOD8 improves 0.71%.
- Added deterministic source-derived hybrid builder with configurable `HYBRID_CODE` and no runtime dispatch overhead.
- Validated 45/45 stable entries and 4,172 calls on both reference and alternate V5 maps; 144,246 direct-import cases including exhaustive ATAN2 result/cycle parity; exhaustive UMOD8 and trig-domain checks; V2 cycle parity for certified imports; 31-byte ZP confinement with all 225 outside ZP bytes unchanged; 2,000 cold-load calls without `MATH_INIT`; deterministic rebuild and 8/8 invalid-map/config checks.
- Clarified non-reentrancy: sequential calls, including calls repeated inside ordinary loops, are fully supported.
- Reference V5 places its private 7680-byte hybrid region at `$A000-$BDFF` (RAM under BASIC ROM); applications must bank BASIC out while executing it or relocate `HYBRID_CODE`.

# Changelog

## 2026-09-14 — UMUL record upgrade + consolidated resource index

- Resident `UMUL16` now uses the qualified 17-ZP record-derived fused quarter-square kernel; V1/V5 preserve the persistent `UMUL32_READY` state contract.
- Resident `UMUL24` now uses the certified 24-ZP `reverse_24zp_carry` record kernel.
- V3/V4 Turbo32 now uses the stack-free 135-ZP `ram135` record-family compromise: reference ZP `$0A-$90`, legal origins `$02-$79`, with BEGIN/CALL/END measured at 326 / 728.947080 mean / 371 cycles.
- The absolute 606.337632-cycle UMUL32 record remains intentionally outside fixed profiles because it reserves hardware stack-page space; shipped fixed choices reserve 0 persistent stack-page bytes.
- At the 2026-09-14 record-upgrade checkpoint, Custom Pareto extra-private-RAM points were 6021 / 6611 / 7371 / 6207 / 7557 bytes; the 2026-09-20 multiplication refresh supersedes them.
- Added `docs/CONSOLIDATED_ROUTINE_TABLE.{md,csv}` plus machine-readable `validation/CONSOLIDATED_ROUTINE_TABLE.json`, covering all 45 stable entries in all five profiles plus V3/V4 Turbo and V4 QS16.


## 2026-09-06 — Documented LEAN FINAL / package audit

### Manual

- Added a **“Turbo modes in plain English”** explanation: REU-as-storage, zero-page-as-fast-workbench, BEGIN/CALL/END diagram, normal-vs-Turbo selection rule, and explicit explanation that the REU DMA installs the accelerator but does not perform the multiplication itself.
- Clarified that `build_source/` is generated on demand and intentionally absent from the distribution ZIP.

### Package cleanup

- Removed generated `build_source/reference` and `build_source/alternate` trees from the shipped ZIP. They duplicated build products, including two extra 16 MiB/512 KiB REU images, and are fully recreated by the supplied build commands.
- Removed `validation/baseline_reviewed_isqrt32/`, which documented the superseded slower clean ISQRT32 candidate and is not needed to validate the active fast kernel.
- Retained `validation/baseline_prior_final/` because it is meaningful evidence: the active binary-delta audit uses it to carry the prior exhaustive validation forward for unchanged routines.
- Renamed the mistyped `CARB_CHANGELOG.txt` to **`CSDB_CHANGELOG.txt`**.
- Added `docs/PACKAGE_CONTENTS.md` and a machine-readable package-hygiene audit.
- Removed two obsolete development-only validators: the old full-reference runner and the hard-coded prior-release ISQRT32 delta regeneration script. Current validation evidence and current portable validators remain.
- Removed unreferenced legacy `.bin`/`.labels` intermediates that are not consumed by the current assembly, documentation or validation paths.
- Corrected stale `SEGMENTS_GAME_MATH_FINAL.csv` paths that still pointed into the old archival `game_math_extension/build/` tree; they now identify the actual integrated PRG shipped in each profile.
- Corrected V4 `SEGMENTS.csv` rows that referred to separate V3-style segment binaries not shipped by the V4 streamlined profile; those ranges are now explicitly identified as integrated in the V4 PRG.
- No arithmetic, ABI, resident-code, Turbo-overlay or REU-data change from the documented Turbo FINAL.


## 2026-09-06 — Complete user manual / documented FINAL

### Documentation

- Added `USER_MANUAL.md`, a complete integration and usage manual covering profile selection, build and custom relocation, the public I/O block, initialization, all 45 stable entries, signed semantics, fixed-point/game math, V3/V4 REU setup, Turbo16/Turbo32 lifecycle and relocation, V4 QS16, compatibility helpers, performance guidance, validation, troubleshooting, and production integration checks.
- Added copy-paste examples that use the generated relocatable `math_api.inc` and its `MATH_X/MATH_Y/MATH_Z/MATH_N/MATH_D/MATH_Q/MATH_R` vector bases.
- Documented the distinction between generated relocatable vector bases and the lowercase byte aliases provided by fixed-reference includes.
- Documented C64 ROM/I/O banking and non-reentrancy/IRQ integration responsibilities that are outside the flat machine validator.
- Corrected the VICE examples in `docs/REU_GUIDE.md` to use the actual shipped `_game_math.reu` filenames.
- Updated the root README to make the complete manual the first integration document.

### Code/ABI

- **No arithmetic, resident-code, Turbo-overlay, REU-data, ABI, address-map, or performance change.** This is a documentation-only superseding package built from the validated Turbo FINAL code.

## 2026-09-06 — Relocatable Turbo16/Turbo32 extension

### Added

- Made V3/V4 Turbo16 and Turbo32 executable-ZP overlays genuinely source/build-time relocatable.
- Added `TURBO16_ZP_BASE`, `TURBO32_ZP_BASE`, `REU_TURBO16_BANK` and `REU_TURBO32_BANK` configuration symbols.
- Added canonical ACME-compatible overlay sources under `relocatable_source/turbo/`.
- REU images now contain freshly assembled overlays for the selected map rather than copied fixed bank-4/5 images.
- Generated V3/V4 caller includes expose the six Turbo lifecycle entries and actual configured overlay geometry.
- Added `docs/TURBO_RELOCATION.md`, `docs/TURBO_API.csv` and a dedicated machine validator.

### Compatibility

- The common stable surface remains **45 entries** on V1–V4.
- V3/V4 additionally expose **6 stateful Turbo lifecycle entries** (BEGIN/CALL/END for 16- and 32-bit multiply).
- Reference source builds reproduce all four resident PRGs and both V3/V4 REU images **byte-for-byte**; default Turbo behavior/performance is therefore unchanged.
- Turbo modes remain exclusive while active: normal/game math must not be called between BEGIN and END.

### Relocation proof

- Alternate Turbo16 ZP: `$3E-$AE` -> `$40-$B0`.
- Alternate Turbo32 ZP: `$0A-$FA` -> `$06-$F6`.
- V3 Turbo banks: `$04/$05` -> `$00/$01`.
- V4 Turbo banks: `$04/$05` -> `$28/$29`.
- **17,164 product calls PASS, plus 32 BEGIN/END lifecycle calls (17,196 Turbo API calls total)** across V3/V4 reference+alternate maps.
- END restores the caller's previous ZP bytes exactly.
- A second BEGIN/CALL/END batch succeeds after the self-modified overlay has been swapped back to REU.
- Reference and alternate cycle vectors are identical: **zero runtime relocation-cycle cost**.
- ACME 0.97 independently reproduces the Turbo16/Turbo32 overlays for both profiles/maps byte-for-byte.
- Configuration regression expanded from 21 to **27** cases with Turbo ZP/bank boundary and collision tests.
- Added endpoint execution sweep (pre-135-ZP Turbo32): Turbo16 `$02/$8F`, Turbo32 `$02/$0F`, V3 Turbo banks `$06/$07`, V4 Turbo banks `$FE/$FF`: **3,556 products PASS** with cycle-vector identity.
- Fixed the bundled deterministic assembler path for the valid Turbo16 `$8F` endpoint; ACME 0.97 independently reproduces the corrected 113-byte overlay exactly.

## 2026-09-06 — Fast ISQRT32 follow-up

### Changed

- Replaced the first clean 16-step restoring ISQRT32 with a faster independently derived hybrid.
- The high byte of the final 16-bit root is obtained exactly from `ISQRT16(N32 >> 16)`; only the eight remaining base-4 digits are refined.
- Public ABI is unchanged: exact `floor(sqrt(N32))`, `N32` preserved, `C=0`.
- V1–V3 reuse their existing square planes for exact residual initialization.
- V4 initializes two 256-byte square planes at `$9800-$99FF` for the fastest residual setup; this adds 512 resident table bytes to the 16M-REU profile.
- Removed the now-dead 16-step ISQRT32 entry body while retaining the independently written four-pair refinement helper used by the new routine.

### Performance

Same 4,130-case deterministic corpus as the preceding reviewed release:

| Profile | Previous mean | Fast mean | Improvement |
|---|---:|---:|---:|
| V1 | 2209.623487 | 1378.900969 | 37.60% |
| V2 | 1872.805327 | 1198.619613 | 36.00% |
| V3 | 1872.805327 | 1197.859322 | 36.04% |
| V4 | 1872.805327 | 1046.622518 | 44.11% |

### Validation

- 5,097 dedicated correctness/input-preservation cases per profile: PASS.
- 4,130-case directly comparable performance corpus per profile: zero errors.
- Alternate source map remains 45/45 entries and 4,172 calls per profile.
- Fast-kernel delta audit confirms no resident changes outside the documented ISQRT32 target/support ranges and V4 square planes.

## 2026-09-06 — Source-Relocatable Reviewed Release

### Changed

- Replaced the earlier post-build binary-relocation release with a genuine source-level, assembly-time configurable build.
- Added symbolic configuration for the stable C64 code/API/table regions, independent game API block, public I/O, ordinary scratch, normal ZP and V2–V4 native SMUL16 executable-ZP placement.
- Added stable REU data-bank configuration for V3/V4 and V4 QS16 eight-bank relocation.
- Kept fixed Turbo16/Turbo32 overlay ownership outside the stable relocatable API contract.
- Replaced the old third-party-derived ISQRT32 recurrence with an independently written restoring base-4 implementation. Public ABI is unchanged: exact `floor(sqrt(N32))`, input preserved, `C=0`.

### Fixed

- Removed the earlier broken/descriptive-only reference configuration problem by using consumable assembly configuration files for every profile.
- Added hard failures for ZP overflow and `$00-$01` processor-port overlap rather than allowing wrapped addresses.
- Added C64 region collision, `$DF00-$DFFF` I/O-page and page-alignment checks.
- Corrected V4 REU scratch ownership to account for the full four-byte C64-side buffer.
- Removed stale ISQRT32 non-commercial/provenance warning from the active implementation documentation.
- Corrected stale V3/V4 license notes that referred to reference bundles absent from the streamlined package.
- Updated all public ISQRT32 performance tables to the replacement implementation.

### Validation

- Reference source builds reproduce the corrected V1, V2, V3 and V4 resident PRGs byte-for-byte.
- Alternate-map execution passes all 45 public entries in each profile: 180/180 entries and 16,688 machine calls total.
- V3/V4 alternate tests verify the generated REU images and relocated C64-side REU destination.
- Deterministic clean rebuild passes for all eight reference/alternate PRGs.
- Configuration regression passes 21 cases covering valid reference/alternate maps plus ZP wrap/overlap, processor-port protection, resident/I/O collisions, alignment and V3/V4 REU-bank constraints.
- The first independent ISQRT32 replacement passed 5,097 correctness/input-preservation cases per profile; it is superseded by the faster hybrid above.
- Binary-delta auditing preserves applicability of the prior exhaustive evidence to all unchanged routines.

## 2026-09-06 — Game-Math FINAL baseline

- Added 19 game/fixed-point entries to the signed+unsigned integer API, bringing the stable surface to 45 entries.
- Added 32/32 divmod, fixed-point shifts, reciprocal, trig/atan2, ISQRT16/32 and distance helpers.
- Fixed V2–V4 native SMUL16 installation/package defect and validated corrected executable-ZP installation.
