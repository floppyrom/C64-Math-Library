# Performance — operation-first C64 Math Library

> **Current performance charts (21 October 2026).** The supported installation method selects **operations and qualified source variants**, not V1–V5 resident profiles. **There is no single universal speed, RAM or zero-page number for an operation**: the physical linked image, shared tables, chosen workload, resource budget and memory placement affect the result. The historical profile-by-profile charts have been preserved, unchanged, in the [historical performance archive](docs/PERFORMANCE_ARCHIVE_HISTORICAL_RESIDENTS_2026-10-21.md).

**For individual routines:** open the [56-operation cycle/RAM/ZP/stack reference](docs/OPERATION_FIRST_ROUTINE_METRICS.md), with one row per public operation and a complete [all-variant CSV](benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv). This table includes only current source-linkable routines, not retired resident profiles. Persistent stack reservations are measured separately from unmeasured transient stack depth.

The library's **56 independently linkable stock-C64 public operations** are configured through [the operation-first setup](docs/OPERATION_FIRST_USER_SETUP.md). The performance evidence below comes from verified *operation-first, fully linked source plans*, not obsolete whole-profile benchmark rows. Values should only be compared **within the same table and benchmark basis**.

## 1. Complete linked-project Pareto chart: seven operations

Seven operations are linked together: `UMUL32`, `SMUL32`, `ISQRT16`, `UDIV32_32`, `UMOD32_32`, `SDIV32_32` and `SMOD32_32`. Every row runs the **same 150 public calls in 24 synthetic frames**, independently replayed at **two memory placements**. The RAM column is actual *full linked-project* consumption at the worst placement: it includes shared code/tables and relevant physical resources, **not a sum of individually measured routine sizes**. The cycle column is the **worst mathematical frame**, Mini6502 CPU-model public calls **plus caller JSR**; it is not PAL elapsed time.

| Peak objective, 16KB RAM | ZP | Total linked RAM | Worst-placement peak CPU math cycles |
| --- | ---: | ---: | ---: |
| Compact with radix4 root (original baseline) | 0 | 1,666 B | 63,581 |
| Compact with square-table root (new) | 0 | 2,350 B | 59,933 |
| Compact with square-table root and V2 DIV/MOD (new) | 12 | 6,737 B | 40,109 |
| Fast-everywhere (original baseline) | 31 | 8,992 B | 16,172 |

**Decision illustrated:** Lower zero-page footprints cost more cycles for this particular trace. The 12-ZP and 31-ZP options are legitimate *different budget choices*, not different historical installer profiles. “V2” in any source description refers to the **provenance of an independently linked kernel**.

Source: [16-choice linked-image benchmark and native correctness qualification](docs/SEVEN_CROSS_FRAME_PRODUCTION.md).

## 2. Source-variant choices within the same seven-operation workload

This is the independently registered nine-choice D=`$00010000` benchmark on the **same exact 150-call/24-frame arithmetic trace**, across two qualified memory placements. All alternatives share the same seven public operations. A source's signed and unsigned DIV/MOD entries can share code: it would be wrong to multiply an isolated source's footprint by its number of public entries.

| Fully linked seven-API source plan | Worst modeled frame | Worst mapped RAM | ZP |
|---|---:|---:|---:|
| FAST31 and original signed/unsigned V2 | 16,172 cycles | 8,992 B | 31 B |
| FAST31 and both D65536 sources | 13,897 cycles | 9,213 B | 31 B |
| **FAST31, unsigned V2, signed D65536** | **13,849 cycles** | **8,992 B** | **31 B** |

The **signed-only D65536** choice saves **2,323 CPU-model worst-frame cycles** (16,172 − 13,849) at **the same 8,992 B worst-placement linked RAM and 31 B ZP** as the source baseline. Adding the unsigned D65536 source as well worsens this workload's peak by **48 modeled cycles** (13,897 − 13,849) and consumes **221 B additional worst-placement RAM** (9,213 − 8,992). Neither a larger variant nor an individually faster special case should automatically win the global optimizer.

Source: [nine-plan source replay and selection](docs/D65536_FRAME_CHOICES.md).

## 3. Native PAL/VIC-II comparison — a different unit and scope

Pinned native **VICE x64sc r46284** executed the three **actual operation-first linked PRGs** for all 24 matching *independent raster-aligned* arithmetic bursts, with VIC display on and off: **144 probes in total**. Below are only the display-**on** worst cases. This table measures elapsed **CIA PHI2 slots**, including native VIC contention and benchmark operand staging; it is **not directly interchangeable with the CPU-model cycles above**.

| Seven-operation installed source plan | Worst VIC-on slots | Worst-frame margin | Linked RAM, $4123 map | Missed bursts |
|---|---:|---:|---:|---:|
| Original FAST31 + signed/unsigned V2 | 19,883 | −227 | 8,957 B | 1/24 |
| FAST31 + both signed/unsigned D65536 | 17,618 | +2,038 | 9,213 B | 0/24 |
| **FAST31 + unsigned V2, signed D65536** | **17,580** | **+2,076** | **8,957 B** | **0/24** |

The nominal PAL interval is **19,656 PHI2 slots** (`312 × 63`). Each listed margin is calculated as **19,656 − measured peak**; negative indicates an isolated-burst overrun. The signed-only linked image saves **2,303 native slots** (19,883 − 17,580) on the maximum recorded burst, at **unchanged 8,957 B RAM** at the native `$4123` test map. Note that this **8,957 B** is a specific *native-placement* linked measurement; **8,992 B** in the previous table is a *worst-of-two-placements* model report. Those figures must **not** be conflated.

These **24 separate bursts are not 24 consecutive music/game frames** and do not certify a complete 50 Hz application, live SID player, IRQ handler, sprites or REU DMA. Their test results are useful *comparative evidence*, not a universal frame-rate guarantee.

Source: [native installed D65536 PAL measurement](docs/NATIVE_INSTALLED_D65536_PAL.md).

## 4. Get the correct per-operation numbers for *your* library

A single static “best cycles per operation” chart would be misleading: `speed` selects **same-input CPU-model measurements per operation**, weighted by the user's real call frequencies, subject to **global RAM, ZP, code-sharing and placement constraints**. When testing an individual operation, inspect each `link:...` variant rather than treating an old V1–V5 column as a selectable option.

```sh
# Discover individually linkable source choices:
python3 tools/math_builder.py --variants UMUL16

# Build one reproducible source-selected UMUL16 benchmark installation:
python3 tools/configure_math.py \
  --operation UMUL16 --objective speed --calls UMUL16=1 \
  --zp-budget 120 --ram-budget 16000 \
  --config-out umul16-speed.json --build-dir build_umul16_speed

# Inspect the builder's actual measured source-variant means and selected resources:
python3 -m json.tool build_umul16_speed/selective_manifest.json
```

The resulting manifest's `cycle_model_benchmark` provides the measured source-variant means, **input-corpus SHA-256**, source/placement basis and `cpu_model_only` qualifier. `resource_use`, `operations` and the physical placement map establish **what your selected source-linked image actually occupies**. No standalone record should be shown as “installed fastest” unless it is a selectable, correctly linked source with a comparable public-call corpus. For multiple operations, explicit positive `--calls OP=N` counts are necessary for `speed`; they are **not** presumed equal.

The original benchmark archives remain available for reproducibility: [full historical chart](docs/PERFORMANCE_ARCHIVE_HISTORICAL_RESIDENTS_2026-10-21.md), [archived CSV inputs](benchmarks/README.md), [source integration and measurement basis](docs/BUILDER_MIGRATION_CYCLE_BASIS.md) and [historical parity limitations](docs/PROFILE_RETIREMENT_EVIDENCE.md). Published single-kernel native record timings are not substituted for source-linked full-public-call measurements.

## 5. Optional REU services: measure DMA separately

The operation-first installer supports explicit, independently loadable
**Turbo16, Turbo32 and QS16** REU services. The final project manifest
reports each source-built module and its combined physical RAM/ZP use
with the selected stock math fallback:

| REU service | C64 RAM reserved beyond stock | Exclusive ZP while active | REU ownership | Normal fallback |
| --- | ---: | ---: | --- | --- |
| Turbo16 | 18,464 B | 122 B | One 64KiB bank + alias probes | `UMUL16` |
| Turbo32 | 18,464 B | 135 B | One 64KiB bank + alias probes | `UMUL32` |
| QS16 | 18,468 B | 16 B | Eight 64KiB banks + alias probes | `UMUL16` |

These RAM amounts include the **entire** loadable PRG envelope, public
I/O, and for QS16 the four-byte external scratch, not just executable
instructions. A generated `math_project_manifest.json` provides the
actual total and bank assignments. The ZP columns mean exclusive
resource ownership, **not stack high-water**. Transient call/IRQ
stack consumption and DMA-inclusive wall-clock costs are not inferred
from these figures.

The native pinned VICE tests validate DMA, lifecycle, hardware absence
and bank-mirroring safety, source-built products, and exact zero-page
restoration. They do **not** provide comparable whole-batch REU
performance against each stock fallback under the same live
VIC/IRQ/SID contention. Therefore the builder does **not**
automatically select any REU service under the `speed` objective.
The original V3/V4 per-CALL Turbo/QS16 cycle figures remain
**historical CPU-side measurements**, not modern DMA-inclusive rankings.

See [operation-first REU configuration and limitations](docs/REU_OPERATION_FIRST_CONSOLIDATION.md).
The optional raster/SID research [PR #385](https://github.com/floppyrom/C64-Math-Library/pull/385)
is **not** an installer acceptance gate.

## Measurement integrity

The three current comparison tables are reproduced **verbatim from their separately documented benchmark sources**. The repository's `tools/test_operation_performance_charts.py` validates that these charts have not drifted, checks their row counts, PAL margins and both cycle-savings calculations, and ensures historical profile means remain in the archive. This is a **source-consistency test**, not an additional native VICE run. To reproduce the actual CPU models or native measurements, use the commands in the linked benchmark documents.
