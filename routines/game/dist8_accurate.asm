; Relocatable V1 accurate distance kernel, original two lookup pages.
; V1 reference: v1_balanced/standalone/dist_s8_s8_u8_accurate.asm.
; The two 256-byte tables are embedded exactly by selective_dist8_accurate.py,
; independently of the release image at selective build time.
; signed inputs: MATH_X/Y low; result unsigned MATH_Z low; C=0.
; CLD required; zero-page=0, two explicitly owned temporary RAM bytes.
KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_RAM = $C020
DIST_MAX = $8100
DIST_MIN = $8200

* = KERNEL_CODE
FAST_DIST8_ACCURATE:
    jsr DIST_ABS_SORT
    ldx TEMP_RAM
    lda DIST_MAX,x
    ldx TEMP_RAM+1
    clc
    adc DIST_MIN,x
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
    rts
DIST_DONE:
    rts
