# Issue #39 — V1 Balanced 69-byte shared-subtraction 24÷8 DIV/MOD release

**12 October 2026.** Source-backed improvement for both V1 public entries `MATH_UDIV24` and `MATH_UMOD24`. The remaining unsigned DIV/MOD campaign is **still open**.

The pre-existing bounded 24÷8 V1 helper handles nonzero 8-bit divisors with a full-width numerator. Its prior 84-byte loop had two subtract blocks, an unconditional jump and separate handling of the ninth remainder bit. The new **69-byte** implementation loads the partial remainder before testing carry (LDA preserves C); the non-overflow path uses CMP D0 to set carry, letting both branches share exactly one SBC/STA/INC sequence. All 24 iterations and the public Q/R/C semantics remain unchanged. The 15 now-free bytes at the end of the original code island are explicitly zeroed in the canonical source.

**No changes to** public ABI/entry addresses, N/D preservation, normal zero page, stack reservation, resident PRG length, or the V2–V5 resident images (including V5's separately imported V2-derived 24-bit engine).

## Public-entry paired 6502 instruction-cycle results

| Case | Old V1 | New V1 | Calls improved per API | Slower |
|---|---:|---:|---:|---:|
| UDIV24 4,753 canonical pairs | 170.726699 | **170.238165** | 82 | **0** |
| UMOD24 1,553 canonical pairs | 248.317450 | **246.822279** | 82 | **0** |
| 4,080 full-width numerator / 8-bit divisor pairs | 1220.796078 | **1202.296814** | 3,779 | **0** |
| 256 small-divisor pairs | 1222.847656 | **1204.648438** | 244 | **0** |

The repeatable archived-old/current-new public-entry screen executes **48,388** old/new machine-code calls: exact arithmetic, quotient/remainder/carry, preserved N/D plus sentinel bytes, stack and **no per-call regression**. These are CPU instruction cycles including RTS, not native VICE wall-clock or DMA timing.

Independent full-resident native VICE x64sc validation ran **256 calls** (64 inputs × two APIs × two images), with old/new output equality and an independent quotient/remainder/carry and N/D oracle. This is a **correctness** certificate, not native cycle timing. The full library also passed **822,050 unsigned** and **364,533 signed** DIV/MOD correctness calls, **136,335 common-input** profile calls and **53,760 seven-workload** small-width calls.

**Reference SHA-256:** new V1 `28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0`; V5 unchanged `5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222`.

**Reproducibility:** `tools/screen_issue39_v1_24by8_shared_subtraction.py` reconstructs its prior V1 input image from the current released source; the proof is `validation/review/ISSUE39_V1_24BY8_SHARED_SUBTRACTION_PAIRED.json`. The canonical source is `relocatable_source/v1_balanced/udiv24_latency_escape_balanced.inc`, and exact public executable mirrors are published under `v1_balanced/standalone/`. The native VICE correctness result is recorded in `validation/review/ISSUE39_V1_24BY8_SHARED_SUBTRACTION_NATIVE_VICE.json`.

The previous isolated screen note `docs/ISSUE39_V1_UDIV24_SHARED_SUBTRACTION_SCREEN_2026-10-12.md` records the unmerged investigation. This release does **not** establish a globally optimal divider or close #39.
