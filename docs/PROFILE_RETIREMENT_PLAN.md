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
