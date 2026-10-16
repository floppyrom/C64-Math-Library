; Relocatable historical V1 8-bit unsigned division producer.
; Port of all 125 reachable instructions in v1_balanced/standalone/
; div_u8_u8_u8_8.asm at $4000-$4125 (294 code bytes).
; Public V1 trampoline at $3120 omitted; original entry L4008 is retained
; as FAST_UDIV8_V1 at KERNEL_CODE+8. Hardware 6502 and source parity.
; Inputs MATH_N and MATH_D low bytes; outputs MATH_Q and MATH_R low bytes.
; Division-by-zero stores Q=R=0 and returns C=1; valid D returns C=0.
; Inputs preserved. Requires one private ZP byte. CLD on entry.
; No REU, lookup tables, init, or ordinary scratch RAM.
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_ZP = $0050

* = KERNEL_CODE
UDIV8_DIV_BY_ZERO:
    sta OUTPUT_QUOT
    sta OUTPUT_REM
    sec
    rts
FAST_UDIV8_V1:
    lda INPUT_DIV
    beq UDIV8_DIV_BY_ZERO
    lda INPUT_NUM
    cmp INPUT_DIV
    bcs L401E
    sta OUTPUT_REM
    lda #$00
    sta OUTPUT_QUOT
    rts
L401E:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L402F
    sta OUTPUT_REM
    lda #$01
    sta OUTPUT_QUOT
    rts
L402F:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L4040
    sta OUTPUT_REM
    lda #$02
    sta OUTPUT_QUOT
    rts
L4040:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L4051
    sta OUTPUT_REM
    lda #$03
    sta OUTPUT_QUOT
    rts
L4051:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L4062
    sta OUTPUT_REM
    lda #$04
    sta OUTPUT_QUOT
    rts
L4062:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L4073
    sta OUTPUT_REM
    lda #$05
    sta OUTPUT_QUOT
    rts
L4073:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L4084
    sta OUTPUT_REM
    lda #$06
    sta OUTPUT_QUOT
    rts
L4084:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L4095
    sta OUTPUT_REM
    lda #$07
    sta OUTPUT_QUOT
    rts
L4095:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L40A6
    sta OUTPUT_REM
    lda #$08
    sta OUTPUT_QUOT
    rts
L40A6:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L40B7
    sta OUTPUT_REM
    lda #$09
    sta OUTPUT_QUOT
    rts
L40B7:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L40C8
    sta OUTPUT_REM
    lda #$0A
    sta OUTPUT_QUOT
    rts
L40C8:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L40D9
    sta OUTPUT_REM
    lda #$0B
    sta OUTPUT_QUOT
    rts
L40D9:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L40EA
    sta OUTPUT_REM
    lda #$0C
    sta OUTPUT_QUOT
    rts
L40EA:
    sta OUTPUT_REM
    lda INPUT_DIV
    sta TEMP_ZP
    ldx #$00
    stx OUTPUT_QUOT
L40F7:
    lda TEMP_ZP
    asl a
    bcs L4103
    cmp OUTPUT_REM
    bcc L4121
    beq L4121
L4103:
    lda OUTPUT_REM
L4106:
    cmp TEMP_ZP
    bcc L410C
    sbc TEMP_ZP
L410C:
    rol OUTPUT_QUOT
    lsr TEMP_ZP
    dex
    bpl L4106
    sta OUTPUT_REM
    lda OUTPUT_QUOT
    clc
    adc #$0C
    sta OUTPUT_QUOT
    rts
L4121:
    sta TEMP_ZP
    inx
    bne L40F7
