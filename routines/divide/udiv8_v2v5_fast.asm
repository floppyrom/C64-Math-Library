; Original V2 and V5 UDIV8 fast branch-chain producer, source-identical
; across the two shipped V2/V5 resident binaries.
; 430-byte contiguous code island $4000-$41AD, 181 instructions.
; The public $3120 trampoline is omitted; the fast entry remains 8 bytes
; after the shared zero-divisor (A=0, C=1) stub.
; N, D, Q and R refer to the low bytes of the public 32-byte I/O area.
; Preserve N and D; quotient and remainder are written. D=0: Q=R=0, C=1.
; Requires 1 explicitly owned zero-page byte; no tables, REU or SMC.
; Decimal flag clear (CLD) on entry.
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
FAST_UDIV8_V2V5:
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
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L40FB
    sta OUTPUT_REM
    lda #$0D
    sta OUTPUT_QUOT
    rts
L40FB:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L410C
    sta OUTPUT_REM
    lda #$0E
    sta OUTPUT_QUOT
    rts
L410C:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L411D
    sta OUTPUT_REM
    lda #$0F
    sta OUTPUT_QUOT
    rts
L411D:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L412E
    sta OUTPUT_REM
    lda #$10
    sta OUTPUT_QUOT
    rts
L412E:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L413F
    sta OUTPUT_REM
    lda #$11
    sta OUTPUT_QUOT
    rts
L413F:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L4150
    sta OUTPUT_REM
    lda #$12
    sta OUTPUT_QUOT
    rts
L4150:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L4161
    sta OUTPUT_REM
    lda #$13
    sta OUTPUT_QUOT
    rts
L4161:
    sbc INPUT_DIV
    cmp INPUT_DIV
    bcs L4172
    sta OUTPUT_REM
    lda #$14
    sta OUTPUT_QUOT
    rts
L4172:
    sta OUTPUT_REM
    lda INPUT_DIV
    sta TEMP_ZP
    ldx #$00
    stx OUTPUT_QUOT
L417F:
    lda TEMP_ZP
    asl a
    bcs L418B
    cmp OUTPUT_REM
    bcc L41A9
    beq L41A9
L418B:
    lda OUTPUT_REM
L418E:
    cmp TEMP_ZP
    bcc L4194
    sbc TEMP_ZP
L4194:
    rol OUTPUT_QUOT
    lsr TEMP_ZP
    dex
    bpl L418E
    sta OUTPUT_REM
    lda OUTPUT_QUOT
    clc
    adc #$14
    sta OUTPUT_QUOT
    rts
L41A9:
    sta TEMP_ZP
    inx
    bne L417F
