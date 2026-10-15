# Issue144: signed 32÷16 full-contract public-entry JMP-chain pruning

**Unrestricted signed input domain; original full quotient AND remainder ABI.**

An arithmetic-source audit found redundant JMP-to-JMP chains before
the actual signed32/16 producer, with profile-specific routing.
This is a true all-input public-call Pareto micro-optimization:
no additional division state, no changed arithmetic producer, and
no worst-case slowdown; only existing JMP target operand bytes change.

| Profile | SDIV stock | SDIV direct | SDIV saved | SMOD stock | SMOD direct | SMOD saved |
|---|---:|---:|---:|---:|---:|---:|
| v1_balanced | 951.776 | 951.776 | 0.0 | 954.776 | 951.776 | 3.0 |
| v2_pareto_fast | 695.891 | 692.891 | 3.0 | 698.891 | 692.891 | 6.0 |
| v3_reu_512k | 695.891 | 692.891 | 3.0 | 698.891 | 692.891 | 6.0 |
| v4_reu_16m | 695.891 | 692.891 | 3.0 | 698.891 | 692.891 | 6.0 |
| v5_hybrid_lowzp | 692.891 | 692.891 | 0.0 | 692.891 | 692.891 | 0.0 |

3279 identical operand pairs/API/profile: 32,790 paired tests,
**65,580 total model public calls**, including all sign quadrants,
divisor zero, signed 32-bit boundary cases, and q0/q1 cases.
Exact quotient Q32, remainder R16, C, X/Y, stack, inputs and
sentinel memory bytes match the original, not just arithmetic.
All model savings are 0, 3 or 6 cycles, **constant per profile/API**.
All 480 native x64sc baseline/optimized public calls pass
the same complete output and status comparisons.
Native correctness tested; native cycle count NOT measured.

## Profile-specific executable routes

- **V1:** SMOD alias `$3FDD JMP $3EE0 JMP $2590`; the
  `$2590` instruction is **JSR**, not a jump. The patch MUST stop
  at `$2590`; only SMOD gains 3 cycles, SDIV unchanged.
- **V2/V4:** SDIV `$3EE0 JMP $2590 JMP $9200` and
  SMOD `$3FDD JMP $3EE0 JMP $2590 JMP $9200`.
  Redirect both public JMP targets to `$9200`.
- **V3:** same but via `$2690` instead of `$2590`.
- **V5:** both public JMPs already target the real signed
  producer at `$5D00`; **zero improvement** so no patch.

## Use and integration safety

Four readable per-profile reversible 6510 enable/disable sources
are under `optional/issue144_signed32_divmod_direct_jump/<profile>.asm`; V5 is explicitly a no-op.
The V1 installer is 22 bytes, V2/V3/V4 installer 42 bytes.
The example source installer RAM at `$0C80` is NOT reserved:
check actual application map or reassemble elsewhere.
Enable+disable **CPU-model cost**: V1 18+18 cycles; V2-V4 30+30
cycles, plus JSR overhead if invoked by subroutine call. For V2/3/4
the patch pays for itself when 3×SDIV_calls + 6×SMOD_calls exceeds
the actual enable/disable invocation overhead. Static builder-time
patching of exactly 2 (V1) or 4 (V2/3/4) JMP operands costs **no**
additional resident code, ZP or data; no V5 patch is needed.

**Changing a JMP target is not atomic.** Never run concurrent math
in an IRQ/NMI or enter either public routine mid-install/mid-restore.
Resident must be writable RAM, or patch the actual generated image
at build time and requalify its checksum. The public API addresses
and both full Q32+R16+carry output contracts remain intact.
Do not attempt to redirect V1 to the `$9200` area, which is not
the V1 signed producer (it contains data).

No production PRGs, REU images, shared ZP, arithmetic core, public
PERFORMANCE leaderboard or normal linker map was changed.
The change is intentionally published as optional, because the
mean benefit is below the general 5% triage heuristic.
No private OptiSearch source or donor code is included.

CPU reproducible benchmark: tools/issue144_signed_divmod_alias_direct_research.py
Model-generated installers: tools/issue144_signed32_divmod_alias_installer.py
Native VICE: tools/native_issue144_signed32_divmod_alias_direct.py
CPU evidence: validation/review/ISSUE144_SIGNED32_16_DIRECT_PUBLIC_JUMP_RESEARCH.json
Installer evidence: validation/review/ISSUE144_SIGNED32_16_DIRECT_PUBLIC_JUMP_INSTALLER.json
Native evidence: validation/review/ISSUE144_SIGNED32_16_DIRECT_PUBLIC_JUMP_NATIVE_VICE.json
