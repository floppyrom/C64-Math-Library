; Issue144 source-only caller-owned all-D16 public ABI UDIV32/16 opt-in.
; V2/V3/V4 reference resident maps; RAM $0800..end must be free.
; No normal ZP added, but uses resident shared scratch and is not reentrant.
; Inputs: MATH_N=$C010..$C013, D=$C014..$C015.
; Returns Q=$C018..$C01B, R=$C01C..$C01D, C=1 only when D=0.
; D8, D=0 and D>=$8000 use existing public $31B0 path.
; NOT a default public ABI promotion. Mathematical source proof in tools/.
!cpu 6510
U3216_N0 = $10
U3216_N1 = $11
U3216_D0 = $12
U3216_D1 = $13
U3216_Q2 = $14
U3216_Q3 = $15
U3216_R0 = $16
U3216_R1 = $17
U3216_LN0 = $18
U3216_LN1 = $19

* = $0800
OPT_U3216_LOW:
    lda $c015
    beq FALLBACK
    bpl COPY_INPUT
FALLBACK:
    jmp $31b0
COPY_INPUT:
    lda $c010
    sta U3216_LN0
    lda $c011
    sta U3216_LN1
    lda $c012
    sta U3216_N0
    lda $c013
    sta U3216_N1
    lda $c014
    sta U3216_D0
    lda $c015
    sta U3216_D1
    jsr $420c
    lda U3216_R1
STEP_0:
    rol U3216_LN1
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_0
    bne TAKE_0
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_0
TAKE_0:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_0:
STEP_1:
    rol U3216_LN1
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_1
    bne TAKE_1
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_1
TAKE_1:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_1:
STEP_2:
    rol U3216_LN1
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_2
    bne TAKE_2
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_2
TAKE_2:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_2:
STEP_3:
    rol U3216_LN1
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_3
    bne TAKE_3
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_3
TAKE_3:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_3:
STEP_4:
    rol U3216_LN1
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_4
    bne TAKE_4
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_4
TAKE_4:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_4:
STEP_5:
    rol U3216_LN1
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_5
    bne TAKE_5
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_5
TAKE_5:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_5:
STEP_6:
    rol U3216_LN1
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_6
    bne TAKE_6
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_6
TAKE_6:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_6:
STEP_7:
    rol U3216_LN1
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_7
    bne TAKE_7
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_7
TAKE_7:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_7:
    rol U3216_LN1
STEP_8:
    rol U3216_LN0
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_8
    bne TAKE_8
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_8
TAKE_8:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_8:
STEP_9:
    rol U3216_LN0
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_9
    bne TAKE_9
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_9
TAKE_9:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_9:
STEP_10:
    rol U3216_LN0
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_10
    bne TAKE_10
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_10
TAKE_10:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_10:
STEP_11:
    rol U3216_LN0
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_11
    bne TAKE_11
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_11
TAKE_11:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_11:
STEP_12:
    rol U3216_LN0
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_12
    bne TAKE_12
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_12
TAKE_12:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_12:
STEP_13:
    rol U3216_LN0
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_13
    bne TAKE_13
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_13
TAKE_13:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_13:
STEP_14:
    rol U3216_LN0
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_14
    bne TAKE_14
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_14
TAKE_14:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_14:
STEP_15:
    rol U3216_LN0
    rol U3216_R0
    rol
    cmp U3216_D1
    bcc NEXT_15
    bne TAKE_15
    ldx U3216_R0
    cpx U3216_D0
    bcc NEXT_15
TAKE_15:
    tax
    lda U3216_R0
    sbc U3216_D0
    sta U3216_R0
    txa
    sbc U3216_D1
NEXT_15:
    rol U3216_LN0
    sta $c01d
    lda U3216_LN0
    sta $c018
    lda U3216_LN1
    sta $c019
    lda U3216_Q2
    sta $c01a
    lda U3216_Q3
    sta $c01b
    lda U3216_R0
    sta $c01c
    clc
    rts
