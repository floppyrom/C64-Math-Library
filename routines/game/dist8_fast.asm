; Independent relocatable V1 fast signed-8 Manhattan approximation.
; Retains the certified arithmetic: max(abs(x),abs(y)) + floor(min/2),
; reduced to unsigned 8 bits. In particular abs(-128) = 128.
; Based on v1_balanced/standalone/dist_s8_s8_u8_fast.asm; resident
; trampoline removed and its two temporary bytes made explicitly owned.
; Input MATH_X/Y low bytes; result MATH_Z low byte; C=0.
; Preconditions: CLD. Inputs retained; ZP=0; 2 scratch RAM bytes.
KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_RAM = $C020

* = KERNEL_CODE
FAST_DIST8_FAST:
    jsr DIST_ABS_SORT
    lda TEMP_RAM+1
    lsr a
    clc
    adc TEMP_RAM
    sta OUTPUT_Z
    clc
    rts

DIST_ABS_SORT:
    lda INPUT_X
    bpl DIST_X_POSITIVE
    sec
    lda #$00
    sbc INPUT_X
DIST_X_POSITIVE:
    sta TEMP_RAM
    lda INPUT_Y
    bpl DIST_Y_POSITIVE
    sec
    lda #$00
    sbc INPUT_Y
DIST_Y_POSITIVE:
    sta TEMP_RAM+1
    cmp TEMP_RAM
    bcc DIST_DONE
    tax
    lda TEMP_RAM
    sta TEMP_RAM+1
    stx TEMP_RAM
DIST_DONE:
    rts
