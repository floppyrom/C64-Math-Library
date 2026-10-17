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

## Workload-weighted speed selection (eight source-qualified APIs)

The `speed` objective supports project-level weighted selection for **eight**
individually qualified APIs: UMUL8, UMUL16, UMUL16_SHR8, UMOD8, UDIV8,
ISQRT32, UMUL32 and SMUL32. Multiple operations **must** each have a positive integer call count,
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
CPU-model cycles. Benchmarks do **not** provide real hardware timing or prove
cycle invariance after physical link relocation; speed selection is therefore
an expected workload estimate, not exact total cycle prediction.

With 1,400 total RAM bytes and the two example APIs, the optimizer can use only
one quarter-square implementation. Heavy UMUL8 workloads select its fast
variant and compact UMUL16; reversing the call weights reverses that choice.
UMUL32 now compares **four** full64 source-linked candidates on the same
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

SMUL32 now also compares **three** signed full64 public-ABI implementations
on its own deterministic 192-pair signed operand corpus: compact 293-byte
source, 375-byte unified producer, and the independently source-linked signed
FAST31 (512 code-slot bytes, four 512-byte lookup slots, 31 ZP). The signed
FAST31 is a composition of the qualified unsigned V2 arithmetic producer
with upper-word signed corrections, **not** the separately recorded V2
692.825-cycle native signed kernel. Its full-call speed is measured separately.
The builder conservatively charges distinct signed and unsigned FAST31 images
if both are selected; they reuse one exclusive 31-byte ZP scratch region but
**do not** yet share executable code or lookup tables. Mixed-call correctness
is tested and these sharing optimizations remain future work.
\nUnsupported APIs fail closed in `speed` mode rather than using historical
resident timing from incomparable benchmark corpora. Ordinary `balanced`,
`size` and `zp` plans remain fully available for all 56 APIs.

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
