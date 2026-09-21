# V5 Hybrid Low-ZP profile

## Purpose

V1 and V2 are alternative complete profiles, but their individual algorithms can be mixed safely **at build time** when their scratch and code dependencies are understood. V5 is the first certified hybrid: it keeps V1's low integration pressure while importing V2 routines that can run inside the same 31-byte normal ZP contract.

This is not two complete libraries loaded side-by-side. V5 produces **one resident library, one public I/O block and one 46-entry API**.

## Selection policy

V5 is selected profile-by-profile rather than being a blind V2 transplant. The current refresh keeps the 31-byte V1 normal-ZP contract while repacking division implementations that win under that constraint. V3/V4 REU-specific choices are irrelevant to V5 because V5 is stock-C64.

Current V5 division highlights on the final resident validator are `UDIV8` **59.383**, `UDIV16` **126.386**, `UDIV24` **187.122**, `UDIV32/16` **756.639**, `SDIV16` **171.905**, and `SDIV24` **253.487** mean cycles. Cross-release selection is certified by the separate same-corpus audit, which reports zero regressions across all 23 measured public division-family paths.

Trig imports remain `COS8` 23 cycles, `SINCOS8` 31 cycles, and exhaustive `ATAN2_8` 44.962814 mean cycles with maximum one-phase-unit error.

## Why not import every V2 routine?

V2's performance comes partly from a larger **union** of scratch allocations and, for native `SMUL16`, a 116-byte executable-ZP core. V5's current contract is stricter: the complete library must remain usable with V1's 31-byte normal ZP allocation. Routines requiring additional persistent/executable ZP remain V1 until a separately validated compact remapping exists.

The hybrid builder is therefore a **certified selector**, not an unsafe arbitrary binary mixer.

## Memory map

Reference V5 keeps the normal `$02-$20` 31-byte ZP window. Its principal relocatable private block is now:

```text
HYBRID_CODE              $A000-$BDFF   7680 bytes
ATAN2 private table pages $6D00-$70FF          4 x 256 bytes
```

The division refresh also uses profile-free signed-division islands recorded in `HYBRID_BUILD_MANIFEST.json`; the exact total private-RAM increase versus V1 is **9,633 bytes**. Within `HYBRID_CODE`, the lower 4 KiB remains the relocated V2 division block, `$B000-$B1FF` retains the modulo/trig/cosine region, the refreshed signed-16 magnitude core uses the `$B200` area, and the direct UDIV16 engine occupies the high `$B800-$BDC9` region.

`HYBRID_CODE` is source-build configurable. The alternate proof moves its base to `$E000`, producing `$E000-$FDFF`, while also relocating the normal resident regions, public I/O and ZP base.

### C64 banking

The reference `$A000-$BDFF` block is RAM underneath BASIC ROM. Writes already reach underlying RAM, but the CPU must see RAM there while imported code executes. Games/demos normally disable BASIC ROM once rather than bank it per call.

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

V5 is a stock-C64 profile. It does not use the REU and does not expose Turbo16/Turbo32 or V4 QS16. It is intended primarily for games/demos that value V1's ZP footprint but have RAM available under BASIC ROM (or another relocatable 7,680-byte block) plus the documented private division/table islands. The exact V5 private-RAM increase versus V1 is 9,633 bytes.

## Q8.8 vector normalization

V5 exposes `MATH_VEC2_NORMALIZE_Q8_8` as part of the common 46-entry API. It uses the same four-byte-scratch logarithmic-ratio backend as V1 and V2, inside V5's existing 31-byte ZP window: **161.332256 cycles mean**, 90–302 cycles on the deterministic corpus, with the common <=0.3621 degree / <=202-LSB precision contract.
