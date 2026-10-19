# Operation-first C64 library: primary build and profile retirement

The stock-C64 builder is the **primary setup path**. A project selects only the
math operations it calls. It does **not** choose V1, V2, V3, V4 or V5 first.
The historical profiles remain available until the performance and hardware
migration acceptance gates below pass. This is a staged retirement, not a
removal of validated legacy binary images.

## Build your application-specific math library

```sh
make builder-list
cp examples/operation-first.json my_math.json
# Edit operations, budgets and objective in my_math.json
make builder CONFIG=my_math.json OUT=build_my_math
```

Expected output in `build_my_math/`:

- `math_selective.prg`: minimal linked C64 load image for selected operations
- `math_api.inc`: exported `MATH_*` call addresses for this specific image
- `selective_manifest.json`: exact source variants, placements, SHA-256,
  allocated RAM and zero-page resources

The example needs 1,318 total main RAM bytes and 2 zero-page bytes at the
standard memory placement (UMUL16 + UDIV16 + ISQRT16, balanced objective).
Memory placement and contents may change when operations or choices change;
consume the generated manifest rather than assuming fixed V1–V5 addresses.
The builder can enforce an application-specific memory map via configuration.

Use `python3 tools/math_builder.py --variants OP` to inspect certified
variants. `--pin OP=link:variant` is for advanced callers; the builder must
never silently substitute a source lacking matched-input correctness proof.
No project source analyser is needed. Use the generated include instead of
copying a resident profile's symbol addresses.

Existing V1 source-locked signed SDIV8 and SMOD8 exports now have per-call
public cycle provenance and retain exactly one 530-byte kernel and one
private zero-page byte when both APIs are selected. With the qualified
UMULDIV16 fusion, the current source-measured catalog is 40/56 APIs,
subject to new dedicated native and full-library CI.

## Workload-weighted speed selection (forty source-qualified APIs)

The `speed` objective supports project-level weighted selection for **forty**
individually qualified APIs: UMUL8, SMUL8, UMUL16, UMUL16_SHR8, SMUL16, SMUL16_SHR8, UMOD8, UDIV8,
ISQRT32, UMUL32, SMUL32, UMUL32_READY, SMUL32_READY, UMUL32_SHR16,
SMUL32_SHR16, UMUL24, SMUL24, UDIV16_SHL8, SDIV16_SHL8, URECIP16_Q16, UDIV32_16, UMOD32_16, UDIV32_32, UMOD32_32, SDIV32_32, SMOD32_32, UDIV24, UMOD24, UMOD16, DIST8_ACCURATE, ATAN2_8, UDIV16, ISQRT16, SDIV32_16, SMOD32_16, SDIV24 and SMOD24. Multiple operations **must**
each have a positive integer call count,
reflecting expected calls per game frame (no implicit equal-frequency guess).
For example:

```sh
python3 tools/math_builder.py --operation UMUL8 --operation UMUL16 \
  --objective speed --calls UMUL8=1000 --calls UMUL16=1 \
  --ram-budget 1400 --zp-budget 4 --build
```

Or supply the same names in a JSON `workload_calls` object. The builder
benchmarks each API's candidate sources on that API's **same fixed deterministic
input corpus** at the requested nominal memory placement, checks the
full candidate variant set and corpus hash, then minimizes the sum of
`calls × mean cycles` under **global** linked-code, scratch, RAM, ZP and
persistent-state constraints. The manifest contains per-operation corpus hashes,
source hashes, mean cycles, call counts and the resulting estimated weighted
CPU-model cycles. For larger selections the speed solver uses an **exact**
branch-and-bound search instead of enumerating the full Cartesian product.
Admissible cycle and resource lower bounds prune impossible or dominated
partial choices, but finalists still receive the original full aligned placement,
producer-sharing, call-exclusive ZP, scratch and persistent-state checks.
A reproducible regression compares the solver to exhaustive enumeration and
checks the original 16-operation mixed-speed frontier and independently
verifies the newly speed-qualified two-variant UDIV24/UMOD24 source corpus.
Benchmarks do **not** provide real hardware timing or prove
cycle invariance after physical link relocation; speed selection is therefore
an expected workload estimate, not exact total cycle prediction.

The signed8 `SMUL8` operation now offers a source-qualified **RAM/ROM-safe**
alternative: historical V1 SMC with four 511-byte table planes (~68 complete
public-call cycles) and a read-only two-table quarter-square kernel (~123
cycles). The second saves more than 1,100 bytes of RAM and needs no writable
code, but is deliberately slower. Automatic speed selection must keep
historical V1 whenever resource constraints permit; 0 ZP for both candidates.
The V1–V5 profiles and original tables remain available.

For ISQRT16, the builder now retains the original 38-byte square-table
kernel and 768 bytes of exact tables, while also offering a standalone 137-byte
zero-ZP, tableless radix-4 restoring kernel with 6 bytes of call-exclusive RAM
scratch. A single-operation size build takes only 175 bytes total main RAM
(including public I/O) at both tested code origins, compared with 1,056 bytes
for the fast table source at $8000 (page alignment included). On 384
identical full-domain input samples the full-public CPU-model calls average
about 65.10 cycles (table) versus 1,215.37 (tableless). The speed objective
chooses the fast source when RAM permits, and otherwise uses the compact
alternative without sacrificing the exact 16-bit result or the zero-ZP ABI.
Exhaustive 65,536-value CPU-model tests plus both layouts in native VICE
qualify the tableless source independently; physical C64 timing is not claimed.
A separate all-56 native integration gate tests **both** independent ISQRT16
source variants at two complete memory layouts ($2000 and $4321), yielding
384 correct combined-image public calls. The root variant alone is pinned
while the other 55 choices retain the original fully budgeted size selection.
This proves relocation and mixed-residency compatibility for root16, not
an exhaustive mixed invocation of every math operation.

`SDIV16_SHL8` has a historical V2 32/16 direct sign/magnitude option
(2,624 code bytes and 12 reserved ZP) alongside a 237-byte/0-ZP
portable exact restoring source. Same-input public Q24/R16/C and
busiest-frame math-model timings determine preference under real resource
budgets. Historic resident-only timings are not directly comparable.

The signed fixed Q8.8 scaled multiplication `SMUL16_SHR8` retains an
independent 184-byte/0-ZP restoring variant (6 scratch), and a source-linked
1,383-byte/0-ZP quarter-square variant (4 scratch) with exact Q24 output.
The quarter-square planes are currently replicated if SMUL16 and SHR8 are
both selected: sharing remains a separate measured future objective.

For SMUL16, a canonical quarter-square signed full32 producer is available
as a separate 1,351-code/table-byte, 4-scratch, zero-ZP Pareto alternative
to the original 161-byte, 6-scratch compact source. Automatic speed builds
select against identical signed32 public-call timings, not REU timings.
No global shared-table coalescing is claimed yet.

For URECIP16_Q16, three independently selectable stock-6510 variants have
exact public D16 -> Q24/C behavior and 0 ZP: 99-byte restoring (1 scratch),
448-byte historical-threshold gate with restoring fallback (1 scratch), and
1,544-byte exact Q24 small-denominator lookup plus indexed threshold
binary search (0 scratch). All preserve Q3/R, N/D and need no REU/SMC/INIT.
The threshold-only route improves mean cycles but worsens the rare slow call;
the builder must evaluate same-input full-call speed and physical budgets,
not claim profile speed parity on incompatible resident/REU timings. See
`RECIP16_THRESHOLD_STOCK_BUILDER.md`.

For UDIV16_SHL8, the operation-first builder now retains two selectable
implementations: a 129-byte/0-ZP portable restoring source and the source-linked
historical V2 split-tail 32/16 arithmetic kernel (2,368 bytes and 12
call-exclusive ZP). The latter stages `N16 << 8` directly without changing
caller operands and delivers the same complete Q24/R16/C contract. On 384
identical public-call operands its model mean is about 719 cycles against
1,777 portable; the auto speed objective chooses V2 only when RAM and ZP fit.
A 150-call/24-frame paired trace covers math CPU cycles, not physical PAL frames.

For SMUL24, the historical V2 $CA-biased kernel now exposes its
signed correction as another public entry from the **same** four quarter-square
tables and 512-byte executable code slot used by UMUL24. Both calls share
a single 24-ZP producer when selected together; the compiler must not
duplicate either the table planes or the code. The 227-byte zero-ZP
portable signed source remains available when memory constraints exclude
the historical fast donor. The new signed speed basis measures 512
identical full public signed 24x24->48 calls at both memory placements.
Use `make builder-speed SPEED_CONFIG=examples/operation-first-shared24-speed.json`.
The 24-frame paired test records per-call and peak-frame regressions.

For UMUL24, `link:v2-quarter-square` uses the original $CA-biased
four-table carry-neutral V2 arithmetic, reassembled into an independently
relocatable X/Y/Z48 public source. The speed objective compares it against
`link:compact-zerozp` on 512 identical full public calls and retains
its 24-ZP and writable-code requirements. Choose it with
`make builder-speed SPEED_CONFIG=examples/operation-first-umul24-speed.json`.
The 156-byte zero-ZP compact alternative remains available under constrained
RAM and ZP budgets.

For UDIV16, the newly linked canonical V2 size-fast kernel uses 0 ZP and
1,513 bytes RAM including the 32-byte public I/O window, while the existing
2-ZP biased kernel uses 355 B. On an identical 384-call public Q16/R16/C
CPU-model corpus, the biased kernel averages 162.729 cycles and the V2
zero-ZP kernel 177.836 cycles at $8000. The builder therefore keeps the
faster biased kernel when 2 ZP bytes fit, and supports 0 ZP for projects
that can allocate the larger V2 source. Both are independently VICE-tested
at two layouts. This is a resource migration, not a speed improvement.

For ATAN2_8, both signed-domain-correct sources use zero ZP. The compact
variant uses 800 B main RAM at $8000 and averages 44.417 CPU-model cycles
per public call; sum-fast uses 1,312 B and averages 40.927 cycles on the
same 384 signed-vector input pairs. All 65,536 signed-byte vectors were
separately proof-tested for identical outputs, and both source kernels
passed native VICE at two relocations. Resource-aware speed selection
uses sum-fast when tables fit and compact when RAM is constrained.

For the exact-table DIST8_ACCURATE source pair, the V1 0-ZP RAM-scratch
path is available at 802 B main RAM; the V2 two-ZP fast path uses 800 B
and averages 78.08 rather than 84.64 CPU-model cycles per call on 384
identical signed-byte inputs. Both retain the original shared 512-byte
major/minor tables and source-exhaustive correctness provenance.

For UMOD16, both 2-ZP biased and 0-ZP direct-chain variants have the
same 384-case public R16/C cycle basis. The 0-ZP direct path saves about
4.6% CPU-model cycles at an extra 716 RAM bytes. The builder retains the
294-byte biased source when the RAM budget is tight and the faster 1,010-byte
zero-ZP path when budgets allow. Existing native VICE tests qualify both.

For 24-bit unsigned division/modulo, both exported public entries share
an exact Q24/R24/C producer. With 3 ZP bytes and at least 1,493 main RAM
bytes the builder chooses the historical writable-code V2 Repose-fast
variant on the 384-case identical-input basis; at 0 ZP or below 1,493 B
it retains the 226-byte compact restoring implementation. Source hashes
include the canonical donor and relocator. The measured mean cycles are
CPU-model whole public calls and do not establish hardware cycles.

With 1,400 total RAM bytes and the two example APIs, the optimizer can use only
one quarter-square implementation. Heavy UMUL8 workloads select its fast
variant and compact UMUL16; reversing the call weights reverses that choice.
UMUL32 now compares **five** full64 source-linked candidates on the same
192-pair operand corpus: the 204-byte portable compact, 375-byte shared
six-operation core, 1,028-byte zero-ZP quarter-square (plus 1,022 table bytes),
and the historical V2 FAST31 native producer adapted to the public ABI.
FAST31 reserves 512 code-slot bytes and four 512-byte page-aligned table
slots, with 31 call-exclusive ZP bytes, zero ordinary scratch, writable code,
no stack-page reservation and no explicit initialization requirement. Page
padding is charged to RAM. The builder selects by the complete public-call
CPU-model mean only where all resource constraints permit it. The published
resident FAST31 record is **not** a directly comparable public-call timing.
Native VICE proof covers the linked public interface at two code layouts.

SMUL32 now also compares **four** signed full64 public-ABI implementations
on its own deterministic 192-pair signed operand corpus: compact 293-byte
source, 375-byte unified producer, and the independently source-linked signed
FAST31 (512 code-slot bytes, four 512-byte lookup slots, 31 ZP). The signed
FAST31 is a composition of the qualified unsigned V2 arithmetic producer
with upper-word signed corrections, **not** the separately recorded V2
692.825-cycle native signed kernel. Its full-call speed is measured separately.
The `link:fast31-shared-full64` candidate exports both signed and unsigned
public entries from a **single** code island, one V2 unsigned arithmetic
producer and four immutable page-aligned quarter-square table slots. When
selected for both operations, one 2,560-byte code/data image, 32-byte I/O,
and 31 call-exclusive ZP bytes replaces two separate images needing 5,152 B
RAM total (both figures at code base `$8000`). This is an additional
candidate, not an irreversible replacement: individually selected historical
FAST31 and zero-ZP compact variants remain available. The signed shared
entry pays the complete unsigned public call plus signed high-word correction.
The two public exports have distinct addresses and full CPU/native VICE
qualification; source and candidate-set hashes remain authenticated.

The physical FAST31 image additionally exports unsigned and signed
`SHR16` fixed-point 48-bit entries, and both original full64 entries are
reused as safe state-independent `READY` aliases. Pin
`link:fast31-shared-full64` for any selection of the six APIs to make the
linker coalesce them into one signed/unsigned six-operation producer, with no
additional tables or code-page allocation. The 512-byte code island and
2,592-byte main-RAM footprint are unchanged at `$8000` even when all six
operations are linked. The READY and SHR16 APIs now each have independently measured full public-call
CPU-model means: three source-certified candidates per API (compact zero-ZP,
shared six-entry unified zero-ZP, and shared FAST31 31-ZP). Signed and unsigned
measurements reuse their respective deterministic 192-input corpora but measure
READY and Q48 calls separately, including the SHR16 output adapter and return.
The global speed optimizer can now compare the four additional APIs with their
complete same-API cycle models, preserving shared code/table resource accounting.
As before, source-model means do not imply physical-C64 or post-link cycle invariance.
\nFor unsigned `UDIV32_16` and `UMOD32_16`, speed selection compares the
131-byte accumulator-remainder and 162-byte portable restoring shared
quotient/remainder kernels on an independent 384-input corpus, preserving
Q32, R16, C=1 on division by zero, C=0 on success, N/D inputs, caller SP
and zero ZP. The shared producer can be selected once for both operations;
measured performance is for complete public calls, not resident V1/V2 timing.

The optional `link:accum-unrolled-32` is a statically unrolled 32-round
zero-ZP quotient/remainder core with 1,771 bytes of executable code and
one ordinary scratch byte. It shares the complete producer when DIV and MOD
are both selected. Main RAM is 1,804 bytes including public I/O at `$8000`,
versus 164 bytes for the compact accumulator implementation. Automatic
speed selection uses matched 384-input full public-call timing, and will
prefer unrolled only if its actual measured cycles and project resources
justify it; the portable reference and compact zero-ZP sources remain
available. This is not the historical V2 663-cycle native ABI transplant.

The qualified `link:v2-sizefast-public` is now a fourth 32/16 public
quotient/remainder candidate: it links the historical V2 12-ZP native
high-word divider/16-step unrolled tail from its canonical source via two
relocated code islands plus a complete public I/O shim. The 2,368-byte packed
code image (including reserved island padding) plus the 32-byte public I/O
uses **2,400 B main RAM**, **12 ZP**, zero ordinary scratch, and stable
NMOS LAX/ANC undocumented opcodes. The 384-pair complete-public-call model
averages ~932.63 cycles at `$8000` (rather than the historic native-only
663.73-cycle record). The optimizer can choose among this source and the
three zero-ZP variants according to RAM, ZP and workload budgets. No public
input, carry or divide-by-zero semantics are changed; nested/interrupt use
of the same ZP workspace is not supported.

Unsigned 32/32 UDIV and UMOD now have the same independent
384-pair full-public-call speed corpus. UDIV compares the standalone
`link:zptail` (325+219 code bytes, 4 ZP) against the
`link:aligned-zerozp` (325+251 code bytes, 4 ordinary scratch RAM)
producer. UMOD initially has one specialized 250+225+21 code-byte,
zero-ZP implementation. Both measure full Q32/R32 outputs, C carry status
on divide-by-zero, preserved 32-bit N/D inputs, and CPU-model cycles
through RTS. A further selectable `link:v2-lowdivisor-hybrid` shares full Q32/R32/C
between DIV and MOD, dispatching D<65536 to the canonical V2 32/16 public
adapter and unrestricted D to the existing native-qualified four-ZP tail.
The source-hashed 2,496-byte compact image reserves 12 non-reentrant ZP bytes,
zero ordinary scratch, and 32 public I/O bytes. This is optional and is
compared as a complete public call on the same 384-pair corpus as the low-RAM
producers; fast narrow divisors do not imply a universal 32-bit speed win.
The producer is tested under native VICE at two RAM/ZP layouts. The source
benchmarks measure CPU-model cycles rather than physical C64 elapsed time.

The additional `link:shared-aligned-zerozp` exports the full public
Q32/R32 routine from the existing independently qualified aligned DIV32
source as both DIV and MOD. Its shared-producer identity makes the builder
emit a *single* 576-byte code image with four bytes of scratch and zero ZP
when both APIs select it: 612 B including the 32-byte public I/O area,
versus 1,108 B for two separate aligned DIV and specialized MOD images.
The dedicated MOD source and the 4-ZP zptail DIV source remain available.
Speed decisions use each API's independent public-call corpus, not native
historical speed numbers. The two public exports are deliberately aliases
of the same quotient+remainder calculation.

Unsupported APIs fail closed in `speed` mode rather than using historical
resident timing from incomparable benchmark corpora. Ordinary `balanced`,
`size` and `zp` plans remain fully available for all 56 APIs. These resource
objectives now also use exact branch-and-bound rather than expanding the
143,327,232-combination 56-operation Cartesian frontier. Safe unaligned
code and disjoint producer-sharing-component lower bounds prune partial
choices; every finalist retains the historical full aligned code placement,
shared physical producer deduplication, call-exclusive ZP and persistent
state budget accounting. Exhaustive-oracle regression checks constrained and
unconstrained selections with aligned and shared modules. This does not
extend measured speed coverage or replace resident V1–V5 profiles.

## Speed-first versus smallest-size install

`make builder` uses the example's `balanced` objective: choosing less RAM
and ZP may intentionally cost many cycles. It is not a promise to match the
fastest legacy source. `make builder-speed` instead uses
`examples/operation-first-speed.json` or your own `SPEED_CONFIG` with
positive calls-per-frame for every selected API; it fails closed for APIs
without authenticated full-call same-corpus speed records. The output is
still the same `math_selective.prg`, generated API include and manifest.
Neither mode loads all 56 routines unless you explicitly select them.

The exact [performance-parity acceptance policy](PERFORMANCE_PARITY_GATE.md)
records which slower alternatives are legitimate Pareto choices and which
untransplanted historical fast kernels block retirement. Preserve the
[biased quarter-square carry-offset technique](BIASED_QUARTERSQUARE_CARRY_OFFSETS.md)
as a reusable speed-kernel research option with immutable older sources and
an exhaustive algebraic regression test.

## Acceptance gates for retiring fixed profiles

1. Every one of 56 public APIs is independently source-linkable — **done**.
2. Multi-operation sharing, state lifetime, ABI, scratch ownership, RAM and
   ZP budgets receive deterministic CPU-model and native VICE qualification —
   **active**, including shared unsigned/signed 32-bit producers.
3. Historical high-speed V1–V5 and OptiSearch variants are imported only after
   source relocation and matched-input performance proof — **not complete**.
4. The builder optimizes a **whole operation set**, honoring workload weights,
   comparable cycles, shared tables/code/state, initializer cost, SMC, and REU
   requirements — **resource frontier active; global speed unfinished**.
5. Stock C64 release/API compatibility and native VICE independent validation
   pass for realistic mixed workloads; hardware-specific REU/Turbo/QS16 need
   qualified equivalents or explicit separate compatibility packages.
6. When all gates pass, archive V1–V5 as reference distributions; do not
   delete historical sources, benchmarks or qualified reproducibility records.

## Scope and limits

The current builder's executable backend targets the stock NMOS C64/6510.
Other planned targets (1541/1571/1581) have **no executable backend yet**.
Legacy V3/V4 REU accelerated math, Turbo16/Turbo32, and QS16 are not all
covered by the 56-operation modular baseline. Never infer performance parity
from an identical public operation name: compare code assembled from the
specific source variant on exactly the same input corpus and calling ABI.

## Complete 56-operation native integration smoke

For signed 24-bit division and modulo the selector now compares the
three already source/native-qualified shared producers (`link:portable-zerozp`,
`link:abs-qzero-guard`, `link:v3-signed-magnitude`) on one authenticated
512-case Q24/R24/C public-call corpus at both code origins. Both API exports
share the producer when they choose the same variant; source hashes,
resource budgets and the historical V3 SMC contract remain enforced. To
build without profiles:
`make builder-speed SPEED_CONFIG=examples/operation-first-signed24-speed.json`.

Signed unrestricted 32/32 DIV/MOD now retain both the 412-byte, 0-ZP,
9-byte-scratch restoring reference and the source-linked
`link:v2-hybrid-signed` magnitude producer. The latter occupies a single
2,880-byte executable image for both SDIV32_32 and SMOD32_32, using
12 call-exclusive ZP bytes and zero ordinary scratch. The signed public
shim normalizes and restores public inputs, computes signed Q32 and R32,
and uses the qualified V2 low-divisor / ZP-tail unrestricted unsigned core.
On an identical 384-case full-public CPU-model corpus, the hybrid averages
610.326 cycles at $8000 versus 3,177.286 for portable; at $7123 the
figures are 610.237 versus 3,170.797. The source-model speed selector
chooses the hybrid automatically when memory and ZP budgets permit; smaller
configurations retain the original compact producer. To install:
`make builder-speed SPEED_CONFIG=examples/operation-first-signed3232-speed.json`.
Source timing is not physical VIC-II-contended PAL frame timing.

The historical signed V2 32/16 magnitude producer is source-linked as
`link:v2-signed-magnitude` for both `SDIV32_16` and `SMOD32_16`, with
a single 2,880-byte code image, 12 call-exclusive ZP bytes, and no ordinary
scratch. The 260-byte / 0-ZP portable alternative remains available. The
`speed` objective compares 384 identical signed input pairs with the
full public Q32/R16/C ABI, while the mixed source-model frame test records
peak and average cycle changes for actual operation call sequences. To try it,
use `make builder-speed SPEED_CONFIG=examples/operation-first-signed32-speed.json`.
The historical V2 producer is not an REU accelerator and the original
V1–V5 binaries remain unchanged.

The stock C64 builder can emit all 56 operations as one linked PRG in a
16,640-byte code span at $2000, with 17,104 bytes of combined RAM and four
call-exclusive ZP bytes, sharing code and tables across 37 physical producers.
An independent two-map real x64sc test now links the complete operation set
at code origins $2000 and $4321, moves its harness to $1000 and buffers
outside executable code, and exercises all unsigned 8-, 16-, 24- and 32-bit
DIV/MOD public entry points, plus signed 8- and 16-bit DIV/MOD. There are
12 independently called APIs with 96 operand pairs each at both origins:
**2,304 linked native VICE calls**. The signed/24-bit validators additionally
verify negative/overflow input cases and preservation of public input/sentinel
bytes where applicable. This is a representative integration smoke check,
not a complete 56-export runtime oracle or physical timing claim.

A second two-map native VICE gate validates unsigned and signed UMUL/SMUL at
8, 16 and 24 bits from the same combined all-56 image, with 96 cases per
API and layout (**1,152 linked multiplication calls**). Its independent
oracles check exact products, preserved caller inputs, carry and sentinels.
Neither integration gate qualifies all 56 public calls under one interleaved
workload or replaces the historical source-specific standalone proofs.
