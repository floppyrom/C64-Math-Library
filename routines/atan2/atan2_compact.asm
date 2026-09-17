; C64 Math Library - compact stock-C64 ATAN2 kernel
;
; Inputs:  X0 = signed 8-bit x, Y0 = signed 8-bit y
; Output:  Z0 = phase 0..255, where $00 = +X and $40 = +Y
; Accuracy: maximum error <= 1 phase unit over all 65,536 input pairs
; Scratch: 0 ZP bytes
; Tables:  LOGTAB 256 bytes + ATANTAB 256 bytes
;
; @ORG@ is replaced by tools/upgrade_atan2.py or benchmark.py before assembly.

X0=$C000
Y0=$C004
Z0=$C008
LOGTAB=$9600
ATANTAB=$9700
.org @ORG@
atan2:
    ldx X0
    bne x_nonzero
    ldx Y0
    beq zero
    bmi x0_yneg
    lda #$40
    bne axis_store
x0_yneg:
    lda #$C0
    bne axis_store
zero:
    lda #$00
axis_store:
    sta Z0
    clc
    rts
x_nonzero:
    sec
    bmi xneg
    lda LOGTAB,x
    ldx Y0
    bmi xpyn
    sbc LOGTAB,x
    tax
    lda ATANTAB,x
    sta Z0
    clc
    rts
xpyn:
    sbc LOGTAB,x
    tax
    lda ATANTAB,x
    eor #$ff
    clc
    adc #$01
    sta Z0
    clc
    rts
xneg:
    lda LOGTAB,x
    ldx Y0
    bmi xnyn
    sbc LOGTAB,x
    tax
    lda ATANTAB,x
    eor #$ff
    clc
    adc #$81
    sta Z0
    clc
    rts
xnyn:
    sbc LOGTAB,x
    tax
    lda ATANTAB,x
    eor #$80
    sta Z0
    clc
    rts
