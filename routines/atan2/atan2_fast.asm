; C64 Math Library - fast stock-C64 ATAN2 kernel
;
; Inputs:  X0 = signed 8-bit x, Y0 = signed 8-bit y
; Output:  Z0 = phase 0..255, where $00 = +X and $40 = +Y
; Accuracy: maximum error <= 1 phase unit over all 65,536 input pairs
; Scratch: 0 ZP bytes
; Tables:  LOGTAB + Q0/Q1/Q2/Q3 = 1280 bytes total
;
; The four quadrant pages remove the compact kernel's quadrant-repair ALU work.
; @ORG@ is replaced by tools/upgrade_atan2.py or benchmark.py before assembly.

X0=$C000
Y0=$C004
Z0=$C008
LOGTAB=$9600
Q0=$9700
Q1=$5500
Q2=$5F00
Q3=$4700
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
    lda Q0,x
    sta Z0
    clc
    rts
xpyn:
    sbc LOGTAB,x
    tax
    lda Q3,x
    sta Z0
    clc
    rts
xneg:
    lda LOGTAB,x
    ldx Y0
    bmi xnyn
    sbc LOGTAB,x
    tax
    lda Q1,x
    sta Z0
    clc
    rts
xnyn:
    sbc LOGTAB,x
    tax
    lda Q2,x
    sta Z0
    clc
    rts
