; V1 SDIV32/32 preserved-input sign rediscovery.
; Removes V1_SCRATCH+$08/$09 sign flags; public N/D remain unchanged.

* = REG_GAME+$0034
SD3232V1_ENTRY:
    lda MATH_D+0
    ora MATH_D+1
    ora MATH_D+2
    ora MATH_D+3
    bne SD3232V1_DNZ
    jsr REG_LOW+$1A00
    rts
SD3232V1_DNZ:
    lda MATH_N+0
    sta V1_SCRATCH
    lda MATH_N+1
    sta V1_SCRATCH+$01
    lda MATH_N+2
    sta V1_SCRATCH+$02
    lda MATH_N+3
    sta V1_SCRATCH+$03
    bpl SD3232V1_N_READY
    sec
    lda #0
    sbc V1_SCRATCH
    sta V1_SCRATCH
    lda #0
    sbc V1_SCRATCH+$01
    sta V1_SCRATCH+$01
    lda #0
    sbc V1_SCRATCH+$02
    sta V1_SCRATCH+$02
    lda #0
    sbc V1_SCRATCH+$03
    sta V1_SCRATCH+$03
SD3232V1_N_READY:
    lda MATH_D+0
    sta V1_SCRATCH+$04
    lda MATH_D+1
    sta V1_SCRATCH+$05
    lda MATH_D+2
    sta V1_SCRATCH+$06
    lda MATH_D+3
    sta V1_SCRATCH+$07
    bpl SD3232V1_D_READY
    sec
    lda #0
    sbc V1_SCRATCH+$04
    sta V1_SCRATCH+$04
    lda #0
    sbc V1_SCRATCH+$05
    sta V1_SCRATCH+$05
    lda #0
    sbc V1_SCRATCH+$06
    sta V1_SCRATCH+$06
    lda #0
    sbc V1_SCRATCH+$07
    sta V1_SCRATCH+$07
SD3232V1_D_READY:
    jsr REG_LOW+$1A2E
    bcs SD3232V1_RET
    lda MATH_N+3
    eor MATH_D+3
    bpl SD3232V1_Q_DONE
    sec
    lda #0
    sbc MATH_Q+0
    sta MATH_Q+0
    lda #0
    sbc MATH_Q+1
    sta MATH_Q+1
    lda #0
    sbc MATH_Q+2
    sta MATH_Q+2
    lda #0
    sbc MATH_Q+3
    sta MATH_Q+3
SD3232V1_Q_DONE:
    lda MATH_N+3
    bpl SD3232V1_SUCCESS
    sec
    lda #0
    sbc MATH_R+0
    sta MATH_R+0
    lda #0
    sbc MATH_R+1
    sta MATH_R+1
    lda #0
    sbc MATH_R+2
    sta MATH_R+2
    lda #0
    sbc MATH_R+3
    sta MATH_R+3
SD3232V1_SUCCESS:
    clc
SD3232V1_RET:
    rts
SD3232V1_END:
