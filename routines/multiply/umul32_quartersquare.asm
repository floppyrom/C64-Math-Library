; 32x32 -> 64 quarter-square convolution, transplanted from the certified
; UMUL8/UMUL16 table algorithm. Sixteen exact 8x8 partial products.
; No REU, zero page, self-modifying code or initialization.
; Input X32/Y32 are preserved, result Z64, C=0, D must be clear.
; 4 bytes call-exclusive RAM scratch; 1022 bytes generated immutable tables.
!cpu 6510
KERNEL_CODE = $8000
Q_LO = $8100
Q_HI = $8300
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_RAM = $C020

* = KERNEL_CODE
FAST_UMUL32_QUARTERSQUARE:
    lda #0
    sta OUTPUT_Z
    sta OUTPUT_Z+1
    sta OUTPUT_Z+2
    sta OUTPUT_Z+3
    sta OUTPUT_Z+4
    sta OUTPUT_Z+5
    sta OUTPUT_Z+6
    sta OUTPUT_Z+7

; x[0] * y[0] contributes at Z[0] (base 256 convolution)
    lda INPUT_X
    sta TEMP_RAM+2
    lda INPUT_Y
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z
    adc TEMP_RAM+2
    sta OUTPUT_Z
    lda OUTPUT_Z+1
    adc TEMP_RAM+3
    sta OUTPUT_Z+1
    lda OUTPUT_Z+2
    adc #0
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    adc #0
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc #0
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc #0
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[0] * y[1] contributes at Z[1] (base 256 convolution)
    lda INPUT_X
    sta TEMP_RAM+2
    lda INPUT_Y+1
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+1
    adc TEMP_RAM+2
    sta OUTPUT_Z+1
    lda OUTPUT_Z+2
    adc TEMP_RAM+3
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    adc #0
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc #0
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc #0
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[0] * y[2] contributes at Z[2] (base 256 convolution)
    lda INPUT_X
    sta TEMP_RAM+2
    lda INPUT_Y+2
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+2
    adc TEMP_RAM+2
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    adc TEMP_RAM+3
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc #0
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc #0
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[0] * y[3] contributes at Z[3] (base 256 convolution)
    lda INPUT_X
    sta TEMP_RAM+2
    lda INPUT_Y+3
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+3
    adc TEMP_RAM+2
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc TEMP_RAM+3
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc #0
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[1] * y[0] contributes at Z[1] (base 256 convolution)
    lda INPUT_X+1
    sta TEMP_RAM+2
    lda INPUT_Y
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+1
    adc TEMP_RAM+2
    sta OUTPUT_Z+1
    lda OUTPUT_Z+2
    adc TEMP_RAM+3
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    adc #0
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc #0
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc #0
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[1] * y[1] contributes at Z[2] (base 256 convolution)
    lda INPUT_X+1
    sta TEMP_RAM+2
    lda INPUT_Y+1
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+2
    adc TEMP_RAM+2
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    adc TEMP_RAM+3
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc #0
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc #0
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[1] * y[2] contributes at Z[3] (base 256 convolution)
    lda INPUT_X+1
    sta TEMP_RAM+2
    lda INPUT_Y+2
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+3
    adc TEMP_RAM+2
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc TEMP_RAM+3
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc #0
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[1] * y[3] contributes at Z[4] (base 256 convolution)
    lda INPUT_X+1
    sta TEMP_RAM+2
    lda INPUT_Y+3
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+4
    adc TEMP_RAM+2
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc TEMP_RAM+3
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[2] * y[0] contributes at Z[2] (base 256 convolution)
    lda INPUT_X+2
    sta TEMP_RAM+2
    lda INPUT_Y
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+2
    adc TEMP_RAM+2
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    adc TEMP_RAM+3
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc #0
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc #0
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[2] * y[1] contributes at Z[3] (base 256 convolution)
    lda INPUT_X+2
    sta TEMP_RAM+2
    lda INPUT_Y+1
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+3
    adc TEMP_RAM+2
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc TEMP_RAM+3
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc #0
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[2] * y[2] contributes at Z[4] (base 256 convolution)
    lda INPUT_X+2
    sta TEMP_RAM+2
    lda INPUT_Y+2
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+4
    adc TEMP_RAM+2
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc TEMP_RAM+3
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[2] * y[3] contributes at Z[5] (base 256 convolution)
    lda INPUT_X+2
    sta TEMP_RAM+2
    lda INPUT_Y+3
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+5
    adc TEMP_RAM+2
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc TEMP_RAM+3
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[3] * y[0] contributes at Z[3] (base 256 convolution)
    lda INPUT_X+3
    sta TEMP_RAM+2
    lda INPUT_Y
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+3
    adc TEMP_RAM+2
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc TEMP_RAM+3
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc #0
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[3] * y[1] contributes at Z[4] (base 256 convolution)
    lda INPUT_X+3
    sta TEMP_RAM+2
    lda INPUT_Y+1
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+4
    adc TEMP_RAM+2
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc TEMP_RAM+3
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc #0
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[3] * y[2] contributes at Z[5] (base 256 convolution)
    lda INPUT_X+3
    sta TEMP_RAM+2
    lda INPUT_Y+2
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+5
    adc TEMP_RAM+2
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    adc TEMP_RAM+3
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc #0
    sta OUTPUT_Z+7

; x[3] * y[3] contributes at Z[6] (base 256 convolution)
    lda INPUT_X+3
    sta TEMP_RAM+2
    lda INPUT_Y+3
    sta TEMP_RAM+3
    jsr umul8_qs
    clc
    lda OUTPUT_Z+6
    adc TEMP_RAM+2
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc TEMP_RAM+3
    sta OUTPUT_Z+7

    clc
    rts

; Q(a+b)-Q(|a-b|) = a*b, using Q(n)=floor(n*n/4).
; Reuse the published UMUL16 511-entry low/high table generator exactly.
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
