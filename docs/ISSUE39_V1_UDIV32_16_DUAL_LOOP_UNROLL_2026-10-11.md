# Issue #39 — V1 Balanced 32/16 public divider dual-loop unroll

**Date:** 2026-10-11. **Status:** source candidate, subject to independent PR and post-merge CI. The overall unsigned DIV/MOD campaign remains open.

## Architecture and ownership
The V1 32/16 source already has two fixed restoring quotient loops. Their bodies have no absolute operands, no side-effectful X use, and only intra-body relative branches. Replace the DEX/BNE at **$4570** (15-round low quotient loop) and **$446A** (16-round conditional high quotient loop) with 3-byte JMPs into position-independent, repeated byte-identical bodies. Keep the first iteration in place, emit the remaining 14 + 15 copies, and restore X=0 before the original epilogues. No new input classifier or dispatch penalty.

The reference island **$1900–$1CF7** is initially zero and contains **1,016 occupied bytes**. Earlier placement into $6C8C collided with V5 hybrid ATAN2 tables, so that trial was *discarded*. The final REG_LOW island rebuilds symbolically in reference and alternate configurations, leaves V5's ATAN2 tables available, adds **zero normal-ZP bytes**, and preserves API addresses and resident PRG length. V5 imports the V1 base image but its active 32/16 API uses the existing V2-derived code; this work does not claim a V5 cycle gain.

## Paired public-entry cycle evidence
Identical deterministic operands, 6502 instruction cycles including routine return; no REU-bus wall-clock claim.

| V1 public operation | Prior mean | Candidate mean | Saved | Faster / equal / slower |
|---|---:|---:|---:|---|
| UDIV32_16 (2,729 operands) | 896.061561 | **825.873947** | 70.187615 | 2,578 / 151 / 0 |
| UMOD32_16 (1,705 operands) | 916.280352 | **843.629912** | 72.650440 | 1,554 / 151 / 0 |

The six independent 512-pair workloads also exhibit **zero new regressions**. For UDIV32_16, mean cycles change: full-width uniform 861.439→795.410; 24-bit numerators 733.881→669.412; 16-bit numerators 665.225→600.998; small divisors 1698.746→1563.240; power-of-two divisors 1494.492→1378.676; quotient-zero/one 659.979→595.840. Maximum measured improvement is 136 cycles/call. This is an executable source synthesis of the loop-unrolling architecture; it is **not** a native OptiSearch timing record or global-optimality proof.

## Qualification
The permanent `tools/validate_v1_3216_unroll.py` reconstructs the previous loops in memory and checks **10,578 same-input pairs / 21,156 executions**, outputs, carry, input preservation, and that no case regresses. Local V1 unsigned validation passed 164,410 calls and signed validation 97,329. Native VICE x64sc full-resident old/new checks matched 80 public calls per image, with the executable reporting VICE 3.10 (the saved archive filename says 3.13.2). Reference source regeneration is byte-identical to the candidate; alternate relocation and V5 hybrid reference/alternate builds succeed, and V5 hybrid mixed-call validation passes.

**Publication gate:** regenerate the shipped resident and hybrid PRGs, all-profile validations and comparable benchmarks, source mirrors, consolidated and public indices, both changelogs, README/manual, release-status metadata, SHA256SUMS/package audit, and pass independent PR/main CI. OptiSearch's `range-local-unroll` vocabulary and strategy contracts were inspected, but the private engine is not in this repository and no native 32/16 record has been claimed. Follow-up campaign audits remain outstanding.
