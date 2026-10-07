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
* = MATH_SMOD16
    jmp RM16S_ENTRY
* = MATH_SMOD24
    jmp RM24S_ENTRY

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
* = REG_KERNEL+$1D74
RM24U_ENTRY:
    !byte $AF,<MATH_N+2,>MATH_N+2
    cmp MATH_D+2
    bcc RM24U_QZERO
    beq RM24U_HIGH_EQUAL
    lda MATH_D+2
    beq RM24U_LOW_D2

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
    beq RM24U_LOW_D2_EQUAL
    lda MATH_N+1
    cmp MATH_D+1
    bcc RM24U_QZERO
    bne RM24U_EQUAL_GE
    lda MATH_N+0
    cmp MATH_D+0
    bcc RM24U_QZERO
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
; Signed 16-bit remainder.  Exact C-style remainder = sign(n) * (|n| % |d|).
; q>=2 reuses the private magnitude core; no quotient sign repair is needed.
; ---------------------------------------------------------------------------
* = REG_LOW+$0BCD
RM16S_ENTRY:
    lda D16F_sn1
    bmi RM16S_NNEG
    lda D16F_sdin1
    bmi RM16S_PN

; ++
RM16S_PP:
    lda D16F_sdin0
    ora D16F_sdin1
    beq RM16S_ZERO
    !byte $AF,<MATH_N+1,>MATH_N+1
    cmp D16F_sdin1
    bcc RM16S_QZERO
    bne RM16S_PP_GE
    lda D16F_sn0
    cmp D16F_sdin0
    bcc RM16S_QZERO
RM16S_PP_GE:
    sec
    lda D16F_sn0
    sbc D16F_sdin0
    sta D16F_r0
    txa
    sbc D16F_sdin1
    sta D16F_r1
    cmp D16F_sdin1
    bcc RM16S_SUCCESS
    bne RM16S_PP_GE2
    lda D16F_r0
    cmp D16F_sdin0
    bcc RM16S_SUCCESS
RM16S_PP_GE2:
    lda D16F_sn0
    sta D16F_n0
    stx D16F_n1
    lda D16F_sdin0
    sta D16F_d0
    lda D16F_sdin1
    sta D16F_d1
    lda D16F_r1
    jsr D16F_quotient_ge_two
    jmp RM16S_SUCCESS

; +-
RM16S_PN:
    lda #0
    sec
    sbc D16F_sdin0
    sta D16F_d0
    lda #0
    sbc D16F_sdin1
    sta D16F_d1
    !byte $AF,<MATH_N+1,>MATH_N+1
    cmp D16F_d1
    bcc RM16S_QZERO
    bne RM16S_PN_GE
    lda D16F_sn0
    cmp D16F_d0
    bcc RM16S_QZERO
RM16S_PN_GE:
    sec
    lda D16F_sn0
    sbc D16F_d0
    sta D16F_r0
    txa
    sbc D16F_d1
    sta D16F_r1
    cmp D16F_d1
    bcc RM16S_SUCCESS
    bne RM16S_PN_GE2
    lda D16F_r0
    cmp D16F_d0
    bcc RM16S_SUCCESS
RM16S_PN_GE2:
    lda D16F_sn0
    sta D16F_n0
    stx D16F_n1
    lda D16F_r1
    jsr D16F_quotient_ge_two
    jmp RM16S_SUCCESS

RM16S_NNEG:
    lda D16F_sdin1
    bmi RM16S_NN

; -+
RM16S_NP:
    lda D16F_sdin0
    ora D16F_sdin1
    beq RM16S_ZERO
    lda #0
    sec
    sbc D16F_sn0
    sta D16F_n0
    lda #0
    sbc D16F_sn1
    sta D16F_n1
    cmp D16F_sdin1
    bcc RM16S_QZERO
    bne RM16S_NP_GE
    lda D16F_n0
    cmp D16F_sdin0
    bcc RM16S_QZERO
RM16S_NP_GE:
    sec
    lda D16F_n0
    sbc D16F_sdin0
    sta D16F_r0
    lda D16F_n1
    sbc D16F_sdin1
    sta D16F_r1
    cmp D16F_sdin1
    bcc RM16S_NEG_R
    bne RM16S_NP_GE2
    lda D16F_r0
    cmp D16F_sdin0
    bcc RM16S_NEG_R
RM16S_NP_GE2:
    lda D16F_sdin0
    sta D16F_d0
    lda D16F_sdin1
    sta D16F_d1
    lda D16F_r1
    jsr D16F_quotient_ge_two
    jmp RM16S_NEG_R

; --
RM16S_NN:
    !byte $AF,<MATH_N+1,>MATH_N+1
    cmp D16F_sdin1
    bcc RM16S_NN_GE
    beq RM16S_NN_HEQ
    jmp RM16S_QZERO
RM16S_NN_HEQ:
    lda D16F_sn0
    cmp D16F_sdin0
    bcc RM16S_NN_GE
    beq RM16S_NN_GE
    jmp RM16S_QZERO
RM16S_NN_GE:
    lda #0
    sec
    sbc D16F_sn0
    sta D16F_n0
    lda #0
    sbc D16F_sn1
    sta D16F_n1
    lda #0
    sec
    sbc D16F_sdin0
    sta D16F_d0
    lda #0
    sbc D16F_sdin1
    sta D16F_d1
    sec
    lda D16F_n0
    sbc D16F_d0
    sta D16F_r0
    lda D16F_n1
    sbc D16F_d1
    sta D16F_r1
    cmp D16F_d1
    bcc RM16S_NEG_R
    bne RM16S_NN_GE2
    lda D16F_r0
    cmp D16F_d0
    bcc RM16S_NEG_R
RM16S_NN_GE2:
    lda D16F_r1
    jsr D16F_quotient_ge_two
    jmp RM16S_NEG_R

RM16S_QZERO:
    lda D16F_sn0
    sta D16F_r0
    lda D16F_sn1
    sta D16F_r1
RM16S_SUCCESS:
    clc
    rts

RM16S_NEG_R:
    lda #0
    sec
    sbc D16F_r0
    sta D16F_r0
    lda #0
    sbc D16F_r1
    sta D16F_r1
    clc
    rts

RM16S_ZERO:
    lda #0
    sta D16F_r0
    sta D16F_r1
    sec
    rts

; ---------------------------------------------------------------------------
; Signed 24-bit remainder.  Magnitude core is shared; quotient sign is dead.
; ---------------------------------------------------------------------------
RM24S_ENTRY:
    !byte $AF,<MATH_D+2,>MATH_D+2
    beq RM24S_DHIGH_ZERO
    bmi RM24S_DNEG
RM24S_DPOS:
    lda D24F_sdin0
    sta D24F_d0
    lda D24F_sdin1
    sta D24F_d1
    stx D24F_d2
    jmp RM24S_NMAKE
RM24S_DHIGH_ZERO:
    lda D24F_sdin0
    ora D24F_sdin1
    beq RM24S_ZERO
    lda D24F_sdin0
    sta D24F_d0
    lda D24F_sdin1
    sta D24F_d1
    stx D24F_d2
    jmp RM24S_NMAKE
RM24S_DNEG:
    lda #0
    sec
    sbc D24F_sdin0
    sta D24F_d0
    lda #0
    sbc D24F_sdin1
    sta D24F_d1
    lda #0
    sbc D24F_sdin2
    sta D24F_d2

RM24S_NMAKE:
    !byte $AF,<MATH_N+2,>MATH_N+2
    bmi RM24S_NNEG
    lda D24F_sn0
    sta D24F_n0
    lda D24F_sn1
    sta D24F_n1
    stx D24F_n2
    jmp RM24S_TEST
RM24S_NNEG:
    lda #0
    sec
    sbc D24F_sn0
    sta D24F_n0
    lda #0
    sbc D24F_sn1
    sta D24F_n1
    lda #0
    sbc D24F_sn2
    sta D24F_n2

RM24S_TEST:
    lda D24F_n2
    cmp D24F_d2
    bcc RM24S_QZERO
    bne RM24S_FIRST
    lda D24F_n1
    cmp D24F_d1
    bcc RM24S_QZERO
    bne RM24S_FIRST
    lda D24F_n0
    cmp D24F_d0
    bcc RM24S_QZERO
RM24S_FIRST:
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
    bcc RM24S_SIGN
    bne RM24S_GE2
    lda D24F_r1
    cmp D24F_d1
    bcc RM24S_SIGN
    bne RM24S_GE2
    lda D24F_r0
    cmp D24F_d0
    bcc RM24S_SIGN
RM24S_GE2:
    ldx #0
    stx D24F_q1
    stx D24F_q2
    jsr D24F_q1_sub_mem

RM24S_SIGN:
    lda D24F_sn2
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
    lda D24F_sn0
    sta D24F_r0
    lda D24F_sn1
    sta D24F_r1
    lda D24F_sn2
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
