; Signed 24x24=>48-bit public product using unsigned private core.
; Exactly 227 bytes code, 9 ordinary call-exclusive scratch, 0 ZP.
; Signed input X[0..2], Y[0..2] preserved; signed Z[0..5] exact, C=0.
; Z[6..7] not part of this output ABI and remain unchanged; CLD required.
; Initial machine-code reference, not the historical 385-cycle fast kernel.
!cpu 6510
KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_RAM = $C020
* = KERNEL_CODE
FAST_UMUL24_COMPACT:
    lda INPUT_X
    sta TEMP_RAM
    lda INPUT_X+1
    sta TEMP_RAM+1
    lda INPUT_X+2
    sta TEMP_RAM+2
    lda #0
    sta TEMP_RAM+3
    sta TEMP_RAM+4
    sta TEMP_RAM+5
    sta OUTPUT_Z
    sta OUTPUT_Z+1
    sta OUTPUT_Z+2
    sta OUTPUT_Z+3
    sta OUTPUT_Z+4
    sta OUTPUT_Z+5
    lda INPUT_Y
    sta TEMP_RAM+6
    lda INPUT_Y+1
    sta TEMP_RAM+7
    lda INPUT_Y+2
    sta TEMP_RAM+8
    ldx #24
umul24_loop:
    lsr TEMP_RAM+8
    ror TEMP_RAM+7
    ror TEMP_RAM+6
    bcc umul24_skip_add
    clc
    lda OUTPUT_Z
    adc TEMP_RAM
    sta OUTPUT_Z
    lda OUTPUT_Z+1
    adc TEMP_RAM+1
    sta OUTPUT_Z+1
    lda OUTPUT_Z+2
    adc TEMP_RAM+2
    sta OUTPUT_Z+2
    lda OUTPUT_Z+3
    adc TEMP_RAM+3
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    adc TEMP_RAM+4
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    adc TEMP_RAM+5
    sta OUTPUT_Z+5
umul24_skip_add:
    asl TEMP_RAM
    rol TEMP_RAM+1
    rol TEMP_RAM+2
    rol TEMP_RAM+3
    rol TEMP_RAM+4
    rol TEMP_RAM+5
    dex
    bne umul24_loop
    clc
    rts

; Modulo-2^48 sign correction of the 24x24 unsigned product:
; upper 24 bits -= Y24 when X23 negative and -= X24 when Y23 negative.
FAST_SMUL24_COMPACT:
    jsr FAST_UMUL24_COMPACT
    lda INPUT_X+2
    bpl smul24_x_done
    sec
    lda OUTPUT_Z+3
    sbc INPUT_Y
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    sbc INPUT_Y+1
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    sbc INPUT_Y+2
    sta OUTPUT_Z+5
smul24_x_done:
    lda INPUT_Y+2
    bpl smul24_y_done
    sec
    lda OUTPUT_Z+3
    sbc INPUT_X
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    sbc INPUT_X+1
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    sbc INPUT_X+2
    sta OUTPUT_Z+5
smul24_y_done:
    clc
    rts
