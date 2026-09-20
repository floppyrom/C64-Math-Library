; Optimized compact ATAN2. Same LOG/ATAN pages and outputs as atan2_compact.
; Inputs X0/Y0 are preserved; Z0 and A return phase; D=0 required, C=0 returned.
; No ZP, scratch, self-modification, or undocumented instructions.
; @ORG@ is replaced by the standalone benchmark/exporter.
X0=$C000
Y0=$C004
Z0=$C008
LOGTAB=$9600
ATANTAB=$9700
.org @ORG@
atan2:
    ldx X0
    beq axis
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
    lda #$00
    sec
    sbc ATANTAB,x
    sta Z0
    clc
    rts
xneg:
    lda LOGTAB,x
    ldx Y0
    bmi xnyn
    sbc LOGTAB,x
    tax
    lda #$80
    sec
    sbc ATANTAB,x
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
