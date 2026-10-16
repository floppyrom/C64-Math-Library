# Builder refactor: operation-first selection (phase 1)

The future **C64 Math Library Builder** will replace user-facing V1–V5 profile
selection with a choice of mathematical **operations**, resource constraints,
and optimization goals. Historical images remain available as regression
oracles until the new linker meets the same correctness and timing contracts.

**An experimental selective linker now supports fourteen operations: UMUL8, UMUL16, UDIV8, UDIV16, UMOD16, UDIV32_32, UMOD32_32, ATAN2_8, ISQRT16, DIST8_FAST, DIST8_ACCURATE, SIN8, COS8 and SINCOS8.**
It uses standalone relocatable sources or newly developed compact algorithms,
not the historical full-profile images or extracted resident mirrors. New
module combinations remain release-unqualified until all CI gates pass. Other operations
remain selection-plan-only until their own source contracts pass qualification.
A mirror extracted from a resident image is not automatically a self-contained
or relocatable module.

## Try it

Browse the 56 stable operations without selecting a fixed profile:

```sh
python3 tools/math_builder.py --list
python3 tools/math_builder.py --list-linkable
```

Create a plan for a new project:

```sh
python3 tools/math_builder.py \
  --operation UMUL16 --operation ATAN2_8 --operation ISQRT16 \
  --objective balanced --zp-budget 20 --ram-budget 4096 \
  --out build_selective/selection_manifest.json
```

Or run interactively (a human-readable list grouped by operation).
For experienced users, an equivalent JSON configuration:

```json
{
  "target": "c64",
  "operations": ["UMUL16", "ATAN2_8", "ISQRT16"],
  "objective": "balanced",
  "constraints": {
    "max_zp_bytes": 20,
    "max_ram_bytes": 4096
  },
  "pins": {}
}
```

Use with `--config selection.json`. Both short `UMUL16`, historical
`MATH_UMUL16`, and typed `mul_u16_u16_u32` names resolve to the same
operation. Use `--preview` to print without writing.

Inspect the available *source* variants (with original provenance, SHA and
qualification status) using:

```sh
python3 tools/math_builder.py --variants UMUL16
```

An advanced selection can copy a content-derived variant ID from
`--variants UMUL16` and pin it with `--pin MATH_UMUL16=mirror:<sha-prefix>`.
Legacy source provenance remains in metadata but is **not a profile choice**.
A pin is a source preference for future linker integration, not proof of
linkability.

The plan records every source choice and explicitly sets:
`status=planning_only_not_a_loadable_binary`,
`unresolved_dependencies=true`, and `linker_status=not_implemented`.
No code size, cycle total or zero-page total is guessed by adding unrelated
routine figures. Standalone timing corpora may differ substantially.

## First compact build (experimental)

Generate a PRG containing only unsigned 16-bit division and/or remainder:

```sh
python3 tools/math_builder.py --operation UDIV16 --operation UMOD16 \
  --objective size --zp-budget 2 --ram-budget 1000 --build
```

Output in `build_selective/`:

- `math_selective.prg`: **585 code bytes**, plus the usual two-byte PRG load header.
- `math_api.inc`: only the selected callable symbols, plus shared I/O symbols.
- `selective_manifest.json`: entry addresses, source SHA, actual segments and RAM/ZP ownership.

The pair shares **2 ZP scratch bytes** (sequential, nonreentrant calls), a
**32-byte caller-owned I/O block**, and has a **617-byte total RAM claim**.
No other math operations, global lookup tables or fixed resident code are
included. For a one-routine 0-ZP modulo build, select:

```sh
python3 tools/math_builder.py --operation UMOD16 --objective zp \
  --zp-budget 0 --ram-budget 1100 --build
```

This selects the independently relocatable direct-chain engine: 976 code/table
bytes + 2 ordinary scratch bytes + 32 caller I/O bytes. It is slower than the
biased modulo source on the prior paired corpus, but uses no ZP. Pin explicitly
via `--pin UMOD16=link:direct-zerozp` or `--pin UMOD16=link:biased`.

The linker also supports full-width 32/32 division and remainder, reusing
the existing portable OptiSearch-derived C64 kernels:

```sh
python3 tools/math_builder.py --operation UDIV32_32 --operation UMOD32_32 \
  --objective size --zp-budget 4 --ram-budget 1200 --build
```

The size-oriented version selects the 544-byte UDIV32 ZP-tail and 496-byte
zero-ZP UMOD32: **1,040 code bytes, 4 shared ZP bytes, 4 ordinary scratch
bytes, and 32 public I/O bytes** (1,076 claimed RAM bytes). With
`--zp-budget 0`, it selects the 576-byte zero-ZP UDIV32 alternative
instead, for **1,072 code bytes and 1,108 total RAM bytes**. The 32-bit
operands and outputs occupy the full four-byte public I/O groups. Divisors
of zero set carry and return zero results, while modulo preserves Q.

**Performance caveat:** the portable 32-bit kernels can be slower than the
resident implementations, especially for certain small-divisor workloads.
These are the first *linkable* choices, not proven universal speed winners.
For most operation combinations, the optimizer enforces global RAM/ZP
constraints without inventing speed rankings from unrelated corpora.
The only measured automatic speed path currently available is the
**UMUL8-only** comparison described below; all other speed-ranking
requests remain guarded until comparable per-operation workload data exist.

Get a **measured**, assembled footprint without retaining build output:

```sh
python3 tools/math_builder.py --operation UDIV16 --operation UMOD16 \
  --zp-budget 2 --ram-budget 1000 --measure
```

The interactive wizard groups all 56 operations with readable descriptions,
shows which are currently linkable, and accepts numbers, ranges or names.

### Historical optimized ISQRT16 lookup source (experimental)

`MATH_ISQRT16` is the first selective migration of a **historical optimized
resident implementation**, rather than a new compact baseline. The independent
`link:square-table` source preserves the V1/V2/V5 descending square-table
comparison kernel with its resident entry trampoline removed. Tables are
generated mathematically, not copied from resident RAM:

- `SQ_LO[r]` and `SQ_HI[r]` are the low/high bytes of `r*r`, for 256 roots.
- `SEED[h] = isqrt((h << 8) | 255)` is the maximum candidate for each high byte.
- The 38-byte kernel scans downward until the table square is no greater than
  the 16-bit input. Results are exact for every `0..65535` value.
- No ZP, stack-page workspace, REU, writable code or initialization is needed.
  The 768 bytes of tables must be page-aligned; real padding is charged to RAM.
- Public input: unsigned 16-bit `MATH_N` (`math_io + 16`). Public output:
  unsigned 16-bit `MATH_Z` (`math_io + 8`). Input retained, carry clear.
- At code origin `$8000`, its linked image is 1024 bytes (38 code,
  768 tables, 218 padding), plus the 32-byte common caller-owned I/O block:
  **1056 total RAM bytes and zero ZP**. Other origins may require less padding.

```sh
python3 tools/math_builder.py --operation ISQRT16 --objective size \
  --zp-budget 0 --ram-budget 1056 --measure
python3 tools/math_builder.py --operation ISQRT16 \
  --pin ISQRT16=link:square-table --build
```

An exhaustive two-relocation CPU image test and independent two-relocation
native x64sc harness are included in the builder gate. No performance ranking
against the historical corpus is asserted until equivalent benchmark inputs and
conditions are checked. Until CI qualification passes, this remains experimental.
Mixed builds with multiple page-aligned modules link correctly but currently use
deterministic conservative ordering; **multi-aligned ordering is not globally
padding-optimal yet**. The optimized ISQRT16 migration is not evidence that the
other 43 operations or unported high-performance variants are link-ready.

### Historical V1/V2 accurate-distance two-table lookup (experimental)

`MATH_DIST8_ACCURATE` has two independent source-exact optimized variants:
`link:v1-ram-tables` (66-byte kernel, **zero ZP**, two owned RAM scratch
bytes) and `link:v2-zp-tables` (58-byte kernel, **two ZP**,
zero ordinary RAM scratch). These retain the shipped lookup-table algorithm,
not the faster but less accurate `DIST8_FAST` approximation.

Both variants share **one immutable 512-byte aligned pair** of table pages
at the generated address, with exact byte-for-byte V1–V5 release-image
provenance from `$9A00` and `$9B00`. This is true even for mixed
trig/distance builds: one 256-byte sine page, one 512-byte accurate-distance
pair, with all padding charged to the finished image.

The contract preserves signed X/Y low input bytes, absolute -128 behaviour,
MATH_Z low-byte output and clear carry, and does not alter neighbouring
I/O bytes. The exact computation is
`(MAJOR[max(abs(x),abs(y))] + MINOR[min(abs(x),abs(y))]) & 255`.
Exhaustive **65,536 x/y pairs at each of two relocations** for *each*
variant and independent native x64sc checks are required for promotion.

```sh
python3 tools/math_builder.py --operation DIST8_ACCURATE \
  --pin DIST8_ACCURATE=link:v1-ram-tables --zp-budget 0 \
  --ram-budget 802 --build
python3 tools/math_builder.py --operation DIST8_ACCURATE \
  --pin DIST8_ACCURATE=link:v2-zp-tables --zp-budget 2 \
  --ram-budget 800 --build
```

The resource figures include the 32-byte public I/O reservation and
page-alignment padding at the default `$8000` code origin. V2's ZP
work area must not conflict with caller-reserved zero page.

### Historical V1–V5 shared trigonometric table (experimental)

Three more independently selectable public operations preserve the original
8-bit sine lookup and phase-shift kernels: `SIN8` (11 bytes), `COS8`
(15 bytes), and `SINCOS8` (22 bytes). All five shipped V1–V5 resident
PRGs contain **identical exact lookup bytes** at `$9400`; the source
generator retains their exact 256-byte signed sine table, not host-side
floating-point approximations. Sine is `table[phase]`, cosine is
`table[(phase+64)&255]`, and SINCOS outputs both.

These routines require **no ZP or private RAM**. One common lookup page is
shared even if all three functions are selected: **48 executable bytes plus
256 table bytes**, not 768 bytes of duplicate lookup tables. The table is
page-aligned and its real padding is charged to the emitted image.
At `$8000`, a combined three-operation build uses 512 image bytes,
including 208 alignment bytes, and 32 caller-owned I/O bytes (544 RAM total).
All inputs are retained, carry clears, and low-byte results are written to
`MATH_Z` (low/second byte for SINCOS); upper unused bytes are unchanged.

```sh
python3 tools/math_builder.py --operation SIN8 --operation COS8 \
  --operation SINCOS8 --zp-budget 0 --ram-budget 544 --build
```

CI verifies byte-for-byte table identity against **all five shipped PRGs**,
all 256 phase values per operation at two relocations, actual mixed linking
with ATAN2 and ISQRT16 aligned tables, and independent native x64sc execution
of each source-linked entry point at two RAM layouts. Selection remains
operation-first: a one-routine request exports only that operation, although
it necessarily includes the one 256-byte lookup page.

### Historical V1 fast unsigned 8-bit division (experimental)

`MATH_UDIV8` now offers the `link:v1-resident-fast` source choice:
the original V1 125-instruction high-performance quotient/remainder branch
chain, with its external trampoline removed. It is **294 bytes of executable
code**, needs one explicitly reserved ZP byte and no ordinary scratch RAM,
tables, initialization or REU. Its entry is at code origin + 8 because the
V1 divide-by-zero return stub precedes it. The linker emits the correct
entry label rather than assuming every module starts at its API address.

Public inputs are the low bytes of `MATH_N` and `MATH_D`, retained on
return. Low-byte `MATH_Q` and `MATH_R` receive the quotient and remainder.
`D=0` yields `Q=R=0` and carry set; otherwise carry is clear. Upper I/O
bytes are not modified. At `$8000`, memory requirements are **294 code +
32 common I/O = 326 bytes**, plus **one zero-page byte**.

```sh
python3 tools/math_builder.py --operation UDIV8 \
  --pin UDIV8=link:v1-resident-fast --zp-budget 1 \
  --ram-budget 326 --build
```

The exhaustive CPU test exercises all **65,536 unsigned numerator/divisor
pairs at each of two RAM/ZP relocations**, including division-by-zero,
carry and unchanged ABI bytes. Separate native x64sc tests exercise two
relocations, comparing quotient, remainder, carry and preserved operands.
This is an original optimized historical implementation, **not** a newly
introduced slower compact alternative. Other profiles' UDIV8 algorithms
and their cycle tradeoffs remain to be migrated and benchmarked on
comparable workloads.

### Historical optimized DIST8_FAST source (experimental)

`MATH_DIST8_FAST` adds an independently linkable V1 resident fast-distance
approximation, `link:resident-approx`. It preserves the shipped source
algorithm without the resident entry trampoline: for signed 8-bit X and Y,
compute `a=abs(X)`, `b=abs(Y)`, and return
`(max(a,b) + floor(min(a,b)/2)) & 255`. The unusual `-128`
case yields magnitude 128 and all arithmetic wraps to unsigned 8-bit output.
This is **not** the more expensive `DIST8_ACCURATE` lookup-table operation.

It uses **61 code bytes, zero ZP, two owned ordinary RAM scratch bytes**,
and the shared 32-byte public I/O block: **95 RAM bytes total** without
alignment padding. The input low bytes of `MATH_X` and `MATH_Y` are
preserved, the low byte of `MATH_Z` is written, the high byte is unchanged,
and carry is clear on return. All 65,536 signed input-byte pairs are checked
at each of two relocations by the CPU-model test, with a separate native VICE
harness at both relocations.

```sh
python3 tools/math_builder.py --operation DIST8_FAST --zp-budget 0 \
  --ram-budget 95 --pin DIST8_FAST=link:resident-approx --build
```

The variant preserves the *historical operation semantics*; performance
ranking against V1/V2/V3/V4/V5 needs a matched-input benchmark corpus.

### Quarter-square fast UMUL8 (experimental source alternative)

UMUL8 now has **two** explicitly selectable kernels, sharing the same
`MATH_X` / `MATH_Y` 8-bit unsigned input and `MATH_Z` 16-bit output
contract. Both preserve operands and return with carry clear:

| Variant pin | Code bytes | Generated table bytes | ZP | Ordinary scratch | Claimed RAM including 32-byte I/O |
|---|---:|---:|---:|---:|---:|
| `link:compact-zerozp` | 60 | 0 | 0 | 3 | 95 |
| `link:quarter-square` | 73 | 1,022 | 0 | 2 | 1,129 |

The new quarter-square kernel computes
`Q(x+y) - Q(abs(x-y))`, where `Q(n)=floor(n*n/4)`.
Its tables contain 511 two-byte entries, generated reproducibly from
the integer formula. The linker emits them as two independent 511-byte
planes; no full-library profile tables or initialization dependency are
copied. Table and kernel bytes, private scratch and public I/O are all
charged to the actual RAM budget.

```sh
python3 tools/math_builder.py --operation UMUL8 \
  --pin UMUL8=link:quarter-square --zp-budget 0 --ram-budget 1129 --measure
```

Automatic **size** selection continues to prefer the compact module.
For a **UMUL8-only** build, `--objective speed` now performs a same-corpus
6502 CPU-model measurement for *both* source variants at the requested
memory origin, including instruction/page-crossing penalties. It picks the
fastest feasible version under the actual RAM/ZP constraints; if 1,129
RAM bytes are unavailable, the 95-byte compact variant remains a valid
fallback. The manifest stores the source hashes, 1,000-pair deterministic
corpus fingerprint, average modeled cycles and origin used.

```sh
python3 tools/math_builder.py --operation UMUL8 --objective speed \
  --ram-budget 1129 --zp-budget 0 --measure
```

**Scope:** this is source-assembled *CPU-model* evidence, not a measured
real-C64 hardware or raster-contended wall-clock performance claim. The
new option is intentionally restricted to UMUL8-only selections.
Requests to auto-rank other operations, or mixed sets lacking verified
comparable workload and cycle data, still fail closed. Expert pins
remain available independently of this automatic objective.

### Compact multiplication: portable zero-ZP UMUL8

The builder also offers `MATH_UMUL8` via `link:compact-zerozp`,
a **60-byte 8×8→16** shift/add module using **0 ZP and 3 ordinary
scratch bytes**. Including shared I/O it requires **95 RAM bytes**.
The low bytes of `MATH_X` and `MATH_Y` supply unsigned operands;
only the low 16 bits of `MATH_Z` are part of the output contract.

```sh
python3 tools/math_builder.py --operation UMUL8 --zp-budget 0 \
  --ram-budget 95 --build
```

The public multiply ABI requires **carry clear on return**, which both
UMUL8 and UMUL16 explicitly enforce. Both are compact algorithmic
baselines; they are not presented as faster than the published
table-accelerated alternatives. Exhaustive UMUL8 input-pair and
mixed UMUL8/UMUL16 scratch/carry tests are in the builder gate.

### Compact multiplication: portable zero-ZP UMUL16

A new `link:compact-zerozp` implementation provides unsigned 16×16→32
multiplication via a small shift/add kernel. It uses **108 bytes of code,
zero ZP, six caller-reserved ordinary RAM scratch bytes and 32 bytes
of shared public I/O**; the exact total claim is **146 RAM bytes**.
`MATH_X` and `MATH_Y` hold the 16-bit operands, and the 32-bit result
appears in `MATH_Z`. Inputs are preserved. The kernel uses documented
NMOS 6502 instructions and requires CLD.

```sh
python3 tools/math_builder.py --operation UMUL16 \
  --zp-budget 0 --ram-budget 146 --measure
python3 tools/math_builder.py --operation UMUL16 \
  --zp-budget 0 --ram-budget 146 --build
```

This is an **ultracompact baseline, not a faster replacement** for the
published large-table UMUL16 kernels. Those remain catalogued as sources,
but their scratch ownership, special input contracts, self-modifying ZP
code and table dependencies must be qualified before selectable linking.

ATAN2 code and tables may be placed *between* ordinary arithmetic
modules: a 256-residue dynamic program finds the minimum possible
page-alignment padding without factorial permutations. For example,
a UMUL16 + ATAN2 compact + UDIV16 combination occupies 1,091 bytes of
PRG payload including 54 padding bytes, 6 RAM scratch bytes and 2 ZP
bytes (1,129 total RAM bytes, including 32 public I/O bytes).

### ATAN2: source/table-aware linking

ATAN2 now provides two selectable, independently published algorithms.
The linker assembles the canonical kernel and regenerates the exact lookup
tables from `routines/atan2/tables.py`; it does **not** copy old resident
images or accidentally leave out tables.

| Variant pin | Executable | Lookup data | ZP | Example PRG payload at $8000 |
|---|---:|---:|---:|---:|
| `link:compact` | 94 B | 512 B | 0 | 768 B including page padding |
| `link:sum-fast` | 85 B | 1024 B | 0 | 1280 B including page padding |

Both use `MATH_X` and `MATH_Y` low bytes as signed 8-bit operands,
write phase to `MATH_Z` low byte and return it in A; C is clear. Tables
must start on 256-byte boundaries, and the linker **charges alignment padding
against the actual RAM budget and PRG length** rather than reporting only
the sum of occupied code/table bytes. These variants have the same established
65,536-vector numerical output contract (maximum error one phase unit).

```sh
python3 tools/math_builder.py --operation ATAN2_8 \
  --pin ATAN2_8=link:sum-fast --zp-budget 0 --ram-budget 1400 --build
```

This builds only the fast algorithm and its four pages, with no other math
operations. To minimize footprint, omit the pin: the size objective chooses
`link:compact`. An exact-assembly check, including padding, is available with
`--measure`.

A JSON configuration can specify a custom, nonoverlapping memory map:

```json
{
  "operations": ["UDIV16", "UMOD16"],
  "objective": "size",
  "constraints": {"max_zp_bytes": 2, "max_ram_bytes": 1000},
  "memory": {
    "code_base": "$7123", "math_io": "$C040", "zp_base": "$60",
    "reserved": [{"name": "loader", "start": "$2000", "end": "$2FFF"}],
    "zp_reserved": [{"name": "irq", "start": "$02", "end": "$4F"}]
  }
}
```

The default code origin is `$8000`, public I/O at `$C000-$C01F`, and
shared scratch at `$50`–`$51` when needed. ROM underlay, I/O address
ranges, system stack, zero-page processor ports, address overflow, and
colliding source/data allocations and caller-reserved RAM/ZP ranges are rejected. The public ABI preserves
N/D. Divide-by-zero sets C, clears Q/R for UDIV16; UMOD16 clears R while
preserving the caller's Q. `CLD` is required before calls.

**No broader optimized-variant claims yet:** fixed source variants and record
kernels with unrelated performance corpora are shown in the inventory but
cannot be silently selected for a compact build. An unsupported routine or
unsupported variant pin makes `--build` fail instead of loading 56 routines.

The compact linker is intentionally marked experimental pending native
VICE qualification. Arithmetic PRGs have a native linked-image test gate;
ATAN2 compact/fast adds full-domain CPU-model and alternate relocation/mixed
ABI tests. Hardware-native ATAN2 qualification is now included in the checksum-pinned
x64sc CI gate (384 signed-vector checks, two algorithms/two RAM maps); it must
pass before the experimental implementation is marked qualified. The assembly
source and the table generator are each SHA-locked in the selection manifest.

## Resource-frontier pruning and reproducibility

Automatic selection now prunes **resource-dominated** source variants before
exploring combinations, but only **within equivalent layout classes**: a
candidate can be discarded when another with compatible alignment geometry
uses no more code/table bytes, no more ZP, and no more ordinary scratch memory.
This reduces wasted combination searches as the certified variant catalog
grows. It does **not** filter the advanced variant inventory or block pinned
choices; for example, explicitly requesting ATAN2's larger sum-fast
implementation remains supported.

This is the **resource** frontier, not a claim of cycle-optimality. A generalized
speed/Pareto optimizer still requires separately certified comparable
per-operation cycle measurements and workload weights. The implemented
single-operation UMUL8 speed selector measures both alternatives directly
on identical inputs; it does not extrapolate that comparison across
unrelated operations.

A selective build stages its PRG, symbol include and manifest in a temporary
output directory before publishing. A staged-write failure leaves any existing
completed build unchanged, and the manifest is published last as a completion
marker. The three separate files are not a single filesystem transaction.

Every generated selective binary manifest now records SHA-256 of the active
builder, linker, ATAN2 emitter and 6502 assembler alongside individual
algorithm sources and generated-table dependencies. Together with the
selected source IDs, memory map, PRG SHA and build constraints, this allows
precise reproduction and auditing of experimental images.

## Target backends and portability boundary

The versioned `math-selection-plan-v2` manifest and operation catalog are
target-independent: developers can describe the
same mathematical requirements for `c64`, `1541`, `1571` and `1581`
without choosing a historical library profile.

```sh
python3 tools/math_builder.py --target 1541 --operation UMUL8 \
  --objective size --zp-budget 8 --ram-budget 512 --preview
```

**This produces a planning manifest only.** The first experimental linkable
modules and their current memory ownership contracts are C64-specific.
A `--target 1541`, `1571` or `1581` request with `--build` or
`--measure` fails explicitly; it does not secretly reuse the C64's
`$C000` I/O buffer or claim that C64 output is drive-safe. Target
capabilities and link-readiness are separate fields in the manifest. Each
future backend will require its own code/data/ZP reservations, calling
conventions, RAM residency assumptions and device-specific correctness
qualification.

This describes general-purpose device-side arithmetic only. It does not
introduce any target-specific binary, bundled firmware or experimental
hardware claims.

## Direction and acceptance criteria

1. **Inventory (implemented).** Index all 56 stable operations from the profile-independent
   `routines/PUBLIC_OPERATIONS.csv`, while indexing variants via
   `routines/SOURCE_CATALOG.csv`, retaining the current source, hash,
   provenance and validation distinctions. Offer interactive/JSON selection,
   variant inspection, pins and strict parameter validation. Preserve existing
   building and publication paths.
2. **Certified linkable module contracts.** Add explicit relocations,
   public input/output ABI, 6502 legality, writable-code needs, source and
   data dependencies, memory ownership, scratch lifetime, initialization,
   and benchmark-corpus identity. Deduplicate shared code and tables.
   Qualified *standalone* does not imply mixed-call or arbitrary-location safety.
3. **Real selective linker (initial UDIV16/UMOD16 implementation).** Assemble/link only the chosen operations and
   transitive dependencies; retain only necessary export stubs. Respect
   reserved ranges, code execution under ROM, stack and ZP conflicts.
   Measure actual linked byte ranges rather than summing reported footprints.
4. **Global constrained optimizer.** Choose among *certified linkable* variants
   for speed/size/ZP, obeying shared resource and hardware constraints.
   Exclude unverified or narrowly conditioned specialists from automatic
   general-purpose selection; allow explicit, checked opt-in.
5. **Full qualification before switching defaults.** Reproduce old V1–V5
   behaviors as fixtures, run exhaustive/edge/random and mixed-call tests,
   verify cycles on matching corpora and native CPU/VICE, check memory
   ownership, reproducible output, and generated-symbol correctness.
   Only then make operation-first selective builds the default.

Until step 5, existing profile binaries, REU image generation, the Pareto
builder and their published benchmark records remain untouched. The new
builder must never silently include all 56 routines when a user has selected
only a subset.

## Validation

```sh
python3 tools/test_math_builder.py
python3 tools/test_selective_linker.py
# or:
make builder-validate
```

The tests cover the real published 56-operation index, historical/typed
aliases, idempotent operation selection, pin errors, resource validation,
catalog checksum verification, deterministic plans, and hard rejection of
an unsupported selective binary.
