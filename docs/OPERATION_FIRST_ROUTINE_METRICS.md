# Operation-first routine metrics: cycles, RAM, zero page and stack

**Current stock-C64 operation-first system.** Measurements are taken
from the **real qualified selective builder**, not historical V1–V5
resident averages. Every one of the 56 public APIs has an isolated
fully assembled source-linked footprint. Each variant's cycle mean
uses the **same input corpus as the other variants of that operation**.
Different operations can have different corpora; cross-operation means
are therefore not a calibrated mixed-application speed ranking.

## One-row-per-operation reference (fastest measured isolated variant)

This is a lookup convenience, **not the universal fastest combined
project**: globally shared kernels, budgets, origins, requested variants
and call frequency can change an actual multi-operation build.

| Operation | Fastest measured linkable variant | Mean CPU cycles/call | Code + tables B | Total isolated RAM B | ZP B | Persistent stack-page B |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `MATH_ATAN2_8` | `link:sum-fast` | 40.927083 | 1109 | 1312 | 0 | 0 |
| `MATH_COS8` | `link:resident-shared-table` | 26.000000 | 271 | 544 | 0 | 0 |
| `MATH_DIST8_ACCURATE` | `link:v2-zp-tables` | 78.080729 | 570 | 800 | 2 | 0 |
| `MATH_DIST8_FAST` | `link:resident-approx` | 76.517578 | 61 | 95 | 0 | 0 |
| `MATH_ISQRT16` | `link:square-table` | 65.101562 | 806 | 1056 | 0 | 0 |
| `MATH_ISQRT32` | `link:v2-highword-source` | 1080.783203 | 960 | 992 | 7 | 0 |
| `MATH_SDIV16` | `link:v2-signed-shared` | 473.937500 | 1705 | 1745 | 0 | 0 |
| `MATH_SDIV16_SHL8` | `link:v2-signed-shifted-public` | 782.507812 | 2624 | 2656 | 12 | 0 |
| `MATH_SDIV24` | `link:v3-signed-magnitude` | 683.181641 | 1897 | 1929 | 9 | 0 |
| `MATH_SDIV32_16` | `link:v2-signed-magnitude` | 866.184896 | 2880 | 2912 | 12 | 0 |
| `MATH_SDIV32_32` | `link:d65536-hybrid` | 594.645833 | 2976 | 3008 | 12 | 0 |
| `MATH_SDIV8` | `link:v1-shared-producer` | 128.515625 | 530 | 562 | 1 | 0 |
| `MATH_SEEK16_INIT` | `link:generated-dda` | 538.025000 | 898 | 1202 | 0 | 0 |
| `MATH_SEEK16_STEP` | `link:generated-dda` | 111.852527 | 898 | 1202 | 0 | 0 |
| `MATH_SEEK16_STEP1` | `link:generated-dda` | 89.954945 | 898 | 1202 | 0 | 0 |
| `MATH_SEEK16_STEP_INT` | `link:generated-dda` | 94.541152 | 898 | 1202 | 0 | 0 |
| `MATH_SEEK8_INIT` | `link:generated-dda` | 390.262500 | 651 | 867 | 0 | 0 |
| `MATH_SEEK8_STEP` | `link:generated-dda` | 82.679023 | 651 | 867 | 0 | 0 |
| `MATH_SEEK8_STEP1` | `link:generated-dda` | 61.090344 | 651 | 867 | 0 | 0 |
| `MATH_SEEK8_STEP_INT` | `link:generated-dda` | 65.598309 | 651 | 867 | 0 | 0 |
| `MATH_SIN8` | `link:resident-shared-table` | 20.000000 | 267 | 544 | 0 | 0 |
| `MATH_SINCOS8` | `link:resident-shared-table` | 36.000000 | 278 | 544 | 0 | 0 |
| `MATH_SMOD16` | `link:v2-signed-shared` | 473.937500 | 1705 | 1745 | 0 | 0 |
| `MATH_SMOD24` | `link:v3-signed-magnitude` | 683.181641 | 1897 | 1929 | 9 | 0 |
| `MATH_SMOD32_16` | `link:v2-signed-magnitude` | 866.184896 | 2880 | 2912 | 12 | 0 |
| `MATH_SMOD32_32` | `link:d65536-hybrid` | 594.645833 | 2976 | 3008 | 12 | 0 |
| `MATH_SMOD8` | `link:v1-shared-producer` | 128.515625 | 530 | 562 | 1 | 0 |
| `MATH_SMUL16` | `link:qs-signed-public` | 608.357422 | 1351 | 1387 | 0 | 0 |
| `MATH_SMUL16_SHR8` | `link:qs-signed-shr8-public` | 646.357422 | 1383 | 1419 | 0 | 0 |
| `MATH_SMUL24` | `link:v2-quarter-square` | 575.091797 | 2560 | 2592 | 24 | 0 |
| `MATH_SMUL32` | `link:fast31-v2-signed` | 825.239583 | 2560 | 2592 | 31 | 0 |
| `MATH_SMUL32_READY` | `link:fast31-shared-full64` | 834.270833 | 2560 | 2592 | 31 | 0 |
| `MATH_SMUL32_SHR16` | `link:fast31-shared-full64` | 897.270833 | 2560 | 2592 | 31 | 0 |
| `MATH_SMUL8` | `link:v1-resident-smc` | 68.144531 | 2090 | 2336 | 0 | 0 |
| `MATH_SMULDIV16` | `link:signed-qs-v2-fused` | 1426.714844 | 4263 | 4299 | 12 | 0 |
| `MATH_UDIV16` | `link:biased` | 162.729167 | 323 | 355 | 2 | 0 |
| `MATH_UDIV16_SHL8` | `link:v2-shifted-public` | 718.700521 | 2368 | 2400 | 12 | 0 |
| `MATH_UDIV24` | `link:v2-repose-fast` | 1117.046875 | 1461 | 1493 | 3 | 0 |
| `MATH_UDIV32_16` | `link:v2-sizefast-public` | 932.630208 | 2368 | 2400 | 12 | 0 |
| `MATH_UDIV32_32` | `link:d65536-hybrid` | 387.127604 | 2592 | 2624 | 12 | 0 |
| `MATH_UDIV8` | `link:v1-resident-fast` | 124.976000 | 294 | 326 | 1 | 0 |
| `MATH_UMOD16` | `link:direct-zerozp` | 504.328125 | 976 | 1010 | 0 | 0 |
| `MATH_UMOD24` | `link:v2-repose-fast` | 1117.046875 | 1461 | 1493 | 3 | 0 |
| `MATH_UMOD32_16` | `link:v2-sizefast-public` | 932.630208 | 2368 | 2400 | 12 | 0 |
| `MATH_UMOD32_32` | `link:d65536-hybrid` | 387.127604 | 2592 | 2624 | 12 | 0 |
| `MATH_UMOD8` | `link:v2-unrolled-fallback` | 90.893000 | 229 | 261 | 2 | 0 |
| `MATH_UMUL16` | `link:quarter-square` | 566.493000 | 1255 | 1291 | 0 | 0 |
| `MATH_UMUL16_SHR8` | `link:quarter-square` | 599.662000 | 1278 | 1314 | 0 | 0 |
| `MATH_UMUL24` | `link:v2-quarter-square` | 508.494141 | 2560 | 2592 | 24 | 0 |
| `MATH_UMUL32` | `link:fast31-shared-full64` | 766.750000 | 2560 | 2592 | 31 | 0 |
| `MATH_UMUL32_READY` | `link:fast31-shared-full64` | 766.750000 | 2560 | 2592 | 31 | 0 |
| `MATH_UMUL32_SHR16` | `link:fast31-shared-full64` | 826.750000 | 2560 | 2592 | 31 | 0 |
| `MATH_UMUL8` | `link:quarter-square` | 84.182000 | 1095 | 1129 | 0 | 0 |
| `MATH_UMULDIV16` | `link:qs-v2-fused` | 1333.273438 | 3655 | 3691 | 12 | 0 |
| `MATH_URECIP16_Q16` | `link:threshold-tables-zerozp` | 180.798828 | 1544 | 1576 | 0 | 0 |
| `MATH_VEC2_NORMALIZE_Q8_8` | `link:certified-stock` | 161.451172 | 3425 | 3619 | 4 | 0 |

## All selectable source variants (complete numeric data)

**122 separately source-linked variant observations covering 56
operations** are available in
[`benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv`](../benchmarks/OPERATION_FIRST_VARIANT_METRICS.csv).
That detailed file includes each source's exact mean CPU-model cycles,
code-and-tables size, full isolated RAM total, alignment/image span,
shared tables, scratch, persistent object state, ZP and persistent
stack-page reservation, benchmark case count/basis/input SHA,
source SHA and linked PRG SHA. Filter its `operation` column to
compare only like-for-like input corpora.

### What the columns mean

- **Mean CPU cycles/call:** public entry through RTS, as measured by
  that operation's original source-qualified Mini6502 benchmark;
  not a physical PAL frame or REU-inclusive elapsed time. Benchmark
  source functions record each input corpus SHA in the CSV.
- **Code + tables B:** independently source-assembled executable
  and owned lookup-table bytes; padding is separately represented
  by `image_span_bytes` and `alignment_padding_bytes` in the CSV.
- **Total isolated RAM B:** the actual physical one-operation linker
  charge, including 32 B of public I/O, scratch, persistent state
  and alignment. This is **not additive** across APIs: code and
  tables may be shared in a real combined library.
- **ZP B:** bytes required by the linked standalone variant; this
  is an ownership reservation, not a sum of simultaneous per-call
  touches. A combined build can share call-exclusive scratch.
- **Persistent stack-page B:** hardware stack page $0100–$01FF
  *reserved for persistent library storage*. Stock selective
  variants currently reserve zero such bytes. **Transient JSR/RTS,
  PHA/PLA or interrupt stack high-water is NOT measured here.**
  Zero does not mean zero runtime stack usage.

## Get your exact installed project footprint and speed choice

```sh
python3 tools/math_builder.py --variants UMUL16

python3 tools/configure_math.py \
  --operation UMUL16 --objective speed --calls UMUL16=1 \
  --zp-budget 120 --ram-budget 16000 \
  --config-out umul16-speed.json --build-dir build_umul16_speed

# Actual selected source, total RAM/ZP, source hashes and measured cycle basis:
python3 -m json.tool build_umul16_speed/selective_manifest.json
```

For multiple operations, the **combined** `selective_manifest.json`
overrides the isolated per-row memory figures. The optional Turbo16
REU service uses **additional** independently reserved executable
ZP and C64/REU memory and is not included in these stock-only rows.
There is no verified DMA-inclusive speed ranking for the optional REU
service. See [REU integration](OPERATION_FIRST_REU_TURBO16.md).

## Reproduce and audit

The report generator calls the current real single-operation speed
selector for **every candidate variant on its common inputs**, and
then independently assembles **each pinned variant** for the physical
resource measurements at the default stock linker origin. Any
cycle-benchmark omission, changed source hash, missing operation or
failed binary link aborts publication; numerical guesses and
historical profile speed exports are never used.

```sh
python3 tools/report_operation_first_metrics.py
python3 tools/report_operation_first_metrics.py --verify
```

This report is a **generated, reproducible reference** for the
particular source revision and standard isolated placement. The
per-operation corpus basis and full SHA provenance are in
[the machine-readable validation record](../validation/OPERATION_FIRST_VARIANT_METRICS.json).
