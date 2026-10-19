# Performance parity gate for retiring V1–V5 as the default setup

The operation-first builder is already the preferred **selection and linking**
path for a stock C64. It has independently linkable source for all 56 public
APIs, but 40 APIs now have authenticated, matched-public-call speed selection.
All 56 are eligible for exact RAM / ZP / balanced resource optimization.
Do not confuse **linkability** with **speed parity**.

## Which slower kernels are legitimate?

A slower source is worth keeping when it is **Pareto-relevant** under a real
constraint: less executable RAM, fewer zero-page bytes, lower table/REU
dependency, a smaller initialization burden, safer non-reentrancy/SMC, or
a different ABI with a verified adapter. Example: ISQRT16's 137-byte
tableless restoring source averages about 1,215 public-call model cycles,
versus about 65 for the faster square-table source, but avoids a large lookup
table. Both have a legitimate place; size mode may choose the former,
speed mode should choose the latter whenever its tables fit.

There is **no reason to market a universally dominated implementation as
a speed improvement**. If implementation B has equal/worse code, table,
ZP, scratch, initialization, CPU/hardware obligations, and is slower on
the same call corpus and worst-frame workload than implementation A,
B belongs only in a reproducible research/compatibility archive or behind
an explicit experimental pin, not in the automatic speed frontier.

The currently shipped example `make builder` runs a **balanced
memory-resource** objective; it is not a fastest-routine installer.
Use `make builder-speed` and provide all operation call frequencies,
RAM/ZP budgets and, where relevant, a real frame schedule. Missing speed
measurements must fail closed and produce a clear migration task.

## Why old V1–V5 results may look much faster

- Historical *native* kernels may consume registers/ZP directly or rely on
  READY state. New independently linkable routines have full public operand
  staging, input preservation, carry/result mapping and RTS/JSR overhead.
- Old resident kernels often use expensive precomputed tables, REU, writable
  zero-page code or private stack-page state. RAM/ZP-constrained fallbacks
  cannot match them without reserving those resources.
- Some older source kernels have **not** been transplanted yet; a portable,
  correctness-first implementation was migrated to complete the 56-API
  catalog. This is an unfinished performance stage, not a parity claim.
- Historical benchmark corpora and cycle bases differ. Never conclude an
  exact speed win/loss by directly subtracting a resident-profile mean
  from an independently sampled builder full-call mean.
- Optimizing weighted **mean** cycles is not equivalent to minimizing
  cycles in the busiest PAL frame. A small but adversarial input class can
  make an apparently faster kernel worse for a game or demo.

## Non-negotiable acceptance rules

1. For each of 56 APIs, map the fastest **source-reproducible** V1–V5,
   OptiSearch and separately qualified research kernels to candidate
   operation-first source variants. Preserve source hashes and old
   reference images. Do not require a project-source analyzer or a named
   legacy profile.
2. When porting, preserve full `MATH_*` public semantics including input
   preservation, carry/zero-divisor behavior, all result bytes, SP, SMC
   ownership and initialization. Reserve code, table, private ZP, RAM,
   stack-page/REU and shared producer/state resources precisely.
3. Run the **same input corpus per API and ABI** for all candidate sources,
   with complete JSR-through-RTS cycles, both relocations and authentic
   native VICE correctness. Preserve mean, max, p95 and slow-call tail,
   not just a single headline average.
4. Evaluate complete multi-operation workloads: explicit calls/frame,
   shared tables and producers, alignment, initialization amortization,
   worst/busiest frame, VIC-II badlines, IRQ/SID/REU contention where
   supported by actual native/hardware traces. The current CPU-model
   mixed-frame scorer is useful but is not physical frame timing.
5. **Never silently replace** the fastest known qualified source with a
   slower one in speed mode if the faster option is feasible. Resource
   objectives may choose slow compact variants, but the manifest and
   documentation must say why.
6. Keep explicit selectable Pareto alternatives and reproducible
   historical reference builds. Archive fixed-profile defaults only
   once stock C64 workload-speed parity and relevant hardware-feature
   replacements or documented separate packages are qualified.

The original $CA-biased V2 UMUL24 source is now also importable as a
source-linked, writable-code speed candidate. It requires 24 ZP bytes and
page-aligned lookup tables, while the 156-byte compact zero-ZP implementation
remains a feasible size fallback. See
`V2_UMUL24_QUARTERSQUARE_TRANSPLANT.md`.

- The signed SMUL24 V2 adapter now shares the original $CA-biased
  unsigned V2 quarter-square product and all four table planes, with the
  signed high-word correction reusing the exact same 24 ZP bytes. The
  independent 227-byte / 0-ZP compact source remains a selectable alternative.
  See [shared signed/unsigned 24-bit multiplication](SMUL24_SHARED_V2_BUILDER.md).
  
The historical V2 32/16 source is independently linkable for `UDIV16_SHL8`.
It stages the shifted 16-bit numerator in the native private state while
preserving public operands, Q24/R16 and carry. At the complete-call ABI it
averages approximately 719 versus 1,777 CPU-model cycles on 384 identical
inputs. The original 129-byte/0-ZP portable implementation remains for
resource-constrained projects; the V2 path needs 2,368 bytes and 12 ZP.
Measured 24-frame math budgets do not imply VIC/IRQ/PAL frame qualification.

The new `URECIP16_Q16` stock C64 frontier offers three independently
source-linked no-REU choices: 99-byte compact restoring, 448-byte
V3/V4-threshold-inspired fast gate with exact restoring fallback, and a
1,544-byte exact Q24 lookup/binary-threshold producer. All use 0 ZP.
The first threshold gate is faster on mean but **not on maximum latency**;
only the source-matched corpus, complete all-divisor public source test,
native VICE and busiest-frame gate may justify promotion. This is not a
transplant of the V3/V4 REU resident binary and does not yet establish
REU-resident hardware timing parity. See `RECIP16_THRESHOLD_STOCK_BUILDER.md`.

The signed shifted-16 API now exposes a canonical V2-fast unsigned 32/16
magnitude producer with a public signed Q24/R16/C adapter. It requires
2,624 code bytes and 12 exclusive ZP bytes; the compact 237-byte
portable zero-ZP version remains selectable. Qualification is against
identical inputs and full public-call costs, not historical resident cycles.

A full signed16x16->32 quarter-square stock-C64 public kernel is now an
explicit 1,351-byte/0-ZP choice alongside 161-byte compact zero-ZP.
The faster variant's exact speed and worst-case latency are certified with
identical input pairs, a busy-math-frame replay, and two-map native VICE,
not only resident-profile timing.

Signed Q8.8 `SMUL16_SHR8` reuses the original unsigned 16x16 quarter-square
planes, exact signed32 wrapper and a bounded 32-byte Q24 output slice. Its
1,383-byte/zero-ZP fast and 184-byte/zero-ZP compact paths require
matched signed public calls and busiest-frame comparison, not unwrapped
resident-profile timing. Table sharing with SMUL16 is future work.

The signed8 `SMUL8` Pareto frontier now has source-matched public-cycle
measurements for original V1 writable SMC (roughly 68 cycles) and the
stock-C64 read-only two-plane QS implementation (roughly 123 cycles).
The read-only source saves over 1,100 bytes, but is **not** a speed win:
speed mode should retain V1 when its RAM and writable-code requirements
are feasible. Separate native VICE and package qualification are required.

The existing historical V1 signed8 division/modulo producer now exposes
authenticated identical-input Q8/R8/C CPU-model source timings for both
public names. Its one 530-byte physical image and one private ZP byte
remain shared when both APIs are selected. No new slower kernel is used.

## Active migration priority after PRs #293–#296

- The historical V3 signed24 kernel is available and CPU/native qualified,
  including mixed synthetic worst-frame scoring.
- The shared historical V2 signed 32/16 magnitude producer from PR #295
  is now exposed for both `SDIV32_16` and `SMOD32_16` as a shared
  source-linked operation-first variant. A new identical-corpus 384-call
  speed basis and mixed busy-frame screen prevent the builder from
  presenting a compact memory fallback as a speed upgrade. The V2 donor
  requires 2,880 code bytes / 12 ZP; the independently selectable compact
  source uses 260 code bytes / 0 ZP. Preserve both Pareto points.
- Signed 24-bit DIV/MOD now has automatic authenticated full-call speed
  selection across the historical V3 magnitude source, a compact zero-ZP
  source and the quotient-zero-optimized zero-ZP source. All remain
  available as Pareto alternatives under different budgets.
- Audit remaining full-width DIV/MOD and full 32-bit signed/unsigned multiplication
  historical producers, including FAST31 / READY / SHR16 and shared
  table alternatives; import only qualified source-linked winners.
- Both signed32/32 public aliases now have a second independently linked
  variant using V2 unsigned magnitude arithmetic under a sign-normalizing
  wrapper. The matched public-call CPU-model speed basis is about 610
  versus 3,177 cycles with the donor feasible (2,880 code/12 ZP), retaining
  a genuine 412-code/0-ZP compact option. This is not a reproduction of
  the historical 514-cycle V2 resident result, and mixed physical frame
  qualification remains a separate task.
- Preserve the [biased quarter-square carry-offset identity]
  (BIASED_QUARTERSQUARE_CARRY_OFFSETS.md) as a later 16-bit high-speed
  donor opportunity. Its historical standalone register ABI timing is
  **not** full public-call performance.

The builder's original fixed V1–V5 outputs and REU/Turbo/QS16 special
surfaces remain supported **as compatibility and performance baselines**,
not the required first step for a new project.
