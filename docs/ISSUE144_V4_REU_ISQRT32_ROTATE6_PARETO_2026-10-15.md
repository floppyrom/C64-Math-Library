# Issue #144 C — V4 16-MiB REU ISQRT32 exact in-place rotate-six optimization

**Full unsigned 32-bit radicand domain; original REU mapping and lookup data preserved.**

V4 differs from non-REU ISQRT32 (PR #155): its $C8FC REU producer
computes a REU address and performs a four-byte DMA before radix-4
refinement. Two source-backed runs of **six ASL A instructions**
at $C90B and $C924 follow `AND #$03` and compute `x << 6`.
For x in 0..3, the exact six-byte in-place substitution is:

```asm
lsr a
ror a
ror a
bcc +1   ; skip one-byte NOP, carry provably clear
nop
```

This emits identical A/N/Z/C/V outputs and does not change X/Y.
The branch is taken for all x in 0..3, producing the same address.
Each substituted site executes in **9 rather than 12 cycles**;
two sites yield a constant **6 CPU-model cycles saved/call**.
Source opcode bytes are `4A 6A 6A 90 01 EA`, unchanged six-byte
footprint per site, no extra production code/ZP/data/REU payload.

## Public-call CPU-model performance on canonical identical inputs

| Profile | Original mean | In-place optimized mean | Saved | Inputs |
|---|---:|---:|---:|---:|
| V4 16-MiB REU | 917.317433 | 911.317433 | 6.000000 | 4,130 |

All 4,130 baseline/candidate comparisons pass exact root and
unchanged four input bytes, C, X/Y, N/Z/V/D and SP; ordinary
ISQRT16 calls were interleaved every 199 cases. Minimum and
maximum paired saving are also exactly six cycles. The actual
CPU model loads the original 16-MiB REU reference image.
Native real x64sc loads the same 16-MiB REU image and compares
**24 baseline plus 24 candidate executions**, identical roots
and full PHP status bytes. Native/VIC-II/REU DMA wall time is
**not measured or claimed to improve by exactly six cycles**.

## Optional use and resource contract

Use the per-profile 6510 BEGIN/END source under `optional`.
Its example caller-owned $0D00 installer occupies 88 bytes;
CPU-model entry costs **66 cycles BEGIN**, **56 END**, excluding
any real caller JSR. If called as subroutines, setup/teardown
with two JSRs costs ~134 cycles, so **23 or more calls**
amortize the runtime patch. A custom builder may apply the same
twelve byte substitutions at build-time with zero runtime
setup cost, but must qualify the complete resident image.
This source-only release does NOT modify the shipped resident.

Require the exact V4 resident image, original 12 ASL bytes
verified, writable RAM at $C90B/$C924, normal MATH_INIT,
existing REU image and exclusive install/restore. Do NOT
run any IRQ/NMI or concurrent math while patching executable
code: 12 byte changes are not atomic. Check $0D00–$0D57
really belongs to the application before loading installers.
Original public entry $5E30 and normal resource budgets unchanged.

Assembly: optional/issue144_v4_reu_isqrt_rotate6/v4_reu_16m.asm
Canonical CPU and restoration reproducer: tools/issue144_v4_reu_rotate6_peephole.py
Native real x64sc/16-MiB REU reproducer: tools/native_issue144_v4_reu_rotate6.py
Model proof: validation/review/ISSUE144_V4_REU_ISQRT32_ROTATE6_MODEL.json
Native proof: validation/review/ISSUE144_V4_REU_ISQRT32_ROTATE6_NATIVE_VICE.json
No private OptiSearch source is included.
