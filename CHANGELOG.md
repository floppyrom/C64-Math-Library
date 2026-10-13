2026-10-13 ISSUE39 ROOT RELEASE HISTORIC DIV/MOD HASH RESEAL
- Replayed all comparable unsigned proofs with exactly the same division code. Historical reports updated only their full-resident provenance hashes for the ISQRT16-only byte-island release; numeric results, ABI, operands and cycle-stream hashes remained unchanged. validation/review/ISSUE39_ROOTS_LEGACY_PROVENANCE_RESEAL.json.

2026-10-13 ISSUE39 INTEGER ROOT NATIVE VICE RELEASE PROOF
- Native x64sc old/new full-resident ISQRT16 and ISQRT32 validation: 768 calls across V1/V2/V3/V5, exact public output, input, carry, return-path sentinels and stack invariants. Full root proof: validation/review/ISSUE39_ROOTS_NATIVE_VICE_2026-10-13.json. V4 unchanged; cycle counts from the independent mini6502 proof only. Issue #39 remains OPEN.

2026-10-13 ISSUE39 INTEGER ROOTS SAME-ISLAND FAST SEED
- ISQRT16 exact floor-root public source upgrade on V1/V2/V3/V5: 294 bytes total replacement of existing ISQRT16 code island, includes 256-byte upper seed table and reuses $9800/$9900 squares. No PRG length/ZP changes. V4 REU root unchanged.
- Rebenchmarked all 65536 ISQRT16 operands and 4130 common ISQRT32 operands, with exact source reference/alternate and V5 hybrid regeneration, standalone/public catalog and all-family ABI checks. Native VICE pending. Issue #39 remains OPEN. docs/ISSUE39_INTEGER_ROOTS_SOURCE_RELEASE_2026-10-13.md

2026-10-13 ISSUE39 V2 UDIV32/16 PAGE PHASE SOURCE OWNERSHIP AUDIT
- Bounded source-assembled V2–V5 shared 32/16 kernel page-phase screen: 14 isolated +/-4..48-byte origin shifts rejected because neighbouring source-owned bytes were occupied. No candidate qualified for timing; this is a geometry no-gain only, not a global optimality claim.
- No PRG, public ABI, ZP, stack, runtime cycles or profile defaults changed. Full exact source baseline and rejected origins recorded in docs/ISSUE39_V2_3216_PAGE_PHASE_FEASIBILITY_2026-10-13.md and validation/review/ISSUE39_V2_3216_PAGE_PHASE_RESEARCH.json. Issue #39 remains OPEN.

2026-10-13 ISSUE39 V1 32/16 TRANSITIVE 32/32 PERFORMANCE PUBLICATION
- Source V1 32/16 hot-path relocation also accelerates 32/32 fallback for a bounded class. Under exact current same-input corpus, V1 UDIV32_32 mean 335.825577 -> 335.750824 and UMOD32_32 399.676833 -> 399.557185. V5 donor remains unchanged. Updated PERFORMANCE.md, V5 HYBRID_PERFORMANCE.csv and SHA-pinned bound checks, no production binary change. Keep issue #39 OPEN.

2026-10-13 ISSUE39 HISTORICAL DIV/MOD REPLAY PINNING AFTER V1 32/16 SOURCE PROMOTION
- Recovered exact prior PR99 V1 resident bytes from SHA-pinned current V1 by reversing ONLY the new 7-byte cold handler, 111-byte 32/16 continuation displacement and unroll return JMP; verify reverse SHA equals immutable prior main before playing historical PR78/PR81 24/8 proofs.
- Updated V2 UMOD8 history against exact SHA-pinned current V2, restoring only the 104 changed wrapper/helper bytes for the original exhaustive 65536-case paired A/B. V5 unchanged-source check short-circuits before invoking historical PR71 inverse. Historical tests and general profile correctness remain independent; issue #39 OPEN. docs/ISSUE39_V1_3216_OOL_ZERO_PRODUCTION_2026-10-13.md

2026-10-13 ISSUE39 V1 32/16 SOURCE INSTALLED NATIVE VICE GATE
- Pinned real x64sc executed 384 old/new complete resident calls across V1 and V5, two public 32/16 aliases and 48 matching operands each. No Q32/R16/carry/N/D/ROM-underlay or output-dump differences. V5 32/16 donor behavior unchanged. Native cycle timing NOT measured.
- Source-built reference/alternate maps, 56 stable APIs, full 822,050 unsigned / 364,533 signed, comparable 136,335, and package/standalone checks passed. Exact source/PRG SHA evidence and native report sealed. Issue #39 still OPEN. docs/ISSUE39_V1_3216_OOL_ZERO_PRODUCTION_2026-10-13.md

2026-10-13 ISSUE39 V1 32/16 RELOCATABLE ZERO-HANDLER PRODUCTION
- Production-staged symbolic V1 32/16 cold zero-handler source: source generator, reference/alternate maps and V5 hybrid refreshed. Main success path -1 cycle in paired CPU model, divide-by-zero +2. 56 stable APIs and resident lengths unchanged; no normal ZP growth.
- Full 822,050 unsigned, 364,533 signed and 136,335 same-input public calls passed. Source-built installed-image native VICE must still pass before merge. Issue #39 remains OPEN. docs/ISSUE39_V1_3216_OOL_ZERO_PRODUCTION_2026-10-13.md

2026-10-13 ISSUE39 V1 UDIV32/16 RARE-ZERO OUT-OF-LINE RESEARCH
- Research-only V1 32/16 optimization: move seven-byte divide-zero cleanup to verified empty $44F0, invert branch, shift 111-byte low-word continuation and adjust $1B6A unrolled-loop backlink. No installed resident/API/normal-ZP changes.
- 15,826 identical operand pairs / 31,652 CPU-model public calls: every tested nonzero divisor saves 1 cycle; divide-zero adds 2 cycles, explicit tradeoff. Official weighted deltas UDIV32/16 -0.834005 and UMOD32/16 -0.734311. Actual native VICE x64sc 192 complete old/new calls passed with exact outputs. Source/alternate/hybrid production integration NOT yet qualified; issue #39 remains OPEN. docs/ISSUE39_V1_3216_RARE_ZERO_OUTOFLINE_2026-10-13.md

2026-10-13 ISSUE39 UNSIGNED DIVMOD COMPLETION MATRIX (DOC-ONLY)
- Published exact per-family evidence/disposition and remaining closure requirements after PR #97, prioritizing unrestricted 32/16 architecture and preventing caller-opt-in specialists from being misrepresented as universal defaults.
- No arithmetic source, resident binary, profile, public ABI, timing measurement or resource allocation changed. No new native VICE qualification claimed; issue #39 and its unsigned-family checkbox remain OPEN. docs/ISSUE39_UNSIGNED_DIVMOD_COMPLETION_MATRIX_2026-10-13.md

2026-10-13 ISSUE39 NATIVE VICE GENERIC U24 TXA PUBLIC RESIDENT
- Ran 960 true x64sc native emulator calls: 48 identical inputs per old and new complete resident, UDIV24/UMOD24 in all five profiles, zero Q where promised, R, carry, input/high sentinel errors. V5 executed RAM under BASIC ROM. No native cycles or REU/VIC wall-time measured.
- Pinned official headless VICE r46274 package SHA, source harness, operand/output digest evidence, both changelogs, docs, status and checksums; full 822,050 unsigned and 364,533 signed emulated validation already passed. Issue39 unsigned family OPEN. docs/ISSUE39_U24_TXA_SOURCE_INTEGRATION_2026-10-13.md

2026-10-13 ISSUE39 GENERIC U24 HIGH-GT LIVE-X PRODUCTION SOURCE
- Source-installed generic 24-bit N2>D2 live-X high-byte subtraction LDA N2 -> TXA for V1/V2/V3/V4; V5 inherited donor code refreshed by source builder. Stable 56-entry API, resident PRG lengths, REU images and normal ZP unchanged. Full source reference/alternate maps and paired current-resident full public ABI qualified; V2–V5 dedicated UMOD24 layout-phase tradeoff recorded.
- Full five-profile 822,050 unsigned, 364,533 signed and 136,335 same-input performance calls passed. Documentation, independent/full-input ranking tables, standalone sources, both changelogs, release-status PRG hashes and checksums regenerated. No native VICE calls have yet been claimed; require separate native proof before production merge. Issue #39 OPEN. docs/ISSUE39_U24_TXA_SOURCE_INTEGRATION_2026-10-13.md

2026-10-13 ISSUE39 GENERIC U24 HIGH-GT TXA SOURCE AUDIT
- Source-reassembled V1/V2 unrestricted UDIV24 high-byte subtraction with preserved prior LAX-held X: LDA N2 -> TXA, saving 2 CPU cycles and 2 instruction bytes on reached high_gt path. {'v1_balanced': {'MATH_UDIV24': {'official_delta': -0.8586156111929307, 'official_faster': 2035, 'official_slower': 0, 'highgt_delta': -1.998046875}, 'MATH_UMOD24': {'official_delta': -0.6844816484224082, 'official_faster': 530, 'official_slower': 0, 'highgt_delta': -1.9833984375}}, 'v2_pareto_fast': {'MATH_UDIV24': {'official_delta': -0.8550389227856091, 'official_faster': 2035, 'official_slower': 0, 'highgt_delta': -1.9892578125}, 'MATH_UMOD24': {'official_delta': 0.003219575016097875, 'official_faster': 13, 'official_slower': 18, 'highgt_delta': 0.0078125}}}
- 34,088 identical input pairs / 68,176 full CPU calls, source-built original matched current resident SHA; zero Q24/R24/carry/input/high sentinel/stack mismatches. No resident/API/normal-ZP changes or native timing claims. V3/V4/V5 builds pending source promotion. Both changelogs, docs, release metadata/hashes updated; issue #39 OPEN. docs/ISSUE39_U24_HIGHGT_LIVE_X_2026-10-13.md

2026-10-13 ISSUE39 UDIV8 PREFIX PUBLIC ABI SOURCE SWEEP
- Source-synthesized six established 8-bit compare/SBC quotient prefixes (K8/12/16/20/24/28) in two caller-owned RAM maps; validated exact full public Q8/R8/carry/ownership/stack against the current SHA-pinned V1–V5 resident UDIV8. 357,720 identical paired operands and 715,440 complete CPU calls, 9 workloads, 0 mathematical or promised-ABI errors.
- Published profile-specific code-byte, mean/tail cycle and workload fingerprints and bounded manual/OptiSearch-informed architecture ranking. Candidates need caller-owned RAM and 1 scratch ZP, not resident source-owned code resources; no default source/binary/API/normal ZP change or native-VICE timing claim. README/manual, both changelogs, release-status metadata and checksum seal updated. Issue #39 OPEN. docs/ISSUE39_UDIV8_PREFIX_PERPROFILE_SCREEN_2026-10-13.md

2026-10-13 ISSUE39 U24 D8 SMC CURRENT PUBLIC OPTIN SCREEN
- Source-replayed already-published 24÷8 self-modifying RAM specialist against exact current V1–V5 full public UDIV24/UMOD24 residents at two relocated RAM origins: 65,080 identical paired eligible inputs / 130,160 full 6502 CPU calls, zero contracted Q24/R24/carry/input/stack errors. Strict N2>0, D8!=0, D1=D2=0 precondition; D=0 and 24-bit divisors explicitly out of scope.
- Caller-opt-in direct entry saves ~46 cycles in V1 and ~18/23 cycles in V2–V5 on tested eligible random D8 inputs, but general default path is unchanged because unqualified dispatch overhead/extra-Q3 side effects are unresolved. Code RAM must be writable and not reentered; no normal ZP growth. Exact SHA-pinned class/operand/cycle evidence, docs, README/manual, two changelogs, release status/checksums published. No new native VICE time claim. Issue #39 OPEN. docs/ISSUE39_U24_D8_RAM_SMC_CURRENT_OPTIN_2026-10-13.md

2026-10-13 ISSUE39 U16 OPTISEARCH PUBLIC ABI AND WORKLOAD AUDIT
- Replayed two already-published Repose/OptiSearch 16-bit sources across all SHA-pinned V1-V5 public ABI residents at two RAM maps: 86,652 paired operands / 173,304 actual 6502-model calls, zero correctness/ownership/stack failures. V1 modulo quotient alias is explicitly not replaced by remainder-only candidate.
- 323-byte 2-ZP biased producer wins official mean cycles on some profiles but regresses on V2-V5 uniform workload; 976-byte zero-ZP direct remainder source is slower than current resident on official inputs. No default promotion; source and standalone liftability preserved. New full class/cycle SHA JSON, docs, both changelogs, README/manual, status and hashes. No resident/ABI/ZP change. No new native VICE timing; issue39 remains OPEN. docs/ISSUE39_U16_OPTISEARCH_PUBLIC_ABI_MATRIX_2026-10-13.md

2026-10-12 ISSUE39 OPTISEARCH U32BY32 V1V5 PUBLIC ABI RESOURCE AUDIT
- Screened three already-public Repose/OptiSearch unsigned 32/32 donor assemblies at two code-RAM origins against exact current V1–V5 resident public UDIV32/32 and UMOD32/32 contracts: 131,330 paired operands / 262,660 complete 6502 calls, zero arithmetic/R/C/N/D/SP/sentinel errors.
- All donor/profile/API official corpora contain regressing calls. Larger code-RAM and 4 ZP or 4 scratch RAM obligations remain; no fixed-profile default replacement justified. Full per-class SHA-pinned evidence, docs, README/manual references, both changelogs, release metadata and package hashes. No shipped binary/API changes, no native VICE bus timing claim, campaign issue 39 OPEN. docs/ISSUE39_U3232_OPTISEARCH_ABI_RESOURCE_SCREEN_2026-10-12.md

2026-10-12 ISSUE39 114BYTE POW2 32BY16 OPT-IN SPECIALIST
- Qualified 114-byte caller-opt-in 32/16 D=power-of-two producer, providing both full quotient and remainder public-buffer contracts; 0 new ZP, 0 extra nested JSR frames. Exact five resident profiles, two legal RAM maps, 67,520 matched operands / 135,040 CPU executions, zero Q/R/C/N/D/sentinel/SP/relocation errors.
- Large gains on the explicit power-of-two workload, with V2–V5 slower cases at high divisor exponents: **no default promotion**. No shipped PRG or public ABI modification. Source, full JSON, README/manual and both changelogs published. Native VICE cycles not claimed. Issue #39 remains OPEN. docs/ISSUE39_U3216_POW2_OPTIN_2026-10-12.md

2026-10-12 ISSUE39 90BYTE POW2 32BY16 OPT-IN SPECIALIST
- Qualified 90-byte caller-opt-in 32/16 D=power-of-two producer, providing both full quotient and remainder public-buffer contracts; 0 new ZP, 0 extra nested JSR frames. Exact five resident profiles, two legal RAM maps, 67,520 matched operands / 135,040 CPU executions, zero Q/R/C/N/D/sentinel/SP/relocation errors.
- Large gains on the explicit power-of-two workload, with V2–V5 slower cases at high divisor exponents: **no default promotion**. No shipped PRG or public ABI modification. Source, full JSON, README/manual and both changelogs published. Native VICE cycles not claimed. Issue #39 remains OPEN. docs/ISSUE39_U3216_POW2_OPTIN_2026-10-12.md

2026-10-12 ISSUE39 N24 TO U24 DONOR NO-GAIN AUDIT
- Five exact-profile research screen of N24->resident UDIV24 reuse for 32/16 quotient and modulo: 30-byte RAM helper, two RAM maps, 11,580 identical operands / 23,160 complete CPU calls, zero arithmetic/Q/R/C/input/SP/sentinel errors.
- N24 with D>=256 loses in all five profiles on 128 seeded operands per API; Q0/N16 niche wins do not justify universal promotion and 12-byte N16 opt-in is already available. Research only, no production code, API, ZP or PRG changes. Native VICE not claimed.
- Source-backed JSON, docs, release-status and checksums; issue #39 unsigned family remains OPEN. docs/ISSUE39_N24_TO_U24_DONOR_SCREEN_2026-10-12.md

2026-10-12 ISSUE39 12BYTE N16 OPTIN 32BY16 SPECIALIST
- Validated 12-byte opt-in 32/16 specialization for known N16, depending on installed UDIV16; no public redirect, no full-width latency tax. Five-profile two-map paired 56,680 operands / 113,360 6502 calls, zero Q/R/C/inputs/SP mismatches.
- V1 N16 D>=256 about 478/481 cycles faster; V2–V5 about 381/384 faster. V2–V5 D8 about 274 cycles slower, so preserve the precondition for performance. Native x64sc 256 old/new calls on current V1/V2 full resident pass; no native timing or V3–V5 native claim.
- Published individually liftable library-dependent assembly, reproducible test/provenance, both changelogs, docs, release status and checksums; no shipped PRG/API or ZP budget modification. Issue #39 remains OPEN. docs/ISSUE39_U3216_N16_12BYTE_OPTIN_2026-10-12.md

2026-10-12 ISSUE39 U3216 N16 DHI-GATED DONOR FIVE-PROFILE SCREEN
- Compared 33-byte in-memory divisor-high-gated 32/16 N16->16/16 reuse on exact V1–V5 residents, public UDIV32/16 and UMOD32/16, four D1 thresholds (1,4,16,64): 79,130 old/new operand pairs / 395,650 public CPU executions, zero Q/R/C/input/SP errors.
- Narrow-divisor reuse is filtered out; full-width numerator controls still incur +17 cycles. Research-only library-dependent donor, additional 2 stack bytes on delegation, $E100 under KERNAL ROM unqualified. Exact per-profile workload and input proof, source, docs, release metadata, both changelogs, SHA256SUMS published, **no production binary/ABI changes**. #39 stays OPEN. docs/ISSUE39_U3216_N16_DHI_GATED_SCREEN_2026-10-12.md

2026-10-12 ISSUE39 N16 DELEGATE U32BY16 FIVE-PROFILE SCREEN
- Tested 26-byte ephemeral N16->UDIV16 producer reuse on V1–V5 exact resident public UDIV32/16 and UMOD32/16 entries; 79,130 input pairs, 158,260 old/new calls, no Q/R/C/input/stack mismatches.
- V1 N16-target ~469 cycles faster and N16/D8 ~542 faster; V2–V5 N16-target ~366 faster but N16/D8 ~292 slower; all full-width-uniform operands +17. Reject default, preserve candidate/source-backed detailed report. Ephemeral E100 code not native-ROM/bank qualified. No binary change. Campaign #39 open. docs/ISSUE39_U3216_N16_DELEGATE_CURRENT_MAIN_2026-10-12.md

2026-10-12 ISSUE39 V2 UMOD8 GUARD D24 EXHAUSTIVE SCREEN
- Full-domain 65,536 N/D calls, 59,136 two-route checks, 2,277 direct candidate calls. V2 D>=24 guard gives the lowest measured mean: 52.204453; D>=25 52.274643, D>=32 52.845413. All higher cutoffs lose overall; no default binary/ABI/ZP/stack change. Source/data, docs and SHA256SUMS updated; issue #39 open. docs/ISSUE39_V2_UMOD8_GUARD_THRESHOLD_SWEEP_2026-10-12.md

2026-10-12 ISSUE39 V2-V5 U16 D-HIGH CUTOFF SWEEP (RESEARCH ONLY)
- Tested 17 existing-size CPX D1 dispatch cutoffs for UDIV16 and UMOD16 in unchanged V2/V3/V4/V5 images. Exact current resident SHA pins; 4,201 UDIV16 and 3,177 UMOD16 inputs per candidate/profile, preserved Q/R/C, N/D, SP and modulo quotient side effect. 64 combinations (cutoffs 1–14) fail correctness.
- Cutoff 16: UDIV16 +0.054035 cycles mean (9 faster,10 slower); UMOD16 -0.116147 cycles mean (11 faster,7 slower). No universally zero-regression non-default candidate; retain cutoff 15. Published complete per-class source-backed evidence, manual, both logs and checksums; no resident/source/API change. Issue #39 unsigned campaign OPEN. docs/ISSUE39_V2V5_U16_D1_CUTOFF_SCREEN_2026-10-12.md

2026-10-12 ISSUE39 V1 68-BYTE RAM SMC 24/8 DIVMOD RELEASE
- V1 bounded 24/8 DIV/MOD producer 61→68 executable bytes, fits existing 84-byte island. Writable executable RAM, no reentrancy/ROM support; prior 61-byte fallback retained. V2–V5 unchanged, no public ABI/ZP/stack/resident-size growth.
- Paired same-input UDIV24 166.190196→165.228277, UMOD24 234.433355→231.489375; D8 stress 976.350000→927.934314. 48,388 paired public calls, zero regressions; 6,344 portable two-map calls, 384 native VICE full-resident calls (not cycle timings).
- Complete five-profile unsigned/signed, common benchmark, reference/alternate relocation and binary isolation; both changelogs, performance tables, release metadata, and SHA checksums rebuilt. #39 remains OPEN. docs/ISSUE39_V1_24BY8_SMC_INTEGRATED_RELEASE_2026-10-12.md

2026-10-12 ISSUE39 V1 24/8 RAM SELF-MOD SPECIALIST CURRENT-61-SCREEN AND PORTABLE SOURCE
- Source-backed 68-byte writable-RAM/self-modifying optional V1 24/8 producer tested against actual released 61-byte core, not the older PR78 69-byte baseline. 48,388 full public 6502 old/new calls and 6,344 independent two-map standalone calls pass, zero arithmetic/flag/input/stack errors or slower pairs.
- Canonical UDIV24 166.190196->165.228277, UMOD24 234.433355->231.489375; 4080-pair N24/D8 976.350000->927.934314. Retain in standalone portfolio, **NOT** shipped resident, requires writable RAM/exclusive non-reentrant code and N2>0,D1=D2=0,D0>0. Both changelogs, research evidence, catalog, documentation, SHA256SUMS updated; no profile binary changes. Issue #39 stays OPEN. docs/ISSUE39_V1_UDIV24_ACCUMULATOR_SMC_SCREEN_2026-10-12.md

2026-10-12 ISSUE39 V1 ACCUMULATOR FULL-RESIDENT NATIVE VICE 384-CALL CERTIFICATE
- Native VICE x64sc full-resident proof supplements the earlier isolated source-kernel test: exact SHA-pinned PR78 versus released PR81 V1 residents, MATH_INIT plus true MATH_UDIV24/UMOD24 public-entry JSRs, 96 same-input pairs per API per resident, 384 native calls total, zero oracle, flag, input preservation, stack or old/new output errors.
- Full-resident result applies to Q/R/C and public ABI correctness only, NOT VICE cycle counts. No source code, public API, code size, profile binary, standalone pickup or ranking changed. Detail: docs/ISSUE39_V1_24BY8_FULL_RESIDENT_NATIVE_VICE_2026-10-12.md, evidence: validation/review/ISSUE39_V1_24BY8_ACCUMULATOR_FULL_RESIDENT_NATIVE_VICE.json. Issue #39 and unsigned family stage remain OPEN.

2026-10-12 ISSUE39 UMOD16 BIASED OPTISEARCH DONOR CURRENT-MAIN SCREEN
- Independently re-screened Repose/OptiSearch standalone UMOD16 biased donor against current V2–V5 UMOD16 complete entries: 27,280 same-input emulator calls across two RAM layouts, exact remainder/carry, inputs and stack.
- Overall 198.601173→185.826393 cycle mean but 1,391/1,705 inputs slower, random input 80.490234→111.772461 and 667 Q16 differences; +262 code RAM, +2 ZP and nested JSR stack. Retain as a standalone specialist, NOT default resident replacement.
- Report docs/ISSUE39_UMOD16_BIASED_CURRENT_MAIN_DECISION_2026-10-12.md; no resident binaries, public performance rankings or stable ABI modified. Issue #39 remains open.

2026-10-12 ISSUE39 V1 ACCUMULATOR-REMAINDER 61-BYTE 24/8 DIVMOD RELEASE
- V1 shared UDIV24/UMOD24 short-divisor kernel: keep partial R in A across all 24 iterations, 69→61 bytes, 23 padded bytes in the original 84-byte owned island. Zero new normal ZP/stack, stable API/addresses and resident size, V2–V5 byte-identical.
- 48,388 paired prior/new complete public CPU calls, no ABI errors or slower pairs; canonical same-input UDIV24 170.238165→166.190196, UMOD24 246.822279→234.433355. Native x64sc 128 isolated source-kernel correctness calls; full-resident native not claimed.
- Five-profile unsigned 822,050 and signed 364,533 calls; 136,335 same-input and 53,760 small-workload calls; historical parent reproducibility, reference/alternate source relocation, V5 isolation. Standalone mirrors, performance tables, release/checksums and docs refreshed. Campaign #39 remains OPEN. docs/ISSUE39_V1_UDIV24_ACCUMULATOR_RELEASE_2026-10-12.md

2026-10-12 ISSUE39 V1 24/8 ACCUMULATOR-REMAINDER CANDIDATE SCREEN (NO RESIDENT CHANGE)
- PR #79 (part of #39) screens a 61-byte accumulator-resident partial remainder against the merged PR #78 69-byte shared-subtraction V1 24/8 core. Zero additional ZP/stack, all public entry addresses and shipped binaries unchanged.
- Reproducible 48,388 old/new complete public UDIV24/UMOD24 6502 calls, no incorrect Q/R/C/N/D/stack and zero slower cases. Official UDIV24 170.238165->166.190196; UMOD24 246.822279->234.433355; 4,080 full-N24/D8 pairs 1202.660784->976.350000, all faster. These are candidate results, not new release rankings.
- Native x64sc and full integrated source/release, historical proof, checksum and main-CI gates remain necessary before any routine promotion. Full issue #39 family campaign remains open. Documentation: docs/ISSUE39_V1_UDIV24_ACCUMULATOR_SCREEN_2026-10-12.md.

2026-10-12 ISSUE39 V1 24/8 SHARED-SUBTRACTION DIVMOD CORE 69 BYTES
- Source-backed V1 UDIV24/UMOD24 shared 24÷8 producer: 84->69 bytes; merged carry-aware subtraction path and cleared the 15 freed trailing bytes. No extra ZP/stack or change to ABI, public addresses, resident PRG length, or V2-V5 binaries.
- 48,388 paired prior/live full-public-entry machine calls, zero arithmetic or carry failures and zero slower cases. Canonical UDIV24 170.726699->170.238165, UMOD24 248.317450->246.822279 cycles; 4,080 N2/D8 targeted cases 1220.796->1202.297 with 3,779 faster, none slower per operation.
- Independent native VICE x64sc 256 old/new resident calls verify Q/R/C and preserved inputs against mathematical oracle; not native cycle timing. All-profile unsigned 822,050, signed 364,533, common 136,335 and seven-class 53,760 machine-code tests pass.
- Generated reference/alternate sources, stable executable mirrors, public rankings, docs, release metadata and checksums synchronized. V5 reference remains byte-identical at SHA256 5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222. Issue39 overall unsigned DIV/MOD campaign stays OPEN.
- Details: docs/ISSUE39_V1_UDIV24_SHARED_SUBTRACTION_RELEASE_2026-10-12.md

2026-10-12 ISSUE39 V1 24/8 SHARED-SUBTRACTION EXPERIMENT (NO RESIDENT CHANGE)
- Added 69-byte in-memory V1 24/8 candidate vs shipped 84-byte loop, source-backed paired public UDIV24/UMOD24 ABI regression veto and seven-workload/stress screen; 0 extra ZP/stack, no shipped bytes or ABI altered. OptiSearch/manual synthesis remains open. See docs/ISSUE39_V1_UDIV24_SHARED_SUBTRACTION_SCREEN_2026-10-12.md.

2026-10-12 ISSUE39 STANDALONE DIRECT-CHAIN UMOD16 ZERO-ZP SPECIALIST
- Published self-contained symbolic Repose/OptiSearch UMOD16 direct-chain donor with C64ML success/zero carry normalization and quotient-buffer preservation; zero ZP, 976 bytes code/data, two ordinary RAM scratch bytes, two nested stack bytes.
- Official 1,705-pair identical-input mean 209.868 cycles (V2-V5 198.601); therefore a memory-budget alternative, not a speed winner. Three relocations/5,115 emulator calls and 192 native x64sc correctness calls pass; native cycle timings not claimed. Source, independent CI proof, standalone pickup, backlog and checksum/package records synchronized.

2026-10-12 ISSUE39 ZERO-ZP ALIGNED UDIV32 STANDALONE PICKUP
- Recovered Repose's independently assembleable aligned UDIV32 quotient+remainder engine: 325-byte entry + 251-byte tail, 576 code bytes, zero ZP and four ordinary scratch RAM bytes. Source-only, not a resident change. Public ABI Q/R/C and preserved N/D/stack validated at three address/ordinary RAM placements.
- Paired current-main 2,729-input corpus: mean 408.012 cycles overall, 196.890 on 2,048 uniform random operands; V2-V4 resident is 242.549 overall, 193.660 random. Explicitly a zero-ZP memory-saving option, NOT a speed winner. Three-map 8,187-call source/corpus verifier with original generated segment SHA proof, plus 192 native x64sc correctness calls. Expanded generic standalone CI to five kernels, 16,095 calls, and native VICE reproducer to 960 calls.
- Updated standalone picker/backlog, pickup docs, both changelogs, checksum package audit. Unchanged V1-V5 residents, REU images, stable API, and canonical benchmark ranks. Issue39 recovery campaign remains open.

2026-10-12 ISSUE39 ZERO-ZP UMOD32 RANDOM-WIDE-DIVISOR STANDALONE SPECIALIST
- Published individually configurable Repose aligned UMOD32 donor (475 executable bytes) plus 21-byte public carry adapter. Uses zero ZP but four bytes of ordinary RAM scratch and an additional JSR frame. Q32 remains untouched; R32, carry and N/D are exact.
- Original donor segment SHA parity and official 1,705-pair same-input corpus checked across two RAM maps (3,410 source-executed calls), plus extended three-map standalone integration validator and 192 local native VICE correctness calls.
- Default standalone RAM placement: 190.867 average cycles on the 1,024 random-input subset (V2-V4 199.833), but 476.938 across the full 1,705-case benchmark (V2-V4 279.620). This is NOT a general-purpose winner; no resident profile/ABI/REU artifacts changed.

2026-10-12 ISSUE39 STANDALONE FAST-KERNEL RELOCATION AND NATIVE VICE
- Added individually editable/readdressable UDIV16, carry-corrected UMOD16 and specialist UDIV32 sources under routines/standalone_lab/portable. Test coverage: 9,657 independent emulator calls across three RAM/ZP layouts, plus 576 native x64sc correctness calls across two RAM layouts. New CI gate recompiles and checks quotient, remainder, carry, unchanged N/D, stack and code.
- Corrected a duplicated internal UDIV32 source label without changing any generated opcode, 544-byte machine code or published timing. The original fixed-map modules and records remain available. The isolated kernel cycle costs are layout-specific; no new V1-V5 public resident implementation or stable profile performance ranking is changed. Issue39 standalone inventory remains open.

2026-10-12 ISSUE39 STANDALONE FAST-KERNEL COLLECTION
- Published standalone_lab UDIV16, carry-corrected UMOD16 and specialized UDIV32 ZP-tail symbolic assembly with explicit fixed-map ABI, 7163-call reproducible emulator gate, resource limits, provenance and future candidate backlog.
- Stable V1-V5 resident binaries and official benchmark ranks unchanged. Native VICE and arbitrary relocation still need qualification for these standalone sources; unsigned family campaign remains open.

2026-10-12 ISSUE39 V5 UMOD32 QUOTIENT-PRESERVING SOURCE FRONTEND
- V5 MATH_UMOD32_32 new 147-byte Q32+R32-compatible delayed-zero front end in previously free $5E80 island, public JMP redirected at $5E03. Existing MATH_UDIV32_32 untouched. No resident, normal-ZP, API or other profile growth. Native VICE 512 old/new calls passed.
- Official 1,705-pair identical-input common corpus: 2.770088 cycles faster, V5 mean 302.353079->299.582991; full 4,314-pair quotient-stratified stress mix saves 0.493278 cycles but includes some slower high-quotient/zero-divisor cases. Source and alternate V5 hybrid builds reproduce candidate. Full unsigned/signed corpus and historical audit checks, standalone source catalogs, changelogs, checksums refreshed. Issue39 unsigned family remains open. docs/ISSUE39_V5_UMOD32_QPRESERVING_REORDERED_2026-10-12.md

2026-10-12 ISSUE39 V2-V4 UMOD32 LATE ZERO CHECK
- Improved V2/V3/V4 MATH_UMOD32_32: move 14-byte divisor-zero check from entry to N=D equality branch. 54-byte fixed-size active remainder frontend at $5472; exactly 50 changed bytes per resident, no resident/ZP/stack/API or REU growth. V1/V5 unmodified. UDIV32_32 cycles and outputs unchanged.
- Same-input 2,491-pair profile screens: savings V2=13.599358, V3=13.594540, V4=13.599358 cycles per public call; 36,036 total old/new 6502 calls, zero ABI errors. Native VICE 1,536 old/new calls also correct (not a timing claim). Full five-profile unsigned and signed validation, sources, alternate build, docs, checksums sealed. See docs/ISSUE39_V234_UMOD32_LATE_ZERO_2026-10-12.md. Unsigned family still OPEN.

2026-10-12 ISSUE39 V1 UMOD16 OPTISEARCH Q0 ABI NO-GAIN
- Rejected V1 UMOD16 remainder-only q=0 frontend under existing Q16+R16 alias contract. Hand-written 34-byte shortcut seems 2.397654 cycles faster on 1,705 shared inputs but leaves incorrect Q16 in 768 cases; compliant 42-byte variant is 2.106745 cycles slower with 1,620 regressions and only 85 wins. Seven additional quotient-class workloads screened: 11,259 total public calls, strict output/flags/input exact, unchanged UDIV16. Repose's original binary not imported. No resident binaries or stable source changed, the unsigned family audit remains open. Details: docs/ISSUE39_V1_UMOD16_REPOSE_Q0_FRONTEND_REJECTION_2026-10-12.md.

2026-10-12 ISSUE39 PR68 V1 16BIT DIRECT Q2 EXIT
- V1 shared UDIV16/UMOD16 core: put q=2 return into short BCC range and move cold 3-byte alignment padding after RTS, preserving the $4200-$4342 323-byte envelope and long quotient loop page phase. 57 in-core byte changes; no V2-V4 resident modification and the same 57-byte inherited V5 change or normal ZP, stack, code-span, API change.
- 13,559 same-input quotient-stratified/edge/random cases per V1 16-bit public API: 8,255 faster, 5,304 equal, zero slower, 0.608821 fewer mean cycles. Native VICE 2,048 V1/V5 old/new public calls all correct. Reference/alternate relocation, 5-profile unsigned correctness and paired corpus, signed correctness, stable historical PR57-62 SHA reconstructions validated.
- Common-input V1 UDIV16 mean 156.348479->156.087578; UMOD16 189.383578->189.127859 cycles. Performance tables, standalone source mirrors, README/manual, changelogs, release metadata, checksums refreshed. Unsigned family campaign remains OPEN. docs/ISSUE39_PR68_V1_U16_DIRECT_Q2_EXIT_2026-10-12.md

2026-10-12 ISSUE39 PR67 HISTORICAL PARENT SHA RECONSTRUCTION
- Preserve PR57-62 historical tests after the V5 PR67 known-carry improvement: the parent reconstructor verifies and undoes exactly the six SHA-pinned V5 PR67 16-bit branch rewrites before restoring the older UMOD8 guard. The 8,868-call historical zero-high bypass audit and its original pre-PR67, pre-UMOD8 and PR57-era SHA checkpoints are reproduced exactly. No shipped arithmetic bytes or public ABI change.

2026-10-12 ISSUE39 PR67 V5 PAIR-CORPUS FIXTURE REFRESH
- Removed the obsolete hard-coded 198.610557-cycle V5/ V2 UMOD16 comparison.
- The permanent 1,705-pair exact V2/V5 public ABI parity test now pins both current shipped resident SHA-256 hashes against the same-input benchmark report and checks each measured mean against the corresponding report metric. This preserves a strict cycle regression check across further source-qualified changes while avoiding stale pre-release literals. All four candidate resident images remain byte-identical to the already staged PR67 release.

2026-10-12 ISSUE39 PR67 KNOWN-CARRY 16BIT DIV/MOD
- Source-backed V2/V3/V4 UDIV16/UMOD16/SDIV16/SMOD16: replace three carry-proven unreachable conditional-plus-JMP pairs per unsigned and signed private divider by direct JMP with two never-executed padding NOPs. Exact instruction addresses, resident length, normal ZP, stack, ABI and tables preserved. V5 rebuilt from V2 donor, V1 byte-identical.
- Same-input V2 unsigned means: UDIV16 161.761451->161.758520, UMOD16 198.610557->198.601173 cycles. This is a small strict nonregression on the measured shared corpus, not a new dividing architecture.
- Public five-profile 16-bit candidate checks, V2–V4 reference/alternate builds, exact six-rewrite resident binary diff V2–V5, all-profile signed/unsigned regression and old/new native VICE full-resident 8,192 public calls passed. New paired signed benchmark published without overwriting PR66 historical evidence. Documentation and packaged checksums refreshed. Unsigned family audit remains open. Details: docs/ISSUE39_PR67_KNOWN_CARRY_16BIT_2026-10-12.md.

2026-10-12 ISSUE39 SIGNED16 PAIRED AND V2 U16 DONOR SCREEN
- Published exact same-input signed16 DIV/MOD audit: 5,477 operands per routine x 2 routines x 5 initialized resident profiles = 54,770 verified public machine-code calls. For SMOD16/SDIV16, V1 229.477816 vs V2 251.548475 cycles on THIS common signed corpus, not the old profile-varying RNG sample. V2 wins most individual cases but regresses q=2..31 substantially; earlier unsigned-source table rankings remain untouched.
- Rejected V2 UDIV16/UMOD16 donor + 13-byte high-divisor selector at unused research islands. Best UDIV16 candidate 173.343349 vs V2 161.761451; best UMOD16 216.641056 vs V2 198.610557. No candidate has a faster case; no arithmetic or ABI changes published.
- Deterministic proof generator, machine-readable evidence and docs: docs/ISSUE39_SIGNED16_PAIRED_AND_V2_16BIT_DONOR_SCREEN_2026-10-12.md. Issue39 unsigned family remains open.

2026-10-12 ISSUE39 V2 GUARDED D24 REMAINDER-ONLY UMOD8
- V2 UMOD8 public ABI stable, source-backed 101-byte D>=24 guard at REG_KERNEL+$1323; preserves Q/N/D, upper R and divide-by-zero carry. Ten inline subtract/compare stages; original fallback retained for smaller divisors. No normal ZP, stack, resident PRG length or REU growth.
- 131,072 exhaustive historical parent/new complete-resident CPU calls: 64.819153→52.204453 mean cycles (-19.46%), 58,290 faster / 504 equal / 6,742 slower, worst +15 cycles. 4,096 independent native VICE old/new full-resident calls passed.
- V5 donor guard isolation restored certified identical V5 output; alternate relocation and five-profile unsigned correctness verified. Source mirrors, common-input benchmark catalog, documentation, release status and checksums updated.
- Original V2 parent SHA e1e828a2748099b6f05b224b98ca26960d120f8ba886c4906e8b52bdb8b4fbcd; new resident 28fc6e653a05b170a80cd7eb50636d755895c5ebb7aab133262ed560fa465dd6. This is not universal Pareto dominance. Unsigned DIV/MOD family campaign is still open; see docs/ISSUE39_V2_UMOD8_D24_RELEASE_2026-10-12.md.

2026-10-11 ISSUE39 INDIVIDUAL SOURCE PICKUP GUIDE
- Added docs/INDIVIDUAL_ROUTINE_PICKUP.md and top-level README/QUICK_START/routines index links so any C64 developer can find the exact V1–V5 source mirror and stable API for each recently optimized UDIV/UMOD operation without searching commit history.
- Clearly distinguish individually indexed executable graph mirrors (not guaranteed one-file drop-ins because shared tables, ZP and private helpers can remain) from curated standalone/liftable modules; document direct per-routine links and minimal resident API example.
- Corrected stale catalog statement: 295 shipped profile-entry mirrors plus 25 separately benchmarked alternatives, each with source hash and evidence. Documentation-only change; shipped arithmetic PRGs, ABI, REU images, benchmark numbers and resource envelopes unchanged.

2026-10-11 ISSUE39 V1/V5 77-BYTE GUARDED REMAINDER-ONLY UMOD8
- V1 Balanced and V5 Hybrid gain a source-backed 77-byte non-ZP UMOD8 remainder-only guard at REG_LOW+$0E00. For D>=32, quotient<=7 and at most seven inline subtract-and-compare stages produce R without ever altering MATH_Q; D<32 reuses the existing V1 or imported V2/V5 public wrapper at MATH_UMOD8+3. Inputs and carry preserved, no new zero page, stack or resident PRG span.
- **262,144 complete paired historical-old/new 6502 calls**, 65,536 exhaustive input pairs per profile, no output/ABI errors. V1 exhaustive mean **65.285156→53.140671** (−18.60%), V5 **64.819153→52.835800** (−18.49%). Same-input common corpus V1 **67.294523→58.439757** (−13.16%), V5 **66.848276→58.129412** (−13.04%).
- All 57,344 D>=32 calls per profile are faster or equal, with zero qualified slowdowns. All 8,192 D<32 fallback calls per profile incur exactly +14 cycles; this deliberate bounded trade-off is not universal Pareto dominance. The smaller-divisor original path avoids hundreds-of-cycles worst tails of an unrestricted repetition engine.
- **320 native VICE x64sc full-resident old/new public calls** passed across V1 and V5, preserving Q0, N/D and carry. Private OptiSearch native candidate timing is not misrepresented as a public-ABI win.
- Prior PR #57/#59/#60/#61/#62 historical proof reports remain reconstructed from their original SHA-qualified parent residents via the new UMOD8 parent capsule, avoiding false provenance or rerunning old tests against new features.
- All-profile unsigned 822,050 and signed 364,533 public calls, 136,335 common-input, 53,760 workload-specific, 262,144 paired new, source reference+alternate relocation and hybrid mixed-call validation form the release gate. Updated source, performance tables/catalogs, both changelogs, docs, README/manual, checksums and CI. Overall unsigned DIV/MOD issue39 family remains open.
- Details: docs/ISSUE39_V1V5_UMOD8_GUARDED_REMAINDER_2026-10-11.md

2026-10-11 ISSUE39 V1 GUARDED 32/32 D8 PUBLIC DIVMOD DELEGATE
- Source-backed V1 32/32 narrow-D8 route at REG_LOW+$0D80, using existing V1 public UDIV32/16 for full-width quotient with R2/R3 cleared. Only reached after D!=0, N>D, D3=0 and guarded D2|D1=0; other inputs go through original shared 32/32 core. No normal ZP, stable input/output/carry API, unchanged resident PRG length.
- Exact merged PR61 SHA parent reconstruction; **51,812 paired historical old/new public 6502 executions**, mathematically correct, full remainder/carry/input preservation, zero slower calls among measured D8 inputs. Worst non-D8 guard penalty +14 cycles (explicitly not universal Pareto dominance). V1 same-input UDIV32_32 **358.009161→335.825577** (−6.2%), UMOD32_32 **435.224633→399.676833** (−8.2%).
- Dedicated D8 full-numerator samples 1943.200→1643.726 UDIV32_32, 1942.482→1643.277 UMOD32_32, 1024/1024 faster per API. D16/D24 denominators incur small +14-cycle guard overhead. An earlier wider-D16 V1 transplant was rejected for rare >400-cycle regressions.
- V5's existing faster D16 imported V2 producer is unchanged byte-for-byte: V5 builder validates, removes the V1 D8 island and restores the old dead high-zero selector before V5-specific narrow helper. Reference and alternate relocatable assemblies validated.
- V1 unsigned 164,410 + full-profile unsigned 822,050 and signed 364,533, common 136,335 and 51,812 paired V1 D8 calls passed. 160 real VICE old/new resident public-entry calls matched mathematical oracle. Previous PR57/PR60/PR61 certificates re-run on SHA-validated historical V1 parent, not the newer V1 live binary.
- Updated public numbers, routine catalogs, both changelogs, docs/manual, checksum package and CI. Unsigned DIV/MOD issue39 family remains open.
- Details: docs/ISSUE39_V1_3232_D8_DELEGATION_2026-10-11.md

2026-10-11 ISSUE39 V1 BALANCED 24/8 EXACT NARROW-DIVISOR DIVMOD
- Source-backed 84-byte exact V1 24/8 restoring core at REG_LOW+$0D00, fed by an N2>0,D2=D1=0 bounded selector for UDIV24 and shared UMOD24. Quotient shifted into public MATH_Q; 8-bit remainder with ninth carry held in MATH_R. Zero new normal ZP and stack, stable ABI and PRG length.
- 56,580 same-input old/new public machine-code executions across canonical, seven profile workloads, 4,080 narrow stress, 4,096 wide controls and 1,024 N2=0 controls per API: no wrong outputs or slower calls. Canonical means V1 UDIV24 177.742058→170.726699, UMOD24 269.788152→248.317450 cycles. Independent full-N2/small-D means 1724.909314→1221.545098 (4,080/4,080 faster per API); maximum individual saving 893 cycles.
- Historical PR60 rejected V1 selector remains reproducible via source-anchored old parent SHA; the negative certificate is not mislabeled as a failure of the new algorithm.
- V5's imported V2 24-bit cores stay unchanged. V5 build reclaims the V1-only 24/8 island and restores its inherited unreachable selector; **V5 reference resident remains byte-for-byte identical**. Reference/alternate source maps and mixed-call ABI rechecked.
- V1 164,410 unsigned and all-profile 822,050 unsigned + 364,533 signed + 136,335 common + 53,760 seven-class calls validated. Genuine VICE full-resident 80 old and 80 new calls matched both public APIs. No claim that a private OptiSearch native timing beat the public ABI.
- Published performance tables, sources, documentation, both changelogs, release/checksums, and CI. Unsigned DIV/MOD campaign remains open.
- Details: docs/ISSUE39_V1_UDIV24_BYTE8_2026-10-11.md

2026-10-11 ISSUE39 UNSIGNED SMALL-WIDTH ARCHITECTURE AUDIT
- Added a new public ABI and cycle gate for 8/16/24-bit UDIV/UMOD: seven same-input classes, 256 operands per class, five resident profiles, 53,760 complete 6502 calls. The corpus demonstrates workload-conditioned V1/V2/V3/V4/V5 trade-offs, particularly V1 16-bit small-divisor efficiency versus V2 24-bit small-divisor efficiency.
- Rejected widening the V1 24-bit narrow-divisor escape: the seemingly improved canonical mean conceals up to 422-cycle regressions on a dedicated >1,700-case corner suite. A separate deterministic paired negative proof prevents accidentally promoting that unsound performance trade-off.
- Ran five native OptiSearchV2 executable strategies per 8/16/24 width on 101 vectors. Native timing is NOT a public ABI comparison or an optimality claim; private tool material remains outside the repository.
- Added documentation and review JSON/CSV with hashes, branch CI audit and publication checks. Resident PRGs, stable ABI addresses, ZP, REU and relocatable arithmetic source remain unchanged. Unsigned DIV/MOD issue39 checkbox remains unchecked.
- Details: docs/ISSUE39_UNSIGNED_SMALL_WIDTH_WORKLOADS_2026-10-11.md

2026-10-11 ISSUE39 V5 32/32 NARROW-DIVISOR DELEGATION
- V5-only shared UDIV32_32/UMOD32_32 route when D3=D2=0 reuses the already imported V2-derived 32/16 quotient engine; direct 21-byte helper at REG_LOW+$0D00, 0 new ZP, no public ABI or resident PRG size change. V1 stays untouched (its candidate suffered up to +403 cycles).
- Same-input V5 UDIV32_32 358.009161→275.013192 cycles (2,729 pairs, 234 faster, 2,486 equal, 9 slower); UMOD32_32 435.224633→302.353079 (1,705 pairs, 234 faster, 1,467 equal, 4 slower). Narrow 16-bit divisor class saves ~934 cycles on average; 17–24-bit divisors pay +10 guard cycles in most cases. Results workload-dependent.
- Paired 21,412 CPU calls, V5 unsigned 164,410 and signed 36,273 calls, real VICE 80 old+80 new calls and hybrid mixed-call validation; all-profile 822,050 unsigned/364,533 signed, 136,335 common corpus. Earlier PR57 zero-high certificate is reconstructed from the historical PR58 V5 parent image and remains valid.
- Regenerated hybrid source/binaries, standalone mirrors, public and consolidated indexes, both changelogs and checksums. OptiSearch private; this is a manual architecture reuse, not an optimizer-native record. Issue39 unsigned campaign remains unchecked.
- Details: docs/ISSUE39_V5_3232_NARROW_DELEGATION_2026-10-11.md

2026-10-11 ISSUE39 V1 32/16 DUAL LOOP UNROLL
- Two V1 32/16 quotient loops unrolled into $1900-$1CF7 (1,016 occupied bytes); 0 additional ZP, no public ABI or resident PRG span growth. Relative branch targets and X=0 at exit preserved.
- Same-input public UDIV32_16 mean 896.061561→825.873947 (2,729 pairs; 2,578 faster, 151 equal, 0 slower); UMOD32_16 916.280352→843.629912 (1,705 pairs; 1,554 faster, 151 equal, 0 slower). Six independent 512-pair workload classes also show no new regressions, up to 136 cycles saved.
- 21,156 paired source-executed calls, native full-resident VICE old/new 80+80 calls, V1 unsigned 164,410, signed 97,329, and all-profile 822,050 unsigned, 364,533 signed, 136,335 common and 30,720 workloads pass. Reference/alternate source, V5 hybrid, catalog and checksum publication regenerated.
- V5 keeps its V2-derived 32/16 core. Earlier table island rejected for V5 ATAN2 overlap. Private OptiSearch is not published; unsigned family campaign remains open.
- Details: docs/ISSUE39_V1_UDIV32_16_DUAL_LOOP_UNROLL_2026-10-11.md

2026-10-11 ISSUE39 V1/V5 32/32 ZERO-HIGH FALLBACK BYPASS
- Post-PR56: divisor high byte zero skips the provably impossible q2/q3 gate and jumps directly from qone to the original legacy divider. Three resident byte changes, no ZP/ABI/PRG span growth.
- Same-input V1/V5: UDIV32_32 359.077684→358.009161 cycles (2,729 calls/profile); UMOD32_32 436.899707→435.224633 (1,705/profile); 243 + 238 faster inputs/profile, exactly 12 cycles saved, no regressions among 8,868 paired calls.
- Five-profile 822,050 unsigned, 364,533 signed, 136,335 common corpus, 30,720 workloads; source relocation, V5 hybrid and full-resident VICE validated. Generated sources, both changelogs and hashes republished; unsigned DIV/MOD family remains open.
- Details: docs/ISSUE39_UDIV32_ZERO_HIGH_BYPASS_2026-10-11.md

2026-10-11 ISSUE39 V1/V5 32/32 PROVEN QUOTIENT-2/3
- 131-byte bounded quotient-two/three fast path added after the existing V1/V5 q=1 32/32 guard. D3 in $40–$7F and N3>2*D3+1 proves 2D<=N<4D; compute R=N−2D, conditionally subtract D, and emit Q=2 or 3. DEY loop preserves SBC carry. All nonqualifying inputs use the original core.
- Common-input V1 and V5: UDIV32_32 370.572004→359.077684 cycles (−3.10%, 2,729 operands/profile), UMOD32_32 444.652199→436.899707 (−1.74%, 1,705/profile). Max one-call speedup 388 cycles; max slowdown 22. Uniform 32×32 inputs improve 21.442 cycles/call, while narrow-divisor inputs incur about +12; explicit Pareto trade-off.
- Zero additional normal ZP; unchanged 56-entry API and resident PRG length. New source island $6860–$68E2. Full 822,050 unsigned, 364,533 signed, 136,335 common-corpus, 30,720 workload calls, reference/alternate source builds, V5 hybrid, catalogs, dual changelogs and checksums republished. Native x64sc old/new 48-case proof passed.
- Manual high-byte range proof, not an OptiSearch-generated native record. Issue #39 unsigned family remains open.
- Details: docs/ISSUE39_UDIV32_32_HIGH_Q23_V1V5_2026-10-11.md

2026-10-11 ISSUE39 32/16 MULTI-WORKLOAD RANKING AUDIT
- Added a deterministic 30,720-call six-workload common-operand benchmark for all five 32/16 unsigned DIV/MOD profiles, including median, p95, extrema and input/source hashes. The published weighted-corpus ranking is preserved; workload-conditioned evidence is now separately reproducible and CI-gated.
- Tested but REJECTED a V1 92-byte q0/q1 shortcut despite an edge-weighted 7.13% UDIV32/16 and 12.27% UMOD32/16 mean improvement: 91% and 86% of calls regressed, up to +51 cycles. Full-width uniform workloads slow by +17 cycles per call, while 16-bit numerators gain substantially. Not a Balanced default.
- No resident arithmetic or public ABI changes. 164,410 V1 unsigned + 97,329 V1 signed trial correctness calls passed; 30,720 shipped-profile scenario calls pass. Full unsigned issue39 campaign remains open.
- Detailed evidence: docs/ISSUE39_UDIV32_16_WORKLOAD_DECISION_2026-10-11.md

2026-10-11 ISSUE39 V1/V5 BOUNDED HIGH-BYTE Q1 32/32 DIV-MOD
- Added a formally bounded 73-byte high-byte quotient-one shortcut for V1 and V5 shared unsigned 32/32 division and modulo. N>D is prechecked, and D3>=128 or (D3>0 and N3<2*D3) proves N<2D; compute R=N-D and Q=1 directly. Other operands rejoin the exact prior restoring core.
- Identical-input UDIV32_32 mean **470.755955→370.572004 cycles (−21.28%)** in V1 and V5, 2,729 matched calls per profile. UMOD32_32 **523.279765→444.652199 (−15.03%)**, 1,705 matched calls per profile. 8,868 paired old/new calls; zero arithmetic, carry or input-preservation errors. Some nonqualifying calls pay up to +22 cycles; this is an explicit mean-speed trade-off, not all-input dominance.
- Source-island reference $6810-$6858, relocated for alternate map. No added normal-ZP, no public ABI relocation, no resident PRG length change. V5 builder recognizes the source-integrated prechecked gate and avoids clobbering the JMP trampoline.
- Full five-profile 822,050 unsigned, 364,533 signed, and 136,335 identical-input machine-code calls; V1/V5 dedicated 32/32 bounded-q1 parity/sentinel gate, source reference+alternate builds, catalogs, both changelogs, performance/index metadata, checksums and package audits requalified.
- Manual algebraic range analysis inspired by V1/V5 vs Repose/OptiSearch-derived V2 architectural comparison; **not** a native OptiSearch record. Private optimizer stays private. Wider issue #39 unsigned family remains open.
- Detail: docs/ISSUE39_UDIV32_32_HIGH_QONE_V1V5_2026-10-11.md

2026-10-11 ISSUE39 V5 UMOD16 REMAINDER-ONLY SOURCE TRANSPLANT
- Imported 69-byte V2 UMOD16 remainder-only frontend into the 77 bytes remaining in the same already-unoccupied V5 REG_LOW final page after PR #52 UMOD24. Final combined code: $2F00-$2FF7 (248/256); reference UMOD16 $2FB3-$2FF7; alternate $AFB3-$AFF7. No additional normal ZP or resident PRG file bytes, no stable API relocation.
- V5 UMOD16 identical-input mean 205.028739->198.610557 cycles (−6.418182, −3.13%); 1,705/1,705 V2 matched per-call cycle values, 1,613 faster than old V5, 92 slower by two cycles. UMOD24, UDIV16 and UDIV24 timing unchanged on 9,035 independently paired controls.
- Full 822,050 all-profile unsigned, 364,533 signed, 136,335 common-input calls; V5 native VICE x64sc old/new 16+16; source reference and alternate 56 public API/mixed-call/ZP confinement certification; standalone/source catalogs, indexes, both changelogs and release seals refreshed.
- Permanent V2/V5 UMOD16 exact timing+output gate in comparable-unsigned CI. Source design is manual transplantation of a V2 frontend (not novel OptiSearch native synthesis); private OptiSearch stays private. Issue39 unsigned family stays unchecked.
- Details: docs/ISSUE39_V5_UMOD16_REMAINDER_TRANSPLANT_2026-10-11.md

2026-10-11 ISSUE39 V5 UMOD24 REMAINDER-ONLY SOURCE TRANSPLANT
- Imported existing V2 179-byte q=0/q=1 remainder-only frontend into V5's previously free REG_LOW final page, reference $2F00-$2FB2 and alternate $AF00-$AFB2. Preserve full public modulo remainder/carry/input semantics with no new normal ZP, no PRG span growth, and unchanged UDIV24.
- Identical-input UMOD24 V5 mean 214.991629 -> 207.490663 cycles (3.49% faster), exactly matches V2/V3/V4 on all 1,553 calls. 914 faster, 375 slower (max +7 cycles); explicitly accepted mean/fast-exit trade-off, 179 newly occupied code bytes. Other V5 unsigned API means unchanged.
- Native VICE x64sc paired 16+16 calls; 9,716 old/new paired public calls; V5 164,410 unsigned and 36,273 signed regression calls; full all-profile 822,050 unsigned/364,533 signed and 136,335 common-input validation; source/alternate builds, mirrors, stable 56-entry ABI, package/checksums requalified.
- Permanent exact V2/V5 output/cycle-parity regression in tools/validate_v5_umod24_frontend.py. Public performance ranks use only common-input corpora. No private OptiSearch code published; full unsigned campaign remains unchecked.
- Detail: docs/ISSUE39_V5_UMOD24_REMAINDER_TRANSPLANT_2026-10-11.md

2026-10-11 ISSUE39 V1 BALANCED 24-BIT NARROW-DIVISOR LATENCY ESCAPE
- V1 Balanced UDIV24/UMOD24: route the costly N2>0,D2=0 and Q>=65536 fallback through the existing V1 32/16 division core; preserve original low-quotient path and reuse LAX-provided X=N2. V5 keeps the optimized V2 donor behavior.
- Paired same-input 4,753 UDIV24 and 1,553 UMOD24 calls: V1 means 189.741847→179.964654 and 306.577592→276.590470 cycles. 162 calls faster, 91 slower (maximum +19), remainder unchanged; the large Q example $FFFFFF/$000001 improves 3235→1986.
- Explicit Pareto tradeoff; selected for much shorter heavy tail and lower means, not all-input dominance. No new ZP, no PRG length or public ABI relocation, V5 helper placed after signed donor islands at $7FA0.
- Full V1/V5 164,410 unsigned and 97,329/36,273 signed machine-code validations plus VICE x64sc paired native checks, V1–V4 reference/alternate maps, published all-API and common-input ranking proof requalified. Other profile code unchanged.
- Benchmarks, source mirrors, profile cross-references, both changelogs, status, checksums and package audit updated. Wider issue #39 unsigned DIV/MOD campaign remains open.
- Detail: docs/ISSUE39_V1_UDIV24_NARROW_ESCAPE_2026-10-11.md

2026-10-11 ISSUE39 COMMON-INPUT UNSIGNED DIVMOD RANKING AUDIT
- Corrects a benchmark-methodology issue: the legacy unsigned family validator deliberately varies random input seeds per profile, making its individual cycle means unsuitable for direct V1–V5 ranking.
- Adds a separate 136,335-call common-input machine-code audit covering 11 public unsigned DIV/MOD APIs and all V1–V5 reference residents, with result/carry/input preservation checks and workload-class, p95, max, mean timings.
- Changes `benchmarks/BEST_PROFILE_RESULTS.csv` to choose winners using identical-input data for these 11 routines, while preserving legacy independent validation/performance rows for extra correctness coverage.
- Publishes `benchmarks/UNSIGNED_COMMON_PROFILE_RESULTS.csv`, a permanent generator and verification gate, documentation, performance table correction, source SHA and corpus fingerprints.
- V1 UDIV24 slow paths are genuine when quotient >255: V1 2,098.8 vs V2 859.9 mean on that slice. In contrast V1 UDIV16 156.348 vs V2–V5 161.761, demonstrating workload-dependent ranking. V3/V4 UDIV24 and UMOD24 cycle vectors match V2 on identical inputs.
- No arithmetic routines or public ABI changed; unsigned family #39 remains open pending remaining architecture audits and no-gain decisions.
- See `docs/ISSUE39_BENCHMARK_COMPARABILITY_AUDIT_2026-10-11.md`.

2026-10-11 ISSUE39 UDIV24/UMOD24 LIVE-X EQUALITY FAST PATH
- In V1 Balanced and V2/V3/V4 direct 24-bit quotient cores, reuse the already-live X=N2=D2 high byte using TXA instead of an extra LDA MATH_D+2, shortening the fast path by two cycles and two code bytes; V5 inherits both donor improvements.
- Paired deterministic public-entry corpus: 31,530 calls across V1–V5, no arithmetic/carry mismatches and no slower calls; exactly 1,994 calls save two cycles. Mean UDIV24 cycles V1–V5: 194.032611, 154.218178, 161.533347, 158.385020, 157.655376. UMOD24 means: 302.877656, 205.325821, 207.136510, 205.247263, 210.894398.
- V2–V4 UMOD24 dedicated remainder paths are unchanged on the benchmark corpus; public ABI and normal-ZP/resource contracts remain unchanged.
- Initial genuine VICE x64sc 3.13.2 paired spot proof: 80 before + 80 after native calls, including REU 512 KiB/16 MiB and V5 C64 CPU-port ROM banking.
- Source/relocation, signed and unsigned family checks, source mirrors, public benchmarks, README/manual, both changelogs, release metadata, SHA256 manifest and package audit refreshed.
- This is a manual register-lifetime synthesis on OptiSearch/Repose-derived architectures, not an independent generic OptiSearch native record. The larger issue #39 unsigned DIV/MOD campaign remains open.
- Documentation: docs/ISSUE39_UDIV24_EQUAL_HIGH_X_LIFETIME_2026-10-11.md

2026-10-11 ISSUE39 UDIV16/UMOD16 SHARED CONDITIONAL TRANSPLANT
- Removed an unreachable BCC after SEC in V2/V3/V4 UDIV16 shared producer; V5 inherits the source-level patch from V2.
- V2/V3/V4/V5 UDIV16 mean cycles: 127.754892 / 125.408794 / 125.605512 / 126.362297.
- V2/V3/V4/V5 UMOD16 mean cycles: 195.931101 / 196.392788 / 195.511912 / 199.898261.
- 25,224 deterministic paired calls: zero mismatches, zero regressions; 2 cycles saved on 248 calls across the eight public-entry corpora. No PRG span, stable ABI, ZP or stack-page change. V1 retained.
- Reference/alternate source rebuilt, all-profile unsigned and signed validators requalified, standalone source mirrors/catalog, benchmark tables, release-status/checksums regenerated.
- Private OptiSearch P40 supplied a constrained search candidate; this is a human-guided transformation, not a large generic OptiSearch discovery. The unsigned DIV/MOD campaign in issue #39 remains unchecked.
- Detail: docs/ISSUE39_UDIV16_BRANCH_TRANSPLANT_2026-10-11.md

2026-10-11 V1 UDIV32/32 + UMOD32/32 NONZERO GATE
- V5 hybrid builder recognizes a fully source-integrated V1 prechecked gate and refuses mixed original/optimized byte states; both reference and alternate builds are independently revalidated.
- V1 zero-ZP shared 32/32 divider reuses the prechecked nonzero-divisor decision, avoiding duplicate D!=0 work on N>D.
- UDIV32/32 428.554036 -> 416.861197 cycles on 6,801 calls; UMOD32/32 552.220863 -> 541.401803 cycles on 1,553 calls.
- ABI and RAM envelope unchanged; 21,508 paired calls with zero slower paths; full unsigned and signed family regression requalified.
- Generated mirrors, performance indexes, 2 changelogs, documentation, checksum and package audits updated.
- The unsigned DIV/MOD family in issue #39 remains open. Full evidence: docs/V1_UDIV32_32_PRECHECKED_GATE_2026-10-11.md.

2026-10-11 V5 ZERO-ZP UDIV32/32 + UMOD32/32 PRECHECKED GATE
- The V5 early-gate proves D!=0 on N>D paths; the private 32/32 divider previously checked D==0 again after copying operands.
- Divisor-zero now jumps to the unchanged Q=R=0, carry-set helper; only proven-nonzero branches enter the normal copy and divider dispatch without the redundant check.
- Means (unchanged deterministic division corpora): UDIV32/32 421.077342 -> 409.633142 cycles, UMOD32/32 548.000000 -> 537.266581 cycles. Min/max 90/2423 -> 67/2404. Reachable code 946 -> 931 bytes, normal ZP 0, PRG payload unchanged.
- 21,508 paired calls (10,754 cases for each alias), no wrong results, no negative deltas; full V5 164,410-call unsigned DIV/MOD validation passed. Source-generated reference bytes match diagnostic patch exactly; alternate-map build and hybrid validation pass.
- Source-level builder guard, annotated standalone mirrors, regenerated published benchmarks, full proof and checksums included. See docs/V5_UDIV32_32_NONZERO_GATE_2026-10-11.md.

2026-10-10 V3/V4 RECIPROCAL X-CACHE (EXHAUSTIVE)
- MATH_URECIP16_Q16 caches the denominator high byte in X and uses CPX across its 15-entry threshold ladder.
- Native V3/V4 PRGs and canonical ASM rebuild byte-identically, with no relocation or new ZP/table use.
- Exhaustive 65,536-denominator mean: 66.233795 -> 57.331436 cycles (-8.902359, -13.44%); code reachable 430 -> 391 bytes.
- 4,095 REU-backed denominators per profile passed real VICE x64sc fingerprint/oracle checks; deterministic source rebuild passed 8/8.
- New proof and constraints: docs/URECIP16_X_CACHE_2026-10-10.md. REU DMA bus-time gains are not claimed.

2026-10-10 V3/V4 REU IMMEDIATE-DMA CORRECTION
- Fixed incorrectly deferred REU fetch/swap/autoload commands in V3/V4 fixed-map PRGs and canonical, relocatable and standalone ASM mirrors. Commands now use $91/$92/$B1 at immediate-result sites.
- Exact reference/alternate rebuilds pass; P38 VICE native arithmetic and Turbo BEGIN/CALL/END smoke tests pass on fixed builds (see docs/REU_IMMEDIATE_DMA_FIX_2026-10-10.md).
- ABI, PRG sizes and REU images unchanged; native hardware/cycle requalification remains open.

2026-10-08 SIGNED MAGNITUDE-CORE REUSE + LIFTABLE MULDIV16
- V2/V3/V4 SDIV16_SHL8 now bind signed magnitudes directly into the selected UDIV32/16 substrate; V5 keeps the same architecture with a post-OptiSearch positive-divisor shortcut.
- Final SDIV16_SHL8 means V1-V5: 846.155071 / 630.032715 / 630.265213 / 628.417884 / 628.885496 cycles.
- V2/V3/V4/V5 SDIV32/16 now use thin signed front ends around the qualified UDIV32/16 magnitude core. Final means: 724.392148 / 724.449509 / 721.003490 / 722.170774; V1 Balanced remains 955.051690.
- V2/V3/V4 SDIV32/32 now normalize/restore public operands around the profile-selected UDIV32/32 core: 420.452435 / 416.865672 / 418.153927 cycles. V1/V5 keep their Balanced private 32/32 paths.
- Signed-layout policy now permits only explicit audited magnitude-core sharing; all unlisted signed/unsigned executable overlap remains an error.
- Full signed DIV/MOD proof: 364,533 calls, zero errors; published signed-source and layout gates pass.
- OptiSearchV2 generic signed 32/32 is noncompetitive (~3480 cycles). Six local MOS6502 rewrite classes produced no legal selected-wrapper rewrite once explicit code-island origins were respected. Post-OptiSearch manual review retained the high-byte divisor shortcut only where placement allowed it.
- MULDIV16 now has canonical symbolic liftable sources under routines/muldiv16/, and the integrated sources include those same files. Exact per-profile standalone mirrors remain for byte-level auditing.
- Technical note: docs/SIGNED_CORE_REUSE_OPTIMIZATION_2026-10-08.md.

## 2026-10-08 — shifted DIV/reciprocal direct-input optimization campaign

- Reworked `MATH_UDIV16_SHL8` and `MATH_SDIV16_SHL8` so V1-V5 bind `N16 << 8` directly into the selected private 32/16 divider state instead of paying generic public-vector adapter work. Final UDIV16_SHL8 means are **770.773617 / 552.649695 / 553.124974 / 552.577740 / 553.298759** cycles for V1-V5.
- Final SDIV16_SHL8 means are **846.155071 / 715.633370 / 714.004798 / 712.609597 / 630.805016**. V5 gains most: **953.277863 -> 630.805016** cycles mean while retaining its **31-byte normal-ZP contract**.
- `MATH_URECIP16_Q16` now seeds `0x00010000` directly into the private 32/16 fallback state. Means become **108.497635 / 94.822998 / 66.233795 / 66.233795 / 95.044128**; V3/V4 keep their faster REU reciprocal path unchanged.
- V5 now reaches the certified relocated V2 UDIV32/16 split-tail entry at `HYBRID_CODE+$0C00`; the helper is installed into a build-verified page-aligned free table run rather than colliding with direct UDIV16 at `$B800-$BDC9`.
- OptiSearch's complete shifted-Q0 schedule sweep confirms that generic restoring/Q0 candidates are far slower than the specialized direct-state design. A post-OptiSearch synthesis pass then removed one redundant zero load, saving a further **2 cycles and 2 bytes** from every UDIV16_SHL8 adapter.
- Final all-profile validation is zero-error: 4,753 UDIV16_SHL8 cases/profile, 4,585 SDIV16_SHL8 cases/profile, and exhaustive 65,536-divisor URECIP16_Q16/profile. See `docs/SHIFTED_DIV_RECIP_OPTIMIZATION_2026-10-08.md`.

## 2026-10-08 — signed DIV/MOD manual + OptiSearch optimization campaign

- Completed the first family in the library-wide issue #39 optimization campaign. SDIV8/16/24 were re-audited and retained after compatible manual/OptiSearch candidates failed to improve the selected fixed-profile implementations; the attempted SDIV24 magnitude-deferral transplant was correctness-clean but timing-neutral.
- V2/V3/V4 `MATH_SDIV32_16` now fuses signed continuation state with direct public Q/R tails. Means improve **833.995638 -> 817.550927**, **833.572737 -> 817.533479**, and **829.631189 -> 813.759215** cycles respectively. `SMOD32_16` and `SDIV16_SHL8` inherit the same improvement; V1/V5 retain their lower-pressure 32/16 implementation.
- All five profiles remove stored sign flags from `MATH_SDIV32_32`: because public N/D are preserved, quotient/remainder signs are rediscovered after the unchanged magnitude core. SDIV32/32 means become **566.839288 / 537.452736 / 536.835972 / 537.194633 / 572.005880** cycles for V1-V5; SMOD32/32 becomes **766.253430 / 730.251986 / 726.236101 / 739.102527 / 765.857040**.
- OptiSearch confirms the fast decomposed-rectangular family remains the right 32/16 speed substrate. Its 32/32 generic restoring Q+R point (~3480 cycles) is not competitive. Remainder-only signed specialization is not promoted because stable SMOD aliases preserve the full Q+R state and the repository's earlier signed remainder A/B was 29-41 cycles slower.
- The final rebuilt V1-V5 signed DIV/MOD corpus passes with zero errors. Signed division validation is now a permanent CI gate. See `docs/SIGNED_DIVMOD_OPTIMIZATION_2026-10-08.md` for the candidate decisions and OptiSearch evidence.

## 2026-10-08 — PR #37: stable MULDIV16 full-width multiply/divide API

- Promoted `MATH_UMULDIV16` and `MATH_SMULDIV16` as stable API entries 55 and 56 across V1-V5 and Custom Pareto builds; the common public surface is now **56 entries**.
- Specialized V5 `MATH_UMULDIV16` and `MATH_SMULDIV16` without increasing its **31-byte normal-ZP contract**. The hybrid builder reuses the qualified V1 17-ZP UMUL16 record producer and feeds its register/ZP product directly into the relocated private V2 UDIV32/16 state.
- V5 UMULDIV16 improves **956.646373 -> 834.646373 cycles mean**, with min/max **456-2078 -> 334-1956** on the unchanged 9,001-case corpus.
- V5 SMULDIV16 improves **1378.300411 -> 888.154427 cycles mean**, with min/max **490-2271 -> 83-1899**. The signed path preserves product-sign state in control flow and uses specialized no-fix, quotient-only, remainder-only, and quotient+remainder tails.
- The same signed sign-flow/tail specialization improves V2/V3/V4 SMULDIV16 from **889.395956 -> 860.448172 cycles mean**, with maximum latency **1893 -> 1869**. Against the composed baseline, mean saving is **272.590601 cycles**, with **91-1025 cycles saved per call** and zero slower cases.
- The final code-for-cycles pass uses otherwise free implementation space; it adds **no ZP, no persistent stack reservation, and no profile PRG-span growth**. The V2-V4 signed body is split across relocation-safe private islands so alternate maps remain clear of SMUL8's signed-sum planes. SMUL8 sum planes are now explicitly relocatable (`$9C00` reference, `$1000` alternate). The divisor is deliberately bound only after multiplication on V5 because its divider D bytes overlap the low-ZP quarter-square pointer image.
- Reference and alternate maps are cycle-vector identical. The focused proof passes **9,001 unsigned + 9,001 signed cases per profile/map**, and the V5 hybrid regression passes exhaustive UMOD8 plus randomized/mixed cross-API coverage.

## 2026-10-07 — UDIV32/16 optimization and bounded unsigned-division latency (PR #33)

- Replaced V2/V3/V4 `MATH_UDIV32_16` with the direct split-byte constrained-tail implementation, including a compact `D<256` path. On the paired integration corpus, mean latency improves **1092.28 -> 715.36 cycles** and maximum latency **1880 -> 1738**.
- Added bounded narrow-divisor fallbacks to the wider unsigned family. `MATH_UDIV24` hard-tail maximum improves **3188 -> 1267 cycles**; `MATH_UDIV32_32` hard-tail maximum improves **2532 -> 1792 cycles**. The 12k narrow UDIV32/32 sample improves **1485.38 -> 710.88 cycles mean** with zero slower cases.
- Added the exact 17-bit-divisor UDIV32/32 tail while leaving the wide-divisor live-high hot path intact. The finalized whole public UDIV32 graph is **2,755 reachable code bytes / 14 ZP bytes / 0 persistent stack bytes**; the wide-divisor live-high core itself remains the four-ZP path.
- Updated V5 relocation for the expanded division-latency helper range (`$5957-$59A6`). V5 retains compact wider-UMOD aliases to the imported UDIV engines; modulo semantics are certified exactly while their timing remains profile-specific.
- Regenerated V2-V5 resident images, standalone sources, public performance/index files, validation evidence, release hashes and package checksums.
- Validation passes **822,050 unsigned division/modulo calls** across all five profiles, **104,121 UDIV32 calls per map/profile** on reference and alternate maps, the V5 hybrid suite, deterministic rebuild, package audit and post-promotion library/Turbo32 CI.

## 2026-10-07 — remainder-only MOD, V4 ISQRT32, FAST24 and Turbo integration pass

## 2026-10-07 — Repose four-ZP UDIV32

- Replace V2/V3/V4 UDIV32 with Repose live-high division plus preserved narrow-divisor loops. UMOD32 inherits the fallback.
- Code 869 → 793 bytes; ZP 8 → 4. Paired uniform mean 368.906 → 191.169 cycles; some wide-divisor cases regress. Narrow samples save 82–91 cycles.
- See [measurements and validation scope](docs/UDIV32_OPTISEARCH.md), including the existing alternate-map SMUL8 issue.

- Added dedicated V2/V3/V4 unsigned remainder front ends for `MATH_UMOD16`, `MATH_UMOD24` and `MATH_UMOD32_32`. The common q=0/q=1/equality cases return the remainder without quotient materialization; harder cases rejoin the exact existing division engines. Canonical 1,553-case means are now **195.951706 / 196.414681 / 195.529942** for UMOD16, **293.183516 / 294.880876 / 293.535093** for UMOD24, and **515.783001 / 509.623310 / 507.496458** for UMOD32_32 in V2/V3/V4.
- The analogous signed remainder front end was measured and rejected: it was correct but 29–41 cycles slower on the research corpus. Shipped SMOD16/SMOD24 arithmetic is unchanged.
- V4 `MATH_ISQRT32` now uses an exact **4 MiB REU prefix accelerator** plus restoring refinement. On the unchanged 4,130-case deterministic corpus it improves **1046.622518 → 917.317433 cycles** (899–1237 → 806–1067), with identical reference/alternate results.
- V2/V3/V4 public `MATH_UMUL24` now writes z3 directly and tail-exits through the public result path, improving **429.555502 → 421.555502 cycles** on the unchanged 10,324-case corpus. V1/V5 remain 474.042329.
- Turbo16 now uses a **122-byte direct-output executable-ZP overlay**: canonical CALL mean **197.046257 cycles (185–220)**, BEGIN/END **300/345**, with zero-penalty ZP origins **$02-$85**. The 134-ZP shifted134 transplant was rejected because its stable-ABI mean was only 209.218776.
- Turbo32 keeps its 135-byte stack-free overlay and writes z4 directly before a shared public tail, improving the canonical CALL mean **684.185219 → 676.185219 cycles (613–788)**. BEGIN/END remain 326/371.
- Turbo validation passes **17,196 lifecycle/API calls** and the **3,556-product** minimum/maximum-origin sweep, including V4 REU banks $FE/$FF. Source regeneration now derives Turbo32 helper extents from canonical source, preventing stale range metadata after tail changes.

## 2026-10-07 — PR #24 carry/register ideas generalized to SMUL16 and SMUL32

- Generalized the carry-priming, live-high-byte binding, known-carry reuse and dead-scratch ideas from the optimized SMUL24 path.
- SMUL8 is unchanged: its direct signed-domain kernel has no analogous wrapper/binder overhead to remove.
- Canonical V1/V2/V3/V4/V5 SMUL16 means are **282.588064 / 245.802333 / 246.107696 / 246.144492 / 282.262957 cycles**; V1/V5 save about 9-10 cycles per call and V2-V4 save exactly 3 cycles per call in matched research corpora.
- Canonical V1/V2/V3/V4/V5 SMUL32 means are **744.128269 / 711.153591 / 711.447073 / 711.706102 / 743.477377 cycles**; NN calls save exactly 2 cycles, other quadrants are unchanged.
- SMUL16_SHR8 and SMUL32_SHR16 inherit the corresponding producer gains. ABI, ZP, persistent-stack and table contracts are unchanged.

## 2026-10-07 — Repose OptiSearchV2 SMUL24 and ATAN2 refinements

- Adapted Repose's carry-primed signed dispatch and dead pointer-low scratch with one shared binder. Public SMUL24 saves 4–5 cycles per measured call and six code bytes, preserving 24 ZP bytes, tables, public inputs and zero persistent stack usage.
- On the same 10,676-case corpus as baseline `ff1b602`, V1/V5 improve **516.095822 → 511.342357** and V2/V3/V4 **472.095822 → 467.342357** cycles. The current upstream stable-input correction is retained.
- Native FAST24 improves **400.301600 → 395.756600** cycles on identical 30,000-pair inputs, with 4,265 independent Reduced6502 result/cycle checks and no mismatches.
- ATAN2 checks negative X before zero: V1 averages **47.462814**, V2/V3/V5 **43.970627** cycles. Negative-X calls save 2 cycles; X=0 costs 4 extra cycles in V1 or 2 in V2/V3/V5. Outputs and resource use are unchanged; V4 retains exact REU lookup.
- Exhaustive ATAN2 and strengthened SMUL24 ABI/interference checks are included in CI. Source mirrors, public tables and current evidence are regenerated.
- Regenerated V5 from current donors, including the upstream SDIV16 late-copy change; signed division/modulo validation passes 364,533 calls.
- See [the review](docs/OPTISEARCH_REVIEW_2026-10-07.md) for scope, attribution, candidate decisions, paired comparisons and reproduction commands.

## 2026-10-07 — SDIV16 deferred q>=2 magnitude copy

- Generalized the stable-input optimization to the fast signed 16-bit divider in V2-V4.
- Positive/positive q=1 cases now subtract directly from preserved public inputs and avoid materializing four private magnitude bytes; q>=2 pays the copy only when needed.
- Canonical V1/V2/V3/V4/V5 SDIV16 means are **187.131298 / 168.393021 / 170.582116 / 168.745038 / 171.905344 cycles**.
- Research PP-focused corpora improve by about 4.7-4.8 cycles; V2 remains exactly packed against the unsigned engine with no overlap.
- Restored the V2 SDIV32_32 helper islands accidentally collapsed during the prior source-regeneration cycle; the repair is taken instruction-for-instruction from the last known-good pre-PR-22 native mirror.
- ABI, ZP use, persistent stack and tables are unchanged; signed-division, layout, publication, deterministic-rebuild and Turbo gates pass.

## 2026-10-07 — SMUL16 stable-input Y0 optimization

- Generalized the stable-input optimization used by SMUL24/SMUL32 to signed 16x16 multiplication.
- V1/V5 FAST17 no longer save Y0 into SMC on X-negative paths; V2-V4 remove the unconditional executable-ZP Y0 save and relocate the 116-byte core symbol map safely.
- Canonical V1/V2/V3/V4/V5 SMUL16 means are **292.349787 / 248.802333 / 249.107696 / 249.144492 / 292.026700 cycles**.
- V2 research shows every call improves by 2-4 cycles; SMUL16_SHR8 inherits the same core improvement.
- ABI, executable-ZP footprint, persistent stack usage and tables are unchanged; signed-multiply, deterministic rebuild, publication and Turbo relocation gates pass.

## 2026-10-06 — SMUL24 stable-input q2 correction

- Removed the mixed-sign X<0,Y>=0 Y2 self-modifying save; the signed correction now re-reads stable public input MATH_IO+$06.
- Canonical V1/V2/V3/V4/V5 SMUL24 means are **512.981735 / 468.662931 / 468.354504 / 468.731839 / 512.416770 cycles**.
- The focused q2 path is exactly **2 cycles faster** with no ABI, ZP, stack-page, or table changes.
- Signed-multiply, multiply-refresh, direct-output, deterministic rebuild, published-source, Turbo relocation/boundary, and package gates pass.

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
