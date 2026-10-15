# Issue144: unrestricted signed 32×32 SHR16 output-slice EXCLUSIVE overlay

**Source-only opt-in batch accelerator; NOT a safe default MATH_SMUL32 replacement.**

For all sign quadrants and arbitrary 32-bit signed operands, the
ordinary public MATH_SMUL32_SHR16 address $5E15 is preserved.
V1/V5 use the $C575 signed SHR16 adapter; V2/V3/V4 use $C50C.
The 6510 source-backed overlay redirects final full-product stores
within each of four distinct signed producer paths directly into
$C008..$C00D and changes the SHR16 adapter JSR into a JMP so
the normal six-byte output copy is skipped.
Exactly **53 CPU-model cycles saved per call**, independent of operands.

| Profile | Baseline cycles | Opt-in cycles | Saved |
|---|---:|---:|---:|
| v1_balanced | 806.609 | 753.609 | 53.000 |
| v2_pareto_fast | 774.643 | 721.643 | 53.000 |
| v3_reu_512k | 774.643 | 721.643 | 53.000 |
| v4_reu_16m | 774.643 | 721.643 | 53.000 |
| v5_hybrid_lowzp | 806.609 | 753.609 | 53.000 |

**12,045 matched signed 32-bit operand pairs across V1–V5**
pass exact six-byte output, input preservation, carry=0, and stack.
Native x64sc: 240 baseline/opt-in executions pass output and flags;
VICE proves correctness, **not CPU cycle timing**.

Five separately assembled 334-byte BEGIN/END installers,
original-source-derived, examples placed in caller-owned $0900..$0A4D.
Each exact original resident configuration requires its own source
file; they are not interchangeable. 49 existing executable bytes
are patched and restored exactly. CPU model runs both actual
assembled entrypoints and checks original SMUL32 and SHR16 after END.
BEGIN costs **218** CPU-model cycles; END costs **224**.
Counting caller JSR overhead (6 cycles each), a batch of
**9 or more calls** amortizes the 454-cycle setup+teardown cost.

CRITICAL: the shared ordinary signed full producer is NOT valid
while this overlay is active. You MUST NOT call MATH_SMUL32,
the READY alias, any other shared signed consumer, or invoke
signed math from IRQ/NMI during BEGIN, the batch, or END.
Avoid concurrent/multitasking reentry; patch transitions are NOT atomic.
This candidate is distinct from the earlier independently resident
signed nonnegative-input clone: the present one accepts ALL signs
but trades away mixed-call composability until disabled.

Verify exact original resident SHA, original code bytes,
all application live memory occupancy, RAM bank mapping,
MATH_INIT, and that $0900..$0A4D is free before loading.
Do not combine with the optional unsigned $0900 overlay.
BEGIN/END clobber A and processor flags; they do not add ZP.

Source: optional/issue144_signed_shr16_exclusive/v1_balanced.asm
Source: optional/issue144_signed_shr16_exclusive/v2_pareto_fast.asm
Source: optional/issue144_signed_shr16_exclusive/v3_reu_512k.asm
Source: optional/issue144_signed_shr16_exclusive/v4_reu_16m.asm
Source: optional/issue144_signed_shr16_exclusive/v5_hybrid_lowzp.asm
Generator/model: tools/issue144_signed_full_exclusive.py
Native VICE: tools/native_issue144_signed_full_exclusive.py
CPU proof: validation/review/ISSUE144_SIGNED_SHR16_FULL_EXCLUSIVE_MODEL.json
Installer proof: validation/review/ISSUE144_SIGNED_SHR16_FULL_EXCLUSIVE_INSTALLER.json
Native proof: validation/review/ISSUE144_SIGNED_SHR16_FULL_EXCLUSIVE_NATIVE_VICE.json

Default resident PRGs/REUs, normal API, zero page, public
PERFORMANCE leaderboard and main library binary are unchanged.
No private OptiSearch generator/source is published.
