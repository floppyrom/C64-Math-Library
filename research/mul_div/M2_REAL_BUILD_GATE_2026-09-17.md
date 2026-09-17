# M2 real-build gate update — 2026-09-17

This document supersedes the **resource/placement estimates** in `M2_GATE_DECISION_2026-09-17.md`. The architectural decision from that document still stands: prepared dynamic fractional scaling is the leading M2 capability, while broad exact `UMULDIV16` remains research/fallback machinery.

## Gate result

A real audited Quake64 build has now passed for both the fast unrolled and compact nearest-Q0.16 prepared-fraction candidates.

```text
Quake64 source  7c84654946a60314568b709e7e7b97467fed69df
ACME            0.97 (Zem)
workflow run    35259498923
head            5b052c8d95845f1309308af6f5dc5fd149cec150
result          PASS
```

The workflow builds an untouched baseline and both experimental variants through:

```text
ACME first pass
mkreloc.py
ACME second pass
checkheap.py
```

All three pass.

## Corrected memory picture

The old placement-only estimate assumed roughly 2.98 KiB of tightest-level slack. The actual audited baseline is tighter:

| Build | GAME end | Net GAME delta | E1M2 slack |
|---|---:|---:|---:|
| baseline | `$9BCF` | — | **1033 B** |
| unrolled nearest | `$9FB6` | +999 B | **34 B** |
| compact nearest | `$9D19` | +330 B | **703 B** |

Therefore the unrolled candidate is a useful speed ceiling but a poor real-game resource point. It consumes essentially the entire E1M2 margin.

The compact candidate is now the preferred Quake proof point. It trades about 206 cycles per PREP+two-APPLY pair for 669 bytes of recovered GAME/heap space.

## Corrected speed/size gate

On the same 5,000 strict near-clip stress edges:

| Path | Complete kernel | Pair mean | Gain vs current Quake pair | Max error |
|---|---:|---:|---:|---:|
| unrolled nearest | 1033 B | **1197.876** | **65.88%** | 1 |
| compact nearest | **364 B** | 1403.540 | **60.02%** | 1 |
| Quake current | existing | 3510.294 | baseline | stress max 107 |

`compact nearest` therefore passes the implementation-plan resource test more convincingly: it remains decisively faster than the real game workaround, preserves the same <=1 prepared error contract, and leaves 703 bytes rather than 34 bytes in the tightest Quake heap gate.

## Current M2 decision

The gate is now:

```text
Hard-to-fake workload                 PASS
Realistic game alternative measured   PASS
Arithmetic correctness/error contract PASS
Real source patch                      PASS
ACME build                             PASS
Relocation regeneration                PASS
Quake heap gate                        PASS
Healthy Pareto resource point          PASS: compact nearest
Actual emulator/gameplay regression    PENDING
Scene-wide VIC/IRQ/SID timing           PENDING
Portable stable library ABI            PENDING
```

This means M2 is beyond synthetic research and has a real-build proof. It is **not release-complete yet**, because the final implementation-plan rule is scene-level usefulness on the actual machine/emulator.

## Next gate

Run the compact-nearest patched GAME under x64sc/VICE, exercise both near-plane orientations and representative E1M2 scenes, and verify:

1. no clipping cracks or endpoint corruption;
2. no SMC/table/banking conflicts;
3. room transitions remain stable under the 703-byte E1M2 margin;
4. the arithmetic saving survives normal VIC DMA, IRQ and SID load;
5. the scene/frame budget improves enough to justify a portable API.

If that passes, freeze the semantic contract before touching the stable library API:

```text
FRAC16_PREP
    trusted/internal: 0 < n < d
    checked/public wrapper semantics to be decided
    nearest Q0.16 default

FRAC16_APPLY_S16
    signed16 component
    max integer deviation from exact trunc(component*n/d) <= 1
```

Exact general `UMULDIV16` should remain available as research/fallback but should not become the headline M2 routine solely because it beats primitive composition.

Full build evidence: `QUAKE64_REAL_BUILD_RESULTS_2026-09-17.md`.
Machine-readable compact benchmark: `QUAKE64_PREPARED_COMPACT_5000.json`.
