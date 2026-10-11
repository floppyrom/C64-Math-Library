# V5 zero-ZP UDIV32/32 + UMOD32/32: prechecked divisor gate

**Date:** 2026-10-11. **Profiles:** V5 Hybrid Low-ZP only.
**ABI:** Existing stable entries, Q/R results, carry flag and N/D input preservation.
**Additional ZP:** 0. **PRG size:** unchanged (49,042 bytes).

## Finding

The early V5 32/32 dispatcher checks `D==0`, `N<D` and `N==D`.
Once control reaches the `N>D` case, the divisor must be nonzero.
The old shared fallback copied operands into private scratch and checked
`D==0` a second time. The optimized fallback branches directly to
the prechecked long-division entry.

For divisor zero, a jump reaches the existing all-zero Q/R, carry-set
handler. Four BNE targets in the early gate move to an unused, three-byte
JMP island; the shared call at `$C130` skips the redundant test.
No public entry is relocated.

**Private scratch caveat:** the divisor-zero short path no longer copies
private `$C040..$C047`. Private scratch is not a public ABI output.
Do not depend on its contents after division.

## Paired deterministic performance

| API | Old mean cycles | New mean cycles | Savings | Cases |
|---|---:|---:|---:|---:|
| UDIV32/32 | 421.077342 | 409.633142 | 11.444200 (2.72%) | 6,801 |
| UMOD32/32 | 548.000000 | 537.266581 | 10.733419 (1.96%) | 1,553 |

Both retain 0 additional ZP; reachable unique code decreases from
946 to 931 bytes. These are deterministic-corpus instruction cycle
means, not exact cycle means over all 2^64 operand pairs.

## Qualification evidence

- 21,508 paired original/candidate calls across the two entry points,
  zero arithmetic or carry mismatches and no negative cycle deltas.
- Fresh V5 unsigned DIV/MOD family: 164,410 calls, zero errors.
- V5 signed DIV/MOD regression: 36,273 calls, zero errors.
- The source-built reference PRG is byte-identical to the independently
  patched 49,042-byte candidate.
- V5 alternate-map build and hybrid validation passed.
- Public source catalog 320/320, standalone-source consistency
  1,617/1,617, package audit 30/30.

All five profiles are in the continuing unsigned DIV/MOD campaign;
**this change is not a declaration that the entire family is optimized**.
It applies only to V5 shared UDIV32/32 and UMOD32/32. V1–V4 and REU
payload images are unchanged.
