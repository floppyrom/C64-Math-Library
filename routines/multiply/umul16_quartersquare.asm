; Portable unsigned 16x16->32 multiplication from four unsigned quarter-square
; 8x8 products. 0 ZP. Caller IO X/Y preserved, Z[0..3] output, C=0.
; Four shared ordinary scratch bytes. Q(n)=floor(n*n/4), n=0..510.
; Does not use self-modification; CLD required, A/X/Y volatile.
!cpu 6502
KERNEL_CODE = $8000
Q_LO = $8100
Q_HI = $8300
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_RAM = $C020

* = KERNEL_CODE
FAST_UMUL16_QUARTERSQUARE:
    lda #$00
    sta OUTPUT_Z
    sta OUTPUT_Z+1
    sta OUTPUT_Z+2
    sta OUTPUT_Z+3

    lda INPUT_X
    sta TEMP_RAM+2
    lda INPUT_Y
    sta TEMP_RAM+3
    jsr umul8_qs
    lda TEMP_RAM+2
    sta OUTPUT_Z
    lda TEMP_RAM+3
    sta OUTPUT_Z+1

    lda INPUT_X
    sta TEMP_RAM+2
    lda INPUT_Y+1
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda TEMP_RAM+2
    adc OUTPUT_Z+1
    sta OUTPUT_Z+1
    lda TEMP_RAM+3
    adc OUTPUT_Z+2
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    adc #$00
    sta OUTPUT_Z+3

    lda INPUT_X+1
    sta TEMP_RAM+2
    lda INPUT_Y
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda TEMP_RAM+2
    adc OUTPUT_Z+1
    sta OUTPUT_Z+1
    lda TEMP_RAM+3
    adc OUTPUT_Z+2
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    adc #$00
    sta OUTPUT_Z+3

    lda INPUT_X+1
    sta TEMP_RAM+2
    lda INPUT_Y+1
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda TEMP_RAM+2
    adc OUTPUT_Z+2
    sta OUTPUT_Z+2
    lda TEMP_RAM+3
    adc OUTPUT_Z+3
    sta OUTPUT_Z+3
    clc
    rts

umul8_qs:
    lda TEMP_RAM+2
    clc
    adc TEMP_RAM+3
    tax
    bcs qs_sum_upper
qs_sum_lower:
    lda Q_LO,x
    sta TEMP_RAM
    lda Q_HI,x
    sta TEMP_RAM+1
    jmp qs_difference
qs_sum_upper:
    lda Q_LO+256,x
    sta TEMP_RAM
    lda Q_HI+256,x
    sta TEMP_RAM+1
qs_difference:
    lda TEMP_RAM+2
    sec
    sbc TEMP_RAM+3
    bcs qs_diff_positive
    eor #$ff
    clc
    adc #1
qs_diff_positive:
    tax
    sec
    lda TEMP_RAM
    sbc Q_LO,x
    sta TEMP_RAM+2
    lda TEMP_RAM+1
    sbc Q_HI,x
    sta TEMP_RAM+3
    rts
