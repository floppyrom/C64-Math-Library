; Three-page ATAN2: biased LOGX/LOGY plus one angle page, zero ZP.
; Inputs preserved; phase returned in Z0/A; D=0 required, C=0 returned.
; The finite angle table is clamped to at least 1. This keeps <=1 phase-unit
; error and makes 1 - angle - borrow negative, so xpyn returns C=0 for free.
; Axis classes remain zero; the four cardinal directions and (0,0) are exact.
X0=$C000
Y0=$C004
Z0=$C008
LOGX=@LOGX@
LOGY=@LOGY@
QPOS=@QPOS@
.org @ORG@
atan2:
    ldx X0
    beq axis
    bmi xneg
    lda LOGX,x
    ldx Y0
    bmi xpyn
    clc
    adc LOGY,x
    tax
    lda QPOS,x
    sta Z0
    rts
xpyn:
    clc
    adc LOGY,x
    tax
    lda #$01
    sbc QPOS,x
    sta Z0
    rts
xneg:
    lda LOGX,x
    ldx Y0
    bmi xnyn
    clc
    adc LOGY,x
    tax
    lda #$81
    sbc QPOS,x
    sta Z0
    clc
    rts
xnyn:
    clc
    adc LOGY,x
    tax
    lda QPOS,x
    eor #$80
    sta Z0
    rts
axis:
    clc
    lda Y0
    beq axis_store
    asl
    lda #$80
    ror
axis_store:
    sta Z0
    rts
