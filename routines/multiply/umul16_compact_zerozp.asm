; Portable unsigned 16 x 16 => 32 multiply, 6510/NMOS 6502, all legal opcodes.
; Source-only selectively linked module, NOT a speed winner over published
; large-table multipliers. Exactly 108 code bytes; 6 ordinary scratch bytes.
; No zero-page allocation, no self-modifying code, no initialization.
; ABI: uint16 INPUT_X/Y preserved; uint32 OUTPUT_Z little endian.
; A/X/flags volatile; decimal mode must be clear; not reentrant.
; All six scratch bytes are caller-reserved and clobbered.
!cpu 6502

KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_RAM = $C020

* = KERNEL_CODE
FAST_UMUL16_COMPACT:
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
umul16_loop:
    lsr TEMP_RAM+5
    ror TEMP_RAM+4
    bcc umul16_skip_add
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
umul16_skip_add:
    asl TEMP_RAM
    rol TEMP_RAM+1
    rol TEMP_RAM+2
    rol TEMP_RAM+3
    dex
    bne umul16_loop
    clc
    rts
