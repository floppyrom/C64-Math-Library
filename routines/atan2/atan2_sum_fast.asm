; Four-page ATAN2: two biased log pages and two reflected angle pages.
; Inputs X0/Y0 are preserved; Z0 and A return phase; D=0 required, C=0 returned.
; Same outputs as the original compact/fast kernels. No ZP or self-modification.
; For nonzero x, LOGX=q(abs(x)); LOGY=82-q(abs(y)), or 174 for y=0.
; CLC/ADC therefore produces an index <=255 and *clears carry on every path*.
; The negative-x paths use an XOR half-turn instead of two additional pages.
; Carry is cleared once at entry; loads and sign branches preserve it until ADC.
X0=$C000
Y0=$C004
Z0=$C008
LOGX=@LOGX@
LOGY=@LOGY@
QPOS=@QPOS@
QNEG=@QNEG@
.org @ORG@
atan2:
    clc
    ldx X0
    beq axis
    bmi xneg
    lda LOGX,x
    ldx Y0
    bmi xpyn
    adc LOGY,x
    tax
    lda QPOS,x
    sta Z0
    rts
xpyn:
    adc LOGY,x
    tax
    lda QNEG,x
    sta Z0
    rts
xneg:
    lda LOGX,x
    ldx Y0
    bmi xnyn
    adc LOGY,x
    tax
    lda QNEG,x
    eor #$80
    sta Z0
    rts
xnyn:
    adc LOGY,x
    tax
    lda QPOS,x
    eor #$80
    sta Z0
    rts
axis:
    lda Y0
    beq axis_store
    asl
    lda #$80
    ror
axis_store:
    sta Z0
    rts
