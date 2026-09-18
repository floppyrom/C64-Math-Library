## 2026-09-18 — stable 46th entry: Q8.8 VEC2 normalization

- Promoted `MATH_VEC2_NORMALIZE_Q8_8` at `REG_GAME_API+$39` / reference `$5E39`, expanding the stable public API from 45 to **46 entries** across V1–V5 and generated Custom Pareto builds.
- Contract: signed Q8.8 X/Y -> signed Q1.15 normalized X/Y; inputs preserved; `C=1` only for `(0,0)`, which returns zero output.
- Final means: **V1 198.770271**, **V2 189.260317**, **V3 170.058633**, **V4 170.058633**, **V5 198.770271 cycles** on the 107,396-vector deterministic corpus.
- V1/V5 retain the 31-byte low-ZP contract; V2 uses the Pareto-fast stock backend. V3/V4 replace the reciprocal/multiply stage with a 32 KiB direct ratio-index table in `$8000-$FFFF` of relocatable `REU_TURBO16_BANK`, requiring no additional V3 REU bank.
- Corrected full-domain certification passes at **<=0.360856382 degrees / <=200 Q1.15 LSB**, inside the public <=0.3621 degrees / <=202-LSB contract.
- Fresh V1–V4 reference/alternate source builds pass **46/46 entries, 4,589 calls per map**. V5 exposes the same routine through its generated and shipped API includes. Custom Pareto validation now totals **55,068 common-API calls** across 12 builds.
- Updated canonical source regeneration, REU image generation, performance/resource tables, API includes, manual, profile-selection/REU documentation and package metadata.

## 2026-09-17 — ATAN2 fast tiers + game audit

- Reworked stock-C64 `MATH_ATAN2_8` around compressed signed-magnitude log differences and generated final-angle tables. Exhaustive 65,536-vector validation keeps maximum error to one 1/256-turn phase unit.
- Final timings: **V1 50.441345 cycles mean (30–53)**; **V2/V3 46.953064 (30–48)**; **V4 remains exact at 48 fixed cycles**; **V5 imports the V2 fast tier at 46.953064**. All stock implementations use 0 extra ZP.
- V1 keeps the compact 512-byte table point. V2/V3 use 1280 bytes of ATAN2 tables. V5 adds the fast tier through three formerly unused 256-byte table pages, remapping the V2 donor's third extra page away from V1-owned data.
- Added hard V5 page-collision guards and exhaustive V5 result/cycle-vector parity against V2, including cold-load/no-`MATH_INIT` coverage. V5 now records **144,246 direct-import cases**.
- Added independent Custom Pareto pack `atan2_fast` (**0 ZP / 768 B**), so the selector accounts for the speed/RAM trade-off explicitly. Current equal-weight extra-RAM points are **6021 / 6611 / 7371 / 6207 / 7557 B** before the full-V2 endpoint.
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
- Exact extra-RAM accounting now includes the actual emitted init helper rather than a conservative allowance. Current default points use 6021 / 6611 / 7371 / 6207 / 7557 bytes of extra private payload before the 221-ZP full-V2 endpoint (208-byte resident increase vs V1).
- Certified selectable packs cover the independent 0-ZP/768-byte `atan2_fast` upgrade, V5 zero-ZP division/modulo/trig imports, initialized UMUL32, V2 UMUL8/SMUL8, the record UMUL16/UMUL24 pack, and native executable-ZP SMUL16. Workload weights can change the chosen pack at the same resource budget.
- Validation: 12 representative generated builds across reference/alternate maps, **45/45 entries and 4,172 calls each (50,064 common-API calls)**; 75,644 direct V2 cycle-parity cases including exhaustive ATAN2; exhaustive 65,536-case UMOD8; 50,144 additional SMUL16 cycle-parity cases; 25,000 mixed-workload iterations; 10,000 ZP-guard iterations; deterministic rebuilds; V1/V5 endpoint identity; and **12/12** invalid resource/configuration tests.

# 2026-09-06 — V5 Hybrid Low-ZP

- Renamed the project presentation to **C64 Math Library**; the stable 45-entry callable surface remains its public API.
- Added **V5 Hybrid Low-ZP**, a stock-C64 profile that keeps V1's 31-byte normal ZP window while importing selected faster V2 division/modulo/trigonometric paths.
- Direct gains vs V1: UDIV16 14.23%, UDIV24 9.37%, UDIV32/16 11.39%, UMOD16 13.97%, UMOD24 9.25%, UMOD32/16 11.35%, COS8 20.69%, SINCOS8 20.51%; UMOD8 improves 0.71%.
- Added deterministic source-derived hybrid builder with configurable `HYBRID_CODE` and no runtime dispatch overhead.
- Validated 45/45 stable entries and 4,172 calls on both reference and alternate V5 maps; 144,246 direct-import cases including exhaustive ATAN2 result/cycle parity; exhaustive UMOD8 and trig-domain checks; V2 cycle parity for certified imports; 31-byte ZP confinement with all 225 outside ZP bytes unchanged; 2,000 cold-load calls without `MATH_INIT`; deterministic rebuild and 8/8 invalid-map/config checks.
- Clarified non-reentrancy: sequential calls, including calls repeated inside ordinary loops, are fully supported.
- Reference V5 places its private 4608-byte hybrid region at `$A000-$B1FF` (RAM under BASIC ROM); applications must bank BASIC out while executing it or relocate `HYBRID_CODE`.

# Changelog

## 2026-09-14 — UMUL record upgrade + consolidated resource index

- Resident `UMUL16` now uses the qualified 17-ZP record-derived fused quarter-square kernel; V1/V5 preserve the persistent `UMUL32_READY` state contract.
- Resident `UMUL24` now uses the certified 24-ZP `reverse_24zp_carry` record kernel.
- V3/V4 Turbo32 now uses the stack-free 135-ZP `ram135` record-family compromise: reference ZP `$0A-$90`, legal origins `$02-$79`, with BEGIN/CALL/END measured at 326 / 728.947080 mean / 371 cycles.
- The absolute 606.337632-cycle UMUL32 record remains intentionally outside fixed profiles because it reserves hardware stack-page space; shipped fixed choices reserve 0 persistent stack-page bytes.
- Custom Pareto current extra-private-RAM points are 6021 / 6611 / 7371 / 6207 / 7557 bytes before the 221-ZP full-V2 endpoint.
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
