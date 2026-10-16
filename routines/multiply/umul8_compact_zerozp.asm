; Portable unsigned 8x8 => 16 multiplication on legal NMOS 6502.
; Canonical standalone compact baseline: ordinary RAM scratch, no ZP or tables.
; Source-linked by selective_linker.py; benchmark speed is NOT yet certified.
; Inputs: INPUT_X and INPUT_Y low bytes unchanged. OUTPUT_Z/Z+1 low-first.
; A/X/flags volatile, CLD required. Non-reentrant, 3 bytes TEMP_RAM scratch.
!cpu 6502

KERNEL_CODE = $8000
INPUT_X = $C000
INPUT_Y = $C004
OUTPUT_Z = $C008
TEMP_RAM = $C020

* = KERNEL_CODE
FAST_UMUL8_COMPACT:
    lda INPUT_X
    sta TEMP_RAM
    lda #$00
    sta TEMP_RAM+1
    sta OUTPUT_Z
    sta OUTPUT_Z+1
    lda INPUT_Y
    sta TEMP_RAM+2
    ldx #$08
umul8_loop:
    lsr TEMP_RAM+2
    bcc umul8_skip_add
    clc
    lda OUTPUT_Z
    adc TEMP_RAM
    sta OUTPUT_Z
    lda OUTPUT_Z+1
    adc TEMP_RAM+1
    sta OUTPUT_Z+1
umul8_skip_add:
    asl TEMP_RAM
    rol TEMP_RAM+1
    dex
    bne umul8_loop
    clc
    rts
