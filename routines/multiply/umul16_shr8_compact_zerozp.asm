; Portable unsigned 16x16 >> 8 => 24-bit fixed-point multiply.
; Standalone relocation-safe reference, not a replacement for faster V2-V4.
; A/X/flags volatile; inputs X/Y untouched; output Z0..Z2, C=0.
; 6 exclusive ordinary-RAM scratch bytes, no ZP/tables/SMC/init/REU.
; Decimal mode must be clear. Z3 is not part of the result contract.
!cpu 6502
KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_RAM = $C020

* = KERNEL_CODE
FAST_UMUL16_SHR8_COMPACT:
    lda INPUT_X
    sta TEMP_RAM
    lda INPUT_X+1
    sta TEMP_RAM+1
    lda #$00
    sta TEMP_RAM+2
    sta TEMP_RAM+3
    sta OUTPUT_Z
    sta OUTPUT_Z+1
    sta OUTPUT_Z+2
    sta OUTPUT_Z+3
    lda INPUT_Y
    sta TEMP_RAM+4
    lda INPUT_Y+1
    sta TEMP_RAM+5
    ldx #$10
shr8_mul_loop:
    lsr TEMP_RAM+5
    ror TEMP_RAM+4
    bcc shr8_skip_add
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
shr8_skip_add:
    asl TEMP_RAM
    rol TEMP_RAM+1
    rol TEMP_RAM+2
    rol TEMP_RAM+3
    dex
    bne shr8_mul_loop
    lda OUTPUT_Z+1
    sta OUTPUT_Z
    lda OUTPUT_Z+2
    sta OUTPUT_Z+1
    lda OUTPUT_Z+3
    sta OUTPUT_Z+2
    clc
    rts
