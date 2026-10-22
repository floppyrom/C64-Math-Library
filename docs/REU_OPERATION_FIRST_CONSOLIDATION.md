# Operation-first REU acceleration: hardware integration

**For the normal installation flow, start with the [README](../README.md).**
This page covers the REU-specific lifecycle, capacity checks and physical
resource ownership. The three source-built services were consolidated into
the operation-first installer in [PR #393](https://github.com/floppyrom/C64-Math-Library/pull/393);
new projects do not require a frozen V3/V4 resident.

The normal [operation-first setup](OPERATION_FIRST_USER_SETUP.md) selects
among all 56 stock-C64 math operations and exact RAM/ZP budgets. An REU
service is an **opt-in hardware companion**, not a historical profile and
not an automatically chosen `speed` variant.

| Service | Select | Stock fallback | REU capacity | Extra C64 RAM reservation | Exclusive ZP |
| --- | --- | --- | --- | ---: | ---: |
| Turbo16 | `--reu-turbo16` | `UMUL16` | 512KiB / 16MiB | 18,464 B | 122 B |
| Turbo32 | `--reu-turbo32` | `UMUL32` | 512KiB / 16MiB | 18,464 B | 135 B |
| QS16 | `--reu-qs16` | `UMUL16` | 16MiB only | 18,468 B | 16 B |

The C64 RAM figure is the entire module's reserved address envelope plus
public I/O (and QS16 scratch), **not** only its machine-code bytes. It is
charged separately from the selected stock library; find the final
combined total, exact placements and REU bank ownership in
`math_project_manifest.json`. The ZP figure is reserved while a batch
is active, not transient CPU stack high-water.

**Select exactly one REU service per project.** Concurrent services
aren't qualified: their C64 load images, public I/O and REU ownership
need a separate multi-module allocator and simultaneous-life-cycle test.

## Create a project

For Turbo32:

```sh
python3 tools/configure_math.py --operation UMUL32 \\
  --objective size --ram-budget 30000 --zp-budget 210 \\
  --reu-turbo32 --reu-kib 512 \\
  --config-out reu32.json --build-dir build_reu32
```

For QS16:

```sh
python3 tools/configure_math.py --operation UMUL16 \\
  --objective size --ram-budget 30000 --zp-budget 210 \\
  --reu-qs16 --reu-kib 16384 \\
  --config-out qs16.json --build-dir build_qs16
```

For Turbo16, change the first example to `--operation UMUL16
--reu-turbo16`; see [Turbo16 details](OPERATION_FIRST_REU_TURBO16.md).

The generated directory contains:

- `math_selective.prg`, `math_api.inc`,
  `selective_manifest.json`: independently linked stock fallback
  and exact math API/physical resources.
- `<service>_reu.prg`, `math_reu_<service>.inc`,
  `<service>_reu_manifest.json`: independent REU program, guarded
  exports, hardware and source provenance.
- `math_project_manifest.json`: combined RAM/ZP charges, stock and
  REU PRG hashes, hardware choice and REU bank ownership.

Edit and rebuild the saved JSON with
`python3 tools/math_builder.py --config reu32.json --build
--out build_reu32_again/selection_manifest.json`.
The builder rejects output directories that would be overwritten.

## Using the result

1. Load **both** the generated stock PRG and the independent REU PRG
   into their documented disjoint memory locations.
2. Call the REU service's exported INSTALL and check Carry. If no REU,
   insufficient capacity or unsafe bank aliasing is detected, do
   **not** call the REU lifecycle; use stock `MATH_UMUL16` or
   `MATH_UMUL32`.
3. After INSTALL, explicitly call BEGIN, repeated CALL and END. Never
   nest BEGIN or call END without a matching BEGIN. Do not use the
   overlay-owned zero-page bytes from math, IRQ or game code while an
   REU batch is active.

The source-built module validates the declared REU tier through real
DMA probe and smaller-capacity alias tests. Turbo32 SWAPs all 135 bytes
of executable zero page on BEGIN/END and restores the caller's state.
QS16 **computes** the 524,284-byte quarter-square lookup table from
mathematics on the C64, DMA-transfers it into eight aligned REU banks,
and verifies every 1KiB block by DMA readback before marking INSTALL
ready. QS16 saves/restores all 16 bytes of its scratch zero page on
BEGIN/END. The old 16MiB `.reu` image is not needed.

The installer reserves the REU companion's entire C64 PRG footprint,
public I/O, executable/scratch zero page, relevant REU banks and alias
probe resources *before* selecting stock implementations. It enforces
the user's combined RAM/ZP budgets and rejects conflicting explicit
user reservations; nothing is obtained by adding isolated reference
table byte counts.

## Qualification and limits

The merged implementation is covered by CPU-model arithmetic,
lifecycle and exact-ZP-restoration tests, plus pinned native VICE x64sc
preflights for absent/present or aliased REU, real DMA and repeated
batches. The shared operation-first acceptance tests cover all three
REU choices, RAM/ZP resource accounting, deterministic saved-config
rebuilds and package integrity. This is the **merged source-built
REU integration**, not a historical bundle or a pending installer port.

These tests do **not** certify arbitrary mixed application frame timing,
IRQ/VIC/SID contention, nested/reentrant operation, a second simultaneous
REU service, or DMA-inclusive application speedups. `--objective speed`
optimizes stock math using measured CPU-model means; REU must be
selected explicitly. No claim of universal Turbo32/QS16 superiority is
made. See the [per-routine CPU metrics](OPERATION_FIRST_ROUTINE_METRICS.md)
and the generated `math_project_manifest.json` for resource totals.

## Historical archives, not required installation

Original V3/V4 PRGs and REU images remain immutable in the source
repository as **test oracles and existing-application compatibility**.
The `tools/export_reu_compat.py` command still reproduces those older,
whole-resident packages, but neither the modern stock PRG nor the new
Turbo16/Turbo32/QS16 modules link or import those frozen residents.
Do not combine old PRGs with the generated stock math ABI.

See [historical export details](REU_COMPAT_EXPORT.md). Drive-side
1541/1571/1581 operation-first arithmetic is a **separate future
backend** and is not installed by this REU configuration.
