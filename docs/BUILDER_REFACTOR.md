### Canonical high-speed V2 unsigned 24-bit DIV/MOD option

The source-linked `MATH_UDIV24` and `MATH_UMOD24` family now has an
additional **explicitly pinnable** `link:v2-repose-fast` variant. This
is a relocation of the actual canonical V2 Repose quotient/remainder
producer, **not** a substituted slow arithmetic algorithm or a copy of
the resident PRG. Its executable body has two tightly packed code
islands of **1,244 + 217 bytes**; both public operations share the
same physical entry and the same 1,461-byte code allocation.
Inputs N24/D24 remain untouched; both Q24 and R24 are written (except
uncontracted high bytes, left unchanged); divide by zero sets carry
and zeros Q/R.

**Hardware and resource contracts:** the historical V2 implementation
uses the stable NMOS 6510 unintended `LAX` and `ANC` opcodes,
**three zero-page scratch bytes**, **no separate RAM scratch**,
no precomputed tables, and a **self-modifying immediate operand**
in the tail path. Code must reside in writable RAM, not ROM, and
decimal mode must be clear. The builder checks all code, IO,
ZP, and reserved-memory intersections. The old 190-byte/4-RAM/0-ZP
`link:portable-restoring` remains the default compact option.

```sh
python3 tools/math_builder.py --operation UDIV24 --operation UMOD24 \
  --pin UDIV24=link:v2-repose-fast \
  --pin UMOD24=link:v2-repose-fast --zp-budget 3 \
  --ram-budget 1493 --build
```

Selection-plan and image manifests SHA-lock the derived relocatable
source and its original historical source plus relocation adapter.
Cross-variant cycle comparisons are made on exactly the same inputs;
the builder **does not yet automatically select a universal fastest
variant**. The historical V1–V5 profile files stay unchanged.

### Portable source-linked unsigned 24/24 DIV/MOD family

`MATH_UDIV24` and `MATH_UMOD24` can each be selected independently,
yet share a single **190-byte restoring source producer**. Both public
entries write an exact 24-bit quotient and a 24-bit remainder, preserve
the input 24-bit numerator and divisor (including upper-byte sentinels),
preserve the fourth Q/R bytes, return C=0 on success, and return
Q=R=0 and C=1 for a zero divisor. Requires decimal mode clear.

The single producer uses **4 bytes of reusable ordinary RAM scratch
and zero zero-page bytes**, with no external tables, initialization,
REU, or writable code. Its full default RAM allocation is
**226 bytes** (190 code, 32 public I/O, 4 scratch); selecting both
public operations does not duplicate the source, or the scratch.
Cross-family selection takes the maximum scratch reservation rather
than adding non-overlapping call-lifetime scratch repeatedly.

```sh
python3 tools/math_builder.py --operation UDIV24 --operation UMOD24 \
  --zp-budget 0 --ram-budget 226 --build
```

**Performance caveat:** this first source-linked zero-ZP variant is a
correctness/reference choice; certified historical V1's q0counter
producer, V2–V4 Repose kernels and V5 hybrid selection are still faster
on relevant workloads and remain intact as separate import targets.
All public V1–V5 profile artifacts are unchanged, and automatic
cycle-ranking is still fail-closed here.

### Independently linkable ISQRT32, complete 32-bit domain

`MATH_ISQRT32` is available as the source-hashed, relocatable
`link:radix4-zerozp` reference variant. It implements exact integer
square root of any unsigned 32-bit radicand (16-bit floor result) using
16 radix-4 restoring iterations. It preserves all four `MATH_N` bytes,
X and Y registers, and the stack pointer; returns carry clear and only
writes the lower two `MATH_Z` output bytes. The caller must enter with
decimal mode clear.

The kernel occupies **204 bytes** and uses **10 bytes of ordinary,
reusable RAM scratch**, no normal zero page, no setup, no REU and no
lookup tables. Default footprint with a 32-byte public I/O block:
**246 bytes**. Code is not modified at runtime and may live in ROM.
The source is independently relocatable and the builder includes
its exact digest in the plan and binary manifest. RAM and reserved
regions are checked across the complete selected operation set.

```sh
python3 tools/math_builder.py --operation ISQRT32 --zp-budget 0 \
  --ram-budget 246 --build
```

**Performance caveat:** this portable fallback is not claimed to be
the fastest ISQRT32. The certified V1/V5 high-word seeded and V2/V3
resident radix-four refiners rely on resident root16 tables, 16-bit
seed helpers, and initialized/zero-page state. V4 has a separate REU
architecture. These historical fast producers are *not yet
independently linkable* and remain the next optimization/import target.
They and all V1–V5 profiles are preserved unchanged.

### One-byte-RAM accumulator remainder variant for unsigned 32/16

An additional independent option, `link:accumulator-remainder`, keeps the
high eight bits of the 17-bit in-progress remainder in accumulator A.
Only the low byte uses scratch RAM, and the 32 quotient bits are shifted
directly in public Q32. Its source occupies **131 bytes** and needs **1
ordinary RAM byte and 0 zero-page bytes**, making the default
two-API combination **164 bytes total** (131 code + 32 IO + 1 scratch).
The original 162-byte/`3 RAM` reference `link:portable-restoring`
remains explicitly pinnable and independently qualified.

Both variants share their producer between `MATH_UDIV32_16` and
`MATH_UMOD32_16`, preserve N32/D16 and the upper two bytes of R,
write full Q32 + R16, clear carry on success and set it on a zero divisor.
The builder defaults to the resource-Pareto-minimal accumulator variant;
this is a **size/RAM selection, not a general speed certification**.
The regression suite additionally checks exact cycles on the same seeded
operand corpus at identical RAM maps and rejects the candidate if its
aggregate cycles are not better than the original restoring reference.
Native VICE tests run both variants and both public aliases independently.

```sh
python3 tools/math_builder.py --operation UDIV32_16 --operation UMOD32_16 \
  --pin UDIV32_16=link:accumulator-remainder \
  --pin UMOD32_16=link:accumulator-remainder --zp-budget 0 --ram-budget 164 --build
```

The optimized V1–V5 producers remain a separate, outstanding
dependency-transplant task; no historic profile is replaced.

### Source-linked portable unsigned 32/16 DIV/MOD

`MATH_UDIV32_16` and `MATH_UMOD32_16` are now independently
selectable. They deliberately share one **162-byte source-level restoring
reference producer**, the same entry address and the same output contract as
the historical resident shared DIV/MOD core. Calling either writes both
the 32-bit quotient and the 16-bit remainder; the two public input fields
remain untouched. Divisor zero yields Q=R=0 and carry set; success clears
carry. The top two bytes of `MATH_R` are left untouched because the
remainder is 16 bits. Requires D=0 on entry.

This non-self-modifying, ROM-compatible kernel uses **three bytes
of reusable ordinary RAM scratch and zero zero-page bytes**. The default
single-family build is 162 code + 32 public I/O + 3 scratch = **197 RAM
bytes**. Selecting both APIs still costs only 197 bytes, not two kernels.
The source hash and full toolchain provenance are recorded in the
selection plan and binary manifest.

```sh
python3 tools/math_builder.py --operation UDIV32_16 --operation UMOD32_16 \
  --zp-budget 0 --ram-budget 197 --build
```

**Performance warning:** This is a qualified *linkability/reference* option
and **not** the V2–V4 resident optimized 32/16 producer. The latter uses
a split quotient/remainder chain, the certified UDIV16 size-fast producer,
and a specialized 32/8 path; those dependencies still need to be migrated.
Until a common-corpus cross-variant measurement is certified, `speed`
selection remains unavailable here. The V1–V5 distribution is unchanged.

### Independently linked SEEK16 four-entry DDA

The original generated SEEK16 (16-bit unsigned X, 8-bit unsigned Y) is
now available as `MATH_SEEK16_INIT`, `MATH_SEEK16_STEP`,
`MATH_SEEK16_STEP_INT` and `MATH_SEEK16_STEP1`. Each has an
independent public address but all four share one **898-byte kernel**:
the original 799-byte zero-page source expands by exactly 99 operand
bytes when using normal RAM inputs. It remains RAM-only and requires
no REU, zero page, initialization or writable code.

The selected kernel owns **248 persistent object bytes** (8 objects)
plus **19 temporary initialization scratch bytes** and up to 7 bytes
of 8-byte state-alignment padding. Default RAM cost is
898+32+19+5+248 = **1,202 bytes**. It exports
`MATH_SEEK16_POS_XL`, `MATH_SEEK16_POS_XH` and
`MATH_SEEK16_POS_Y`, corresponding to the arrays at state offsets
0, 8 and 16. The public ABI passes 16-bit target X in `MATH_X`,
8-bit target Y in `MATH_Y`, and speed in `MATH_N`.
The caller keeps the state live across successive frames.

SEEK16 and SEEK8 may coexist without duplicate code or state, but
the two families reserve **separate** eight-object state blocks.
Their init calls reuse the same 19-byte scratch buffer. Mixed
selections continue to be budgeted globally, with alignment and
user-reserved spans checked. Speed selection remains fail-closed
until cross-family cycle corpora are comparable.

```sh
python3 tools/math_builder.py --operation SEEK16_INIT --operation SEEK16_STEP \
  --operation SEEK16_STEP_INT --operation SEEK16_STEP1 --zp-budget 0 \
  --ram-budget 1202 --build
```

### Independently linked SEEK8 four-entry stateful DDA

The builder can now link the **unchanged generated SEEK8 instructions**, relocated to 651 bytes with absolute RAM inputs as
four distinct public entry points: `MATH_SEEK8_INIT`, `MATH_SEEK8_STEP`,
`MATH_SEEK8_STEP_INT`, and `MATH_SEEK8_STEP1`. Any selected combination
occupies the code exactly **once**, while exports retain distinct addresses.
The source's 32-byte Euclidean correction table is part of the relocated 651-byte image.
No REU, MATH_INIT, zero-page reservation or writable code is required.

Stateful modules require different accounting from temporary scratch. The
builder reserves **160 persistent RAM bytes** for eight object slots, plus
**19 bytes of reusable call-lifetime initialization scratch** and up to seven
alignment bytes. It never shares the persistent state with other routines,
even when adding calls sequentially. Default at `MATH_IO=$C000`, the
state occupies `$C038-$C0D7`, with exported
`MATH_SEEK8_POS_X=$C038` and `MATH_SEEK8_POS_Y=$C040`.
Default output total: 651 code + 32 public IO + 19 scratch + 5
alignment + 160 persistent state = **867 RAM bytes** (0 ZP).

SEEK8 INIT follows the existing public ABI:
`MATH_X` low target X, `MATH_Y` low target Y, and
`MATH_N` low/high speed fraction/integer+mode. X selects slot 0..7 and is
preserved. INIT and all stepper entries preserve user inputs, and steppers
report arrival through carry. All modes can be interleaved between eight
objects with persistent state retained. Source and emitter are SHA-locked.

```sh
python3 tools/math_builder.py --operation SEEK8_INIT --operation SEEK8_STEP \
  --operation SEEK8_STEP_INT --operation SEEK8_STEP1 --zp-budget 0 \
  --ram-budget 867 --build
```

Single-operation speed optimization for SEEK8 remains intentionally disabled
until a matched-input performance basis is qualified. Native VICE and
CPU-model tests exercise two code/IO/scratch relocations; full-state safety
and mixed-operation resource contracts are checked in the builder tests.

# Builder refactor: operation-first selection (phase 1)

The future **C64 Math Library Builder** will replace user-facing V1–V5 profile
selection with a choice of mathematical **operations**, resource constraints,
and optimization goals. Historical images remain available as regression
oracles until the new linker meets the same correctness and timing contracts.

**An experimental selective linker now supports eighteen operations: UMUL8, UMUL16, UDIV8, UDIV16, UMOD16, UDIV32_32, UMOD32_32, ATAN2_8, ISQRT16, DIST8_FAST, DIST8_ACCURATE, SIN8, COS8, SINCOS8, SDIV8, SMOD8, SMUL8 and UMOD8.**
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


### Shared historical signed 8-bit DIV/MOD producer

Both `MATH_SDIV8` and `MATH_SMOD8` are backed by the same historical V1
signed quotient/remainder routine. The `link:v1-shared-producer` module
contains **530 bytes of original code**, requires **one ZP byte**, and
uses no lookup table, RAM scratch or REU. The builder exports both public
symbols with **one physical producer** when both operations are selected.

Results preserve the original signed 8-bit quotient truncation and signed
remainder, input bytes and the high output bytes; carry is set on zero divisor
(and the low Q/R bytes are zero). Zero divisor is therefore handled without
a separate adapter. At default RAM placement, a single or paired selection
costs 530 code + 32 public I/O = **562 bytes of RAM**. The original
trampoline is removed while the resident fast calculation survives.

```sh
python3 tools/math_builder.py --operation SDIV8 --operation SMOD8 \
  --zp-budget 1 --ram-budget 562 --build
```

All 65,536 signed numerator/divisor cases are tested at two relocations,
including carry, ABI preservation and full generated-binary immutability;
the source-linked VICE CI also tests both relocations. The two public
names are independently validated by source hashes before aliasing.

### Original V1, V2 and V5 fast UMOD8 selectable variants

The original V1 `UMOD8` source module remains the **157-byte size winner**.
Two additional independently linkable historical alternatives now preserve
the real Pareto and Hybrid optimized implementations:

| Selection pin | Code | ZP | Writable RAM? | Fast divisor branch |
|---|---:|---:|---|---|
| `link:v1-fast-fallback` | 157 bytes | 2 bytes | Yes | divisor >= 32 |
| `link:v2-unrolled-fallback` | 229 bytes | 2 bytes | Yes | divisor >= 24 |
| `link:v5-unrolled-hybrid` | 205 bytes | 2 bytes | Yes | divisor >= 32 |

The high-divisor branches and small-divisor reducers retain the historical
instructions, including the self-modified immediate subtraction loop in writable
code RAM. All produce **only the low remainder byte** of `MATH_R`;
the quotient, both public input groups and unused output bytes remain unchanged.
Zero divisor produces remainder 0 and carry set. No REU is required.

```sh
python3 tools/math_builder.py --operation UMOD8 \
  --pin UMOD8=link:v2-unrolled-fallback --zp-budget 2 \
  --ram-budget 261 --build
python3 tools/math_builder.py --operation UMOD8 \
  --pin UMOD8=link:v5-unrolled-hybrid --zp-budget 2 \
  --ram-budget 237 --build
```

These source-faithful options are compared only on **matched divisor corpora**
before any automatic speed ranking. The faster choice may vary with divisor
distribution; smaller code is not presumed faster. CPU model checks cover all
65,536 operand pairs at each of two code/ZP relocations per variant; native
VICE checks each source-linked variant at both relocations and CI protects the
two intentional self-modifying immediate operands from other writes.

### Qualified single-operation UMOD8 speed selection

The builder may now use the reproducible 1,000-pair *source-assembled
CPU-model* corpus for `--objective speed --operation UMOD8`, honoring
both the caller's RAM/ZP budget and any explicitly pinned historical
implementation. It measures the actual relocatable source at the requested
code/I/O/ZP placement, verifies public ABI on every operand pair, and
records the full per-variant cycles, corpus hash and source hashes.

For the default `$8000` code origin and `$C000` I/O layout, all
three variants use two ZP bytes. The certified source-assembled mean
cycles over the identical corpus were V1 **95.635**, V2 **90.893**,
V5 **94.165**; these are **not native hardware timings**.

| Available main RAM | Fastest eligible source in this corpus |
|---|---|
| 189–236 B | V1 fast/fallback (157 code B) |
| 237–260 B | V5 unrolled hybrid (205 code B) |
| 261+ B | V2 unrolled fallback (229 code B) |

RAM includes the common 32-byte public I/O reservation, and the code
must be writable for these SMC producers. The user can still request
`--objective size` or explicitly pin any implementation. The speed
selector **refuses mixed-operation rankings** without a comparable
joint workload.

```sh
python3 tools/math_builder.py --operation UMOD8 --objective speed \
  --zp-budget 2 --ram-budget 261 --build
```

### Source-exact original V1 UMUL8 (51-byte entry/core)

The original shipped V1 `MATH_UMUL8` is now a third independently selectable
8-bit unsigned multiplier, not replaced by a generic compact algorithm. Its
22-byte entry and 29-byte helper are assembled contiguously (51 code bytes);
the two aligned quarter-square lookup pages contain 511 exact entries each,
plus the original unused gap bytes. Every lookup entry is checked byte-for-byte
against the published V1 resident image.

Use `--pin UMUL8=link:v1-resident-fast --zp-budget 4 --ram-budget 1311`.
The code requires four exclusive consecutive zero-page bytes as two pointers;
it requires neither self-modifying code nor REU nor one-time initialization.
The public low X and Y bytes remain unchanged; the 16-bit result occupies the
low two Z bytes, carry clears and high output bytes are preserved.
At code origin $8000, 51 code + 1022 lookup bytes + 206 alignment/gap bytes
plus 32-byte public I/O = **1311 total main RAM bytes**. The memory cost varies
with code origin; all padding and unowned gap bytes count toward the footprint.

The **same locked 1000-pair CPU-model corpus** now measures all three UMUL8
implementations, with an explicit ZP origin in the benchmark. Automatic speed
selection remains scoped to **UMUL8 alone**, resource constraints and pins are
enforced, and mixed-operation speed comparisons continue to fail closed.
All 65,536 x/y products are checked at two independently relocated RAM/ZP
placements, followed by native VICE execution at both placements.

```sh
python3 tools/math_builder.py --operation UMUL8 \
  --pin UMUL8=link:v1-resident-fast --zp-budget 4 --ram-budget 1311 --build
python3 tools/math_builder.py --operation UMUL8 --objective speed \
  --zp-budget 4 --ram-budget 1311 --measure
```

### Source-aligned UMOD8 cycle measurement (V1, V2, V5)

`tools/test_selective_umod8_speed.py` benchmarks all three independently
source-linked historical UMOD8 variants on the **same deterministic 1,000-case
unsigned numerator/divisor corpus**, including the small-divisor region in
which the V2/V5 unrolled fallback is designed to help. It records the SHA256
of that corpus and all three source files, together with mean call-through-RTS
cycles, per-variant size and ZP usage, and a separate mean for divisors 3–31.
The benchmark runs the emitted source-assembled machine code with the
deterministic 6502 CPU model, validating public input preservation, quotient
preservation, remainder and carry on every call.

```sh
python3 tools/test_selective_umod8_speed.py
```

**These are comparable CPU-model estimates, not independently timed native
VICE results.** They provide a reproducible basis for examining
size/speed trade-offs. The builder does not yet auto-select UMOD8 by
cycle speed, and does not rank unrelated operation families using an
unmatched benchmark corpus.

### Same-corpus UDIV8 speed selection

Once the original V1 and V2/V5 UDIV8 producers are available, **UDIV8
alone** supports `--objective speed` over a locked **1,000-pair shared
numerator/divisor CPU-model corpus**. Both kernels are source-assembled
at the requested code, I/O and zero-page origins and every measured call
verifies unsigned quotient/remainder, zero-divisor carry, intact inputs
and neighbouring output bytes, and balanced stack. Benchmarks and input
corpus hashes appear in the manifest. These are **CPU-model cycles**, not
independent VICE cycle measurements.

V1 uses 294 code bytes / **326 RAM bytes including shared I/O**;
V2/V5 uses 430 code bytes / **462 RAM bytes including I/O**. Both use one
zero-page byte. Thus budgets from 326 to 461 bytes select V1 regardless
of timing, and larger RAM budgets permit choosing the measured faster
implementation. Explicit pinning and RAM/ZP limits remain authoritative.
Mixed-operation speed selection remains unavailable without a matched
weighted workload model.

```sh
python3 tools/math_builder.py --operation UDIV8 --objective speed \
  --zp-budget 1 --ram-budget 462 --measure
```

### Source-identical V2/V5 UDIV8 fast-chain alternative

V2 and V5 ship *byte-for-byte identical* UDIV8 code at the original
`$4000-$41AD` executable island. Rather than manufacture a duplicate
implementation, the operation-first linker exposes the original source as
`link:v2-v5-fast`: **430 code bytes, 1 zero-page scratch byte, no
private RAM scratch, no lookup tables or REU**. Original `$3120` jump
trampoline is omitted, and the public entry is code origin + 8.

The default minimum-RAM choice remains the smaller V1 kernel
(`link:v1-resident-fast`, 294 code bytes). V2/V5's longer unrolled
fast branch chain is retained as a historical speed-oriented alternative,
without asserting a superior average speed on unmatched published
benchmark corpora. The builder accepts an explicit pin:

```sh
python3 tools/math_builder.py --operation UDIV8 \
  --pin UDIV8=link:v2-v5-fast --zp-budget 1 \
  --ram-budget 462 --build
```

At the original source address `$4000` and ZP `$10`, the generated
430-byte PRG code island is tested byte-for-byte against **both** shipped
V2 and V5 resident PRGs. An additional two-location test calls the
source-assembled code for all 65,536 numerator/divisor pairs per location,
checking dividend/divisor preservation, quotient/remainder, zero-divisor
carry, upper output byte sentinels and stable stack. Native x64sc verifies
the source-built selected image at two more RAM and ZP placements.

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

### Original V1 unsigned UMOD8 (fast subtraction with SMC fallback)

`MATH_UMOD8` now provides `link:v1-fast-fallback`, retaining the
original **157-byte V1** unsigned modulo producer without the old
3-byte public trampoline. The source has two optimized cases:
a straight-line subtraction chain for divisors at least 32, and a
small-divisor producer using two private zero-page bytes. The fallback
uses two writable immediate-operand bytes in its subtraction loop,
so the **code must reside in writable RAM** and is non-reentrant.

The implementation preserves dividend, divisor, high output bytes,
and the **entire quotient `MATH_Q`**, unlike a shortcut that calls
`UDIV8` and clobbers Q. It writes the low byte of `MATH_R`,
sets carry on division by zero with R=0, and clears carry otherwise.
It needs **157 bytes of code + 32 bytes shared I/O = 189 bytes RAM**,
**2 ZP bytes**, no tables, no REU and no init. Only the two declared
immediate operands may change between calls.

```sh
python3 tools/math_builder.py --operation UMOD8 \
  --pin UMOD8=link:v1-fast-fallback --zp-budget 2 \
  --ram-budget 189 --build
```

The test campaign covers **65,536 unsigned N/D pairs at two relocations**,
checks divisor-zero flags, quotient preservation, stack/operand bytes,
writable-code footprint and mixed linking with UDIV8 and signed division.
Native x64sc verifies both relocated builds independently. Other historical
UMOD8 variants remain available as future migration candidates.

### Original 46-byte signed SMUL8 (writable self-modifying source)

`MATH_SMUL8` now offers `link:v1-resident-smc`: the exact **46-byte**
historical 6502 signed 8×8 multiplier from V1–V5. This is **not** the
slower compact shift/add replacement. It uses four original 511-byte
lookup tables, retained byte-for-byte from every released V1–V5 PRG.
Their historical absolute pages differ between profiles, but their
mathematical bytes are identical.

This routine writes the low operand bytes of its four indexed lookup
instructions on each call. **Its code must be in writable RAM, never
ROM/cartridge ROM or read-only memory, and calls must not overlap.** The
builder records `requires_writable_code: true` in variant metadata.
Zero-page usage and separate scratch RAM are both **zero**. The four tables
are emitted at successive 512-byte offsets with page-aligned starts;
alignment, three inter-table holes, and other shared family tables
are included in the image RAM budget.

At default code origin `$8000`, 46 code bytes, 4×511 lookup bytes
and 214 padding bytes occupy 2304 image bytes plus a 32-byte public I/O
block: **2336 bytes of total RAM, zero ZP**. At `$80D2`,
padding falls to four bytes (2094 image bytes and 2126 bytes of RAM).

```sh
python3 tools/math_builder.py --operation SMUL8 \
  --pin SMUL8=link:v1-resident-smc --zp-budget 0 \
  --ram-budget 2336 --build
```

All 65,536 signed operand pairs are checked by reference-table arithmetic
and on actual assembled 6502 bytecode at two RAM relocations. Tests verify
that only the four documented operand bytes change, that source tables
remain immutable, carry clears, the inputs and upper result bytes are
preserved, and the stack is balanced. Native VICE tests use two separate
code and I/O placements.

### Faster-source UMUL16: quarter-square composition

Alongside the 108-byte compact shift/add source, `MATH_UMUL16` can now
select `link:quarter-square`. It evaluates four exact unsigned 8×8
quarter-square products, combines them with carry propagation into a 32-bit
result, and reuses the 511-entry low/high lookup-table generator already
used by UMUL8. Both sources preserve X/Y and return `C=0`.

| UMUL16 variant | Kernel | Tables | ZP | Ordinary scratch | RAM with shared I/O |
|---|---:|---:|---:|---:|---:|
| `link:compact-zerozp` | 108 B | 0 B | 0 B | 6 B | 146 B |
| `link:quarter-square` | 233 B | 1022 B | 0 B | 4 B | 1291 B |

Explicit pinned build (source/table SHA-locked, no resident image):

```sh
python3 tools/math_builder.py --operation UMUL16 \
  --pin UMUL16=link:quarter-square --zp-budget 0 \
  --ram-budget 1291 --build
```

With `--objective speed` for **UMUL16 alone**, the builder executes both
source-assembled implementations on the same deterministic CPU-model corpus
(1,000 16×16 operand pairs, seeded edge/uniform). It records the corpus
SHA, individual mean cycles and the chosen implementation in the manifest;
RAM/ZP constraints still apply. These measurements are **CPU-model cycles**,
not native VICE performance timings. A mixed-operation speed optimization
request still refuses to claim comparability.

The source-linked and native VICE qualification for this new variant is
tracked by PR #201, qualified independently before publication.

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
