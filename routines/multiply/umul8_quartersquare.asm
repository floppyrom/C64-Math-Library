; Unsigned 8x8 -> 16 via floor(n*n/4) quarter-square tables.
; No ZP or initialization. 2 bytes ordinary scratch; caller IO X/Y -> Z.
; Data pages are linked from an exact generator; no resident image reused.
; The tables are 511 words split into 511-byte LO and HI planes.
; Requires D=0, preserves inputs, clears C, A/X/flags volatile.
!cpu 6502
KERNEL_CODE = $8000
Q_LO = $8049
Q_HI = $8248
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_RAM = $C020
* = KERNEL_CODE
FAST_UMUL8_QUARTERSQUARE:
    lda INPUT_X
    clc
    adc INPUT_Y
    tax
    bcs sum_upper
sum_lower:
    lda Q_LO,x
    sta TEMP_RAM
    lda Q_HI,x
    sta TEMP_RAM+1
    jmp difference
sum_upper:
    lda Q_LO+256,x
    sta TEMP_RAM
    lda Q_HI+256,x
    sta TEMP_RAM+1
difference:
    lda INPUT_X
    sec
    sbc INPUT_Y
    bcs diff_positive
    eor #$ff
    clc
    adc #1
diff_positive:
    tax
    sec
    lda TEMP_RAM
    sbc Q_LO,x
    sta OUTPUT_Z
    lda TEMP_RAM+1
    sbc Q_HI,x
    sta OUTPUT_Z+1
    clc
    rts
