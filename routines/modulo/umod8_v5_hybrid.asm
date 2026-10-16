; Source-accurate fast UMOD8 V5 relocation from v5_hybrid_lowzp.
; Three reachable executable source islands packed together: main fast chain,
; small-divisor fallback adapter, and historical writable-code reducer.
; 205 bytes, 2 ZP scratch bytes, 0 normal RAM scratch, no REU.
; V5 fast-path threshold $20, fallback self-modifies two immediate bytes.
; Inputs N,D untouched; writes only R low, never Q; D=0 -> R=0,C=1.
; Requires CLD and writable executable RAM; not re-entrant.
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
    adc #$00
    clc
    rts
LB06E:
    adc TEMP_ZP+1
    clc
    rts
