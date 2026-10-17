; Signed 32x32 >>16 fixed-point, exact low 48 bits via signed full64 core.
; Source-linked reference, not a replacement for historical speed-optimized UMUL32.
; 334 bytes executable, 12 bytes call-exclusive ordinary RAM scratch, zero ZP.
; Preserves full signed X32/Y32. Outputs signed (X*Y)>>16 in Z[0..5]; Z[6..7] volatile. C clear, CLD required.
; No tables, REU, SMC, undocumented opcodes, or initialization.
!cpu 6510
KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_RAM = $C020
* = KERNEL_CODE
FAST_UMUL32_COMPACT:
    lda INPUT_X
    sta TEMP_RAM
    lda INPUT_X+1
    sta TEMP_RAM+1
    lda INPUT_X+2
    sta TEMP_RAM+2
    lda INPUT_X+3
    sta TEMP_RAM+3
    lda #0
    sta TEMP_RAM+4
    sta TEMP_RAM+5
    sta TEMP_RAM+6
    sta TEMP_RAM+7
    sta OUTPUT_Z
    sta OUTPUT_Z+1
    sta OUTPUT_Z+2
    sta OUTPUT_Z+3
    sta OUTPUT_Z+4
    sta OUTPUT_Z+5
    sta OUTPUT_Z+6
    sta OUTPUT_Z+7
    lda INPUT_Y
    sta TEMP_RAM+8
    lda INPUT_Y+1
    sta TEMP_RAM+9
    lda INPUT_Y+2
    sta TEMP_RAM+10
    lda INPUT_Y+3
    sta TEMP_RAM+11
    ldx #32
umul32_loop:
    lsr TEMP_RAM+11
    ror TEMP_RAM+10
    ror TEMP_RAM+9
    ror TEMP_RAM+8
    bcc umul32_skip
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
    lda OUTPUT_Z+6
    adc TEMP_RAM+6
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    adc TEMP_RAM+7
    sta OUTPUT_Z+7
umul32_skip:
    asl TEMP_RAM
    rol TEMP_RAM+1
    rol TEMP_RAM+2
    rol TEMP_RAM+3
    rol TEMP_RAM+4
    rol TEMP_RAM+5
    rol TEMP_RAM+6
    rol TEMP_RAM+7
    dex
    bne umul32_loop
    clc
    rts

; Correct the unsigned 64-bit product into signed 64-bit modulo 2^64.
; For negative X, subtract Y32 from high half; for negative Y, subtract X32.
FAST_SMUL32_COMPACT:
    jsr FAST_UMUL32_COMPACT
    lda INPUT_X+3
    bpl smul32_x_done
    sec
    lda OUTPUT_Z+4
    sbc INPUT_Y
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    sbc INPUT_Y+1
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    sbc INPUT_Y+2
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    sbc INPUT_Y+3
    sta OUTPUT_Z+7
smul32_x_done:
    lda INPUT_Y+3
    bpl smul32_y_done
    sec
    lda OUTPUT_Z+4
    sbc INPUT_X
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    sbc INPUT_X+1
    sta OUTPUT_Z+5
    lda OUTPUT_Z+6
    sbc INPUT_X+2
    sta OUTPUT_Z+6
    lda OUTPUT_Z+7
    sbc INPUT_X+3
    sta OUTPUT_Z+7
smul32_y_done:
    clc
    rts

; Public fixed-point signed arithmetic shift: preserve the low 48 bits of
; signed (X32*Y32)>>16.  The unsigned shift/add core and high-product
; two's-complement correction above operate on the complete 64-bit product.
; Z[6..7] outside this entry's contract are volatile.
FAST_SMUL32_SHR16_COMPACT:
    jsr FAST_SMUL32_COMPACT
    lda OUTPUT_Z+2
    sta OUTPUT_Z
    lda OUTPUT_Z+3
    sta OUTPUT_Z+1
    lda OUTPUT_Z+4
    sta OUTPUT_Z+2
    lda OUTPUT_Z+5
    sta OUTPUT_Z+3
    lda OUTPUT_Z+6
    sta OUTPUT_Z+4
    lda OUTPUT_Z+7
    sta OUTPUT_Z+5
    clc
    rts
