# Issue144 A — independent signed32 SHR16 direct producer; mixed-call safe

**Individually accessible opt-in implementation for ALL signed 32-bit inputs.**
Unlike the exclusive overlay, this source makes a separate copy of the
original published full signed producer rather than modifying it.
The nine (V2/V3/V4) or ten (V1/V5) executable source islands and
their absolute self-modifying operand-byte references are relocated
into caller-owned RAM. The producer writes only the exact six output
bytes from product bits 16–63 without an intermediate eight-byte
full product + six-byte copy.

The original SMUL32 and UMUL32 residents remain executable;
sequential calls to both normal producers were interleaved in all
CPU-model and native VICE comparisons. Ordinary SHR16 public JMP
address remains $5E15; an optional *in-memory* two-byte target patch
at $5E16/$5E17 directs calls to the independent entry.
This opt-in does not alter binary files on disk.

## Paired same-input public-call CPU-model cycles

| Profile | Original | Independent | Saved | Smallest gain | Code bytes |
|---|---:|---:|---:|---:|---:|
| v1_balanced | 806.609 | 750.611 | 55.998 | 55 | 1405 |
| v2_pareto_fast | 774.643 | 720.949 | 53.694 | 36 | 1371 |
| v3_reu_512k | 774.643 | 718.751 | 55.892 | 55 | 1371 |
| v4_reu_16m | 774.643 | 718.751 | 55.892 | 55 | 1371 |
| v5_hybrid_lowzp | 806.609 | 750.611 | 55.998 | 55 | 1405 |

**12,045 paired 32-bit signed corpus calls** across five profiles
(2,409 same operand pairs/profile). Every candidate call is faster;
all six output bytes, inputs, carry=0 and stack match, and normal
SMUL32/UMUL32 calls succeed when interleaved.
Independent native x64sc correctness: 240 baseline/candidate calls
across V1–V5, with ordinary signed and unsigned full multiplication
interleaved *before every* SHR16 invocation. Native cycles NOT measured.
Unlike an earlier exclusive overlay, **no BEGIN/END batch overhead**.

## Resource and caller integration contract

Source assemblies are individually usable per profile; assembly
placement is an *example*, not permanently reserved library RAM.
Current emitted code uses $0800..$0DC0 (1405 bytes for V1/V5,
1371 for V2/V3/V4) with gaps between relocated islands.
**On a normal C64 $0801 is BASIC program RAM**; verify caller
ownership and no loader/screen/stack/IRQ/data conflicts, or rebuild
and requalify with a different placement before adoption.
Requires original MATH_INIT, shared installed lookup tables
and the ordinary mathematical scratch ZP. **NOT interrupt/NMI
reentrant:** simultaneous math calls can corrupt shared zero page.
Disable or synchronize other callers while modifying the signed
SHR16 public JMP operands; the two-byte target update is not atomic.
Normal full signed and unsigned producers remain usable between
completed independent SHR16 calls, unlike in the exclusive overlay.
No regular resident PRG, REU payload, public symbol location, normal
ZP budget, or ordinary performance leaderboard is changed.

Assembler sources: optional/issue144_signed_shr16_independent/<profile>.asm
Independent generator and common-input CPU model:
  tools/issue144_independent_signed_shr16.py
Independent real native VICE mixed-call harness:
  tools/native_issue144_independent_signed_shr16.py
CPU proof: validation/review/ISSUE144_SIGNED_SHR16_INDEPENDENT_MODEL.json
VICE proof: validation/review/ISSUE144_SIGNED_SHR16_INDEPENDENT_NATIVE_VICE.json
No private OptiSearch source, donor archive or proprietary method is published.
