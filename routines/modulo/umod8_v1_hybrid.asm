; Original V1 unsigned 8-bit modulo with two-case fast/fallback split.
; Main >=32-divisor subtraction chain and small-divisor direct remainder body.
; Exact 157 executable bytes, resident trampoline removed; NMOS 6502.
; Unlike UDIV8, this UMOD8 kernel writes ONLY low byte of MATH_R.
; Divisor=0 -> R=0 and C=1, otherwise C=0. Input N/D, Q preserved.
; Two explicit zero-page scratch bytes; immediate operands modified in RAM
; for the low-divisor subtraction loop; non-reentrant, CLD required.
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_REM = $C01C
TEMP_ZP = $0050

* = KERNEL_CODE
FAST_UMOD8_V1:
    lda INPUT_DIV
    cmp #$20
    bcs L1E0D
    lda INPUT_NUM
    jmp L3203
L1E0D:
    lda INPUT_NUM
    cmp INPUT_DIV
    bcc L1E48
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L1E48
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L1E48
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L1E48
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L1E48
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L1E48
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L1E48
    sbc INPUT_DIV
L1E48:
    sta OUTPUT_REM
    clc
    rts
L3203:
    sta TEMP_ZP
    lda INPUT_DIV
    sta TEMP_ZP+1
    jsr L4612
    sta OUTPUT_REM
    rts
L4600:
    cpx #$01
    bcc L460E
    beq L460A
    and #$01
    clc
    rts
L460A:
    lda #$00
    clc
    rts
L460E:
    lda #$00
    sec
    rts
L4612:
    lda TEMP_ZP
    ldx TEMP_ZP+1
    cpx #$03
    bcc L4600
    cmp TEMP_ZP+1
    bcs L461F
    rts
L461F:
    sbc TEMP_ZP+1
    cmp TEMP_ZP+1
    bcs L4626
    rts
L4626:
    sbc TEMP_ZP+1
    sbc TEMP_ZP+1
    bcc L463E
    sbc TEMP_ZP+1
    bcc L463E
    stx L4636+1
    stx L463A+1
L4636:
    sbc #$00
    bcs L4636
L463A:
    adc #$00
    clc
    rts
L463E:
    adc TEMP_ZP+1
    clc
    rts