# Issue144 D — V2 SEEK16_INIT speed-one relocated research

**RESEARCH ONLY: NOT PROMOTED TO DEFAULT V2, REU OR OTHER PROFILES.**

An earlier in-place speed-one candidate (rejected PR #142) overwrote
the occupied foreign byte at $19F0 and active table at $1A00.
This source-backed test instead copies the entire INIT executable
island to separately available caller RAM $0D00-$0E22, while
retaining resident SEEK16 helper islands/zero-page and public object
state. A disposable copy of the public JMP $5E48 points at the
new island; the installed resident PRG is unchanged.

291-byte candidate versus 270-byte original mirror (+21 bytes),
300 identical operand/vector INIT tests with all 248 state bytes,
caller X, carry and SP checked, followed by STEP and state comparison.
Overall mean gain **4.227 CPU-model cycles**;
the speed-one workload gains about 16.7 cycles but some operands
regress up to 18 cycles. Other speeds can regress, thus this does
not qualify for the 5% general-call default-promotion heuristic.

Native VICE uses four diverse V2 scenarios, 64 baseline STEP
calls and 64 optimized STEP calls, all output/flags/stack
identical. Native cycle timing is NOT measured.

The exported source is an exact public standalone executable
mirror relocated with independently applied fastpath, not an
independent reusable SEEK engine. The example $0D00-$0E22
RAM must be proven free in the actual application layout.
No code or data may be placed over $19F0/$1A00.

Source: optional/issue144_seek16_k1_relocated/research_source.asm
Generator and model tests: tools/issue144_seek16_k1_relocate.py
Native x64sc: tools/native_issue144_seek16_k1_relocate.py
CPU proof: validation/review/ISSUE144_SEEK16_K1_RELOCATED_RESEARCH.json
Native proof: validation/review/ISSUE144_SEEK16_K1_RELOCATED_NATIVE_VICE.json
No private OptiSearch code; all normal V1-V5 PRGs, REUs and public
PERFORMANCE leaderboard remain unchanged.
