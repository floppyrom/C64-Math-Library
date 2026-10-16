; Relocatable historical V5 UMOD8 fast and unrolled-fallback code.
; Exact original 208 reachable bytes less 3-byte public trampoline = 205.
; Preserves >32 source fast chain and V5 hybrid subtraction expansion for
; small divisors, including two self-modified immediate operands.
; Source must execute in writable ordinary RAM. Non-reentrant, CLD required.
; N/D preserved, only low R written, Q and high bytes untouched.
; C=1 and R=0 on zero divisor; else C=0.
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_REM = $C01C
TEMP_ZP = $0050

* = KERNEL_CODE
FAST_UMOD8_V5:
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
    jsr LB012
    sta OUTPUT_REM
    rts
LB000:
    cpx #$01
    bcc LB00E
    beq LB00A
    and #$01
    clc
    rts
LB00A:
    lda #$00
    clc
    rts
LB00E:
    lda #$00
    sec
    rts
LB012:
    lda TEMP_ZP
    ldx TEMP_ZP+1
    cpx #$03
    bcc LB000
    cmp TEMP_ZP+1
    bcs LB01F
    rts
LB01F:
    sbc TEMP_ZP+1
    cmp TEMP_ZP+1
    bcs LB026
    rts
LB026:
    sbc TEMP_ZP+1
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    sbc TEMP_ZP+1
    bcc LB06E
    stx LB066+1
    stx LB06A+1
LB066:
    sbc #$00
    bcs LB066
LB06A:
    adc #$00
    clc
    rts
LB06E:
    adc TEMP_ZP+1
    clc
    rts
