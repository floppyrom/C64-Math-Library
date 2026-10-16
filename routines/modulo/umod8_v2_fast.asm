; Source-accurate fast UMOD8 V2 relocation from v2_pareto_fast.
; Three reachable executable source islands packed together: main fast chain,
; small-divisor fallback adapter, and historical writable-code reducer.
; 229 bytes, 2 ZP scratch bytes, 0 normal RAM scratch, no REU.
; V2 fast-path threshold $18, fallback self-modifies two immediate bytes.
; Inputs N,D untouched; writes only R low, never Q; D=0 -> R=0,C=1.
; Requires CLD and writable executable RAM; not re-entrant.
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_REM = $C01C
TEMP_ZP = $0050

* = KERNEL_CODE
FAST_UMOD8_V2:
    lda INPUT_DIV
    cmp #$18
    bcs L5330
    lda INPUT_NUM
    jmp L3203
L5330:
    lda INPUT_NUM
    cmp INPUT_DIV
    bcc L5383
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L5383
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L5383
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L5383
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L5383
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L5383
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L5383
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L5383
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L5383
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcc L5383
    sbc INPUT_DIV
L5383:
    sta OUTPUT_REM
    clc
    rts

L3203:
    sta TEMP_ZP
    lda INPUT_DIV
    sta TEMP_ZP+1
    jsr L5212
    sta OUTPUT_REM
    rts

L5200:
    cpx #$01
    bcc L520E
    beq L520A
    and #$01
    clc
    rts
L520A:
    lda #$00
    clc
    rts
L520E:
    lda #$00
    sec
    rts
L5212:
    lda TEMP_ZP
    ldx TEMP_ZP+1
    cpx #$03
    bcc L5200
    cmp TEMP_ZP+1
    bcs L521F
    rts
L521F:
    sbc TEMP_ZP+1
    cmp TEMP_ZP+1
    bcs L5226
    rts
L5226:
    sbc TEMP_ZP+1
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    sbc TEMP_ZP+1
    bcc L526E
    stx L5266+1
    stx L526A+1
L5266:
    sbc #$00
    bcs L5266
L526A:
    adc #$00
    clc
    rts
L526E:
    adc TEMP_ZP+1
    clc
    rts
