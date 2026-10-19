## Unreleased — original V1 DIST8_FAST measured full-public speed

- Authenticate original 61-byte signed8 fast distance approximation against 512 full-public signed pairs at two relocations, preserving the existing output semantics and 0 ZP / 2 scratch bytes.
- Register measured source for operation-first speed selection under RAM budgets. Preserve V1–V5 images and avoid slower substitutes. Isolated coverage reaches 43/56 only after complete exact-head qualification.

## Unreleased — shared original SIN8/COS8/SINCOS8 public speed provenance

- Authenticate the unchanged 11/15/22-byte canonical V1–V5 trigonometric
  sources on all 256 phases, two code origins and exactly one shared
  immutable sine-table page, with complete X/Y/Z/C and SP preservation.
- Enable measured speed objective for all three public API names without
  replacing a historical fast source; qualified catalog grows to 42/56.
- Native VICE r46284 and exact SHA256 publication required before merge.

## Unreleased — signed SMULDIV16 quarter-square + V2 fast public source

- Compose the immutable canonical signed 16×16 quarter-square source and
  already source-qualified V2 signed 32/16 division magnitude core with an
  independent public SMULDIV16 adapter; no changes to profile binaries.
- Retain the 439-byte/zero-ZP compact source; the fast 4,263-byte image
  requires 12 exclusive ZP and 4 ordinary scratch bytes.
- Verify 512 matched Q32/R16/C and signed full-product calls at two origins,
  a 150-call/24-frame busiest-math workload, two native VICE r46284 layouts,
  and source integrity. Coverage gains are provisional until the dependent
  unsigned UMULDIV16 source and full exact-head CI pass.

## Unreleased — qualified read-only signed8 quarter-square Pareto choice

- Preserve the exact V1–V5 46-byte signed SMUL8 SMC source and all four
  511-byte historic lookup planes while introducing a stock 6510 read-only
  producer with two 511-byte quarter-square planes and a 64-byte signed
  correction slot, 1,159 image bytes, 0 ZP and two scratch bytes.
- Exhaustively test 65,536 signed8 pairs at two code origins, 512 identical
  complete-public-call cycle measurements, and a 150-call/24-frame math
  replay. Historical V1 remains faster (~68 mean CPU-model cycles vs ~123),
  while the new choice saves more than 1,100 bytes of total main RAM.
- Add native VICE r46284, exact signed public-call preservation, RAM-aware
  selection, and mixed UMOD8/SMUL8 speed checks. Never substitute the
  read-only candidate for the fast historical kernel in speed mode unless
  project RAM/writable-code constraints exclude V1.
- Operation-first catalog increases to 37/56 APIs with same-public-call
  speed selection after exact-head publication and native CI validation.
  Historical profiles remain unchanged.

## Unreleased — signed Q8.8 scaled quarter-square multiplier

- Add an independently source-linked `SMUL16_SHR8` quarter-square implementation
  with bounded signed32 correction and 32-byte public Q24 byte-slice.
- Retain 184-byte/0-ZP compact source (six scratch) and 1,383-byte/0-ZP
  QS source (four scratch) as separately selectable size/speed alternatives.
- Add two-address-space 512-call source-model qualification, 150-call/24-frame
  math latency tests and 192 real native VICE r46284 signed public calls.
- Speed-selection coverage reaches 36/56 APIs on the combined dependency tree
  **once complete exact-head CI qualifies**; all five historical profiles remain.

## Unreleased — signed16 quarter-square canonical source performance

- Source-link the canonical 233-byte unsigned quarter-square 16x16 engine,
  its two immutable 511-byte planes and a bounded signed high-word correction
  entry for `SMUL16`. Exact full signed32 output, 0 ZP, 4 scratch bytes.
- Preserve the compact 161-byte/0-ZP, 6-scratch signed alternative;
  compare 512 matched full public calls, paired 24-frame math cycles and
  192 native VICE r46284 calls at two relocated public addresses.
- After complete qualification, speed selection expands to 35 of 56 APIs.
  Historical V1–V5 binaries, REU, and Turbo alternatives remain unchanged.

## Unreleased — source-linked historical V2 signed shifted16 speed

- Offer historical V2 32/16 split-tail magnitude with direct signed
  `SDIV16_SHL8` Q24/R16/C adapter; source-qualify on 384 matched public
  calls at two relocation origins, busy math frames and pinned VICE r46284.
- Retain both 2,624-byte/12-ZP speed and 237-byte/zero-ZP compact options.
  Qualified installer speed coverage rises to 34/56 pending full CI.
- No historical V1–V5 profiles, REU services or Turbo binaries are changed.

## Unreleased — stock-C64 reciprocal threshold and exact-table Pareto frontier

- Add three source-linked URECIP16_Q16 choices: original 99-byte zero-ZP
  restoring source; 448-byte V3/V4-inspired large-denominator quotient
  1..15 threshold gate, sharing its original exact fallback; and a
  1,544-byte 0-ZP exact table/binary-threshold producer.
- Guard output Q24/C, untouched Q3/R/N/D bytes, relocations, source hashes,
  all 65,536 divisors, three-way identical-input full public-call timings,
  automatic RAM/ZP-aware selection and dual-origin native VICE.
- Explicitly retain historical V3/V4 REU reciprocal baseline and forbid
  comparison of old resident timings with new public wrapper timings.
- Increase authenticated operation-first speed-selection support to 33/56
  **subject to complete CI and package checksum qualification**.

## Unreleased — historical V2 UDIV16_SHL8 source-linked speed selection

- Port the canonical V2 32/16 split-tail producer to full Q24/R16/C
  shifted-numerator API, preserving input and output sentinels.
- Retain both 129-byte/0-ZP compact and 2,368-byte/12-ZP V2 Pareto variants;
  compare 384 complete-public same-input calls at two origins.
- Add source-authenticated speed selection, 150-call/24-frame math workload
  comparison and pinned native VICE r46284 relocation tests. Increase speed
  qualification coverage to 32/56, pending exact-head publication gates.
- Preserve all five historical binaries, their source hashes and hardware
  compatibility surfaces.

## Unreleased — two-layout full-56 ISQRT16 dual-source native proof

- Add a real VICE integration gate for both ISQRT16 implementations selected
  inside a full 56-operation resident PRG, using two relocated layouts and 96
  deterministic operand cases per case: 384 complete public native calls.
- Keep all other 55 implementation choices pinned to the resource-optimal
  baseline when replacing the root kernel. This isolates source correctness
  and avoids re-enumerating the all-56 global resource frontier; no public
  operations, source assemblers or old-profile outputs change.
- Check exact Z16 and carry, preserved N16, valid RAM/ZP budget, nonoverlap
  with monitor harness and buffer arrays, and two independently preserved
  source-output digests. This is a representative combined image test,
  not an exhaustive runtime verification of the 56-operation catalog.

## Unreleased — tableless zero-ZP ISQRT16 and automatic size/speed fallback

- Add an independently linkable 137-byte restoring ISQRT16 implementation,
  with six bytes of reusable call scratch, zero ZP and no writable code,
  lookup tables, initializer or additional hardware. The historical 806-byte
  source and its exact aligned table layout remain unchanged.
- The exact resource optimizer can now select ISQRT16 under a 175-byte total
  RAM budget (including public I/O). With at least 1,056 bytes at $8000,
  comparable same-input speed selection retains the much faster original
  square-table implementation: 65.10 vs 1,215.37 simulated cycles per
  complete public call on an authenticated 384-case corpus.
- Extend ISQRT16 standalone qualification to exhaustive 65,536 input values,
  both real VICE RAM layouts and the already-qualified old table source;
  enforce source identities, unchanged caller input, output, stack, carry and
  no self-modification. No historical fixed profile sources are altered.

## Unreleased — V2 canonical UDIV16 zero-ZP historical donor and speed provenance

- Transplant the complete 1,481-byte original V2 size-fast 16/16 divider as a
  stock NMOS 6510 independently linkable source. Only fixed profile jump stubs
  and symbolic N/D/Q/R names are rewritten; generator checks the original
  canonical V2 donor text, and the existing fast 323-byte biased 2-ZP kernel
  remains the resource-small, cycle-fast default.
- Public full-call, exact same 384 N16/D16 inputs at $8000: biased 162.729
  CPU-model cycles (355 RAM bytes including 32-byte public I/O, 2 ZP);
  V2 zero-ZP 177.836 cycles (1,513 RAM bytes, 0 ZP). This is a **resource
  alternative**, not a claimed speedup. The builder chooses biased whenever
  the 2-byte ZP budget fits, and V2 when ZP=0 with enough RAM.
- Both relocations ($8000, $7123) checked against exact Q16/R16/C and caller
  input, sentinel, SP and code preservation. Native VICE at both maps passes
  384 public calls. Matched-input CPU-model speed selection is now qualified
  for 22 operations. Profile PRGs and original canonical source stay unchanged.

## Unreleased — same-corpus phase-accurate ATAN2 speed frontier

- Add ATAN2_8 as a 21st independently speed-qualified API. The historical
  85-byte sum-fast + 1,024-byte table producer averages 40.927 CPU-model
  cycles per public call, versus 44.417 for the 94-byte compact + 512-byte
  table producer. The faster source uses 1,312 B RAM at $8000; compact
  requires only 800 B. Both require no ZP and preserve the public ABI.
- Fixed 384-pair input corpus and public output hash, source/table provenance,
  exact phase/A/carry/input/sentinel/stack checks, two source relocations,
  RAM budget fallback and fail-closed resource contracts. Both historical
  sources already passed exhaustive 65,536-vector proof and real native VICE.
- No historical resident profile code is changed. CPU-model cycles are not
  measured physical machine timings.

## Unreleased — source-qualified accurate-distance speed choice

- Qualify `DIST8_ACCURATE` as a 20th workload-speed API using a fixed,
  identical signed-byte 384-pair CPU-model public-entry corpus. The V2
  ZP-scratch source averages 78.08 cycles; the V1 0-ZP RAM-scratch source
  84.64 at $8000. Both use the unchanged exact historical 512-byte tables.
- Preserve input bytes, R8/carry, stack, output sentinels and code/table
  immutability under two memory layouts, plus missing-source and resource
  metadata fail-closed checks. Builder keeps V1 at ZP=0 and chooses V2
  when 2 ZP bytes are available. No physical C64 timing is asserted.

## Unreleased — same-input complete public speed selection for UMOD16

- Add `UMOD16` to the builder's comparable weighted-speed frontier (19 APIs).
  Independently link the existing 2-ZP biased source and the 0-ZP direct
  chain; compare 384 identical deterministic operand pairs at the public
  `R16/C` ABI, with N/D, quotient, high-byte sentinels, stack and code intact.
- On the fixed corpus, direct zero-ZP averages approximately 504 CPU-model
  cycles versus 529 for the biased source at $8000: faster but requiring
  1,010 main RAM bytes versus 294. When RAM is constrained, choose biased;
  when ZP=0, choose direct or reject budgets that cannot fit it.
- Both source variants have native VICE two-map coverage via the existing
  selective-linker gate. No assembler source or old resident profile changes.

## Unreleased — authenticated same-corpus speed selection for UDIV24/UMOD24

- Extend the operation-first builder's workload-weighted `speed` objective
  from 16 to **18** source-qualified public APIs by adding `UDIV24` and
  `UMOD24`. Independently assemble and benchmark both shared Q24/R24/C
  producers on the identical deterministic 384-pair public-call corpus.
- Source-authenticate the V2 Repose 3-ZP writable-SMC donor and the 0-ZP
  portable restoring alternative, with complete N/D, output sentinel,
  carry and stack preservation. The compact 226-byte RAM alternative wins
  when budgets prohibit the 1,493-byte V2 high-speed producer.
- For code base $8000 the CPU-model complete-call means are 2,127.995
  (portable) versus 1,117.047 (V2), a 47.5% mean cycle reduction on this
  corpus. No physical C64 timing or profile parity is claimed. Both source
  variants already have independent two-map native VICE qualification.

## Unreleased — all-56 resident native VICE multiplication integration

- Validate a single 56-operation linked C64 PRG at $2000 and $4321 using
  the six unsigned/signed 8-, 16- and 24-bit multiplication public entries:
  96 complete native x64sc calls per API and map, **1,152 calls** in total.
- Reuse proven standalone public ABI validators to check products, carry,
  operand preservation and sentinel bytes. Preserve executable/data/harness
  nonoverlap across both code layouts, with a four-byte ZP budget.
- Keep this as an independent CI workflow step alongside the earlier 2,304
  DIV/MOD integration calls. No math producer, benchmark or V1–V5 profile
  implementation is changed; physical hardware timing is not claimed.

## Unreleased — expanded 56-operation integrated native VICE division proof

- Expand the all-56 linked-PRG two-map native VICE integration gate from four
  to twelve public DIV/MOD operations: unsigned 8, 16, 24 and 32 bits plus
  signed 8- and 16-bit quotient/remainder producers. Run 96 operand cases per
  export per RAM origin ($2000 and $4321): **2,304 native public calls**.
- Preserve negative-operand and sign/overflow edge cases, zero-divisor carry,
  24-bit high-output sentinel bytes, and input preservation where required.
  Keep the harness and all operand/result stripes clear of code and public IO.
- Reuse independently qualified native x64sc validators without changing
  any arithmetic implementation, selection policy, or historical profile.
  This remains representative combined-image integration, not a full runtime
  qualification of every one of the 56 exports or a hardware cycle claim.

## Unreleased — full 56-operation linked native VICE integration test

- Build all 56 C64 math operations into one compact PRG and independently
  exercise the 16-bit/32-bit division and modulo exports across two non-ROM
  code origins using real x64sc VICE: 768 complete public Q/R/C calls.
- Validate no overlap between executable code, monitor harness, operand
  corpus and output buffers; retain four-byte ZP and 18,000-byte main RAM
  budgets. No packaged C64 binaries are changed or added.

## Unreleased — exact resource selection across all 56 operations

- Replace the `size`, `balanced`, and `zp` Cartesian product evaluator with
  deterministic exact branch-and-bound. A complete 56-operation selection
  otherwise has 143,327,232 post-Pareto candidate combinations.
- Use admissible unaligned code lower bounds for connected groups of
  potentially shared physical producers, plus live scratch, persistent-state,
  and ZP minima. Final candidates still use the original code layout,
  producer sharing, budget checks and lexicographic tie-breaks.
- Add constrained and unconstrained exhaustive-oracle comparisons involving
  FAST31, aligned ATAN2/ISQRT32, shared DIV/MOD and pinned hybrid options.
  Include a full 56-operation stress check. Arithmetic source, public ABI
  and historical resident profiles remain unchanged.

## Unreleased — exact scalable global workload-speed selection

- Replace the speed objective's exponential full Cartesian enumeration with
  an exact branch-and-bound solver for the sixteen currently speed-qualified
  operations. The solver uses independent per-operation same-corpus CPU-model
  cycle lower bounds, plus safe unaligned packed-code, ZP, shared scratch and
  persistent-state bounds. Full final candidates still use the original
  page-aligned, shared-producer-aware linker cost function and deterministic
  cycle/RAM/ZP/fingerprint tie-breaks; no heuristic selection is introduced.
- Preserve pinned variants and explicit per-operation workload frequencies;
  reject incomplete, non-finite or non-positive candidate cycle measurements.
  Exhaustive regression compares randomized mixed shared FAST31/DIV/MOD/
  ISQRT selections under differing RAM and ZP limits. A sixteen-operation
  stress test checks that the solver does not enumerate the entire product.
- The change affects *selection scalability*, not 6502 kernel timing or
  the public library ABI. V1–V5 historical binaries remain unchanged.
- Only prune on RAM score ties when weighted CPU costs are provably
  identical or exactly representable integers; preserve fractional-cycle
  ordering for near-equal candidates.

## Unreleased — compact source-relocated V2 32/32 hybrid (2496 B)

- Pack the unchanged V2 32/16 donor into shorter relocatable code islands,
  followed by the existing full-width ZP-tail and shared public dispatch.
  Shrink the hybrid image from 3,200 to 2,496 bytes (704 B, 22%) while
  keeping 12 call-exclusive ZP bytes and full 32-bit Q/R/C semantics.
- Preserve standalone V2 source ABI/layout by making code-island offsets
  an explicit optional assembler argument; donor bytes remain unmodified.
- Require exact resource contracts for the speed benchmark, validate
  two-map complete public calls in the CPU model and native VICE, and
  retain historical 3,200 B evidence in the earlier research entry.

## Unreleased — selectable unrestricted V2-lowdivisor 32/32 hybrid

- Promote the native- and CPU-qualified unrestricted public Q32/R32/C
  hybrid as `link:v2-lowdivisor-hybrid` for both `UDIV32_32` and
  `UMOD32_32`. A single source-authenticated 2,496-byte NOP-padded
  executable and 12 call-exclusive ZP slots serve both aliases; combined
  main RAM is 2,528 B including the common 32-byte public I/O region.
- Extend the authenticated 384-pair matched public-call speed basis to the
  unrestricted hybrid. The project selector retains small 4-ZP and zero-ZP
  implementations when RAM/ZP budgets prohibit the fast option. Hybrid
  benchmarks include both narrow and wide divisors, zero, C flag and Q/R.
- Add linked-binary two-map CPU proof, producer-sharing/resource fail-closed
  gates and native VICE both-export qualification. Preserve raw V2,
  full-width tail and source-generator SHA provenance in the manifest.

## Unreleased — unrestricted 32/32 historical V2 low-divisor hybrid experiment

- Assemble the existing certified V2 12-ZP 32/16 public Q/R producer and
  the independently certified 4-ZP full-width 32/32 tail in one source-
  authenticated 3,200-byte RAM image. Dispatch by the high divisor word:
  narrow divisors take historical V2; wide divisors retain full-width
  fallback. Clear the high public remainder word only after the 16-bit
  divisor path. Both public Q32/R32/C aliases share a dispatcher.
- Add two-code-map, unrestricted-operand CPU-model old/new correctness,
  carry/input/SP/code immutability, low-versus-wide mean-cycle comparison,
  and a real native VICE both-API/two-map qualification.
- Research only; 12 call-exclusive ZP and 3,200 executable RAM bytes make
  the new candidate a possible Pareto speed-over-RAM option, not a
  replacement for the stock 0/4-ZP alternatives or validated resident
  V1–V5 builds. No cycle-speed win or default promotion is claimed without
  the required benchmarks and exact-head tests.

## Unreleased — 32/32 DIV/MOD quotient/divisor cycle-tail research

- Add a deterministic, two-relocation nine-band public-ABI audit for
  `UDIV32_32` and `UMOD32_32` across all currently selectable
  32-bit quotient/remainder producers. Each run verifies exact Q32/R32/C,
  preserved numerator/divisor/SP and immutable code while measuring complete
  source-linked public-call cycles, nearest-rank p95, median and worst cases.
- Report source SHA256, RAM/ZP, 64 identical inputs per divisor/quotient band,
  candidate-wise means and paired fastest/slower/equal counts to expose
  small-divisor and high-quotient regressions hidden by one average.
  Two-code-map assertions and the full source audit are CI-required;
  the complete JSON diagnostic is uploaded as a 30-day GitHub Actions artifact.
- Research-only: no new kernel, production promotion, V1–V5 binary replacement,
  or native-VICE timing claim. The existing 16 speed-modelled APIs remain
  unchanged.

## Unreleased — shared zero-ZP Q32/R32 DIV and MOD physical producer

- Publish an optional `link:shared-aligned-zerozp` source-linked variant
  for both `UDIV32_32` and `UMOD32_32`, using the qualified 325+251
  zero-ZP aligned divide source with two public entry aliases.
  Both calls produce the complete Q32/R32, preserve inputs, and propagate
  divide-zero carry, so one kernel can replace two independently linked
  files without altering public behavior.
- Deduplicate 576 executable bytes and four private ordinary-RAM scratch
  bytes across both APIs, with one physical image occupying **612 B total
  main RAM** (including the common 32B public interface), compared to
  **1,108 B** for separately selected aligned DIV and specialized MOD.
  Code saving: 496 B; ZP remains zero.
- Extend the deterministic 384-pair public-call speed model to include
  the shared candidate for both APIs, with strict source-hash, segment,
  shared-producer and caller-ABI checks. Add two-map alternating DIV/MOD
  CPU-model regression, a 612B RAM gate, weighted speed selection under
  hard RAM constraints, and native VICE validation of both linked exports.
  This is not yet a transplant of the historical fast V1–V5 DIV32 kernels.

## Unreleased — 32/32 unsigned public division/modulo cycle baseline

- Add 384 identical-input complete public-call cycle models for
  `UDIV32_32` and `UMOD32_32`, including divisor zero, Q32/R32,
  C=1 on D=0, input preservation, SP/stack, deterministic SHA hashes
  and non-self-modifying executable immutability. Independently source-
  qualify both DIV32 variants (4-ZP tail vs 4-byte RAM-scratch aligned),
  plus the dedicated zero-ZP modulo source; no historical donor times.
- Expand workload-aware speed selection from 14 to **16** public APIs,
  with exact source size/ZP/scratch assertions and original code-segment
  relocations. Add two-layout per-operation model tests, zero-ZP fallback,
  mixed weighted calls, and candidate/resource tamper rejection.
- This stage establishes a baseline for the next optimized 32/32 kernel
  transplant; the existing public algorithms are unchanged.

## Unreleased — selectable canonical V2 fast unsigned 32/16

- Make the fully qualified historical V2 size-fast 32/16 DIV+MOD donor
  source an independently linkable, shared fourth variant
  `link:v2-sizefast-public`: two relocated core islands, a complete public
  Q32/R16 adapter, 2,368-byte deterministic packed image, 12 exclusive ZP
  and zero ordinary scratch RAM. One linked binary exports both DIV and MOD.
- Extend the identical 384-pair public-call CPU-model speed basis to the
  newly source-authenticated donor and its complete adapter (mean ~932.63
  cycles at `$8000`). Preserve compact zero-ZP (131 B), portable zero-ZP
  (162 B), and unrolled zero-ZP (1771 B) candidates. Full public Q/R/C
  correctness and original inputs/SP are tested at two memory placements;
  source-code and output provenance are sealed.
- Add two-map operation-first linked-PRG CPU and native x64sc qualification
  (DIV/MOD), 12-ZP/2400-B resource boundary and low-resource fallback
  tests. The historical native-only performance figure is not conflated
  with the public-call mean. The opcode and non-reentrant constraints remain
  explicit.

## Unreleased — historical V2 12-ZP 32/16 public-adapter research

- Import no duplicate executable: the relocation adapter reads the certified
  `v2_pareto_fast/resident/modules/pareto_udiv32_16.a` donor directly and
  moves its two code islands plus twelve private ZP operands. It adds a
  public staging/output shim to preserve the operation-first Q32+R16 ABI,
  public N32/D16 inputs, divide-by-zero output and carry.
- Add exact two-relocation CPU-model correctness and same-input complete
  public-call cycle comparisons against the qualified 1,771-byte, zero-ZP
  unrolled baseline, and direct-source native x64sc Q/R/C proof for both
  DIV/MOD exports. Stable LAX/ANC 6510 opcodes are an explicit dependency.
- Research only: no production builder variant has been registered, no
  profile timings imported as public-call measurements. Qualification and
  resources determine whether this fast donor merits a separate selection.

## Unreleased — selectable zero-ZP unrolled shared U32/16 producer

- Promote source-qualified 32-round unrolled accumulator divider into the
  operation-first builder as `link:accum-unrolled-32` for both
  `UDIV32_16` and `UMOD32_16`, sharing one public Q32/R16 producer,
  1,771 executable code bytes and one ordinary RAM scratch byte, zero ZP.
- Extend the common 384-pair public Q/R/C speed model to three variants,
  with exact source hashing, return-cycle measurements and identical
  operands. Source correctness is separately tested at two code origins,
  and the builder tests resource-constrained speed selection, mixed DIV/MOD
  outputs, immutable code, and 1,804-byte combined main-RAM charge.
- Qualify both linked exports on two native VICE memory maps. This is an
  optional speed-over-RAM frontier; the 131B zero-ZP accumulator and 162B
  reference variants are preserved, and the historical V2 fast register
  core remains future work.

## Unreleased — experimental unrolled zero-ZP public U32/16 producer

- Create a static 32-iteration unrolled derivative of the qualified
  131-byte accumulator-remainder 32/16 divider, using distinct local branch
  labels and preserving complete public quotient Q32, remainder R16, C flag,
  caller input memory, and X=0 on exit. No extra RAM scratch or zero-page
  bytes are required; the tradeoff is larger resident code.
- Add exact old/new matched-operand CPU-model proof at two code origins,
  complete Q/R/C public calls, code immutability and mean-cycle comparison.
  Native x64sc tests compare all Q/R/C outputs on 768 isolated old/new DIV
  and MOD calls across two code origins; do not claim hardware cycle speed.
- Research only: no selectable builder variant or default policy change until
  source qualifications and RAM-vs-speed Pareto screening are complete.

## Unreleased — unsigned 32/16 shared-quotient speed foundations

- Qualify `UDIV32_16` and `UMOD32_16` for project-weighted automatic
  `speed` selection: 384 identical source-assembled public calls for each
  candidate, including divide-by-zero behavior (Q=R=0/C=1), full Q32,
  R16, preserved inputs/SP, and instruction-image immutability.
- Compare the 131-byte/1 scratch accumulator-remainder source with the
  162-byte/3 scratch portable restoring baseline, both using zero ZP,
  shared quotient/remainder entrypoints and source-hash provenance.
  Add two-relocation, exact-RAM, global weighted-sharing and fail-closed
  candidate/resource CI regressions. Speed-selected operations: 12→14.
- These are portable-source baseline comparisons; no historical V1/V2
  native DIV32/16 optimized kernel has been transplanted yet.

## Unreleased — matched-input READY/SHR16 FAST31 speed promotion

- Add four same-operand public-call speed bases for UMUL32_READY,
  SMUL32_READY, UMUL32_SHR16, and SMUL32_SHR16. Each API compares compact
  zero-ZP, shared unified zero-ZP, and shared FAST31 on a deterministic
  192-pair signed/unsigned corpus with source SHA, exact geometry, public
  I/O preservation, stack/carry correctness and 10 SMC-byte protection.
  Q48 uses the complete >>16 six-byte output and does not reuse full64
  arithmetic-only cycle measurements.
- Expand workload-weighted profile-independent global `speed` selection
  from eight to **twelve** APIs, retaining exact 512-byte code/four aligned
  512-byte table slots, 31 call-exclusive ZP, per-producer sharing and
  low-ZP fallbacks. Add budget/weighted-selection and fail-closed candidate
  regression tests plus required CI execution.
- CPU-model benchmark times remain estimates at the nominated placement;
  actual native VICE is a correctness gate, not a claim of hardware timings.

## Unreleased — six-entry FAST31 operation-first builder selection

- Register the certified shared V2 FAST31 image under the existing
  `link:fast31-shared-full64` identity for `UMUL32_READY`,
  `SMUL32_READY`, `UMUL32_SHR16`, and `SMUL32_SHR16`.
  READY aliases use the unchanged unsigned/signed full64 entry addresses;
  SHR16 entries share a single carry-preserving 48-bit output shifter.
- All **six** public operations now independently link and may share one
  FAST31 512-byte code slot and four 512-byte lookup slots, with only
  31 call-exclusive ZP bytes and 32 public IO bytes: **2,592 B main RAM**
  at `$8000`. The existing 375-byte zero-ZP six-entry unified fallback
  remains independently selectable.
- Add exact linked-binary CPU correctness and native VICE tests of all
  six mixed public exports across two relocation maps, plus resource
  boundary and reserved-ZP negative tests. Separate speed selection for
  READY and SHR16 remains future work; no incomparable full64 timings
  are reused for the four additional API contracts.

## Unreleased — six-entry FAST31 source qualification

- Extend the qualified 31-ZP, four-table, 512-byte shared FAST31 source
  with separate signed/unsigned Q48 SHR16 exports, while keeping the original
  full64 entrypoints as state-independent READY aliases. The extra two Q48
  wrappers share a single six-byte public-output shifter, preserving carry
  clear from the full-width arithmetic call. No duplicate 32-bit product
  producer or extra lookup pages are introduced.
- Add exact two-code-map CPU-model qualification of all six operations,
  10 exclusive SMC operand whitelist assertions, original input preservation,
  C=0, and full signed/unsigned fixed-point high-48 output assertions.
  Qualify all six code-assembled entrypoints under native VICE.
- This is a source-level **research stage**. The four additional operations
  are not yet registered as FAST31-selectable builder variants; a separate
  builder-API promotion with resource/ownership and speed accounting is
  required after native correctness is confirmed.

## Unreleased — FAST31 two-entry shared signed/unsigned producer

- Add `link:fast31-shared-full64` for both `UMUL32` and `SMUL32`,
  backed by one independently linked image with unsigned entry calling the
  original V2 arithmetic and a second signed entry correcting the high word.
  The shared identity deduplicates exactly one 512-byte code slot and four
  512-byte lookup slots; both APIs reuse 31 call-exclusive zero-page bytes.
- Main RAM for both operations at `$8000`: **2,592 B**, down from
  **5,152 B** when both separate FAST31 variants are pinned; save **2,560 B**.
  Both source-linked signed and unsigned historical variants remain usable
  independently; zero-ZP fallbacks remain in place.
- Extend both signed and unsigned 192-input comparable CPU-model performance
  bases to this shared source. Add mixed signed/unsigned alternating calls,
  two relocation maps, exact resource boundary/restriction tests, authenticated
  distinct public entrypoints and four native VICE runs across the two maps.
  All results remain CPU-model timing unless independently measured in VICE.

## Unreleased — signed FAST31 selectable-builder promotion

- Add `link:fast31-v2-signed` as a fourth-generation source-linked signed
  SMUL32 implementation. The global optimizer can compare three signed
  full64 candidates on one 192-pair operand corpus, including full public
  input staging/sign corrections and return. FAST31 is only chosen when the
  complete 31-ZP and page-aligned RAM resource constraints fit.
- Add two-relocation exact ABI/binary tests, zero-page overlap/budget
  negatives, alternating signed/unsigned FAST31 calls sharing exclusive ZP,
  and native VICE tests of the **builder-generated** signed binary. The
  signed and unsigned routines still carry independent table/code images.
- Retain zero-ZP compact and six-entry unified fallbacks; make SMUL32 the
  eighth operation supported by weighted project speed selection.

## Unreleased — signed FAST31 public-ABI source research

- Add `smul32_fast31_public.asm`: independently relocatable signed 32×32
  full-64 result using the certified V2 31-byte-ZP native unsigned producer,
  with exact X/Y sign correction restricted to the high product word.
  Unmodified public operands; C=0; D=0 prerequisite. The module is
  self-modifying and uses four exact 511-entry quarter-square tables.
- Generalize the existing source-locked FAST31 emitter to accept a second
  signed source and entry point while retaining the qualified unsigned default.
  Add two-relocation CPU-model and native VICE public-call tests. This
  candidate is **research-only** until source, native VICE, RAM geometry
  and signed speed comparisons qualify it for selective builder promotion.

## Unreleased — historical FAST31 builder promotion

- Enable the V2 31-ZP native producer as `link:fast31-v2-public` in the
  operation-first `UMUL32` catalog. The linker charges exact page-aligned
  code/table footprints, 31 call-exclusive ZP bytes, zero ordinary scratch,
  and writable executable RAM; generated lookup provenance is separately
  source-hash checked.
- Extend the shared 192-pair full64 CPU-model speed basis to all four
  competing algorithms using identical operands and full public call cycles.
  Automatically choose FAST31 only when its measured result and ZP/RAM budgets
  allow; retain zero-ZP quarter-square and compact fallbacks.
- Add independent-link CPU-model exact ABI, relocation, resource boundary and
  generated-binary native VICE two-map gates. This is not yet a port of
  historical signed FAST31, READY/SHR16 kernels or drive-side hardware.

## Unreleased — historical FAST31 unsigned 32-bit producer research

- Adapt the certified V2 31-byte-ZP native UMUL32 arithmetic source into a
  **standalone public-ABI research prototype**. Inputs remain in public X/Y,
  output full Z64, C=0; wrapper stages register operands and exports CPU/ZP
  result. Restores six table pointer highs on every public call for mixed-call
  safety; 31 volatile ZP bytes, four immutable 511-entry quarter-square planes,
  no REU or stack-page allocation, writable code required.
- Add a relocatable deterministic assembler and independent CPU-model and
  native VICE two-map qualification. This prototype is **not registered as a
  builder variant** until the native and resource audits qualify its contract,
  matched-input speeds and mixed-operation ownership.

## Unreleased — 32-bit unsigned quarter-square speed-source transplant

- Add a relocatable stock-C64 32x32->64 unsigned table-based convolution,
  adapted from the already source-qualified 8x8/16x16 quarter-square algorithm.
  Physical layout: 1028 bytes code, two 511-byte generated tables, four
  call-exclusive RAM bytes, zero ZP, no REU or initializer.
- Retain portable compact (204 B) and shared six-entry (375 B) alternatives.
  Add source/ABI checks at two relocations, native x64sc qualification and
  same-192-input CPU-model cycle benchmarks. UMUL32 joins workload-weighted
  speed selection without importing incomparable historical V1–V5 means.
- This is an algorithmic table-method transplant, not yet a direct port of
  the V2/V3/V4 FAST31/V29 resident kernel. Other 32-bit APIs remain separate.

## Unreleased — workload-weighted multi-operation CPU-model speed selector

- Extend the certified same-corpus speed selector from one operation to any
  combination of six benchmark-qualified public APIs, using explicit positive
  call counts and a global linked RAM/ZP budget. Each API compares its own
  variants on identical inputs; never combine unrelated historical profile
  cycle numbers or presume equal call frequencies.
- Emit a deterministic mixed-operation benchmark report, workload calls,
  corpus/source provenance and estimated workload cycles in the binary manifest.
  Preserve the original single-operation speed manifest contract.
- Add a tight-budget performance regression where reversed UMUL8/UMUL16
  workloads change which quarter-square kernel is linked. Add two-relocation
  native VICE mixed-operation tests, invalid-count/unsupported-API guards,
  documented CLI/JSON example and CI qualification.
- CPU-model estimates use nominal code placement; physical selected linked
  code placement and host hardware timing are not claimed as exact cycle truth.

## Unreleased — operation-first primary build setup (profiles become opt-in)

- Make the profile-independent C64 builder the README/quick-start front door.
  `make` now displays builder help; `make builder` compiles an example and
  `make builder CONFIG=... OUT=...` creates project-specific minimal PRGs.
- Publish validated, reproducible `examples/operation-first.json`, a migration
  guide with explicit performance/hardware qualification gates, and a CI smoke
  build that checks the selected API set plus RAM/ZP accounting.
- Preserve `make all`, V1–V5 reference files, Pareto builder, REU/Turbo/QS16
  features and benchmark provenance as opt-in compatibility tools. Full
  global automatic speed optimization remains incomplete.

## Unreleased — six-entry compact 32-bit producer sharing

- Introduce one 375-byte source-assembled, legal-NMOS signed/unsigned 32-bit
  multiplication producer, exporting independent UMUL32, SMUL32, READY aliases,
  and both >>16 Q48 fixed-point adapters. The 12 ordinary scratch bytes are
  call-exclusive; no zero-page, tables, REU, initialized READY state or SMC.
- The operation-first builder now offers `link:unified-375` for all six APIs.
  Global resource selection links its physical code image once when this is
  beneficial, but preserves smaller independently selectable standalone
  sources and existing pin semantics for single-operation builds.
- Selecting all six reduces executable code from 1,076 to **375 bytes**
  (−701 bytes, −65.1%), and total main RAM with I/O and scratch from 1,120
  to **419 bytes**, at unchanged ZP=0. No historical V1–V5 resident code or
  published speed metrics change.
- Add 2-map exact 64/48-bit edge/random CPU, carry/input/stack/code proofs,
  selective size/pin/budget regressions, and native VICE test of all six entry
  points, plus updated footprint-qualified preexisting READY and SHR16 tests.

## Unreleased — global shared-producer resource selection and performance workbench

- Correct automatic global RAM/size/ZP variant selection: a locally dominated
  source cannot be removed from the search frontier when it exports a shared
  physical producer that other selected operations might reuse. Retain
  share-eligible choices before global combination scoring; expert pins,
  single-operation results and emitted arithmetic code remain unchanged.
- Add a synthetic two-operation regression where retaining one 110-byte shared
  producer beats an 80-byte local alternative plus that same producer (190
  bytes), including a restrictive RAM budget and pin-rejection test.
- Add an on-demand / targeted-PR performance workbench: deterministic
  six-operation matched-input CPU-model report plus a SHA-256-stamped source
  snapshot for reproducible local native-6510/VICE qualification. No new
  historical speed ranking or resident-profile binary is published.

## Unreleased — measured source-only migration baseline groundwork

- Add deterministic 256-input, two-relocation CPU-model cycle reporting
  for the six newly source-linked operations. The report prints canonical
  corpus SHA-256, exact linked source SHA-256, call-through-RTS cycle
  distribution and actual memory/ZP resources, with ABI correctness checks.
- Wire the benchmark into the existing operation-first builder CI as an
  evidence-generating gate. This adds no resident changes and publishes
  **no unverified speed rankings or historical fast-kernel claims**.
- Document matched-input/per-operation comparison constraints and the
  remaining historical fast donor/transplant work.

## Unreleased — final operation-first source link: certified VEC2 normalization

- Add independently selectable `MATH_VEC2_NORMALIZE_Q8_8`
  `link:certified-stock`, transplanting the V1/V5 logarithmic-ratio
  source and exact generated stock table bytes into one reproducible,
  relocateable, page-aligned source. No floating-point approximation,
  precision-reduced replacement or reliance on the legacy resident image.
- Preserve signed Q8.8 X/Y and return signed Q1.15 unit vector in Z[0..3];
  carry set only for (0,0). Keep existing full-domain limits of
  <=0.3621 degrees and <=202 LSB from the unchanged certified donor.
- Declare 4 reusable ZP bytes, zero ordinary scratch, 3587 bytes of
  page-aligned source image span (including gaps, 2560 table bytes and
  865 occupied code bytes). Requires writable C64 RAM for existing
  self-modifying lookup dispatch, and uses the donor's stable NMOS LAX.
- Add three relocated CPU-model parity maps including page alignment,
  signed edge/random vectors and mixed link, and two native VICE maps.
  With stacked prerequisite migrations merged, all 56 public operations
  are independently source-linkable; speed-optimization and fast
  historical kernel transplantation remain separate work.

## Unreleased — independent signed/unsigned MULDIV16 sources

- Add zero-ZP `MATH_UMULDIV16` (288 B) and `MATH_SMULDIV16`
  (439 B) independent source-linked producers. Each performs a complete
  16×16 -> 32-bit product before a true 32/16 quotient/remainder
  division; six bytes of exclusive ordinary scratch RAM are shared.
- Preserve X16/Y16/D16 fields, produce Q32 and R16; signed path
  truncates quotient toward zero and follows the product sign for
  remainder. D=0 returns zero Q/R and C=1.
- Three RAM/I/O relocation maps, signed/unsigned edge/random
  reference tests, budget enforcement and two native VICE placements.
  The portable sources are not the faster historical fused resident
  donor kernels; no speed claims or profile binaries are changed.
- Once preceding READY PRs merge, independently linkable API reaches 55/56.

## Unreleased — safe state-independent 32-bit READY fallbacks

- Link `MATH_UMUL32_READY` and `MATH_SMUL32_READY` independently
  using the existing 204-byte unsigned and 293-byte signed full64
  `link:compact-zerozp` source kernels, respectively. Both use
  12 bytes of call-exclusive ordinary RAM scratch and zero ZP.
- In the operation-first builder, READY aliases are deliberately safe
  under arbitrary mixed calls, requiring neither pointer lifetime nor
  initialization. Selecting ordinary and READY versions deduplicates the
  exact core and links both entry symbols at no additional code cost.
  This *does not* claim the historical READY speed advantage.
- Three CPU-model relocated maps test signed/unsigned edges, deliberate
  scratch invalidation by 24-bit multipliers, stack/code integrity,
  alias dedup and strict budget enforcement; native x64sc checks
  both entries at two independent placements.
- Independently selectable catalog reaches 53/56 once parent PR merges.
  Existing resident profiles, timing data and pointer contracts unchanged.

## Unreleased — independently linked signed 32x32 SHR16 fixed-point

- Add standalone `MATH_SMUL32_SHR16` `link:compact-zerozp` using a
  private signed full64 product producer plus exact 16-bit arithmetic
  shift adapter; 334 code bytes, 12 reusable ordinary RAM bytes,
  zero ZP, 378 bytes including shared public I/O.
- Preserve complete signed32 X/Y, return exact low signed48
  two's-complement `(X * Y) >> 16` in Z[0..5], clear carry.
- Add three relocated 6502 CPU-model test maps, mixed signed/unsigned
  scratch sharing and two native x64sc qualification maps. Independently
  linkable catalog becomes 51/56; historical V1–V5 resident code and
  published performance data remain unchanged.

## Unreleased — standalone signed 32x32 full product

- Source-link `MATH_SMUL32` `link:compact-zerozp` using an exact
  signed32×signed32→signed64 kernel (293 executable bytes, 12
  reusable ordinary scratch RAM bytes, zero ZP, 337 total
  RAM bytes including I/O). Preserves both complete X/Y operands
  and writes all eight product bytes with carry clear.
- Qualify signed extremes, three independently relocated CPU-model
  runs, mixed UMUL32_SHR16 calls, full code/stack ABI and two
  native VICE placements. Checksum/package audit included.
- Raises independently linkable operation count to 50/56 after
  dependent merges. Historical V1–V5 resident sources and
  cycle measurements remain untouched.

## Unreleased — independently linked UMUL32_SHR16

- Add `MATH_UMUL32_SHR16` `link:compact-zerozp` (245 bytes
  executable, 12 bytes reusable ordinary RAM, 0 ZP; 289 bytes
  including public I/O). Exact `(unsigned X32 * unsigned Y32)>>16`
  48-bit result in Z[0..5]; X/Y preserved, carry clear.
- Add three relocated CPU-model edge/random and mixed UMUL32
  qualification cases, two native VICE memory maps, strict RAM
  resource accounting, changelog and sealed package audit.
- Independently linked operation catalog rises to 49 of 56
  once this and the parent shared signed32 DIV/MOD PR merge.
  Resident V1–V5 code and historical cycle numbers unchanged.

## Unreleased — shared signed 32/32 division and modulo

- Add independently linkable `MATH_SDIV32_32` and `MATH_SMOD32_32`
  using one 412-byte source-linked signed 32-bit restoring producer
  (9 bytes reusable ordinary RAM scratch, 0 zero page, total
  453 RAM including public I/O).
- Exact signed quotient truncation toward zero, signed full-width R32,
  D=0 carry signalling, `-2147483648/-1` wrap and preserved N/D.
- Add three relocated CPU-model exhaustive-edge/seeded-random
  producer tests, mixed-operation scratch-sharing and two-map
  native VICE verification, with checksum/package audit updates.
- Operation-first independently linked coverage increases to
  48 of 56 when merged. Historical profile kernels and published
  performance measurements unchanged.

## Unreleased — shared signed 32/16 divide and modulo

- Register `MATH_SDIV32_16` and `MATH_SMOD32_16` as independently
  selectable shared-source `link:portable-zerozp` operations.
  260 code bytes, 3 ordinary-RAM scratch bytes, no zero page,
  295 RAM bytes including public I/O; code counted once for both.
- Signed N32/D16 produce exact signed Q32/R16 with truncate-to-zero
  quotient, numerator-signed remainder, two's-complement overflow
  wrap and carry-set division-by-zero; input/high R bytes unchanged.
- Qualify three relocated CPU model maps and two native VICE maps,
  mixed signed/unsigned operations, deduped entries and RAM budgets.
  Proposed catalog reaches 46/56 after prior stacked migrations.
  Retain historical V1–V5 source binaries and performance figures.

## Unreleased — shared signed 24-bit DIV/MOD source

- Add independently selectable `MATH_SDIV24` and `MATH_SMOD24`
  backed by a single 325-byte `link:portable-zerozp` quotient and
  remainder producer with 7 call-exclusive ordinary RAM bytes, zero
  ZP and 364 main RAM bytes including I/O.
- Correct signed quotient truncation and numerator-signed remainder
  across 24-bit edge values, with signed wrap for -8388608/-1 and
  carry-set divide-by-zero, preserving input and high Q/R bytes.
- Add 3-map CPU-model/mixed-call and 2-map native VICE qualification,
  shared-source dedup and exact RAM-budget checks. Proposed
  operation-first coverage reaches 44/56 after stacked PRs merge.
- Historical V1–V5 resident kernels and speed records unchanged.

## Unreleased — independent signed SDIV16_SHL8 module

- Add standalone `MATH_SDIV16_SHL8` signed fixed-point `link:portable-zerozp`:
  237 executable bytes, 3 bytes of reusable ordinary RAM scratch,
  zero ZP, 272 RAM total including shared public I/O.
- Compute `(signed N16 << 8)/signed D16` with exact wrapped Q24,
  truncation toward zero, signed remainder R16, carry-set D=0
  signaling and preserved N/D/high Q/R fields.
- Three CPU-model memory-map relocations, mixed non-overlapping
  signed/unsigned operations, exact budget failures and two native
  VICE maps. Independently linkable catalog advances 41 to 42 of
  56 after parent merges. Historical profiles and timing records unchanged.

## Unreleased — source-linked signed SDIV16/SMOD16 shared producer

- Add `MATH_SDIV16` and `MATH_SMOD16` as separate selectable
  APIs backed by one 206-byte `link:portable-zerozp` quotient-and-
  remainder routine with 3 bytes of exclusive-call RAM scratch,
  zero ZP, and 241 RAM bytes including public I/O.
- Signed quotient truncates toward zero (16-bit wrapped result on
  -32768/-1), remainder follows numerator sign, N/D and high Q/R
  bytes preserved. D=0 zeros Q/R and sets carry.
- Add mixed-API link/dedup and scratch-lifetime tests, three CPU
  relocations and native VICE checks at two code/I/O maps.
- Operation-first coverage increases from 39/56 to 41/56 upon merge,
  with V1–V5 fast-profile sources and timing records intact.

## Unreleased — independent UMUL32 full 64-bit source

- Add source-linked `MATH_UMUL32` `link:compact-zerozp`:
  204 executable bytes, 12 reusable ordinary RAM scratch bytes,
  0 ZP, 248 main RAM bytes including public I/O. Full 32×32→64
  unsigned product, preserved X/Y and carry clear.
- Three relocated CPU-model product/ABI tests, two native VICE maps,
  mixed calls with UMUL24, SMUL24 and URECIP16_Q16, strict RAM budget
  qualification, checksummed source and documentation.
- Raises independently linkable public catalog coverage to 39/56
  once merged, preserving V1–V5 fast kernels and published timings.

## Unreleased — signed full-width 24-bit multiplication module

- Add standalone `MATH_SMUL24` `link:compact-zerozp` with exact
  signed 24×24→48-bit product, 227 bytes of code, 9 bytes of reusable
  RAM, zero ZP and 268 total bytes including shared public I/O.
- Preserve signed X/Y and out-of-contract high Z bytes, clear carry.
  Three relocation/ABI CPU-model checks exercise signed extremes;
  two native x64sc maps validate live 6510 outputs and input canaries.
  Verify mixed-call scratch lifetime and fail-closed exact RAM budget.
- Independently source-linkable operation count rises to 38/56
  once merged. V1–V5 code/performance metrics are unchanged.

## Unreleased — signed 16-bit fixed-point SHR8 kernel

- Introduce independently linkable `MATH_SMUL16_SHR8`
  `link:compact-zerozp` (184 B code, 6 B reusable private RAM,
  0 ZP, 222 B total with I/O). Computes exact arithmetic
  `(signed X16 * signed Y16) >> 8` into public Z[0..2], C=0.
- Preserve caller X/Y and non-contracted high Z bytes. Add
  three relocated CPU-model signed product tests, mixed-operation
  scratch lifetime and exact-budget checks, and two native x64sc
  placements with signed extremes and memory canaries.
- Expands independently source-linkable builder coverage to 37/56
  once merged; leaves historical V1–V5 resident code untouched
  and makes no unsupported mixed-operation speed claims.

## Unreleased — zero-ZP signed 16-bit multiplication source

- Add independently linked `MATH_SMUL16` `link:compact-zerozp`
  implementation using a source-local 108-byte unsigned core and
  signed high-product correction: 161 executable bytes, 6 bytes RAM
  scratch, 0 ZP; 199 bytes total including public I/O.
- Preserve 16-bit signed X/Y (and upper operand bytes), write the exact
  signed 32-bit Z product while leaving Z[4..7] untouched and carry clear.
  Qualify negative/positive extremes including -32768, mixed calls,
  three CPU-model memory maps and two native VICE maps.
- Raises builder independent-link coverage to 36/56 once merged.
  Historical V1–V5 resident algorithms and published cycle counts
  are unchanged; fast-source transplant remains future work.

## Unreleased — independent 24-bit unsigned multiply source

- Introduce `MATH_UMUL24` `link:compact-zerozp` standalone source,
  a 156-byte code / 9-byte ordinary RAM / zero-ZP exact unsigned
  24×24→48-bit public producer (197 bytes including public I/O).
- Cover full-width product, ABI high-byte preservation, two native
  VICE relocations, three CPU-model relocations, mixed-call scratch
  sharing, zero-page constraints, and memory-budget rejection.
- Increases operation-first independently linkable coverage to 35/56
  when merged. No V1–V5 resident or historical-performance changes;
  further fast-core source transplantation is still required.

## Unreleased — independent URECIP16_Q16 module

- Add zero-ZP source-linked `MATH_URECIP16_Q16` portable reference:
  99 code bytes, 1 call-exclusive ordinary RAM scratch byte, and
  132 RAM bytes including public I/O.
- Exact unsigned `floor(65536 / D16)` Q24 ABI, with zero-divisor
  carry signalling, preserved D, untouched Q[3] and R bytes.
- Add arithmetic edge/random, relocation, budget and mixed-operation
  CPU-model tests, native x64sc two-map validation and new independent
  operation catalog entry (34/56 after merge).
- Historical V1–V5 resident code and performance numbers unchanged;
  the high-speed threshold/reciprocal paths remain future transplant work.

## Unreleased — source-linked UDIV16_SHL8 reference

- Independently selectable `MATH_UDIV16_SHL8` source:
  129 executable bytes, one ordinary-RAM scratch byte and zero ZP
  (162 bytes including public I/O). Implements exact unsigned
  `(N16 << 8)/D16` with quotient Q24, remainder R16 and carry-set
  divide-by-zero behavior, retaining input and high-byte ABI.
- Add relocation and mixed-arithmetic CPU-model regression tests,
  budget failure checks and two-map native x64sc qualification.
  Preserve V1–V5 resident sources and historical speed records.
- This operation increases operation-first independent-link coverage
  from 32 to 33 of the public 56-operation catalog once merged.

## Unreleased — matched-input UMUL16_SHR8 fast source option

- Add standalone `MATH_UMUL16_SHR8` `link:quarter-square` source:
  256 bytes code + 1,022 generated lookup bytes + four reusable RAM
  scratch bytes + zero ZP, 1,314 RAM including public I/O. Preserves the
  portable 164-RAM `link:compact-zerozp` alternative.
- Extend source-parameterized UMUL16 quarter-square emitter without
  modifying its existing default emitter contract. Add independent
  full-width relocation/ABI tests and native x64sc shifted-product
  correctness at two code and I/O maps.
- Enable scoped `--objective speed` for `UMUL16_SHR8` only, ranking
  both assembled sources on exactly 1,000 paired inputs and honoring
  actual RAM/ZP budgets. Mixed-operation speed ranking still fails closed.
- Historical V1–V5 profiles and performance numbers are unchanged.
  The original resident fast-core extraction remains to be done.

## Unreleased — operation-first UMUL16_SHR8 standalone reference

- Add an independently linkable 126-byte, zero-ZP `MATH_UMUL16_SHR8`
  portable source with six reusable RAM scratch bytes and an exact
  24-bit unsigned fixed-point output contract.
- Include deterministic two-placement CPU-model qualification, mixed
  `UMUL16` calls, budget checks, and native x64sc correctness coverage.
  Keep all historical V1–V5 profile sources, optimized implementations
  and performance records untouched; this is *not* an automatic speed
  replacement. The fast resident dependency transplant remains open.

## Unreleased — certified same-input ISQRT32 speed selection

- Extend operation-first `--objective speed` to `MATH_ISQRT32`
  alone, comparing its highword fast and compact zero-ZP variants on
  a frozen 512-value full-width seeded+square-boundary corpus.
- Measure each relocated source's actual 6502 instructions, then
  apply code, RAM and ZP budgets globally for the selected operation.
  Keep low-memory fallback and expert pins; prohibit unqualified
  mixed-operation speed ranking.
- Preserve corpus/source/toolchain SHA256 provenance and add CPU
  ABI/resource tests at two memory maps, without updating the
  historic five-profile benchmarks.

## Unreleased — canonical-source V2 highword fast ISQRT32 variant

- Add opt-in `MATH_ISQRT32` `link:v2-highword-source`, retaining
  original V2 highword seed and four-step radix-4 refinement path,
  192 executable bytes plus 3 exact 256-byte table pages; seven
  reusable ZP bytes, no self-modifying code or REU.
- Hash-lock highword/refinement source dependencies and lookup table
  bytes in source manifests; verify mathematical table contents.
  Include dual-address memory relocation, mixed ISQRT16 linking,
  carry/register/input preservation, common-corpus cycle tests and
  actual native VICE qualification against the portable reference.
- Keep `link:radix4-zerozp` available and keep historical profile
  binaries intact; global speed-choice infrastructure is still
  restricted to routines with common certified input corpora.

## Unreleased — historical V2 fast 24/24 DIV/MOD selective transplant

- Add the certified historical V2 direct Repose UDIV24/UMOD24 producer
  as an opt-in modular `link:v2-repose-fast` source variant, using
  1,244+217 bytes of code, 3 ZP bytes, and a writable immediate tail
  operand. Requires legal NMOS 6510 `LAX`/`ANC` semantics, and
  does not use lookup tables or REU.
- Source hashing captures the original historical producer, the
  relocation adapter and the linked derivation. Both APIs share the
  same physical code; optional fast selection does not disturb the
  zero-ZP compact reference or the original V1–V5 profiles.
- Added two-map CPU source-equivalence and full-domain division tests,
  same-corpus exact-cycle comparisons, and actual VICE verification
  of both APIs and both 24-bit variants.
- This *adds* a speed alternative; global all-catalog cycle ranking,
  variant co-selection and default-distribution replacement remain open.

## Unreleased — operation-first UDIV24 and UMOD24 source link

- Enable separate selection of unsigned 24/24 DIV and MOD through a
  shared **190-byte**, zero-ZP, four-RAM-byte restoring kernel. Preserve
  24-bit input fields, Q/R upper sentinels, carry and division-by-zero
  semantics. No writable instructions, REU, or initialization.
- Test 24-bit boundaries and randomized operands on two code/I/O maps,
  both API aliases and mixed-resource budgets; add real native VICE
  public-call qualification and 2072-file package hash release seal.
- Keep the historical certified V1–V5 fast producers intact for
  later modular dependency transplant and common-corpus speed ranking.

## Unreleased — operation-first ISQRT32 full-domain reference

- Independently link `MATH_ISQRT32` as a **204-byte/10-RAM/0-ZP**
  full-domain restoring radix-4 source. Preserves N32/X/Y/stack and
  upper output bytes; no ROM writes, tables, REU or setup.
- Add boundary/perfect-square/random CPU-model correctness,
  source/ABI/relocation and 246-byte minimum RAM checks;
  native VICE verifies 96 roots per relocation across two maps.
- Historical fast V1–V5 ISQRT32 implementations remain unchanged and
  are not ranked against the portable source until their dependencies
  are integrated and measured on a common corpus.

## Unreleased — unsigned 32/16 one-byte-RAM Pareto producer

- Introduce a second independently linkable shared DIV32/16+MOD32/16
  variant, `link:accumulator-remainder`, using a **131-byte**
  non-self-modifying source and **one RAM byte / zero ZP**.
- Preserve the existing source-linked `link:portable-restoring`
  reference as a pin-selectable fallback. Default size/RAM Pareto
  selection now chooses the smaller candidate; no unqualified
  cross-profile speed claim is made.
- Add paired exact-cycle CPU-model comparisons on identical 32/16
  operands and both relocated maps; extend native VICE to qualify
  both variants and both public entries with independently seeded calls.

## Unreleased — operation-first unsigned 32/16 DIV/MOD reference kernel

- Add independent selectable `MATH_UDIV32_16` and `MATH_UMOD32_16`
  with a single 162-byte source-linked, zero-ZP restoring reference
  producer. Both public aliases write Q32 and R16, preserve input bytes
  and report zero divisor in carry. Three bytes of nonreentrant RAM scratch.
- Add two-map CPU-model edge/random/divide-by-zero and native VICE
  qualification, full image/ABI checks, RAM budget enforcement, and
  user-reserved overlap rejection.
- The original optimized V1–V5 split 32/16 producers are **not replaced**;
  further migration and comparable cycle benchmarking remain necessary.

## Unreleased — operation-first SEEK16 movement family

- Link four SEEK16 public operations from a single generated 898-byte
  RAM-operand DDA engine with distinct INIT/STEP/STEP_INT/STEP1 exports.
- Allocate 248-byte independent persistent state for eight 16-bit-X
  objects, sharing reusable 19-byte init scratch with SEEK8.
  Enforce state alignment, no overlap and global mixed-operation budgets.
- Export X low/high and Y position array symbols; maintain the public
  MATH_X/MATH_Y/MATH_N calling convention and CPU/VICE relocation gates.
- V1–V5 profile images remain unchanged; speed rankings remain fail-closed.

## Unreleased — operation-first SEEK8 movement family

- Add four independently selectable SEEK8 public API entries from one
  source-locked, generated DDA kernel (651 bytes for RAM inputs) (INIT, STEP, STEP_INT, STEP1).
  Keep their four distinct addresses while sharing exactly one physical
  producer and its internal 32-byte Euclidean correction table.
- Add persistent state ownership to the builder: reserve 160 bytes for
  eight objects, with separate 19-byte reusable init scratch and aligned
  placement. Honor RAM budgets and reject any reservation overlap.
- Export both position array addresses and retain public MATH_X/MATH_Y/MATH_N
  calling convention. Add two-relocation, eight-slot CPU/VICE qualification.
- No change to the historical V1-V5 PRG/REU distribution or mixed-family
  speed selection (which remains fail-closed without comparable corpora).

## Unreleased — original V1 UMUL8 builder migration

- Introduce an operation-first original V1 UMUL8 source variant with the shipped
  22-byte entry / 29-byte helper assembled contiguously, two exact 511-entry
  quarter-square pages, four relocatable ZP scratch bytes, and no REU.
- Extend same-input 1,000-case source-assembled CPU-model UMUL8 speed comparison
  to the original V1 alongside compact and portable quarter-square kernels.
  Preserve existing single-operation speed guard and RAM/ZP budget constraints.
- Add exhaustive 65,536-case model tests at two RAM/ZP relocations, native VICE
  tests at both locations, and byte-for-byte V1 table provenance.

2026-10-16 UMOD8 CERTIFIED SINGLE-OPERATION SPEED SELECTION (UNRELEASED)
- Extended operation-first --objective speed eligibility to historical UMOD8 only when it is the sole requested operation, using the certified V1/V2/V5 identical 1,000-pair source-assembled 6502 CPU-model benchmark.
- Benchmark reproduces and SHA-locks original small-divisor-weighted corpus, relocates real machine code to caller memory layout, validates each output and carry, preserves N/D/Q/high bytes and stack, and records source SHA + mean call cycles. Source itself uses writable code and 2 ZP.
- With default placement, 189-236 RAM bytes chooses V1 (95.635 mean cycles), 237-260 chooses V5 (94.165), >=261 chooses V2 (90.893); these are CPU-model means, not native VICE timing claims. Explicit pins and memory budget remain authoritative.
- Mixed-operation automatic speed ranking stays prohibited pending an aligned joint workload; no historical resident images or release benchmarks changed.

2026-10-16 BUILDER UMOD8 THREE-VARIANT MATCHED SPEED VALIDATION (UNRELEASED)
- Retained the matched-input V1/V5 CPU-model cycle test from superseded PR #211 and extended it to the merged V2 variant. Same 1,000-pair source-assembled corpus, with explicit small-divisor (3..31) mean, corpus SHA, and each immutable source SHA.
- Tests validate remainder, zero-divisor carry, input/quotient preservation, stable stack and per-variant RAM/ZP footprint; all three historic implementations are selectable, but unqualified cross-operation or automatic UMOD8 speed ranking remains disabled.
- No change to original V1-V5 resident executable images, benchmark claims, or operation count.

2026-10-16 BUILDER V2/V5 HISTORICAL FAST UMOD8 ALTERNATIVES (UNRELEASED; QUALIFICATION PENDING)
- Added independent source-faithful V2 (229 bytes, fast divisor >=24) and V5 (205 bytes, fast divisor >=32) unsigned 8-bit remainder kernels alongside the existing V1 157-byte source. All require two caller-free ZP bytes and writable executable RAM for exactly two immediate operand patches, with no lookup data, REU, or setup.
- Public ABI retains unsigned N/D, untouched Q, upper I/O bytes, remainder low byte and carry only on division-by-zero; no cosmetic smaller-but-slower substitute was introduced.
- Added exact mirror opcode/geometry parity checks, all 65,536 N/D cases at each of two code/ZP relocations per candidate, source immutability apart from the documented SMC bytes, RAM budgeting, and native x64sc ABI tests. V1–V5 release PRGs and published timing records are unchanged.
- UMOD8 keeps V1 as the default minimum-memory choice; speed selection remains gated on a matched-input workload corpus.

2026-10-16 OPERATION-FIRST HISTORICAL UMOD8 FAST/FALLBACK (UNRELEASED, QUALIFICATION PENDING)
- Migrated the original V1 MATH_UMOD8 producer as a standalone 157-byte relocatable NMOS kernel, preserving the >=32 divisor direct-subtraction fast path and the small-divisor fast remainder fallback, with the public entry trampoline removed. One 2-byte owned ZP allocation, no lookup tables or other RAM scratch; 189 RAM bytes including public I/O.
- Preserves the full quotient register group and input bytes; writes only low MATH_R, with R=0 / C=1 for a zero divisor, C=0 otherwise. The two immediate bytes in the original fallback are self-modified and require writable non-reentrant RAM code.
- Exhaustive all 65,536 N/D byte pairs at two ZP/code relocations, source instruction-state footprint, public ABI and quotient sentinel checks, mixed sharing with UDIV8/SDIV8/SMOD8, and native VICE at two placements. V1-V5 resident reference images and historical performance benchmarks remain unchanged. Eighteen of 56 public operations are now experimentally linkable pending exact-head CI.

2026-10-16 HISTORICAL SMUL8 WRITABLE-CODE SOURCE MIGRATION (UNRELEASED, CI PENDING)
- Added MATH_SMUL8 link:v1-resident-smc, retaining the exact 46-byte self-modifying historical signed 8x8 producer, instead of introducing a compact but slower replacement. Its four immutable 511-entry table pages match shipped V1-V5 bytes (including V2-V4 relocated complement pages), with 0 ZP, 0 extra scratch, and a required writable 46-byte code region.
- Explicit resource accounting: four 512-byte aligned regions, 2044 source table bytes, 214 default-origin alignment/hole bytes, 2304 total image bytes and 32 public I/O bytes (2336 RAM). All 65536 input pairs tested in both mathematical reference and source-built CPU emulation at two origins, plus native x64sc two-origin checks. Only four executable operand bytes are intentionally modified.
- This is the 17th independently linkable public operation in the operation-first builder. V1-V5 resident binary releases and published performance figures remain untouched; global speed selection beyond comparably measured single-operation multiplication is still not supported.

2026-10-16 SELECTIVE UMUL16 QUARTER-SQUARE SPEED ALTERNATIVE (UNRELEASED; CI QUALIFICATION PENDING)
- Transplanted independently source-linked UMUL16 quarter-square alternative (233 code bytes + 2×511 precomputed table bytes + 4 RAM scratch, zero ZP) alongside the existing 108-byte compact implementation. Inputs retained, full 32-bit result and carry-clear ABI checked.
- Added same-source, same-corpus CPU-model speed measurements for each 16×16 variant, with 1,000 deterministic edge and uniform operand pairs, source/corpus SHA provenance and RAM/ZP gating. Mixed-operation speed ranking remains explicitly unsupported.
- Added source assembly, relocation, mixed-call, ABI and native VICE regression tests. The resident V1–V5 implementations and benchmarks remain unchanged.

2026-10-16 OPERATION-FIRST SHARED SIGNED DIV8/MOD8 SOURCE PORT (MERGE CANDIDATE; CI QUALIFICATION REQUIRED)
- Preserve exact historical V1 530-byte signed SDIV8/SMOD8 routine and signed quotient/remainder public semantics in a relocatable producer. The two public operations coalesce to one code image, one ZP byte and 562 bytes including shared I/O.
- Independently SHA-authorize the shared aliases, test all 65,536 signed input pairs at each of two RAM layouts, test exclusive-call scratch/stack/upper-output preservation, plus two native x64sc maps. Historical V1–V5 released binaries are unchanged.
- Operation-first linker supports 16 of 56 operations as source-selectable, with shared immutable trig/distance tables and shared signed producer. Comparative speed ranking for multiple operations remains unqualified.

2026-10-16 BUILDER HISTORICAL ACCURATE DISTANCE V1 AND V2 (UNRELEASED; QUALIFICATION PENDING)
- Added two independent exact V1/V2 MATH_DIST8_ACCURATE source ports. The V1 66-byte implementation uses 2 caller-free scratch RAM bytes, 0 ZP; the V2 58-byte implementation uses 2 explicitly owned ZP bytes, no RAM scratch. Both preserve 8-bit signed-input magnitude/swap and table lookup, carry-clear and I/O sentinels.
- Original 256+256 immutable high/min contribution pages are checked byte-for-byte against all five shipped V1-V5 resident PRGs. Added globally shared aligned distance table pair after optional shared sine page, proper multi-module RAM/ZP/padding accounting, output provenance and complete source-dependency hashes.
- Exhaustive 65,536 signed x/y pairs at two relocations per variant, mixed linked sine/ATAN2/ISQRT16 tests, budget-negative tests and four independent native VICE layouts now gate promotion. This is the fourteenth linkable operation; no historical resident binaries or published cycle records changed.

2026-10-16 BUILDER SHARED HISTORICAL TRIG8 FAMILY (UNRELEASED; QUALIFICATION PENDING)
- Added SIN8, COS8, SINCOS8 as independently selectable V1-V5 source-exact trig8 entry points (11/15/22 code bytes). All three share one source-locked 256-byte page-aligned sine table, exact against the bytes at $9400 in every shipped V1–V5 PRG. No ZP, private RAM, initialization, or REU.
- Extended resource accounting for a single shared lookup page, including alignment padding, origin relocation, per-operation exported symbols, metadata and toolchain SHA provenance; no redundant tables in mixed trig builds.
- Added five-profile binary source-parity tests, exhaustive 256-phase CPU-model ABI checks at two code/memory layouts, mixed ATAN2/ISQRT links, and native x64sc execution at two relocations. This increases independently linkable operations from 10 to 13 of 56.
- No historical resident files or performance numbers changed. Global shared-resource speed optimization and unported algorithms remain in subsequent builder stages.

2026-10-16 BUILDER HISTORICAL V1 UDIV8 SELECTIVE MODULE (UNRELEASED; QUALIFICATION PENDING)
- Transplanted the V1 optimized unsigned 8-bit division public producer (125 instructions, 294-byte source island, trampoline omitted) as link:v1-resident-fast. The entry is 8 bytes inside the code island; one relocatable ZP scratch byte, no extra RAM scratch, tables, REU or initialization.
- Preserve original 8-bit quotient/remainder, dividend/divisor inputs, carry error on D=0, and high I/O byte sentinels. Exhaustive 65,536 n/d pairs in two separate CPU relocations, mixed-module and minimum-budget checks, plus separate two-map native x64sc harness in CI.
- Operation-first builder now has ten of 56 public operations linkable; V1-V5 resident releases and benchmark records unchanged. Comparative speed ranking requires a matched corpus; the remaining historical variants are not yet selectively linkable.

2026-10-16 OPERATION-FIRST DIST8_FAST HISTORICAL PORT (UNRELEASED; QUALIFICATION PENDING)
- Transplanted the V1 signed DIST8_FAST max/half-min arithmetic with trampoline removed, preserving abs(-128), unsigned 8-bit wraparound, inputs and carry contract; 61-byte independently relocatable kernel, 0 ZP and 2 explicit RAM scratch bytes, total standalone 95 RAM bytes including shared public I/O.
- Added exhaustive 65,536-pair CPU-model tests at two relocations, native x64sc test harness at two relocations, mixed-call checks and CI gates. Corrected the ISQRT16 variant validation-path metadata. Neither library resident releases nor benchmarks changed.
- This is now the ninth operation with selective source linking; speed selection for multi-operation selections is still gated on comparable workload data, and all remaining operations/optimized variants still require migration and qualification.

2026-10-16 OPTIMIZED ISQRT16 SELECTIVE SOURCE MIGRATION (UNRELEASED; QUALIFICATION PENDING)
- Port the V1/V2/V5 resident 16-bit square-table search (without resident trampoline) as a 38-byte relocatable standalone link kernel; regenerate three 256-byte lookup tables deterministically, with page-alignment padding, exact RAM accounting, zero ZP, no initialization and explicit SHA-locked generator provenance.
- Add complete 65,536-input CPU-model checks at two relocations, mixed table-aligned linking smoke tests, native x64sc correctness checks at two maps, source-pin/constraint and build-manifest tests. This expands the experimental linkable catalog to 8/56 operations, not the complete historic performance spectrum. No shipped profiles, published cycle records or default release change.

2026-10-16 MEASURED SELECTIVE UMUL8 SPEED CHOICE (EXPERIMENTAL PHASE 3; UNRELEASED)
- Enable --objective speed for UMUL8-only selective builds by assembling each known variant at the requested origin and measuring both with the same deterministic 1,000-pair edge/uniform CPU-model corpus. Choose the fastest variant that actually fits RAM/ZP budgets; 95-byte RAM fallback uses the compact module if 1,129-byte quarter-square cannot fit.
- Record cycle basis, input corpus SHA-256, per-variant mean CPU-model cycles, requested code/IO origin, and source/toolchain SHA-256 in the output manifest. These are model cycle counts, not native hardware timings. Speed objectives for other operations and incompatible mixed-operation workloads remain explicitly unsupported.
- Add budget/pinning/provenance/repeatability/CLI regression tests and preserve the existing production binaries and benchmark records.

2026-10-16 EXPERIMENTAL BUILDER FAST-MULTIPLY PHASE 2 (UNRELEASED)
- Add an independently relocatable UMUL8 quarter-square option: 73 bytes of NMOS 6502 code, 1022 bytes of generated Q(n)=floor(n*n/4) lookup planes, 2 ordinary scratch RAM bytes and zero ZP. Preserves the existing compact 60-byte alternative and the public input/output/carry ABI.
- Extend the selective linker with source and table-generator SHA checks, exact image span accounting, typed public include export, and deterministic side-by-side variant selection. Size optimization keeps the compact kernel; experts may explicitly pin quarter-square.
- Add exhaustive 65,536-pair formula and native CPU-image correctness tests at two relocation maps, a same-corpus CPU-model cycle comparison, and separate native x64sc qualification. This remains research/experimental until all new CI gates pass; no fixed-profile artifacts or published benchmark numbers are modified.

2026-10-16 EXPERIMENTAL OPERATION-FIRST MATH BUILDER (DRAFT PR #197; NOT RELEASED)
- Split 56 stable public operations into `routines/PUBLIC_OPERATIONS.csv`; builder no longer derives its API from V1 profile metadata. Added regression proving all operations remain selectable without V1 catalog rows. Extend hardware-neutral selection plans to 1541, 1571 and 1581 as explicit plan-only targets; binary generation remains C64-only until device-specific address maps/ABI and validation exist. No device-side binary is claimed or emitted. Introduce a user-facing operation selector covering all 56 stable operations, with numbered categorized interactive selection, typed aliases, resource budgets, variant inventory and deterministic selection manifests. Historical V1-V5 names survive only as provenance/baselines, not required end-user build modes.
- First experimental compact source-only linker supports UMUL8, UMUL16, UDIV16, UMOD16, UDIV32_32, UMOD32_32 and ATAN2_8 with portable low-ZP and zero-ZP source choices. Example 16-bit DIV+MOD uses 585 code bytes and two shared scratch ZP bytes; full 32-bit DIV+MOD uses 1040 code bytes/four ZP or 1072 code bytes/zero ZP. All figures are assembler-contract targets pending CI, not published performance revisions.
- Selective output files are now staged before publication and PRG checksummed; a failed staged write does not partially replace an existing build. The manifest is committed last as a completion marker. Resource Pareto pruning is restricted to matching code/table alignment classes, preserving future non-equivalent implementations. Auto-selection now prunes memory-dominated alternatives without removing pinned expert variants, and output manifests seal the actual builder/linker/ATAN2/assembler toolchain hashes in addition to source/table provenance. The new native multiplier harness also records carry-clear flags, matching public ABI. Global feasible-source selection checks RAM/ZP budgets, caller-owned reserved ranges, source SHA lock, ROM/I/O collisions, code/operand isolation and experimental compatibility. Emits loadable PRG, typed/public API include and precise memory manifest. Speed ranking is intentionally refused until same-corpus source-model cycle qualification is available.
- Add new 60-byte zero-ZP UMUL8 source (3 ordinary scratch bytes, 95 RAM bytes including public I/O); 65,536-pair per-map model and linked native VICE qualification added, pending execution. Restore required carry-clear UMUL16 public ABI via CLC, making that kernel 108 bytes and its RAM claim 146 bytes; extend mixed-call proof. Added a 108-byte portable zero-ZP UMUL16 (six bytes ordinary scratch) with X/Y→Z ABI and source/model/native qualification gates. Replaced edge-only ATAN2 placement with a 256-state globally padding-minimal subset-sum layout, including an interposed ATAN2 test. Added compact-opt/sum-fast ATAN2 source/table linking with exact page-alignment padding, zero ZP, full signed 65,536-vector correctness checks, SHA-locked table-generator provenance and a native x64sc correctness gate. Added multi-origin emulator/model edge/random/divisor-zero and mixed-call validation and pinned headless native VICE checks. Keep PR draft until checks are green; historical binaries, REU images and all benchmark publications unchanged. See docs/BUILDER_REFACTOR.md.

2026-10-16 ISSUE144 NINE-KERNEL MATCHED SOURCE-CANDIDATE SCORECARD
- 31,800 same-input public model calls across V1-V5 and reference/alternate maps; all nine original expensive kernels, arithmetic and SEEK STEP oracle pass, zero measured slowdowns.
- Source-vs-frozen mean savings: ISQRT32 V1/V5 -51, V2/V3 -47, V4 -135.205; SEEK16_INIT V1/V5 -1.913, V2 -14.029, V3/V4 -12.435; V2-V4 UDIV/UMOD32_16 -3.743 and SMOD32_16 -6.707. Four 32x32/SHR16 multiply APIs unchanged.
- Both-map 45-row CSV/JSON and crossmap SHA-provenance permanently retained. CPU cycles only, not physical REU/VIC/DMA/IRQ timing; no frozen binaries or historical PERFORMANCE changes. Issue #144 remains open.

2026-10-16 ISSUE144 F VERSIONED DUAL-MAP SOURCE DISTRIBUTION AND VERIFY GATE (CANDIDATE; NOT SHIPPED)
- Add tools/issue144_versioned_distribution.py: builds reference + alternate V1/V2/V3/V4/V5 canonical-source PRGs (10 total), both V3 512-KiB/V4 16-MiB REU images in each map (4 total), caller math_api.inc, 56-entry source manifests and full source API validation. Creates stable-content versioned ZIP, independent file SHA-256 inventory, ZIP-level .sha256, complete qualification reports and same 438-input old-versus-new ISQRT32 benchmark. Refuses stale V4 source that lacks the PR #192 direct-ZP 16-cycle gain.
- Add CI verification and 90-day per-commit Actions artifact upload; manual explicit workflow_dispatch prerelease gate checks exact-main CI green and refuses existing release tags. Seven historical default binaries and their PERFORMANCE.md rows remain unchanged. No automatic GitHub production/default release or physical VIC/REU/IRQ certification. See docs/ISSUE144_VERSIONED_DISTRIBUTION_2026-10-16.md.

2026-10-16 ISSUE144 C V4 REU DIRECT-TO-ZP ISQRT32 CANONICAL SOURCE PROMOTION (QUALIFICATION PENDING)
- Adopt the PR #191 16-cycle all-input direct-DMA root optimization inside V4's normal relocatable source without expanding the 8-byte ordinary zero-page workspace, external caller RAM or REU image. Preserve the immediately preceding canonical source as an independently runnable reference/alternate memory-map baseline; retain 2,132 old/new full-root pairs and all 56 public-API entries per map plus pinned native 16 MiB REU x64sc. Explicitly restore $DF02/$DF03 to the public REU scratch address after each lookup. Repair the original fast-four and maskshift historical test gates so they remain pinned to their original source stages instead of treating this later source advancement as a regression. Seven historic default binary files and PERFORMANCE.md remain unchanged; physical REU/VIC/IRQ timings and a new versioned production binary release remain unqualified. See optional/issue144_v4_isqrt32_direct_reu_zp/README.md.

2026-10-16 ISSUE144 C/F CANONICAL V4 REU DIRECT-ZP SOURCE CANDIDATE PERFORMANCE PUBLICATION
- The 32/32-green PR #192 (`eb64e84a`) adopted native-verified REU direct-record DMA into normal eight-byte root ZP with $DF02/$DF03 restored, and built independent reference/alternate versioned candidate PRGs and applicable V3/V4 REU images. On the same 438-root public-call corpus used by PR #190: V4 new source mean 788.876712 cycles vs historical frozen binary 924.082192 (135.205479 saved), including exactly 16 additional cycles saved vs pre-direct-ZP candidate 804.876712; 0 slower, p95 1022 to 869. All other profiles unchanged. Public results and SHA manifests are preserved separately in benchmarks/ISSUE144_ISQRT32_V4_DIRECTZP_SOURCE_CANDIDATE_2026-10-16.csv and validation/review/ISSUE144_V4_DIRECTZP_CANONICAL_CANDIDATE_RELEASE_2026-10-16.json, without replacing the prior benchmark source snapshot. Seven historical shipped PRGs/REUs and PERFORMANCE.md are unchanged, hardware DMA/IRQ checks and tagged default release remain OPEN.

2026-10-16 ISSUE144 C V4 REU DIRECT-TO-ZP ISQRT32 CANONICAL SOURCE PROMOTION (QUALIFICATION PENDING)
- Adopt the PR #191 16-cycle all-input direct-DMA root optimization inside V4's normal relocatable source without expanding the 8-byte ordinary zero-page workspace, external caller RAM or REU image. Preserve the immediately preceding canonical source as an independently runnable reference/alternate memory-map baseline; retain 2,132 old/new full-root pairs and all 56 public-API entries per map plus pinned native 16 MiB REU x64sc. Explicitly restore $DF02/$DF03 to the public REU scratch address after each lookup. Repair the original fast-four and maskshift historical test gates so they remain pinned to their original source stages instead of treating this later source advancement as a regression. Seven historic default binary files and PERFORMANCE.md remain unchanged; physical REU/VIC/IRQ timings and a new versioned production binary release remain unqualified. See optional/issue144_v4_isqrt32_direct_reu_zp/README.md.

2026-10-16 ISSUE144 C V4 REU ISQRT32 DIRECT ZERO-PAGE DMA RESEARCH (OPT-IN)
- Optional eight-byte-ZP-layout permutation directs the existing four-byte V4 REU prefix root/residual record into ZP_MAIN+$52..+$55, instead of copying four bytes from REU_SCRATCH. Explicit $DF02/$DF03 restoration retains the established destination for other math routines. No new normal zero page, caller RAM or REU payload.
- 1,066 paired unrestricted source-model public root calls in each reference/alternate map (2,132 pairs), exactly 16 modeled instruction cycles saved on EVERY input, zero slower. Both full 56-entry source validators PASS (43,356 calls). 24 actual native pinned x64sc old/new pairs with emulated 16 MiB REU produced byte-identical output/status. Qualification: tools/issue144_v4_reu_direct_zp_screen.py, optional/issue144_v4_isqrt32_direct_reu_zp/, validation/review/ISSUE144_V4_ISQRT32_DIRECT_REU_ZP_2026-10-16.json.
- Experimental source only: production V4 canonical source, frozen five PRGs/two REUs and PERFORMANCE.md unchanged. Physical VIC/REU DMA elapsed time, IRQ/NMI and default-source promotion remain open.

2026-10-16 ISSUE144 B NORMAL-RESIDENT DUALTAIL UDIV32/16 SOURCE-ONLY OPT-IN
- V2/V3/V4 source-selected 461-byte secondary low-divisor quotient engine relocates to already claimed REG_LOW+$0C00; no caller-owned RAM, extra ZP or published PRG/REU replacement. Original $1C00-class bytes zero; normal reference and alternate memory map validated.
- 51,252 paired same-input public signed/unsigned DIV/MOD CPU-model calls pass with full Q/R/C/N/D and volatile signed status. +27.0299 cycles on eligible low D, +10.8715 mean over mixed unsigned corpus, +19.9919 on sign-enriched signed corpus, 2-cycle worst regression.
- 1,152 pinned real x64sc baseline/candidate calls pass. 130,068 V2–V4 all-56-entry reference/alternate source-built public calls pass with an explicit runtime write guard around the resident code island.
- V5 cannot inherit the V2 helper with the current linker: direct-import unsupported opcode confirmed; separate 43,356 V5 stock hybrid public calls PASS at 31 ZP. Isolated optional builder refuses V5 and preserves original source. IRQ/NMI nested-use, indirect references and full physical VIC/REU wall-time gates remain OPEN; issue #144 B remains OPEN.
- See docs/ISSUE144_B_DUALTAIL_INRESIDENT_2026-10-16.md.

2026-10-16 ISSUE144 C/F ISQRT32 SAME-INPUT SOURCE RELEASE CANDIDATE (NO DEFAULT-BINARY PROMOTION)
- PR #188 merged (29/29 exact-head PR checks PASS); canonical source builders emitted independently SHA-sealed V1-V5 PRGs and V3/V4 REUs for reference and alternate relocation maps, plus caller includes and build manifests, without overwriting the historical seven binaries. All 56 public APIs tested: 21,678 source-model calls per profile/map (216,780 total); native x64sc ISQRT32 with emulated V3/V4 REU passed.
- Same 438-input frozen-binary vs new source-built comparison: MATH_ISQRT32 saves 51 cycles V1/V5, 47 cycles V2/V3, 119.2055 mean cycles V4 (range 101-137); no slower calls, exact roots. Separate emulator-only V4 CIA timer measured 749-1018 ticks including instrumentation on 16 inputs; physical REU/VIC/DMA/IRQ claims remain OPEN. Publish provenance and candidate figures in benchmarks/ISSUE144_ISQRT32_SOURCE_CANDIDATE_2026-10-16.csv and validation/review/ISSUE144_SOURCE_RELEASE_CANDIDATE_2026-10-16.json. Default PRGs/REUs, PERFORMANCE.md and historical performance tables remain unchanged.

2026-10-16 ISSUE144 B DUALTAIL SIGNED32 DIVMOD PUBLIC AND NATIVE QUALIFICATION (OPTIN ONLY)
- The optional $0800 lowD U3216 magnitudes also serve signed SDIV32_16/SMOD32_16 V2/V3/V4. 23,604 paired same-input source CPU model public calls, both memory maps, all four signed quadrants and D=0, exact Q/R/C/N/D/stack and processor status; +19.9919 modeled cycles mean on signed corpus, worst -2. Pinned native x64sc signed 576 original/candidate public calls passed, zero volatile CPU-state differences. Native harness correction constrains result capture to $0500-$0697, avoiding the optional executable at $0800. Research-only; 461 caller-owned bytes remain mandatory, no production promotion or reference PRG/REU/benchmark updates. See docs/ISSUE144_B_DUALTAIL_DIRECT_DISPATCH_SCREEN_2026-10-16.md

2026-10-16 ISSUE144 B UNRESTRICTED LOWD/HIGHD U3216 DUALTAIL DIRECT-DISPATCH RESEARCH
- Assembled all-domain source-only D16 <= $7FFF no-overflow 16-step low-word tail plus unchanged high-D producer, classification folded into existing private U3216 divisor dispatch. Both full Q32/R16/C public UDIV32_16 and UMOD32_16 entries, 27,648 paired source-built CPU-model calls across V2-V4 and reference/alternate maps, all exact (55,296 total calls). Eligible low-D calls save 27.0299 cycles on average; high-D −0.4852, D8 −1.9639, D=0 −2. Entire 2,304-case-per-API mixed corpus saves 10.8715 cycles mean with worst −2.
- 576 real pinned x64sc baseline/candidate public calls on two relocations and both entries PASS (no observed status differences). Optional 461 code bytes still occupy application-owned $0800. Normal resident U3216_MAIN_END/D8 span contains no unoccupied 461-byte island across six maps; NO default/production release. Frozen five PRGs/two REUs/PERFORMANCE and private OptiSearch unchanged. See docs/ISSUE144_B_DUALTAIL_DIRECT_DISPATCH_SCREEN_2026-10-16.md.2026-10-16 ISSUE144 SEEK16 V1/V5 NORMAL RESIDENT BATCH SOURCE QUALIFIED
- Source-only V1/V5 SEEK16_INIT integer-accumulator batch now fits 45 bytes at resident REG_API+$0599 (no additional normal ZP/application RAM); 1,088 paired public INIT and 26,112 following STEP calls per profile pass. Mean saving 10.566176 modeled cycles, min 0, max 36; real native x64sc and alternate/reference source-map checks PASS. No frozen PRGs/REUs, PERFORMANCE.md or default binary publication changed. docs/ISSUE144_SEEK16_V15_NORMAL_BATCH_2026-10-16.md

2026-10-16 ISSUE144 B SIGNED 32/16 R-FIRST REMAINDER/QUOTIENT FUSION (SOURCE ONLY)
- V2/V3/V4 signed32 normal resident removes a redundant JSR/RTS and CLC on negative-N / positive-D paths by placing the same R-then-Q sign correction order in private D32F normal code, tail-calling the existing Q correction. No new normal ZP, caller RAM or illegal opcodes. V5 inherited source validation is a separate gate.
- 26,352 paired V2–V4 public signed DIV/MOD model comparisons across both maps: 11 cycles saved on each negative-N positive-D call, no slowdown elsewhere, 2.8051 cycles mean on sampled full-width/sign-enriched corpus. Full Q/R/C/N/D and A/X/Y/flags/SP match; prior 14-cycle Q-first trial rejected because it changed A/V.
- 576 actual checksum-pinned x64sc calls passed with identical captured full state. Source-generator/full 56-entry/V5 and publication qualification separately required. Historical PRGs/REUs and production PERFORMANCE.md remain unchanged. Issue 144 remains open.

2026-10-15 ISSUE144 V1/V5 ISQRT32 51-CYCLE NORMAL-RESIDENT CANONICAL SOURCE (NO REFERENCE-BINARY RELEASE)
- Installed source-owned direct-highword ISQRT32 in original V1 normal resident root slot and unused +$0AA8 helper. Actual derived V5 builder inherits the same source, with no extra normal ZP or caller RAM; public API remains unchanged. Source generator regeneration is stable.
- Independently qualified V1 and V5 on reference+alternate relocation maps: 56 public entries and 21,678 ordinary source-model calls per profile/map (86,712 calls total); 2,628 paired root32 ordinary inputs saved exactly 51 modeled cycles each, with no slow cases. 192 native checksum-pinned x64sc root calls passed for V1/V5 baseline/candidate across both maps.
- Research checkers recover only pinned original source for paired baselines. Reference five PRGs/two REUs and production PERFORMANCE.md remain historical; full V5 imported native 56-entry mix, IRQ/NMI and physical timing are pending. Issue #144 remains open.

2026-10-15 ISSUE144 V5 INHERITED V1 ISQRT32 51-CYCLE NORMAL RESIDENT RESEARCH (NO BINARY PROMOTION)
- V5 reference+alternate hybrid source builder retains V1 root resident ownership; 2,658 paired ordinary public ISQRT32 calls save exactly 51 modeled CPU cycles each without slower cases, caller RAM or normal ZP growth. 72 sequential ISQRT16 interleaving smokes passed.
- Real SHA256-pinned VICE x64sc passed 96 original/candidate public root calls across both layouts. Full imported V5 56-entry mixed/IRQ and wall bus-time are NOT certified. Frozen five PRGs, two REUs and PERFORMANCE.md unchanged.

2026-10-15 ISSUE144 V1 ISQRT32 51-CYCLE NORMAL-RESIDENT HIGHWORD SEED FEASIBILITY (RESEARCH ONLY)
- Independently tested a direct-highword V1 ISQRT32 public producer inside unused pre-existing resident bytes: helper REG_GAME+$0AA8 (reference $CBA8); reference and alternate maps both avoid nonzero occupied helper code, without caller RAM or new ZP.
- Each layout passed 657 matched full-width 32-bit public CPU-model calls, exactly 51 modeled cycles saved per call with no slower inputs; root/carry/input/X/Y/SP preserved. 96 real x64sc V1 public calls also passed, with full captured status equality on both layouts.
- Nothing installed into the production V1/V5 source, PRGs, REUs or PERFORMANCE.md. V5 inheritance, full 56-entry mixed-call ABI, IRQ/reentrancy and physical bus timing are NOT yet qualified.

2026-10-15 ISSUE144 V2/V3 ISQRT32 DIRECT HIGHWORD SEED IN NORMAL RESIDENT SOURCE (NOT BINARY RELEASE)
- Installed the independently qualified unrestricted direct-highword sqrt seed as final-owner source in the existing 192-byte normal V2/V3 root slot, without new ZP or caller-owned RAM.
- PR #174 demonstrated 47 CPU-model cycles saved for every one of 3,388 paired calls and 192 native x64sc calls with actual V3 512KiB REU. Production-source branch checks include normal public API and two memory relocations.
- Source-generator includes the new root module but full historical-image regeneration may rewrite other unrelated optimized source; use non-destructive generator-owner check.
- Five frozen reference PRGs, REUs and production PERFORMANCE.md unchanged. Physical REU/VIC DMA timing, IRQ/NMI interference and full release publication remain open.

2026-10-15 ISSUE144 V2/V3 NORMAL-RESIDENT ISQRT32 HIGHWORD SEED SOURCE INTEGRATION (NO BINARY RELEASE)
- Install independent full-domain ISQRT32 highword seed as canonical V2/V3 final-owner source modules within existing 192-byte root slot; no added normal ZP or caller RAM.
- PR #174 research qualified 3,388 paired public model calls: exactly 47 cycles saved each, no slower inputs; 192 real x64sc public calls V2/V3 both relocations, V3 512KiB REU, all equal. New source branch's dedicated model/native/56-entry ABI gate PASS.
- Preserve all historical PRGs/REUs and PERFORMANCE.md; note legacy whole-monolith regeneration from historical binaries can revert unrelated source optimizations. Source owner generator tested nondestructively; physical VIC/REU cycles and binary release remain open.

2026-10-15 ISSUE144 V2/V3 ISQRT32 NORMAL-RESIDENT HIGHWORD-SEED RESEARCH (SOURCE-ONLY OPTIN)
- Reused already verified unrestricted direct-highword-seed strategy without its caller-owned $0C00 overlay: helper fits within the pre-existing 192-byte V2/V3 $CB40-$CBFF normal resident slot (alternate map $8A40-$8AFF); source and public entry unchanged in the committed default.
- Independent source model 847 input pairs/profile/layout (3,388 paired): exactly 47 CPU-model cycles saved each, zero slower cases, correct root/carry/inputs/XY/SP, no additional normal zero-page or caller RAM; reference/alternate full-source assemblies differ only in root slot.
- Native VICE 3.10 x64sc: 192 baseline-plus-candidate public calls V2/V3 and both relocations pass byte-identical root/status; actual V3 512-KiB REU attached. Physical/native cycle timing not measured. Not promoted; no PRG, REU, PERFORMANCE or public API modification; larger mixed-call/source-regeneration/resource qualification remains open.

2026-10-15 ISSUE144 V4 ISQRT32 MASKSHIFT CANONICAL-SOURCE TRIAL (NOT BINARY RELEASE)
- Replace two six-ASL REU prefix index shifts after AND #$03 with LSR/ROR/ROR/AND #$C0, no added ZP or REU data.
- Independent current-main source-built same-input paired qualification 2,109 V4 public calls: exactly 8 modeled cycles saved every case, zero regressions or overflow V changes; actual 16-MiB REU VICE 48 calls PASS. Exact fast-four baseline pinned.
- Frozen reference PRGs, REU images and production PERFORMANCE.md unchanged. Full source/library/ABI, package and release gates required before merge; physical VIC/REU DMA time unmeasured.

2026-10-15 ISSUE144 V4 ISQRT32 FAST-FOUR CANONICAL SOURCE TRIAL (NOT BINARY RELEASE)
- V4 REU ISQRT32 canonical source-build input uses four 16-bit refinement steps followed by the original final two 17-bit steps; prepromotion source pinned for paired reference.
- Prior independent 8,619-radicand research: 111.190 mean CPU-model cycles saved, no slower cases, no new normal ZP or REU tables; V volatile flag differs on 195/8,619 model calls and is not a public contract.
- Existing five reference PRGs, two REU images, and production PERFORMANCE.md remain unchanged. New source and VICE qualification, public API, source-map and package gates required before merge. Physical REU/VIC/DMA timing outstanding.

2026-10-15 ISSUE144 PRODUCTION SOURCE INTEGRATION TRIAL (NOT RELEASED)
- Canonical V2–V4 resident SEEK16_INIT sources now use the previously opt-in normal-footprint in-hole Euclid/fractional helper placement; common 32/16 division source uses the qualified shared-take tail (PRs #169/#170). All public API labels and normal ZP allocations intended unchanged.
- This is a source-level production trial, not a release: shipped five resident PRGs, both REU images, PERFORMANCE.md and published cycle numbers remain unchanged pending full five-profile reference/alternate source validation, native VICE, mixed-call, resource, release and checksum gates. PR #171.

2026-10-15 ISSUE144 SEEK16 NORMAL-RESIDENT IN-HOLE + U3216 SOURCE-ONLY RESEARCH (NOT DEFAULT)
- Three independent opt-in V2/V3/V4 SEEK16 INIT source variants reuse 192 bytes recovered from the compact 32/16 division tail, replacing repeated accumulator JSR/RTS, relocating Euclid + fractional helpers to the reclaimed resident island. No extra caller RAM, normal ZP or public-entry changes.
- Same-input local 1,920 ordinary SEEK16 INIT calls/profile followed by STEP: V2 mean -22.1448 cycles, V3/V4 mean -20.4781, no slower measured call, exact full SEEK object state/carry/X/SP. Three 56-entry source validators passed 65,034 calls total.
- Real VICE 3.13.2 x64sc V2/V3/V4 baseline-vs-candidate native INIT+STEP state/status snapshots passed 32 INIT and 32 STEP calls per profile (384 compared bytes), including 512-KiB/16-MiB REU. Source-rebuilt REU bytes unchanged.
- Individually liftable full source examples in optional/issue144_seek_inhole_shared; new reproducible current-main reference+alternate/source-validator/paired-model/native workflow. V1/V5, physical bus timing, arbitrary IRQ/NMI mixing, full production promotion and performance tables remain unchanged.

2026-10-15 ISSUE144 U3216 FULL-DOMAIN SHARED-TAKE INLINE SOURCE (RESEARCH ONLY)
- Independently authored standard-layout NMOS 6510 source alternative replaces duplicated forced/taken 32/16 low-tail subtraction with a shared path, saving 192 bytes of V2 general-tail source assembly (685 -> 493); preserves the D8/D0 dispatch and stable public ABI.
- Same-input 10,735 alternating UDIV32_16/UMOD32_16 public-call CPU-model cases PASS. V2 mean saved 6.3371 cycles overall / 6.7192 uniform, worst 1-cycle slowdown on 108 cases. D8 and D0 unchanged, no default promotion.
- Four-profile (V1-V4) source builds and broad source validators PASS 86,712 calls; 48 native VICE 3.13.2 full-public calls PASS across V2, V3+512KiB REU, V4+16MiB REU. Reproducer and pinned optional ASM in optional/issue144_u3216_shared_take_inline; private OptiSearch implementation excluded.
- This modest win does not close Issue144 unrestricted division architecture; no PRGs/REUs/performance records or builder defaults changed. V5, production integration and physical REU/VIC timing remain future qualification.

2026-10-15 ISSUE144 V4 ISQRT32 FAST-FOUR SOURCE-ONLY RESEARCH (NOT DEFAULT)
- Independently authored opt-in V4 16-bit first-four-radix-4-step refinement; retains full 17-bit last two steps and current-main immediate $91 REU DMA.
- Same-input 8,619 full-public CPU-model calls PASS: 918.542406 -> 807.352361 mean cycles (111.190045 saved), no slower case; 48 native VICE calls PASS on actual 16-MiB REU after hardware-correct DMA.
- Source-based independent reproducer `tools/issue144_v4_isqrt_fast4_source_native_qualify.py` builds reference/alternate V4 maps and tests 2,109 additional public calls plus 48 actual x64sc calls with the 16-MiB REU; dedicated pinned-native CI added.
- Overflow (V) is volatile and differs on 195 model calls. Physical DMA/VIC cycle cost, current-main production requalification and wider issue144 work remain open. Five shipped PRGs, two REU images and PERFORMANCE unchanged.
- A stale 8 October offline source snapshot had $81. Current GitHub main already uses $91/$92; false-positive production bug report #166 is closed with correction. No private OptiSearch code shipped.

2026-10-15 ISSUE144 32/16 HIGH-DIVISOR SIGN-FASTSKIP AND FULL-CALL HYBRID (RESEARCH ONLY)
- Independent NMOS 6510 model 18,224 high-D tail pairs PASS; sign-bit skip saves 11.088 mean cycles vs stock-like tail but 2,324 slower calls (worst 15 cycles). Assembled caller-owned 1,038-byte V2/V3/V4 hybrid combines low-D no-overflow and high-D sign-fastskip: 14,220 paired full Q32/R16/C/N/D/SP public DIV/MOD checks PASS, uniform N32/D16 savings 28.923 / 31.923 modeled cycles. But 99/640 UDIV uniform slower (worst -17), D8/zero fallback +9/+6 cycles, and requires $0800-$0C0D caller RAM. No native VICE or alternate-map proof; REJECT default promotion, Issue #144 B OPEN. No PRGs, REUs, builder, ZP, PERFORMANCE or private OptiSearch changed. See docs/ISSUE144_UDIV32_16_HIGHDIV_SIGN_FASTSKIP_HYBRID_SCREEN_2026-10-15.md

2026-10-15 ISSUE144 UDIV32_16/UMOD32_16 NO-OVERFLOW LOW-DIVISOR OPTIONAL ASSEMBLY
- Source-only V2/V3/V4 reference-map $0800-$09FE (511 bytes) low-divisor $0100-$7FFF producer (no extra normal ZP): 12,976 correct isolated tail tests, 684->444 bytes, 56.773 cycles mean tail saved, zero domain regressions. Full public Q32/R16/C/N/D/SP: 4,261 paired all-D16 cases per API/profile (51,132 baseline+candidate calls), source ASM machine-byte parity PASS; eligible range saves 59.725 UDIV / 62.725 UMOD cycles, uniform full-width saves 24.324 / 27.324. Explicit D8/zero/high-D fallback regresses 7–11 cycles. Pinned real x64sc 288 native baseline+candidate calls PASS. Optional only, V1/V5 and alternate relocations unsupported, shared scratch/non-reentrant; no default or PERFORMANCE promotion, shipped PRGs/REUs unchanged. See docs/ISSUE144_UDIV32_16_NOOVERFLOW_LOW_D_OPTIN_2026-10-15.md

2026-10-15 ISSUE144 RADIX256 32/16 REU QUOTIENT-DIGIT NO-GO SCREEN (RESEARCH ONLY)
- Numerically exact for 1,155,360 full-width N32/D16 pairs; 64-KiB q0/t0 REU table has <=2 bounded corrections per digit. Independent assembled 6510 + V4 REU digit passed 4,040 pairs (199 code bytes, +16 scratch ZP, 446.705 mean modeled cycles/digit). Paired 698-case high-divisor lower-tail: existing shared restoring 460.599 CPU cycles versus new REU+software-multiply 893.676; zero-cost oracle multiplication 351.722, zero-cost oracle multiplication and lookup 231.722. Two public UMUL8 calls at 69 cycles each cannot meet the 54.438-cycles-per-multiply break-even even before REU register reinitialization or DMA wait. This candidate is REJECTED for production; research source/evidence retained. Normal 5 PRGs, REUs, API, ZP, PERFORMANCE unchanged. docs/ISSUE144_RADIX256_6510_COST_GATE_2026-10-15.md

2026-10-15 ISSUE144 32/16 FULL-WIDTH SHARED-SUBTRACTION RESEARCH (NONPRODUCTION)
- Public mini6502 isolated low-tail 7,554 nonzero-divisor same-input checks PASS, 684->492 bytes and 7.511 modeled tail cycles saved. Full-public V2/V3/V4 source-built 1,280-case Q32/R16/C comparison on reference+alternate maps PASS, 6.592 cycles saved uniform full-width, 4.758 mixed mean; 13 one-cycle mixed regressions. Independent pinned native x64sc V2/V3/V4 288 full-public baseline/candidate DIV/MOD calls PASS. Only a ~1% full-call gain; no default producer promotion. V1/V5 and mixed-call certification still pending; shipped PRGs, REUs, PERFORMANCE, ABI and ZP unchanged. docs/ISSUE144_UDIV32_16_SHARED_TAKE_TAIL_SCREEN_2026-10-15.md

2026-10-15 ISSUE144 SEEK16 INIT ACCUMULATOR INLINING FIVE PROFILE OPTIN
- SEEK16_INIT accumulator direct inline + JMP continuation in separately allocated caller RAM: five public profiles, 20,400 paired full-state CPU model calls with STEP follow-up, 70 real native INIT and 1,120 STEP executions PASS. Mean savings V1/V5 22.105 cycles (some -1 worst), V2 25.451, V3/V4 23.704. Original residents and REU images unchanged; not a default promotion. docs/ISSUE144_SEEK16_INIT_INLINE_ACCUM_V1_V5_2026-10-15.md

2026-10-15 ISSUE144 SIGNED32 DIVMOD NATIVE VICE HARNESS STABILITY
- Initialize 6510 SP=$FF explicitly before MATH_INIT in the signed32/16 DIV/MOD VICE harness; run three independent 480-call native repetitions (1,440 calls) to screen startup-state flakiness. No math algorithm, performance metrics, ABI, ZP, shipped binaries, or REU image changed.

2026-10-15 ISSUE144 V4 REU ISQRT32 INPLACE ROTATE6 PARETO
- Source-only V4 REU ISQRT32 all-input 12-byte in-place peephole: two 6x ASL groups -> LSR/ROR/ROR/BCC+1/NOP, exact public output/flags, 6 CPU-model cycles saved on all 4,130 canonical inputs (917.317433 -> 911.317433), 48 real native x64sc REU-16MiB baseline/candidate calls PASS. Optional reversible 88-byte BEGIN/END assembly, no extra normal ZP/code/data; normal resident PRG/REU and ordinary PERFORMANCE remain unchanged. docs/ISSUE144_V4_REU_ISQRT32_ROTATE6_PARETO_2026-10-15.md

2026-10-15 ISSUE144 UNSIGNED 32/16 FULL Q R NARROW NUMERATOR OPTIN
- Source-only 22-byte all-input UDIV32_16/UMOD32_16 full-Q/R/C guarded narrow-numerator option: 12,800 same-input paired CPU model cases and 480 native x64sc calls PASS. Saves ~21–32 cycles on 10% narrow workload (V1–V5) but COSTS 14/11 cycles per uniform full-width call; deliberately not a default promotion. Documented volatile X/Y/NZV may differ; no shipped resident PRGs, REUs, ordinary ZP/ABI or PERFORMANCE change. docs/ISSUE144_UNSIGNED32_16_NARROW_NUMERATOR_GUARD_2026-10-15.md

2026-10-15 ISSUE144 SIGNED32/16 ZERO-FOOTPRINT PUBLIC-JMP DIRECT OPTIN
- All-input signed32/16 SDIV/SMOD full-Q+R public-entry JMP-chain micro-optins: V2/3/4 save 3/6 cycles per call, V1 SMOD saves 3, V5 already direct. 32,790 matched input cases and 480 real native x64sc calls PASS; reversible V1/2/3/4 source installers 22/42 B. No ordinary resident PRG/REU/zero-page/API/PERFORMANCE changes. docs/ISSUE144_SIGNED32_DIVMOD_DIRECT_JMP_2026-10-15.md

2026-10-15 ISSUE144 ISQRT32 ALL-DOMAIN DIRECT HIGHWORD SEED
- Source-only all-domain ISQRT32 non-REU highword-seed opt-in (V1/V2/V3/V5): 47 cycles faster V2/V3, 51 cycles V1/V5 on all 16,520 canonical paired CPU calls; 192 native original/opt-in x64sc calls PASS; V4 original 16MiB REU 24-call control PASS but unchanged. 95–102 bytes in caller-owned RAM, no ordinary ZP/PRG/REU/API/PERFORMANCE changes. docs/ISSUE144_ISQRT32_FULL_INPUT_DIRECT_HIGHWORD_SEED_2026-10-15.md

2026-10-15 ISSUE144 SIGNED SHR16 INDEPENDENT MIXED-CALL PRODUCER
- Source-only all-sign SMUL32_SHR16 independent producer: 1,371–1,405 bytes additional caller-owned code RAM, 12,045 paired CPU-model calls across V1–V5 saving 53.69–56.00 mean cycles; 240 native x64sc old/new calls with normal SMUL32 and UMUL32 interleaved. Original full producers untouched (sequential mixed-call safe, not IRQ/NMI reentrant). No default PRG, REU, ABI, ZP or ordinary PERFORMANCE leaderboard changes. docs/ISSUE144_SIGNED_SHR16_INDEPENDENT_MIXED_2026-10-15.md

2026-10-15 ISSUE144 SIGNED SHR16 EXCLUSIVE FIVE PROFILE EXTENSION
- Source-only unrestricted all-sign SMUL32_SHR16 exclusive overlay V2/V3/V4: 53 CPU-model cycles faster per public call across 12,045 paired calls, 240 native x64sc original/candidate calls PASS across V1-V5. Reversible 334-byte BEGIN/END, changes 49 in-memory code bytes, 218/224 cycle setup/teardown. Shared SMUL32 cannot be called while overlay enabled, no regular profile/ABI/ZP or PERFORMANCE promotion. docs/ISSUE144_SIGNED_FULL_DOMAIN_EXCLUSIVE_2026-10-15.md

2026-10-15 ISSUE144 SIGNED SHR16 FULL DOMAIN EXCLUSIVE PRODUCER
- Source-only unrestricted all-sign SMUL32_SHR16 exclusive overlay V2/V3/V4: 53 CPU-model cycles faster per public call across 7,227 paired calls, 144 native x64sc original/candidate calls PASS. Reversible 334-byte BEGIN/END, changes 49 in-memory code bytes, 218/224 cycle setup/teardown. Shared SMUL32 cannot be called while overlay enabled, no regular profile/ABI/ZP or PERFORMANCE promotion. docs/ISSUE144_SIGNED_FULL_DOMAIN_EXCLUSIVE_2026-10-15.md

2026-10-15 ISSUE144 SEEK16 INIT RELOCATION UNPROMOTED
- Unpromoted V2 SEEK16_INIT speed-one source relocation research: 291 bytes in caller RAM, $19F0 and $1A00 preserved, 300 paired model INIT+STEP states and 128 native STEP executions matched; overall gain only ~4.2 CPU cycles, some slower calls. No resident integration. docs/ISSUE144_SEEK16_INIT_RELOCATED_K1_RESEARCH_2026-10-15.md

2026-10-15 ISSUE144 FOUR 32BIT MULTIPLY NARROW16 OPTINS
- Published four source-only opt-in U32 and S32 full/SHR16 multiply variants for the strict both-upper-words-zero operand domain: 22,900 paired CPU model calls, 960 real x64sc calls across all profiles passing. No regular profile/API/ZP/REU/benchmark leaderboard modification. docs/ISSUE144_A_FOUR_MUL_NARROW16_SPECIALIST_2026-10-15.md

2026-10-15 ISSUE144 B/C DOMAIN-QUALIFIED OPTIONAL SOURCES
- Source-only opt-in B/C specialists, no installed library change: power-of-two D16 remainder-only 25 bytes/38 cycles (NOT quotient-producing); low16 ISQRT32 via existing ISQRT16; five-profile CPU/native proof including real V4 REU image. An all-input guard and quotient-complete pow2 selector remain research-only. Regular library binaries, ZP, public API and PERFORMANCE leaderboard unchanged. docs/ISSUE144_BC_DOMAIN_SPECIALIST_PARETO_2026-10-15.md

2026-10-15 ISSUE144 SIGNED SHR16 NONNEGATIVE SPECIALIST AND QUADRANT RESEARCH
- Domain-qualified optional signed 32x32 SHR16 public-entry alias for nonnegative input pairs: 58.372 CPU-model cycles saved on 715 paired cases/profile V2-V4, 144 native x64sc baseline/alias calls PASS, reversible source-assembled signed JMP enable/disable. General all-sign hybrid screened: 16.438 mean saved but negative-quadrant regressions, NOT promoted. Stock PRGs, REU, ABI, normal ZP and regular leaderboard unchanged. docs/ISSUE144_SIGNED_SHR16_SPECIALISTS_2026-10-15.md

2026-10-15 ISSUE144 INDEPENDENT SHR16 MULTIPLY CLONE PARETO POINT
- Opt-in original-source-derived unsigned 32x32 SHR16 separate-RAM producer saves exactly 62 CPU-model cycles on 7,227 common pairs V2/V3/V4, with 144 native x64sc baseline/clone correctness calls passing. Interleaves ordinary UMUL32 and SMUL32, unlike prior exclusive overlay. Uses separate $0D05–$0E49 RAM and shared ZP/tables; NOT reentrant, no shipped code/REU, normal ABI change, no private OptiSearch redistribution. docs/ISSUE144_UMUL32_SHR16_SEQUENTIAL_CLONE_2026-10-15.md

2026-10-15 ISSUE144 V2-V4 EXCLUSIVE MULTIPLY SHR16 RESEARCH
- Source-backed optional V2/V3/V4 UMUL32_SHR16 exclusive batch saves 53 CPU-model cycles on 7,227 matched operand pairs; BEGIN/END 76/80 cycles, four-call crossover including caller JSRs. 144 native x64sc old/new calls pass. Shared UMUL32 core is unsafe for other calls while patched; no default PRG, REU, ZP or public ABI modification. See docs/ISSUE144_V234_SHR16_EXCLUSIVE_BATCH_2026-10-15.md

2026-10-14 ISSUE144 V2 EXCLUSIVE SHR16 DIRECT-SLICE RESEARCH
- Research-only opt-in V2 unsigned 32x32 SHR16 direct-result-slice overlay measured 53 CPU-model cycles faster for all 2,409 paired operands; BEGIN/END overhead 76/80 cycles, four-call full-program crossover. Native VICE baseline/overlay and assembled BEGIN/CALL/END both passed 48 calls. Affects shared UMUL32 producer while active; ordinary public mixed-call ABI NOT qualified, no resident PRG/REU/default profile changed and no automatic promotion. See docs/ISSUE144_V2_SHR16_EXCLUSIVE_BATCH_RESEARCH.md

2026-10-14 ISSUE39 CAMPAIGN MAIN POSTMERGE CERTIFICATION
- Completed the full Issue #39 audit: all eight SEEK8/16 public operations qualified with V1-V5 reference/alternate sources, native VICE/REU checks and 408-byte mixed-state safety. Three independent main push workflows green at d296ace693543025f8aba582a0c933c867939a3a (full library, comparable unsigned, fixed multiply). No additional unqualified shortcut, no public ABI/PRG/REU/ZP changes; rejected V2 memory overlap documented, private OptiSearch excluded. Final status, evidence and package SHA256 sealed. validation/review/ISSUE39_SEEK_FAMILY_POSTMERGE_MAIN_CERT_2026-10-14.json

2026-10-14 ISSUE39 SEEK8/16 COMPLETE FAMILY AUDIT
- Final audited all eight SEEK8/16 public APIs. 480 INIT / 246,480 STEP CPU-model calls across all slots/maps, 40 INIT / 640 STEP native x64sc calls with V3/V4 REU. V2 k0=1 shortcut rejected: foreign resident bytes at $19F0 and table $1A00, not an available code island. No new qualified speed winner; shipped binaries, REU, public ABI and ZP remain unchanged. Prior SEEK16_INIT optimization remains in release. Main CI required for Issue #39 closeout. docs/ISSUE39_SEEK_FAMILY_COMPLETION_2026-10-14.md

2026-10-14 ISSUE39 SEEK8/16 ALL-MODE NATIVE VICE CERTIFICATION
- Native x64sc executes all eight SEEK8/16 INIT/STEP, STEP_INT and STEP1 public modes on V1–V5, 40 INIT and 640 STEP calls; checks movement, arrival carry, X, stack and post-arrival stability against independent model, using real V3/V4 REU images. No native cycle timing claimed. No production binary/API/REU/ZP changes; main certification and full SEEK family closeout still pending. docs/ISSUE39_SEEK_NATIVE_ALL_MODES_2026-10-14.md

2026-10-14 ISSUE39 SEEK8/16 EIGHT-OBJECT INTERLEAVING RESEARCH
- Five profiles, reference/alternate, eight concurrent slots and all INIT/STEP/STEP_INT/STEP1 modes qualified: 480 INITs, 246,480 STEP calls, 86,960 model frames, slot isolation and post-arrival safety. Mixed DIV/MOD and memory-island gates passed. No changes to public API, resident PRGs, REU or speed tables. Native all-stepper proof and full SEEK optimization still open. docs/ISSUE39_SEEK_ALL_SLOTS_RESEARCH_2026-10-14.md

2026-10-14 ISSUE39 SEEK16 EUCLIDEAN INIT LOOP RELEASE
- V1 unsigned division/modulo secondary full regression: all arithmetic correct; six mean-cycle changes from relocated branch alignment independently rebenchmarked and pinned, maximum +0.035416 cycles/call; see validation/review/UNSIGNED_DIVISION_VALIDATION.json. No native cycle timing.
  Additional Issue #136 native x64sc mixed SEEK/DIVMOD proof: 325 public calls, V1–V5 (V3/V4 real REU), correct outputs, movement, carry and stack. Native cycle timing not measured; see validation/review/ISSUE136_SEEK_DIVMOD_NATIVE_VICE.json.
- SEEK16 Euclidean INIT scale loop: one byte smaller, faster on CPU-model paired calls, unchanged major-axis INIT and SEEK8/STEP paths. Five profiles, two relocation maps, 240 baseline/candidate native VICE public calls. Repaired Issue #136 V1/V5 UDIV32/SEEK state collision by moving the low-round island to $4D80-$4FEC, preserving the public ABI. Passed 18,280 mixed DIV/MOD public calls and 13,580 SEEK steps. Rebenchmarked transitive V1 timing; unchanged REU/ZP. Standalone mirrors, performance, package audit and checksums regenerated. PR/main CI pending; Issue #39 still open for SEEK family. docs/ISSUE39_SEEK16_EUCLIDEAN_INIT_RELEASE_2026-10-14.md

## 2026-10-14 ISSUE39 NORMALIZE POSTMERGE FINAL CERTIFICATION

Confirmed PR #132 installed the 865-byte V1/V2/V5 normalizer with 16 fewer code bytes and identical signed results. Mean CPU-model cycles 160.150080 -> 159.128794. Verified 1,073,960 paired-map model calls, 320 real x64sc old/new calls, 723,073-cell precision certificate, unchanged four-byte scratch, public API and V3/V4 REU. Native VICE cycle timing was not measured. The fully qualified distance/normalization family is complete; Issue #39 remains OPEN for SEEK8/16 INIT/STEP. Both changelogs and checksum ledger sealed.
Main merge 07f89e65661a1a543c7315d1ce5dc8319278e61b; full main run 38586383233, comparable 38586383155, fixed multiply 38586383270. Completion certificate: validation/review/ISSUE39_NORMALIZE_POSTMERGE_COMPLETION_2026-10-14.json.

---

## 2026-10-14 ISSUE39 NORMALIZE STOCK LOG BRANCH PRODUCTION

Optimized V1/V2/V5 VEC2_NORMALIZE_Q8_8: redundant BNE/BEQ branch collapse, 16 fewer code bytes, mean CPU-model 160.150080 -> 159.128794 cycles. 1,073,960 public model calls; 320 old/new x64sc calls. Exact signed outputs and full-domain angular/component accuracy preserved; no extra ZP or REU. Rebuilt standalone sources, performance tables, verified reversible old PRG bytes and checksums. PR #132 merged; post-merge main certification passed. See docs/ISSUE39_NORMALIZE_BRANCH_RELEASE_2026-10-14.md.

---

## 2026-10-14 ISSUE39 DIST8 POSTMERGE FINAL CERTIFICATION

Final certification of shipped DIST8_FAST/DIST8_ACCURATE optimization after PR #130 merge, four green main checks. 1,310,720 paired CPU-model baseline/candidate calls, 655,360 new shipped benchmarks, 119,220 reference/alternate calls and 480 native VICE baseline/candidate public calls on SHA-distinct PRGs. Exact 8/10-byte source-backed swap only; no ABI, resident size, normal ZP or REU changes. VICE cycle timing not measured. Both changelogs and SHA256 resealed. Issue #39 remains open for VEC2 normalization and seek. Main `44fc91813d945c05194d2f4962bb89f9d5f88449`; full [#38573248160](https://github.com/floppyrom/C64-Math-Library/actions/runs/38573248160), comparable [#38573248208](https://github.com/floppyrom/C64-Math-Library/actions/runs/38573248208), fixed [#38573248172](https://github.com/floppyrom/C64-Math-Library/actions/runs/38573248172), Turbo32 [#38573248117](https://github.com/floppyrom/C64-Math-Library/actions/runs/38573248117).
Certificate `validation/review/ISSUE39_DIST8_POSTMERGE_COMPLETION_2026-10-14.json`.

---

## 2026-10-14 ISSUE39 DIST8 SHARED REGISTER-SWAP SOURCE RELEASE

Source-integrated DIST8_FAST/DIST8_ACCURATE common stack-swap elimination (TAX/LDA/STA/STX) for V1–V5. Exact 1,310,720 old/new emulator calls; 119,220 reference/alternate model calls; 480 native x64sc baseline/candidate calls; production exhaustive 655,360 calls. Saves 9 cycles on the swap branch in V1/V5 and 8 in V2–V4 (CPU model, not VICE timing). PRG lengths, stable ABI, REU and ZP unchanged. Standalone, metrics and package checksums synchronized. Independent PR/main CI pending; Issue39 still open for normalization and seek. See `docs/ISSUE39_DIST8_REGISTER_SWAP_RELEASE_2026-10-14.md`.

---

2026-10-14 ISSUE39 DIST8 SHARED SWAP RESEARCH — NOT RELEASED
- In-memory same-address DIST8_FAST/DIST8_ACCURATE swap candidate exhaustively passed 655,360 paired public operand cases across all five profiles (1,310,720 original/candidate CPU-model calls). All output/scratch bytes, inputs, carry and stack agree; V1/V5 save 4.535019 mean modeled cycles per public call, V2/V3/V4 save 4.031128. Native cycle timing NOT measured. No production binaries, ABI, ZP, standalone sources or REU changed. This is NOT a shipped optimization; further source integration, relocation, native VICE and full release checks remain. Evidence: validation/review/ISSUE39_DIST8_REGISTER_SWAP_RESEARCH_2026-10-14.json

## 2026-10-14 ISSUE39 TRIG ANGLE FAMILY FINAL CERTIFICATION

**Complete:** SIN8/COS8/SINCOS8 plus ATAN2_8, all five profiles, both source relocations. 7,680 CPU-model SIN/COS/SINCOS public calls; 655,360 exhaustive signed ATAN2 public calls; 480 real x64sc native calls (including V3/V4 REU image). V1 SINCOS 39 model cycles vs combined two-call saving 13; V2–V5 SINCOS 31 and saving 15. All combined outputs equal separate calls. No production PRG, ABI, ZP, table or reserved stack change, no private OptiSearch source. Native cycles were **not** measured.

Certified main `50b75c5eeeec6ea170ba1940ca4e0ac4176b7089`; full library [#38550154962](https://github.com/floppyrom/C64-Math-Library/actions/runs/38550154962), comparable [#38550155125](https://github.com/floppyrom/C64-Math-Library/actions/runs/38550155125), native [#38548516375](https://github.com/floppyrom/C64-Math-Library/actions/runs/38548516375). See `validation/review/ISSUE39_TRIG_ANGLE_FAMILY_COMPLETION_2026-10-14.json`. Issue #39 OPEN for distance and seek.

---

2026-10-14 ISSUE39 TRIG ANGLE NATIVE VICE VALIDATION
- 480 installed x64sc public calls in all five profiles covering SIN8/COS8/SINCOS8/ATAN2; compared exact outputs against independent model, preserved operands, carry clear and stable stack. V3/V4 REU image tested. No native cycle measurement; source, standalone, ZP and public ABI unchanged. Final PR/main CI pending.

2026-10-14 ISSUE39 TRIG ANGLE PUBLIC TABLE AUDIT RESEARCH
- SIN8/COS8/SINCOS8 qualified on all 256 phases, 7,680 five-profile/two-map CPU calls; SINCOS outputs equal separate operations. Existing ATAN2 exhaustive 655,360-call public dispatch proof retained. V1 SINCOS 39 cycles, 13 saved vs two separate; V2-V5 31 cycles, 15 saved. No public ABI, resident binary, table/ZP or private OptiSearch source changes. Native VICE and final CI pending; Issue39 trig remains OPEN. docs/ISSUE39_TRIG_ANGLE_FAMILY_REVIEW_2026-10-14.md

## 2026-10-14 ISSUE39 REU MULTIPLY FAMILY FINAL CERTIFICATION

**Completed:** Turbo16, Turbo32 and V4 QS16; merged source and relocation fix PR #124. Published reference PRGs and REU images unchanged. CPU-model comparison uses the same operands and includes deterministic REU transfer costs: Turbo16 197.046 versus normal 216.734, batch crossover 33; Turbo32 676.185 versus normal 693.453, batch crossover 41. V4 QS16 281.727 versus 216.734, no speed crossover. Exact 57,759 public model products, earlier 17,196 relocation API calls/3,556 boundary products, and 120 native VICE calls with real 512 KiB/16 MiB REU images passed. Native cycle timing **not measured**. Alternate V4 QS16 REU bank $30 is corrected.

**Final validated main:** `abf288e8cb20ad75b068e5d425517654ba30c219`; full-library [#38545214940](https://github.com/floppyrom/C64-Math-Library/actions/runs/38545214940), comparable unsigned [#38545214835](https://github.com/floppyrom/C64-Math-Library/actions/runs/38545214835), native [#38539477409](https://github.com/floppyrom/C64-Math-Library/actions/runs/38539477409). Reproducible certificate: `validation/review/ISSUE39_REU_MULTIPLY_FAMILY_COMPLETION_2026-10-14.json`. Issue #39 remains open for trig, distance and seek.

---

## 2026-10-14 — Issue #39 merged PR closeout (#118–#124)

**Merged into `main` through `03ba4fc98893` (14 October 2026).** The entries below are **merge closeouts**, not preliminary research staging. Earlier notes farther down that say *CI pending* describe the state at the time of staging and are superseded by this section. Cycle improvements are deterministic **CPU-model** comparisons; native VICE correctness does not imply native cycle measurements. Private OptiSearch source remains unpublished.

- **[PR #118](https://github.com/floppyrom/C64-Math-Library/pull/118)** (merge `33f364cfe046`): V1/V5 UMUL24 rare-carry return: 1 CPU-model cycle saved for each of 10,324 paired inputs/profile; 384 native x64sc correctness calls, no extra resident/ZP bytes. **Status:** Production change integrated; full PR and post-merge qualification passed.
- **[PR #119](https://github.com/floppyrom/C64-Math-Library/pull/119)** (merge `4d913d9b5e5a`): Unsigned multiply UMUL8/16/24/32 plus READY family completion; five-profile/relocation/READY ABI and OptiSearch resource-class audit. **Status:** Completion certificate, changelogs and checksum publication; no further binary edits.
- **[PR #120](https://github.com/floppyrom/C64-Math-Library/pull/120)** (merge `3f4da1ab061a`): Signed multiply SMUL8/16/24/32 plus READY family validation: exhaustive 8-bit signed domain on five profiles, 600 native x64sc public calls plus 120 READY preparations; OptiSearch donor screen. **Status:** Qualified no-gain review: retained existing public-compatible implementations.
- **[PR #121](https://github.com/floppyrom/C64-Math-Library/pull/121)** (merge `bfc43c2f6643`): Signed multiply family final release certification; prepared READY saves 25 cycles in V1/V5 but costs 3 cycles in V2–V4 compared on identical inputs. **Status:** Status, release certificate and checksums sealed; no arithmetic binary edits.
- **[PR #122](https://github.com/floppyrom/C64-Math-Library/pull/122)** (merge `ce4e7bcf785f`): UMUL32_SHR16 and SMUL32_SHR16 fixed output return-tail optimisation: 2 CPU-model cycles saved per call on each of 4,361 paired operands/profile/map; 480 native x64sc before/after calls. **Status:** Production binaries changed at exactly four bytes/profile, no resident span/ZP/stack growth; 16-bit SHR8 paths unchanged.
- **[PR #123](https://github.com/floppyrom/C64-Math-Library/pull/123)** (merge `e9a3d6dabccb`): Fixed multiply outputs family completion (UMUL16_SHR8, SMUL16_SHR8, UMUL32_SHR16, SMUL32_SHR16). **Status:** Published permanent four-operation audit, completion certificate, docs, changelogs and SHA256SUMS; no additional binary edits.
- **[PR #124](https://github.com/floppyrom/C64-Math-Library/pull/124)** (merge `03ba4fc98893`): REU Turbo16/32 and V4 QS16 matched batch audit and V4 QS16 alternate relocation correction (symbolic I/O/ZP/bank references); 57,759 CPU-model public calls and 120 native x64sc REU-mode calls. **Status:** Merged and post-merge main full-library/comparable/Turbo32/fixed-family checks green. REU *family completion* remains pending (Issue #39 checkbox open), despite merged fix.

**Post-merge validation at PR #124 `main`:** full-library [#38540701276](https://github.com/floppyrom/C64-Math-Library/actions/runs/38540701276), comparable unsigned [#38540701196](https://github.com/floppyrom/C64-Math-Library/actions/runs/38540701196), Turbo32 [#38540701380](https://github.com/floppyrom/C64-Math-Library/actions/runs/38540701380), and fixed-output family [#38540701127](https://github.com/floppyrom/C64-Math-Library/actions/runs/38540701127) all **PASS**. Issue #39 remains open for REU final certification and subsequent families.

---

2026-10-14 ISSUE39 REU MULTIPLY NATIVE VICE AND V4 QS16 RELOCATION
- Actual VICE x64sc with 512-KiB/16-MiB REU images qualified 120 Turbo16/Turbo32/QS16 BEGIN/CALL/END calls. Carry, products, operands, output sentinels and stack passed; native cycle timing was NOT measured. V4 QS16 alternate relocation now uses symbolic MATH_IO, REU_SCRATCH, ZP_MAIN and REU_QS16_BASE_BANK. Reference PRG/REU bytes unchanged; same-corpus Turbo16 batch crossover 33 and Turbo32 41, QS16 no crossover. Exact PR/main CI pending.

2026-10-14 ISSUE39 REU MULTIPLY MODES THREE-MODE PUBLIC PROFILE AUDIT
- Same-input REU multiply architecture: V3/V4 Turbo16 197.046 public model cycles vs ordinary 216.734, 645 lifecycle cycles, 33-call crossover; Turbo32 676.185 vs 693.453, 697 lifecycle, 41-call crossover; V4 QS16 281.727 vs 216.734, no speed crossover. 57,759 public product calls across installed/reference/alternate V3/V4, plus prior 17,196 Turbo relocation API and 3,556 boundary calls. No resident/REU/ABI/stack/ZP growth, no private source publication. Native VICE REU and full PR/main qualification pending.
- docs/ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md

2026-10-14 ISSUE39 FIXED MULTIPLY OUTPUTS FINAL PUBLICATION
- UMUL16_SHR8 and SMUL16_SHR8 unchanged, existing 10,196-case all-profile reference/alternate register-return qualification. UMUL32_SHR16 and SMUL32_SHR16 source-integrated -2 CPU-model cycles on all 4,361 matched calls/entry/profile/map, no code span/ZP/stack growth. 480 native original/new installed public calls identical; native cycle timing NOT measured.
- Postmerge main ce4e7bcf785f8b0fb292be1b044adce9fa3c1978: full 38529409135, comparable 38529409155, Turbo32 38529409200. REU Turbo/QS and other Issue39 families remain OPEN.

2026-10-14 ISSUE39 FIXED SHR16 TWO-CYCLE NATIVE VICE CONFIRMATION
- Installed x64sc old/new signed/unsigned UMUL32_SHR16/SMUL32_SHR16: 480 public calls across five profiles, complete bytewise identical output/flags/stack snapshots. The 2-cycle saving is from paired CPU model, not VICE timing. No new code memory or ZP. Independent PR/main CI pending.

2026-10-14 ISSUE39 FIXED OUTPUT SHR16 REDUNDANT CARRY TAIL
- 32-bit fixed-output UMUL32_SHR16 and SMUL32_SHR16: removed redundant CLC following C=0 full-product producer. Matched -2 CPU-model cycles for all 4,361 cases per operation/profile/map; five profiles, both relocations, exactly four code-byte substitutions/profile; no resident, ABI, ZP or persistent stack growth. Native VICE and postmerge checks PENDING.
- UMUL16_SHR8 and SMUL16_SHR8 retained the existing qualified register-output adapters without code changes. docs/ISSUE39_FIXED_SHR16_RETURN_TAIL_2026-10-14.md

2026-10-14 ISSUE39 SIGNED MULTIPLY FAMILY FINAL MAIN CERTIFICATION
- Five stable SMUL8/16/24/32 + conditional SMUL32_READY implementations retained after public-ABI manual and private OptiSearch resource screen. Exhaustive SMUL8 all five profiles (327,680 calls); SMUL16 4,457 and SMUL24/32 2,409 matched pairs/profile; READY same-input 2,409 pairs/profile. V1/V5 READY -25 cycles; V2-V4 READY +3 for stable redirect; normal low-ZP entry must remain mixed-call safe.
- 600 native VICE signed calls and 120 READY preparation calls qualified, native timing not measured; no PRG, public ABI, ZP or persistent stack growth.
- PR #120 main 3f4da1ab061ad56f3745e3742a45b838321cf410 full CI 38522745848, comparable 38522745889, signed family 38522745760. Issue #39 remains open for fixed outputs, REU, trig, distance and seek.

2026-10-14 ISSUE39 SIGNED MULTIPLY FAMILY ABI RESOURCE QUALIFICATION
- Completed per-implementation audit of five stable SMUL8/16/24/32 and conditional SMUL32_READY APIs. Exhaustive SMUL8 65,536 each of V1-V5; 16/24/32 matched corpora 4,457/2,409/2,409; independent ordinary/READY paired 2,409 per profile, V1/V5 dirty-pointer interleavings. The existing 264,999-call signed regression and both relocation maps remain release gates.
- 600 installed-resident native x64sc calls plus 120 READY state preparation calls, exact product/carry/inputs/output sentinels/stack. Native cycles NOT measured. Private OptiSearch sign-first/probability layout, conditional carry, centered tables and SMUL32 compact126 screened; no demonstrable compatible full public ABI gain; no code or resident/ZP/stack/table growth.
- Publication is staged pending independent PR and main CI. Issue #39 remains OPEN; shifted multiplication and REU Turbo/QS are independent later steps. docs/ISSUE39_SIGNED_MULTIPLY_FAMILY_2026-10-14.md

2026-10-14 ISSUE39 UNSIGNED MULTIPLY FAMILY COMPLETE
- UMUL8/16/24/32 and stateful READY: five-profile ABI, reference/alternate source-build and deterministic mixed-call review completed. UMUL8 exhaustive 65,536; UMUL16 10,169; UMUL24 10,324; UMUL32/READY 2,409 matched inputs/profile.
- V1/V5 UMUL24 uniform -1 CPU-model cycle (466.042329 to 465.042329), 384 native x64sc old/new calls; no extra resident/ZP bytes. Normal UMUL32 pointer repair retained; private OptiSearch candidates not promoted without ABI/resource proof.
- Postmerge main 33f364cfe0465a4df92e82dec1d94039ec2e1d5d full CI 38486190274, comparable 38486190247; family gate 38485318288. Other Issue39 families and REU Turbo/QS remain OPEN.

2026-10-14 ISSUE39 V1V5 UMUL24 RARECARRY NATIVE SOURCE VALIDATION
- Pinned real x64sc old/new public UMUL24 and SMUL24 verified on V1/V5: 384 calls, identical products, preserved inputs, carry and sentinels; unchanged signed private executable. Native cycles were NOT measured. validation/review/ISSUE39_V1V5_UMUL24_RARECARRY_NATIVE_2026-10-14.json.

2026-10-14 ISSUE39 V1V5 UMUL24 RARE-CARRY CLC
- Source-integrated V1/V5 rare-carry CLC: -1 CPU-model cycle on all 10,324 matched unsigned calls/profile; 466.042329 -> 465.042329; V2-V4 unchanged, zero ZP/resident growth.
- Signed and mixed-call, relocation, standalone and package checks pass at staging; native VICE and PR/main CI pending. docs/ISSUE39_V1V5_UMUL24_RARECARRY_RELEASE_2026-10-14.md

2026-10-13 ISSUE39 UMUL32 READY MIXED-CALL POINTER LIFETIME (RESEARCH-ONLY)
- Tested V1/V5 ordinary and READY 32x32 public entries after 14 other APIs x 4 operand states: 56 states/profile, 1,456 ordinary and 1,456 READY arithmetic/ABI probes per profile. Ordinary passed every probe; READY was wrong on 312/profile after UMUL24, SMUL16 and SMUL24 overwrote pointer-high bytes $09/$0B/$0D. No resident, source, ZP or API change; 22-cycle bypass is unsafe without valid READY state. docs/ISSUE39_UMUL32_READY_POINTER_LIFETIME_2026-10-13.md

2026-10-13 ISSUE39 UMUL24 V2/V3/V4 POSTMERGE RELEASE CERTIFICATION
- Production PR #114 merged into main as eafb2b45e15542242925602e2bee21e063d559c3. All seven head-SHA push/PR workflows passed, plus post-merge main Validate library #38475292294, Comparable unsigned #38475292291, and Turbo32 #38475292298. 576 native x64sc calls passed product/carry/input/stack invariant checks (native cycle timing not measured).
- Public UMUL24 V2/V3/V4 same-input mean 419.292135 -> 417.783224 cycles; 7,789/10,324 calls save exactly 2 cycles, 2,535 unchanged, none slower. Exactly two code-byte changes per target resident, zero resident/ZP growth; V1/V5 unchanged. Issue #39 remains OPEN. docs/ISSUE39_V2V4_UMUL24_NOCARRY_CLC_2026-10-13.md

2026-10-13 ISSUE39 V2V4 UMUL24 NOCARRY CLC NATIVE VALIDATION
- Pinned real x64sc old/new public UMUL24 and SMUL24 verified on V2/V3/V4: 576 calls, identical products, preserved inputs, carry and sentinels; unchanged signed private executable. Native cycles were NOT measured. validation/review/ISSUE39_V2V4_UMUL24_NOCARRY_CLC_NATIVE_2026-10-13.json.

2026-10-13 ISSUE39 UMUL24 NONCARRY CLC PRODUCTION
- V2/V3/V4 UMUL24 redundant CLC removal: 7,789/10,324 calls -2 cycles and 2,535 unchanged; mean 417.783224 cycles; 0 extra resident/ZP bytes. V1/V5 unchanged.
- Signed/mixed regression, standalone source, alternate maps and package checked. Native VICE and all PR/post-merge main checks passed. docs/ISSUE39_V2V4_UMUL24_NOCARRY_CLC_2026-10-13.md

2026-10-13 ISSUE39 UMUL16/UMUL24 OPTISEARCH RESOURCE SCREEN (RESEARCH ONLY)
- Compared full public UMUL16 benchmarks to a verified arithmetic-only private near-page candidate, and reviewed the public 24-ZP FAST24 carry-transfer record against a retained private 27-ZP record. Timings are NOT ABI/CPU-model comparable; candidate relies on executable ZP and stack-page code. No production gain promoted; source and resident PRGs unchanged. Issue #39 remains open. See docs/ISSUE39_UMUL16_UMUL24_OPTISEARCH_RESOURCE_AUDIT_2026-10-13.md.

2026-10-13 ISSUE39 V1/V5 UMUL8 POSTMERGE RELEASE CERTIFICATION
- V1/V5 UMUL8 PR #109 is merged on main as f754cc87d0ba3518377a4e2d19a9e8fc6ac0d75a. Independent PR qualification and post-merge main checks passed: full validation #38463930923, comparable unsigned #38463930890, and Turbo32 #38463930880. No change to the measured six-cycle same-input CPU-model win, ABI, ZP or resident size; issue #39 remains open for the rest of the multiply campaign. Native VICE invariant replay: 256 calls; native cycle timing not measured.

2026-10-13 ISSUE39 V1/V5 UMUL8 DIRECT-OUTPUT SOURCE PRODUCTION
- V1 and V5 UMUL8 low-result direct store: exhaustive public same-input six-cycle gain, 90.490234375 to 84.490234375 cycles; current-source 256-call native VICE public replay passed. Eleven byte substitutions per resident, no resource growth, V2-V4 unchanged. PR #109 merged and all three post-merge main checks passed. docs/ISSUE39_V1V5_UMUL8_DIRECT_OUTPUT_PRODUCTION_2026-10-13.md

2026-10-13 ISSUE39 V1/V5 UMUL8 DIRECT-OUTPUT RESEARCH (NOT RELEASED)
- Source-only candidate to write the unsigned 8x8 low product byte directly into MATH_Z and shorten the public return: exhaustive current-main CPU-model screen covers 65,536 operand pairs each in V1/V5 and checks product, carry, public inputs, stack and output sentinels; uniform 6-cycle paired improvement expected. Research include is not selected by the production builder; no shipped binaries or stable API changed.
- Archived-reference source/V5 hybrid preflight preserved PRG size and changed 11 bytes; 256 native x64sc old/new calls preserved public invariants. Non-carry flags volatile, native cycle timing not measured. Full current-main source, mixed-call, VICE and release qualification still required. docs/ISSUE39_V1V5_UMUL8_DIRECTOUT_RESEARCH_2026-10-13.md. Issue #39 remains OPEN.

2026-10-13 ISSUE39 UMUL32/READY COMPARABLE-INPUT AUDIT
- Verified current V1–V5 public UMUL32 and UMUL32_READY on the identical ordered 2,409-pair corpus per profile (24,090 CPU-model public entries). Complete 64-bit products, input preservation and carry passed. READY saves 22 cycles/pair in V1/V5; V2/V3/V4 show zero paired difference. Earlier published 2,409 vs 1,024-case means were not comparable. No implementation, public ABI, resident, ZP or REU change. Issue #39 remains open. See docs/ISSUE39_UMUL32_READY_PAIRED_AUDIT_2026-10-13.md and validation/review/ISSUE39_UMUL32_READY_PAIRED_AUDIT.json.

2026-10-13 ISSUE39 UMUL24 PR105/PR106 POSTMERGE MAIN VALIDATION
- PR #105 (V2/V3/V4 UMUL24 noncarry tail) merged as d1688725c8f9e7f35e6de4d36815d2a6d0265b40; postmerge main: Validate library #38402703856, Comparable unsigned #38402703783, Turbo32 #38402703796 — all SUCCESS.
- PR #106 (V1/V5 UMUL24 private tail-call) merged as 335185f3ad0233763d4aafdad91301f6261604b3; postmerge main: Validate library #38410138207, Comparable unsigned #38410137785, Turbo32 #38410137989 — all SUCCESS.
- Both releases retain their native x64sc proof, public ABI, normal zero-page and resident size. Publication metadata-only closeout; no executable, performance measurements or resident images changed; issue #39 remains OPEN.

2026-10-13 ISSUE39 V1V5 UMUL24 NATIVE SOURCE VALIDATION
- Pinned real x64sc old/new public UMUL24 and SMUL24 verified on V1/V5: 384 calls, identical products, preserved inputs, carry and sentinels; unchanged signed private executable. Native cycles were NOT measured. validation/review/ISSUE39_V1V5_UMUL24_TAILCALL_NATIVE_2026-10-13.json.

2026-10-13 ISSUE39 V1V5 UMUL24 PRIVATE CORE TAILCALL
- Source-integrated V1/V5 UMUL24 tail-call: -8 cycles on all 10,324 official pairs, 474.042329 -> 466.042329 cycles; V2–V4 unchanged. No additional resource footprint.
- Signed/mixed calls, relocated source, standalone publication, native VICE and checksum/package evidence validated; PR #106 and postmerge main CI PASS (see closeout above). docs/ISSUE39_V1V5_UMUL24_PRIVATE_TAILCALL_2026-10-13.md

2026-10-13 ISSUE39 UMUL24 NATIVE SOURCE RESIDENT VALIDATION
- Pinned real x64sc old/new public UMUL24 and SMUL24 verified on V2/V3/V4: 576 calls, identical products, preserved inputs, carry and sentinels; unchanged signed private executable. Native cycles were NOT measured. validation/review/ISSUE39_UMUL24_TAIL_NATIVE_2026-10-13.json.

2026-10-13 ISSUE39 UMUL24 NONCARRY FALLTHROUGH PRODUCTION
- V2/V3/V4 UMUL24 source direct return: 7,789/10,324 calls -3 cycles and 2,535 unchanged; mean 419.292135 cycles; 0 extra resident/ZP bytes. V1/V5 unchanged.
- Signed/mixed regression, standalone source, alternate maps, native VICE and package checked. PR #105 and postmerge main CI PASS (see closeout above). docs/ISSUE39_UMUL24_TAIL_FALLTHROUGH_2026-10-13.md

2026-10-13 ISSUE39 V2 UMUL8 SOURCE-RELEASE NATIVE VICE
- 128 actual x64sc old/new source-installed V2 UMUL8 public calls (64 identical operands per image), exact Q16/input/carry/stack/sentinel outputs. Non-carry status bits (N/Z/V) are explicitly volatile and their differences are recorded. No native cycle-timing assertion; six-cycle saving is from exhaustive same-input model. V2-only, no resource growth. See validation/review/ISSUE39_V2_UMUL8_DIRECTOUT_NATIVE.json. Issue #39 remains OPEN.

2026-10-13 ISSUE39 UMUL8 DIRECT OUTPUT SOURCE RELEASE
- V2 UMUL8 source-owned public direct output: -6 cycles on all 65,536 tested 8x8 inputs (78.494141 to 72.494141), zero ZP/resident growth, no change to V1/V3/V4/V5. Both source maps and complete public ABI regression pass. Native VICE pending. docs/ISSUE39_V2_UMUL8_DIRECT_OUTPUT_2026-10-13.md

2026-10-13 ISSUE39 INTEGER ROOTS POSTMERGE MAIN VALIDATION
- Integer roots PR #102 merged; main workflows Validate library #38389399637, Comparable unsigned #38389399688 and Turbo32 #38389399617 all SUCCESS on b179436082933d4edd80bca0256c11fc09d143be. No resident arithmetic, ABI, resource, size or cycles changed by this metadata closeout. Source/native checksums preserved; release status and user documentation synchronized, issue #39 still OPEN. docs/ISSUE39_INTEGER_ROOTS_SOURCE_RELEASE_2026-10-13.md

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
