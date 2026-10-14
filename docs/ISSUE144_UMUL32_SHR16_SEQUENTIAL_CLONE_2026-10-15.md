# Issue #144 — independent sequential SHR16 multiplier clone

**Validated opt-in Pareto source, NOT an installed default profile replacement.**

The same separate-RAM clone is qualified for two call conventions:
direct JSR $0E03 saves 62 cycles; preserving the installed public
JSR $5E12 entry while replacing its JMP target saves 59 cycles.
The public-entry adaptation changes only two JMP operand bytes
at $5E13/$5E14 and can be reversed by the provided patch source.
It does NOT patch the stock core, unlike the exclusive batches.

Instead of temporarily modifying the standard library's shared
unsigned 32-bit multiplier (PRs #145–#146), this variant clones
its two executable islands to a separate RAM region, relocates
internal absolute code/self-modifying references, and directly
stores the shifted 48-bit product. The original MATH_UMUL32
executable remains untouched by the clone itself. The zero-page
scratch and original immutable quarter-square lookup tables
remain shared, so the calls must be sequential/non-reentrant.

## Shipped public versus independent clone on the same 2,409 pairs

| Profile | Ordinary SHR16 | Cloned SHR16 | Savings | Matched pairs | Native original/clone |
|---|---:|---:|---:|---:|---:|
| v2_pareto_fast | 753.235 | 691.235 | 62 | 2,409 | 48 |
| v3_reu_512k | 753.235 | 691.235 | 62 | 2,409 | 48 |
| v4_reu_16m | 753.235 | 691.235 | 62 | 2,409 | 48 |

All 7,227 model paired cases pass complete 48-bit shifted output,
carry, input/stack invariants. Mixed ordinary MATH_UMUL32 and
MATH_SMUL32 calls were executed before and after each clone call;
the clone did not overwrite the stock executable core. Native
x64sc executes 144 baseline/clone cases across all three profiles.
**62 CPU-model cycles are saved per direct call on every input tested.**
With the original public $5E12 entry retained, the same 7,227
paired inputs save exactly 59 cycles each. An additional 144
native x64sc baseline/retargeted-public-entry calls pass, and
the reversible public JMP installer is source-assembled, checked
in each profile and restores the legacy destination correctly.
Native emulator timing is NOT measured; only correctness is native.

## Exact resource and linking contract

- Clone executable RAM: $0D05–$0E49 (325 address bytes),
  with the public-style alternate entry at $0E03; avoid overlap with
  application code, screen, loader and interrupt hooks.
- Emitted instruction bytes: 317; gaps between islands can
  exist and must remain reserved for the assembled code span.
- Requires the current V2, V3 or V4 C64ML resident, its ordinary
  immutable quarter-square tables ($7000 region), initialized
  pointer state and MATH_INIT, plus existing shared scratch ZP.
- Ordinary full UMUL32 and signed SMUL32 remain callable between
  invocations, unlike the 53-cycle exclusive patch. Do not execute
  either normal and cloned routines simultaneously or from IRQ/NMI:
  shared scratch and code self-modification make this non-reentrant.
- Same result I/O ABI: unsigned 32x32 operands at $C000/$C004,
  six output bytes at $C008–$C00D, C=0, preserved operands/stack.
- This is an opt-in fixed-address specialist source for a future
  builder, NOT an automatic regular MATH_UMUL32_SHR16 replacement.
  The hard-coded clone location is one tested location, not proof
  that any other location or arbitrary user layout is safe.

Current production PRGs, REU images, normal ZP budgets and API
addresses are unchanged. No private OptiSearch source is present.

Independent producer source: optional/issue144_v234_umul32_shr16_independent/standalone_clone.asm
Optional public-entry enable/disable source: optional/issue144_v234_umul32_shr16_independent/public_entry_redirect.asm
Public-entry CPU proof: validation/review/ISSUE144_SHR16_PUBLIC_ENTRY_OPTIN_CPU_MODEL.json
Public-entry native proof: validation/review/ISSUE144_SHR16_PUBLIC_ENTRY_OPTIN_NATIVE_VICE.json
Source-assembled patch/restore proof: validation/review/ISSUE144_SHR16_PUBLIC_ENTRY_INSTALLER_CPU_MODEL.json
Model/test generator: tools/issue144_shr16_independent_clone.py
Native x64sc: tools/native_issue144_shr16_independent_clone.py
Model evidence: validation/review/ISSUE144_SHR16_STANDALONE_CLONE_CPU_MODEL.json
Native evidence: validation/review/ISSUE144_SHR16_INDEPENDENT_CLONE_NATIVE_VICE.json
