# Historical UMUL24/SMUL24 donor ranking on identical full public calls

This is the next phase of the operation-first C64 performance transition after
the signed32/32 recovery in PR #302 (tracked under issue #303).

## What this tests

The operation-first C64 builder currently has independently linkable compact
UMUL24 (156 executable bytes, 9 ordinary scratch, zero ZP) and SMUL24
(227 executable bytes, 9 ordinary scratch, zero ZP). These are exact
portable shift/add products and are **not historical-fastest speed donors**.

All five initialized, unchanged resident V1–V5 implementations are compared
with both compact operation-first sources at $8000 and $7123, using the same
384 signed/unsigned 24-bit input pairs. We check the complete six-byte
product, carry=0, caller X24/Y24 preservation, and stack integrity. Report
each candidate's public entry-through-RTS mean, p95, maximum cycles and
operand-category costs. Record actual released PRG, REU and new linked-image
SHA256s along with the deterministic corpus digest.

Reproduce:

    python3 tools/research_umul24_smul24_parity.py --cases 384 \
      --out build/umul24_smul24_donors.json

The previously published fastest-profile figures (~417.78 cycles for UMUL24,
~467.34 for SMUL24 in the V2 Pareto profile on DIFFERENT corpora) are merely
donor triage context. This research script **must not be used as an authenticated
automatic speed model** because historical and new source placements, table
ownership, ZP/SMC contracts and possible REU/initialization differ.

## Next migration after donor ranking

1. Identify the fastest real public producer per signedness and operand mix,
   including code/table sharing, zero page and stack resources.
2. Recover relocatable source and complete dependencies, using authenticated
   immutable lookup tables and the carry-safe quarter-square offset technique
   where warranted. Do not silently replace the historic source geometry.
3. Build independent UMUL24/SMUL24 aliases in the operation-first selector,
   keeping existing compact 0-ZP routines as resource options.
4. Test the full public X24/Y24/Z48/C ABI at $8000 and $7123 with real native
   VICE r46284, mixed calls, source immutability, and initialization checks.
5. Compare the transplanted linked variants at identical placement and corpus,
   report maximum call and busiest arithmetic-only frame as well as mean, and
   promote to speed selection only after all qualification passes.
6. Preserve the released V1–V5 binary, quarter-square data and source evidence.

No old profile is removed by this research PR. Drive/REU/Turbo hardware
qualification remains a separate migration workstream.
