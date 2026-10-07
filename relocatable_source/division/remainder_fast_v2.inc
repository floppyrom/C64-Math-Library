; Dedicated remainder-only fast paths for V2/V3/V4.
; The hard arithmetic remains shared with the selected division engines.
; q=0/q=1 exits omit quotient materialization; signed paths never repair
; quotient sign.  Public N/D inputs and divide-by-zero carry semantics remain.

* = MATH_UMOD16
    jmp RM16U_ENTRY
* = MATH_UMOD24
    jmp RM24U_ENTRY
* = MATH_UMOD32_32
    jmp RM3232U_ENTRY
; ---------------------------------------------------------------------------
; Unsigned 16-bit remainder.
; Mirrors DU16F through q=1, then rejoins the exact q>=2 state.
; ---------------------------------------------------------------------------
* = REG_LOW+$104C
RM16U_ENTRY:
    !byte $AF,<MATH_N+1,>MATH_N+1
    cmp MATH_D+1
    bcc RM16U_QZERO
    beq RM16U_HIGH_EQUAL

    lda MATH_N+0
    sbc MATH_D+0
    sta MATH_R+0
    txa
    sbc MATH_D+1
    cmp MATH_D+1
    bcc RM16U_QONE_A
    jmp DU16F_q1_high_ge

RM16U_HIGH_EQUAL:
    lda MATH_N+0
    sbc MATH_D+0
    bcc RM16U_QZERO
    cpx #1
    bcc RM16U_D8
    sta MATH_R+0
    !byte $0B,$00
    sta MATH_R+1
    rts
RM16U_D8:
    jmp DU16F_precheck_equal_d8

RM16U_QONE_A:
    sta MATH_R+1
    rts

RM16U_QZERO:
    lda MATH_N+0
    sta MATH_R+0
    stx MATH_R+1
    rts

; ---------------------------------------------------------------------------
; Unsigned 32/32 remainder.
; Same early compare as D3232, but q=0/q=1 never touch MATH_Q.
; ---------------------------------------------------------------------------
* = REG_KERNEL+$177F
RM3232U_ENTRY:
    lda MATH_D+0
    ora MATH_D+1
    ora MATH_D+2
    ora MATH_D+3
    beq RM3232U_LEGACY

    lda MATH_N+3
    cmp MATH_D+3
    bcc RM3232U_QZERO
    bne RM3232U_LEGACY
    lda MATH_N+2
    cmp MATH_D+2
    bcc RM3232U_QZERO
    bne RM3232U_LEGACY
    lda MATH_N+1
    cmp MATH_D+1
    bcc RM3232U_QZERO
    bne RM3232U_LEGACY
    lda MATH_N+0
    cmp MATH_D+0
    bcc RM3232U_QZERO
    bne RM3232U_LEGACY

    lda #0
    sta MATH_R+0
    sta MATH_R+1
    sta MATH_R+2
    sta MATH_R+3
    clc
    rts

RM3232U_QZERO:
    lda MATH_N+0
    sta MATH_R+0
    lda MATH_N+1
    sta MATH_R+1
    lda MATH_N+2
    sta MATH_R+2
    lda MATH_N+3
    sta MATH_R+3
    clc
    rts

RM3232U_LEGACY:
    jmp REG_GAME

; ---------------------------------------------------------------------------
; Unsigned 24-bit remainder.
; Delay q1/q2 zeroing until q>=2 so the two dominant exits are remainder-only.
; ---------------------------------------------------------------------------
* = REG_LOW+$0F00
RM24U_ENTRY:
    !byte $AF,<MATH_N+2,>MATH_N+2
    cmp MATH_D+2
    bcs RM24U_TOP_GE
RM24U_QZERO_STUB:
    jmp RM24U_QZERO
RM24U_TOP_GE:
    beq RM24U_HIGH_EQUAL
    lda MATH_D+2
    bne RM24U_HIGH_NONZERO
    jmp RM24U_LOW_D2
RM24U_HIGH_NONZERO:

    lda MATH_N+0
    sec
    sbc MATH_D+0
    sta MATH_R+0
    lda MATH_N+1
    sbc MATH_D+1
    sta MATH_R+1
    lda MATH_N+2
    sbc MATH_D+2
    cmp MATH_D+2
    bcc RM24U_QONE_LIVE
    bne RM24U_QGE2_LIVE
    sta MATH_R+2
    lda MATH_R+1
    cmp MATH_D+1
    bcc RM24U_QONE_MEM
    bne RM24U_QGE2_MEM
    lda MATH_R+0
    cmp MATH_D+0
    bcs RM24U_QGE2_MEM
RM24U_QONE_MEM:
    clc
    rts
RM24U_QONE_LIVE:
    sta MATH_R+2
    rts
RM24U_QGE2_LIVE:
    ldx #0
    stx MATH_Q+1
    stx MATH_Q+2
    jmp DU24F_q1_sub_live
RM24U_QGE2_MEM:
    ldx #0
    stx MATH_Q+1
    stx MATH_Q+2
    jmp DU24F_q1_sub_mem

RM24U_HIGH_EQUAL:
    lda MATH_D+2
    bne RM24U_EQUAL_HIGH_NONZERO
    jmp RM24U_LOW_D2_EQUAL
RM24U_EQUAL_HIGH_NONZERO:
    lda MATH_N+1
    cmp MATH_D+1
    bcc RM24U_QZERO_STUB
    bne RM24U_EQUAL_GE
    lda MATH_N+0
    cmp MATH_D+0
    bcc RM24U_QZERO_STUB
RM24U_EQUAL_GE:
    lda MATH_N+0
    sbc MATH_D+0
    sta MATH_R+0
    lda MATH_N+1
    sbc MATH_D+1
    sta MATH_R+1
    lda MATH_N+2
    sbc MATH_D+2
    sta MATH_R+2
    clc
    rts
RM24U_LOW_D2_EQUAL:
    jmp DU24F_low_d2_equal
RM24U_LOW_D2:
    jmp DU24F_low_d2

RM24U_QZERO:
    lda MATH_N+0
    sta MATH_R+0
    lda MATH_N+1
    sta MATH_R+1
    stx MATH_R+2
    rts

; ---------------------------------------------------------------------------
; Signed remainder fast gates. q=0/q=1 are resolved without quotient work;
; q>=2 falls back to the selected signed divider unchanged.
; ---------------------------------------------------------------------------
* = MATH_SMOD16
    jmp RM16S_ENTRY
* = MATH_SMOD24
    jmp RM24S_ENTRY

* = REG_LOW+$0BCD
RM16S_ENTRY:
    lda MATH_D+0
    ora MATH_D+1
    beq RM16S_ZERO

    ; |n| -> private magnitude scratch.
    lda MATH_N+1
    bmi RM16S_NNEG
    lda MATH_N+0
    sta D16F_n0
    lda MATH_N+1
    sta D16F_n1
    jmp RM16S_DMAG
RM16S_NNEG:
    lda #0
    sec
    sbc MATH_N+0
    sta D16F_n0
    lda #0
    sbc MATH_N+1
    sta D16F_n1
RM16S_DMAG:
    lda MATH_D+1
    bmi RM16S_DNEG
    lda MATH_D+0
    sta D16F_d0
    lda MATH_D+1
    sta D16F_d1
    jmp RM16S_COMPARE
RM16S_DNEG:
    lda #0
    sec
    sbc MATH_D+0
    sta D16F_d0
    lda #0
    sbc MATH_D+1
    sta D16F_d1

RM16S_COMPARE:
    lda D16F_n1
    cmp D16F_d1
    bcc RM16S_QZERO
    bne RM16S_SUB1
    lda D16F_n0
    cmp D16F_d0
    bcc RM16S_QZERO
RM16S_SUB1:
    sec
    lda D16F_n0
    sbc D16F_d0
    sta D16F_r0
    lda D16F_n1
    sbc D16F_d1
    sta D16F_r1
    cmp D16F_d1
    bcc RM16S_QONE
    bne RM16S_FALLBACK
    lda D16F_r0
    cmp D16F_d0
    bcs RM16S_FALLBACK
RM16S_QONE:
    lda MATH_N+1
    bpl RM16S_SUCCESS
    lda #0
    sec
    sbc D16F_r0
    sta D16F_r0
    lda #0
    sbc D16F_r1
    sta D16F_r1
RM16S_SUCCESS:
    clc
    rts
RM16S_QZERO:
    lda MATH_N+0
    sta D16F_r0
    lda MATH_N+1
    sta D16F_r1
    clc
    rts
RM16S_ZERO:
    lda #0
    sta D16F_r0
    sta D16F_r1
    sec
    rts
RM16S_FALLBACK:
    jmp D16F_div_s16

* = REG_LOW+$0D80
RM24S_ENTRY:
    lda MATH_D+0
    ora MATH_D+1
    ora MATH_D+2
    beq RM24S_ZERO

    lda MATH_N+2
    bmi RM24S_NNEG
    lda MATH_N+0
    sta D24F_n0
    lda MATH_N+1
    sta D24F_n1
    lda MATH_N+2
    sta D24F_n2
    jmp RM24S_DMAG
RM24S_NNEG:
    lda #0
    sec
    sbc MATH_N+0
    sta D24F_n0
    lda #0
    sbc MATH_N+1
    sta D24F_n1
    lda #0
    sbc MATH_N+2
    sta D24F_n2
RM24S_DMAG:
    lda MATH_D+2
    bmi RM24S_DNEG
    lda MATH_D+0
    sta D24F_d0
    lda MATH_D+1
    sta D24F_d1
    lda MATH_D+2
    sta D24F_d2
    jmp RM24S_COMPARE
RM24S_DNEG:
    lda #0
    sec
    sbc MATH_D+0
    sta D24F_d0
    lda #0
    sbc MATH_D+1
    sta D24F_d1
    lda #0
    sbc MATH_D+2
    sta D24F_d2

RM24S_COMPARE:
    lda D24F_n2
    cmp D24F_d2
    bcc RM24S_QZERO
    bne RM24S_SUB1
    lda D24F_n1
    cmp D24F_d1
    bcc RM24S_QZERO
    bne RM24S_SUB1
    lda D24F_n0
    cmp D24F_d0
    bcc RM24S_QZERO
RM24S_SUB1:
    sec
    lda D24F_n0
    sbc D24F_d0
    sta D24F_r0
    lda D24F_n1
    sbc D24F_d1
    sta D24F_r1
    lda D24F_n2
    sbc D24F_d2
    sta D24F_r2
    cmp D24F_d2
    bcc RM24S_QONE
    bne RM24S_FALLBACK
    lda D24F_r1
    cmp D24F_d1
    bcc RM24S_QONE
    bne RM24S_FALLBACK
    lda D24F_r0
    cmp D24F_d0
    bcs RM24S_FALLBACK
RM24S_QONE:
    lda MATH_N+2
    bpl RM24S_SUCCESS
    lda #0
    sec
    sbc D24F_r0
    sta D24F_r0
    lda #0
    sbc D24F_r1
    sta D24F_r1
    lda #0
    sbc D24F_r2
    sta D24F_r2
RM24S_SUCCESS:
    clc
    rts
RM24S_QZERO:
    lda MATH_N+0
    sta D24F_r0
    lda MATH_N+1
    sta D24F_r1
    lda MATH_N+2
    sta D24F_r2
    clc
    rts
RM24S_ZERO:
    lda #0
    sta D24F_r0
    sta D24F_r1
    sta D24F_r2
    sec
    rts
RM24S_FALLBACK:
    jmp D24F_div_s24
