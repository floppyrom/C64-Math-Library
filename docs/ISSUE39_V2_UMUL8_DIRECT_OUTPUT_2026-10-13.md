# Issue39 V2 UMUL8 zero-growth direct-output optimization

13 October 2026. This is a **native-qualified source release; independent PR/main CI pending**.

Manual technique: replace the public UMUL8 copy of the low product byte from a shared zero-page temporary with a direct write to public MATH_Z in the quarter-square producer. The low-byte write preserves carry for the high-byte subtraction. The 37-byte kernel starts at $52FE, using two previously empty bytes before the original 35-byte $5300 kernel. The 14-byte public wrapper leaves five NOP padding bytes in its former 19-byte slot. Executable byte span and resident image length do not grow, no new zero page, REU, table or stack storage is required.

The full 65,536-pair same-input 6502 model measured **78.494141 -> 72.494141 cycles** (exactly -6 cycles on every input); the published prior PUBLIC_PERFORMANCE historical harness recorded 78.494614, which uses a slightly different timing basis and is not silently treated as paired. All 56 public entries and 21,678 mixed API calls pass each of the reference and alternate source maps. V1/V3/V4 and V5 hybrid remain unchanged. Private OptiSearch code is not included.

**Native x64sc PASS:** 128 actual full-resident old/new calls over 64 fixed/edge/random operand pairs. Guaranteed public output, caller inputs, carry, stack and sentinels agree with the pinned pre-release image. Non-carry N/Z/V status flags are explicitly volatile per USER_MANUAL.md; the observed status differences are recorded in the native report. Native cycle timing was not measured. **Pending:** independent PR and post-merge main CI. Issue #39 remains OPEN.
