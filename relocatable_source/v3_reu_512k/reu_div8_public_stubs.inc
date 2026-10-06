; Relocation-safe V3/V4 REU-backed 8-bit divide/modulo front end.
;
; UDIV8 uses a CPU quotient-0..3 fast path before falling back to the exact
; two-plane REU lookup.  Across the exhaustive 8-bit domain q=0 accounts for
; 32,640 calls, q=1 for 16,384, q=2 for 5,461 and q=3 for 2,731, so paying a
; few subtract/compare steps is substantially cheaper than launching the REU
; for those cases.  Inputs remain untouched; divide-by-zero semantics stay
; q=0, r=0, C=1.
;
; UMOD8 keeps the existing single-plane REU remainder lookup at REG_API+$0A40.
; The original exact UDIV8 REU core at REG_API+$0A00 remains present and is
; intentionally not used by the public UDIV8 entry after this overlay.
;
; The hybrid core lives in the free REG_KERNEL+$0D00 island ($4D00 reference
; map), between the UDIV24 body and the UDIV32/16 continuation.
* = MATH_UDIV8
    jmp REU8_div_u8

* = MATH_UMOD8
    jmp REG_API+$0A40

* = REG_KERNEL+$0D00
REU8_div_u8:
    lda MATH_D
    beq REU8_zero

    lda MATH_N
    cmp MATH_D
    bcc REU8_q0

    ; C=1 after the failed BCC, so each SBC is exact without an extra SEC.
    sbc MATH_D
    cmp MATH_D
    bcc REU8_q1

    sbc MATH_D
    cmp MATH_D
    bcc REU8_q2

    sbc MATH_D
    cmp MATH_D
    bcc REU8_q3

    ; q >= 4: exact REU lookup using the original quotient/remainder planes.
    lda MATH_N
    sta $DF04
    lda MATH_D
    sta $DF05

    lda #REU_UDIV8_Q_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_Q

    lda #REU_UDIV8_R_BANK
    sta $DF06
    lda #$81
    sta $DF01
    lda REU_SCRATCH
    sta MATH_R
    clc
    rts

REU8_q0:
    sta MATH_R
    lda #0
    sta MATH_Q
    clc
    rts

REU8_q1:
    sta MATH_R
    lda #1
    sta MATH_Q
    clc
    rts

REU8_q2:
    sta MATH_R
    lda #2
    sta MATH_Q
    clc
    rts

REU8_q3:
    sta MATH_R
    lda #3
    sta MATH_Q
    clc
    rts

REU8_zero:
    lda #0
    sta MATH_Q
    sta MATH_R
    sec
    rts
