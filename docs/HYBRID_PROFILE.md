# V5 Hybrid Low-ZP profile

## Purpose

V1 and V2 are alternative complete profiles, but their individual algorithms can be mixed safely **at build time** when their scratch and code dependencies are understood. V5 is the first certified hybrid: it keeps V1's low integration pressure while importing V2 routines that can run inside the same 31-byte normal ZP contract.

This is not two complete libraries loaded side-by-side. V5 produces **one resident library, one public I/O block and one 46-entry API**.

## Selection policy

The initial V5 preset is deliberately conservative. A V2 path is imported only when:

1. it is measurably faster than V1;
2. it does not require ZP outside the V1 normal window after relocation;
3. its code/data dependencies can be privately relocated without altering other V1 routines;
4. the direct imported path can retain V2 cycle timing without a dispatcher tax;
5. the complete 46-entry library still passes the common validation suite.

Certified imports:

| Stable entry | V1 mean | V5/V2 mean | Gain | Extra normal ZP |
|---|---:|---:|---:|---:|
| `MATH_UDIV16` | 160.064966 | **137.282268** | 14.23% | 0 |
| `MATH_UDIV24` | 224.668396 | **203.612991** | 9.37% | 0 |
| `MATH_UDIV32_16` | 857.373105 | **759.730823** | 11.39% | 0 |
| `MATH_UMOD8` | 65.285156 | **64.819153** | 0.71% | 0 |
| `MATH_UMOD16` | 163.064966 | **140.282268** | 13.97% | 0 |
| `MATH_UMOD24` | 227.668396 | **206.612991** | 9.25% | 0 |
| `MATH_UMOD32_16` | 860.373105 | **762.730823** | 11.35% | 0 |
| `MATH_COS8` | 29 | **23** | 20.69% | 0 |
| `MATH_SINCOS8` | 39 | **31** | 20.51% | 0 |
| `MATH_ATAN2_8` | 50.441345 | **46.953064** | 6.92% | 0 |

The V5 direct paths were compared against V2 with cycle-vector equality; these are not estimates from instruction counting.

`MATH_UDIV16_SHL8` and `MATH_URECIP16_Q16` also call imported division entries and therefore benefit indirectly, but their outer V1 implementations remain V1 and are not presented as byte/cycle-identical V2 imports.

## Why not import every V2 routine?

V2's performance comes partly from a larger **union** of scratch allocations and, for native `SMUL16`, a 116-byte executable-ZP core. V5's current contract is stricter: the complete library must remain usable with V1's 31-byte normal ZP allocation. Routines requiring additional persistent/executable ZP remain V1 until a separately validated compact remapping exists.

The hybrid builder is therefore a **certified selector**, not an unsafe arbitrary binary mixer.

## Memory map

Reference V5:

```text
V1 resident regions      unchanged
MATH_IO                  $C000-$C01F
V1_SCRATCH               $C040-$C057
normal ZP                $02-$20       31 bytes
HYBRID_CODE              $A000-$B1FF   4608 bytes
ATAN2 extra table pages   $6E00/$6F00/$7000   3 x 256 bytes
```

Private hybrid layout:

```text
$A000-$AFFF  relocated V2 division block
$B000-$B07F  relocated V2 UMOD8 block
$B080-$B08A  V2 COS8 implementation
$B090-$B0A0  V2 SINCOS8 implementation
$B100-$B1FF  private V2 cosine table
$6E00-$6EFF  fast ATAN2 final-angle page Q1 (formerly unused V1 table page)
$6F00-$6FFF  fast ATAN2 final-angle page Q2 (formerly unused V1 table page)
$7000-$70FF  fast ATAN2 final-angle page Q3 (V2 donor $9100 remapped away from V1-owned data)
```

`HYBRID_CODE` is source-build configurable. The alternate proof moves it to `$E000-$F1FF` while also moving the normal resident regions, public I/O and ZP base.

### C64 banking

The reference `$A000-$B1FF` region is RAM underneath BASIC ROM. Writes already go to the underlying RAM, but the CPU must see RAM there when executing V5-imported routines. For typical game/demo startup, disabling BASIC ROM once is preferable to banking it for every call because per-call banking would add cycles not included in the published math timings.

## Build model

V5 remains source-reproducible without copying thousands of lines of donor source into a fifth tree. `tools/build_hybrid.py` rebuilds canonical V1 and V2 sources, then acts as a small deterministic linker/relocator for the certified import set. Stable V1 public wrapper addresses are preserved; imported wrapper bodies are replaced in place and their private kernel targets are relocated into `HYBRID_CODE`.

This design means:

- existing callers use the same `MATH_*` names;
- no runtime profile switch exists;
- no dispatcher cycle penalty is added to direct imports;
- only one public `MATH_IO` workspace exists;
- V1's non-reentrant contract remains unchanged;
- sequential calls and ordinary game loops are fully supported.

## Validation evidence

`validation/hybrid/HYBRID_VALIDATION.json` records:

- common 46-entry validation on reference and alternate maps, 4,589 calls each;
- **144,246 direct-import test cases**, including exhaustive 65,536-vector `ATAN2_8` result/cycle parity and an independent <=1 phase-unit error check;
- exhaustive `UMOD8` correctness over all 65,536 input pairs;
- exhaustive `COS8/SINCOS8` phase-domain checks;
- exact V2 cycle-vector parity over thousands of wide-division cases and all trig phases;
- dynamic ZP guards on reference and alternate maps: all 225 bytes outside each 31-byte window remained unchanged;
- mixed-state stress interleaving imported and untouched V1 routines;
- 2,000 cold-load calls across reference/alternate maps without `MATH_INIT`, covering imported paths and an untouched V1 safe path, confirming V1-style optional initialization.

Additional files:

- `HYBRID_DETERMINISTIC_REBUILD.json` — reference and alternate builds reproduce byte-identically;
- `HYBRID_CONFIG_VALIDATION.json` — valid maps accepted and unsafe overlap/I/O/alignment/overflow maps rejected;
- `v5_hybrid_lowzp_reference_validation.json` / `...alternate...` — complete 46-entry validation records.

## Current scope

V5 is a stock-C64 profile. It does not use the REU and does not expose Turbo16/Turbo32 or V4 QS16. It is intended primarily for games/demos that value V1's ZP footprint but have RAM available under BASIC ROM (or another relocatable 4608-byte region) plus three relocatable page-aligned ATAN2 table pages. The exact V5 private-RAM increase versus V1 is 5,376 bytes.

## Q8.8 vector normalization

V5 exposes `MATH_VEC2_NORMALIZE_Q8_8` as part of the common 46-entry API. It intentionally uses the V1-compatible 31-ZP backend rather than importing V2's larger-ZP normalizer: **198.770271 cycles mean**, 129–333 cycles on the deterministic corpus, with the common <=0.3621 degree / <=202-LSB precision contract.
