# Issue #39 — V2 32÷16 isolated page-phase feasibility screen

13 October 2026. **Research-only; do not promote or close issue #39.**

Post-PR100 reference baseline: V2 resident SHA-256
`c3c0898bc61a9836e7f58d1b51088ccc644613bf68d9e4199aa1243c4f164c84`.
The V2–V5 shared unrestricted 32÷16 algorithm owns the kernel source
`U3216_ENTRY` at $4E00 with `U3216_MAIN_END` at $50DE,
and its separate byte-divisor path begins at $5272.

The reproducible symbolic assembler experiment independently attempted 14
isolated shifts, from −48 to +48 bytes, while preserving the public
entry addresses, unrelated source owners, 32/8 island and reference
resident length. The original reference source was reproduced
**byte-for-byte** before any trial.

| Candidate placements | Outcome |
|---|---|
| −48, −32, −24, −16, −12, −8, −4 | Invalid: occupied bytes immediately before $4E00 |
| +4, +8, +12, +16, +24, +32, +48 | Invalid: first collision at $50DE |
| 0 (current placement) | Valid source/reference baseline |

**All 14 alternative layouts were rejected by strict source-ownership
checks before 6502 timing, because the displaced bytes would collide
with an existing owner.** Thus the valid candidate count is zero and
the number of paired old/new CPU executions is zero. This is a **bounded
address-layout infeasibility result**, **not** evidence that a redesigned
kernel or coordinated relocation cannot be faster, and **not** a claim
that all possible 32÷16 optimizations are exhausted.

See `tools/screen_issue39_v2_3216_pagephase.py` and
`validation/review/ISSUE39_V2_3216_PAGE_PHASE_RESEARCH.json`.
The next legitimate architecture screen should modify an instruction
transition within a fixed resource envelope or jointly repack the
conflicting neighbouring source owners, followed by identical-input
UDIV/UMOD ABI/cycle audits across V2–V5.

**No production resident, ABI, ZP ownership or standalone implementation
was changed. OptiSearch remains private. The unsigned-family campaign
checkbox in issue #39 stays unchecked.**
