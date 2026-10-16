; Independent historical V1 DIST8_ACCURATE kernel, trampoline omitted.
; Shipped exact max/min absolute-coordinate + two-page table algorithm.
; Signed low-byte X/Y inputs preserved, zero carry on return, low Z output.
; abs(-128) = 128, table sum wraps modulo 256; CLD prerequisite.
KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
DIST_MAJOR = $8100
DIST_MINOR = $8200
TEMP_RAM = $C020

* = KERNEL_CODE
FAST_DIST8_ACCURATE:
    jsr DIST_ABS_SORT
    ldx TEMP_RAM
    lda DIST_MAJOR,x
    ldx TEMP_RAM+1
    clc
    adc DIST_MINOR,x
    sta OUTPUT_Z
    clc
    rts

DIST_ABS_SORT:
    lda INPUT_X
    bpl DIST_X_POS
    sec
    lda #$00
    sbc INPUT_X
DIST_X_POS:
    sta TEMP_RAM
    lda INPUT_Y
    bpl DIST_Y_POS
    sec
    lda #$00
    sbc INPUT_Y
DIST_Y_POS:
    sta TEMP_RAM+1
    cmp TEMP_RAM
    bcc DIST_DONE
    tax
    lda TEMP_RAM
    sta TEMP_RAM+1
    stx TEMP_RAM
    rts
DIST_DONE:
    rts
