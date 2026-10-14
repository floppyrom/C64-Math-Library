# Issue #144 — Exclusive V2 direct-result-slice UMUL32_SHR16 research

**Research qualification PASS; not a composable standard library routine.**

The current public shifted-output routine computes a full unsigned 64-bit
product and then performs six output-byte copies. An exclusive source-backed
overlay redirects the six high-result stores into the desired shifted
destination and suppresses the two discarded-result stores. A tail-dispatch
removes the secondary output copy loop. The low-order multiplication
arithmetic still executes and preserves its carries into bit 16.

## Paired public-call baseline (same 2,409 pairs across every profile)

| Profile | UMUL32 | UMUL32_SHR16 | SMUL32 | SMUL32_SHR16 |
|---|---:|---:|---:|---:|
| v1_balanced | 712.235 | 775.235 | 743.609 | 806.609 |
| v2_pareto_fast | 690.235 | 753.235 | 711.643 | 774.643 |
| v3_reu_512k | 690.235 | 753.235 | 711.643 | 774.643 |
| v4_reu_16m | 690.235 | 753.235 | 711.643 | 774.643 |
| v5_hybrid_lowzp | 712.235 | 775.235 | 743.609 | 806.609 |

These timings are CPU-model public entry through RTS; caller JSR and
input writes are excluded. This is a *single matched 2,409-pair corpus*.
Different historical performance rows use different samples.

## V2 exclusive overlay result

- Regular public MATH_UMUL32_SHR16: **753.235 CPU-model cycles**.
- Exclusive direct-slice candidate: **700.235 CPU-model cycles**.
- Saving: **53 cycles (7.04%) for each of 2,409 pairs**.
- BEGIN cost: **76 cycles**; END cost: **80 cycles**
  (entry-through-RTS, excluding each caller JSR).
- Crossover: positive batch saving starting at **3 calls** under the
  entry-only convention, or **4 calls** counting both caller JSRs.
- Native x64sc baseline/temporarily patched proof: 48 calls PASS.
- Native x64sc baseline/source-assembled BEGIN/CALL/END proof:
  48 calls PASS. Native cycle timing **was not** measured.
- V2 ordinary public producer was revalidated after END under
  CPU-model execution. This does not prove IRQ/reentrancy safety.

## Exact operating restrictions

This kit targets **only the SHA-pinned V2 profile**. Call MATH_INIT
before BEGIN. Between BEGIN and END, do **not** invoke MATH_UMUL32,
MATH_UMUL32_READY or any other routine transitively relying on its
shared 32-bit unsigned producer. Disable any IRQ/NMI use of that core;
the overlay is non-reentrant. Ensure patched RAM is visible and the
kit's chosen code address does not overlap your program. The example
origin $0900 may be changed before assembly.

The current source writes 13 executable bytes to a *shared* core.
Patch installation/removal and possible code/data mapping hazards
make it unsuitable for automatic use in a mixed-call public profile.
For an eventual standalone builder, a private-core duplicate or
an explicitly exclusive selected-routine bundle is required.

The published production PRGs, REU payloads, ABI, ordinary normal ZP
budgets and PERFORMANCE.md are **unchanged**. OptiSearch P40 remains
private; no private code is included here.

## Reproduction

- Source: optional/issue144_v2_umul32_shr16_exclusive/overlay_begin_end.asm
- CPU model: tools/issue144_shr16_direct_slice_overlay_research.py
- ASM batch crossover: tools/qualify_issue144_v2_shr16_batch.py
- Native VICE: tools/native_issue144_shr16_overlay.py and
  tools/native_issue144_shr16_batch_source.py
- Proof records: validation/review/ISSUE144_SHR16_DIRECT_SLICE_OVERLAY_RESEARCH.json, validation/review/ISSUE144_V2_SHR16_BATCH_BREAK_EVEN.json, validation/review/ISSUE144_SHR16_OVERLAY_NATIVE_VICE_RESEARCH.json, validation/review/ISSUE144_V2_SHR16_BEGIN_END_NATIVE_VICE.json
