# Quake64 prepared-fraction real-build results — 2026-09-17

**Status:** ACME / relocation / heap integration gate passed for both unrolled and compact nearest-Q0.16 candidates. Emulator/scene runtime gate is still pending.

Audited target:

```text
Kweepa/Quake64 @ 7c84654946a60314568b709e7e7b97467fed69df
ACME 0.97 (Zem)
Python 3.12.14
```

The experiment modifies only the near-plane interpolation path:

```text
.near0 / .near1
    dynamic strict fraction 0<n<d
    PREP once
    APPLY signed16 X delta
    APPLY signed16 Y delta
```

The shared `.nlrun -> scale_nd + lerp16` path remains intact for the other Cohen-Sutherland clipping planes.

## 1. Authoritative real-build pipeline

GitHub Actions checks out three identical audited Quake64 snapshots and runs the same GAME build gate on each:

```text
baseline
unrolled nearest prepared fraction
compact nearest prepared fraction
```

Each build runs:

```text
source generators
ACME support assets / overlay
GAME first ACME pass
mkreloc.py
GAME second ACME pass
checkheap.py
```

Workflow evidence:

```text
run             35259498923
head commit     5b052c8d95845f1309308af6f5dc5fd149cec150
conclusion      success
artifact        quake64-nearclip-real-build
artifact id     10514185994
artifact digest sha256:07199cecd9e0b32444158b06a3373cc83f13dc2fd31f7bb7685cc1231e5a75eb
```

All three second-pass GAME builds and all three heap checks passed.

## 2. Actual GAME footprint

| Build | `end_game` | `game.prg` bytes | Increment vs baseline |
|---|---:|---:|---:|
| baseline | `$9BCF` | 37,585 | — |
| unrolled nearest | `$9FB6` | 38,584 | **+999 B** |
| compact nearest | `$9D19` | 37,915 | **+330 B** |

The source-level standalone kernels assemble to 1,033 B unrolled and 364 B compact. The net GAME deltas are 999 B and 330 B because the near-clip patch itself also removes the old stack save/restore instructions around X/Y interpolation.

The actual compact candidate therefore buys back **669 bytes** relative to the unrolled real build, exactly matching the standalone code-size delta.

## 3. Real Quake heap gate

Quake64's own `checkheap.py` reports:

| Level | Baseline slack | Unrolled slack | Compact slack |
|---|---:|---:|---:|
| E1M1 | 2338 B | 1339 B | **2008 B** |
| E1M2 | 1033 B | **34 B** | **703 B** |
| E1M3 | 2788 B | 1789 B | **2458 B** |
| E1M4 | 2500 B | 1501 B | **2170 B** |

This corrects the earlier placement-only estimate. The real audited baseline has only **1033 bytes** of slack in E1M2, not the roughly 2980 bytes inferred before the full build chain was exercised.

The unrolled kernel technically fits, but leaves only **34 bytes** in the tightest level. Under the implementation-plan resource law that is not a healthy production Pareto point.

The compact candidate leaves **703 bytes** in E1M2. That is still a meaningful cost relative to baseline, but it is a substantially more credible integration point.

## 4. Speed/size Pareto result

On the paired 5,000-edge strict near-clip stress corpus:

| Candidate | Code | PREP mean | APPLY mean | X+Y pair mean | Gain vs current Quake pair | Max error |
|---|---:|---:|---:|---:|---:|---:|
| compact nearest | **364 B** | 917.424 | 243.058 | **1403.540** | **60.02%** | **1** |
| unrolled nearest | 1033 B | **711.760** | 243.058 | **1197.876** | **65.88%** | **1** |
| Quake current | existing | — | — | 3510.294 | baseline | stress max 107 |

Machine-readable benchmark evidence:

```text
QUAKE64_PREPARED_COMPACT_5000.json
workflow run     35259126799
artifact digest  sha256:ab1748d3097cef29d7a689f0db9e1dcf6d40296dbe8bfc30bbd95f0a8251bdb9
```

The broad stress-corpus error for Quake's current reduced-ratio path is not a claim about visible error frequency in normal gameplay. The relevant prepared-fraction result is that both nearest candidates produced zero prepared-contract failures and maximum integer error one.

### Pareto cost of compact PREP

Compared with unrolled nearest:

```text
compact adds        205.664 cycles per PREP+2xAPPLY pair
                    +17.17%

compact saves       669 bytes
                    -64.76% standalone kernel size
                    +669 bytes E1M2 heap slack in the real build
```

This is the kind of trade the implementation plan asks us to make at **scene/resource level**, not by cycle count alone.

## 5. Current M2 integration decision

The real build changes the preferred Quake proof point:

```text
unrolled nearest
    fastest demonstrated Quake-native point
    real E1M2 slack: only 34 B
    -> research speed ceiling, not preferred production point

compact nearest
    ~17% slower than unrolled prepared path
    still ~60% below current Quake arithmetic pair on stress benchmark
    real E1M2 slack: 703 B
    max prepared error: 1
    -> leading real-game Pareto point
```

This strengthens the M2 case for **prepared dynamic fractional scaling** while weakening the case for publishing the largest/faster implementation by default.

The useful capability is not “we have a 1 KiB divider that benchmarks faster.” It is:

> A real C64 3D engine can replace a repeatedly normalized dynamic interpolation ratio with a prepared <=1-error fraction, retain hundreds of bytes of its tightest heap margin, and substantially reduce the arithmetic region.

## 6. What has passed and what has not

Passed:

```text
real audited Quake64 source patch
ACME 0.97 assembly
relocation regeneration
second-pass GAME assembly
Quake64 checkheap.py
compact/unrolled same-input arithmetic benchmark
prepared-contract correctness on 5,000 edges / 10,000 components
```

Not yet passed:

```text
actual C64/VICE scene execution of the patched GAME
near0/near1 visual/gameplay regression test
representative scene timing with VIC DMA + IRQ + SID active
full Quake64 disk/package build and play-through
stable C64 Math Library ABI/profile integration
```

Therefore this is **real-build evidence, not release certification**.

## 7. Next gate

Use compact-nearest as the first runtime experiment because it is the healthier real-game Pareto point. The next test should load the patched Quake64 build in x64sc/VICE and exercise repeated near-plane crossings while checking:

- no clipping cracks, stalls or corrupt endpoints;
- both near0 and near1 orientations;
- negative/positive X and Y deltas;
- room transitions and E1M2 heap pressure;
- actual per-frame timing rather than isolated arithmetic timing.

If that passes, M2 has enough real-game evidence to design a checked portable `FRAC16_PREP` / `FRAC16_APPLY_S16` contract. The exact broad `UMULDIV16` should remain a fallback/research primitive rather than become the headline M2 API.
