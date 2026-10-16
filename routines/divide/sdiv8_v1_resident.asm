; Independent relocatable V1 signed 8-bit division/remainder producer.
; Exact 234-instruction / 530-byte body relocated from v1_balanced/
; standalone/div_s8_s8_s8_8.asm ($BDE0..$BFF1), trampoline omitted.
; Both MATH_SDIV8 and MATH_SMOD8 were historically API aliases to the
; same producer at $BDE8; select either or both and share one code image.
; Inputs: signed N/D low bytes. Q/R low bytes are quotient/remainder.
; D=0 returns Q=R=0 with carry set. Inputs/high bytes preserved.
; ZP=1 private byte; no regular scratch, REU, tables or init. CLD.
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_ZP = $0050

* = KERNEL_CODE
SDIV8_ZERO:
    sta OUTPUT_QUOT
    sta OUTPUT_REM
    sec
    rts
FAST_SDIV8_V1:
    lda INPUT_DIV
    beq SDIV8_ZERO
    bpl LBDF4
    eor #$FF
    clc
    adc #$01
LBDF4:
    sta TEMP_ZP
    lda INPUT_NUM
    bpl LBE00
    eor #$FF
    clc
    adc #$01
LBE00:
    cmp TEMP_ZP
    bcs LBE1C
    sta OUTPUT_REM
    lda #$00
    sta OUTPUT_QUOT
    bit INPUT_NUM
    bmi LBE13
    clc
    rts
LBE13:
    sec
    sbc OUTPUT_REM
    sta OUTPUT_REM
    clc
    rts
LBE1C:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBE54
    sta OUTPUT_REM
    lda #$01
    sta OUTPUT_QUOT
    bit INPUT_NUM
    bmi LBE3D
    bit INPUT_DIV
    bmi LBE36
    clc
    rts
LBE36:
    lda #$FF
    sta OUTPUT_QUOT
    clc
    rts
LBE3D:
    lda #$00
    sec
    sbc OUTPUT_REM
    sta OUTPUT_REM
    bit INPUT_DIV
    bpl LBE4D
    clc
    rts
LBE4D:
    lda #$FF
    sta OUTPUT_QUOT
    clc
    rts
LBE54:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBE65
    sta OUTPUT_REM
    lda #$02
    sta OUTPUT_QUOT
    jmp LBFC8
LBE65:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBE76
    sta OUTPUT_REM
    lda #$03
    sta OUTPUT_QUOT
    jmp LBFC8
LBE76:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBE87
    sta OUTPUT_REM
    lda #$04
    sta OUTPUT_QUOT
    jmp LBFC8
LBE87:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBE98
    sta OUTPUT_REM
    lda #$05
    sta OUTPUT_QUOT
    jmp LBFC8
LBE98:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBEA9
    sta OUTPUT_REM
    lda #$06
    sta OUTPUT_QUOT
    jmp LBFC8
LBEA9:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBEBA
    sta OUTPUT_REM
    lda #$07
    sta OUTPUT_QUOT
    jmp LBFC8
LBEBA:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBECB
    sta OUTPUT_REM
    lda #$08
    sta OUTPUT_QUOT
    jmp LBFC8
LBECB:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBEDC
    sta OUTPUT_REM
    lda #$09
    sta OUTPUT_QUOT
    jmp LBFC8
LBEDC:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBEED
    sta OUTPUT_REM
    lda #$0A
    sta OUTPUT_QUOT
    jmp LBFC8
LBEED:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBEFE
    sta OUTPUT_REM
    lda #$0B
    sta OUTPUT_QUOT
    jmp LBFC8
LBEFE:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBF0F
    sta OUTPUT_REM
    lda #$0C
    sta OUTPUT_QUOT
    jmp LBFC8
LBF0F:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBF20
    sta OUTPUT_REM
    lda #$0D
    sta OUTPUT_QUOT
    jmp LBFC8
LBF20:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBF31
    sta OUTPUT_REM
    lda #$0E
    sta OUTPUT_QUOT
    jmp LBFC8
LBF31:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBF42
    sta OUTPUT_REM
    lda #$0F
    sta OUTPUT_QUOT
    jmp LBFC8
LBF42:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBF53
    sta OUTPUT_REM
    lda #$10
    sta OUTPUT_QUOT
    jmp LBFC8
LBF53:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBF64
    sta OUTPUT_REM
    lda #$11
    sta OUTPUT_QUOT
    jmp LBFC8
LBF64:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBF75
    sta OUTPUT_REM
    lda #$12
    sta OUTPUT_QUOT
    jmp LBFC8
LBF75:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBF86
    sta OUTPUT_REM
    lda #$13
    sta OUTPUT_QUOT
    jmp LBFC8
LBF86:
    sbc TEMP_ZP
    cmp TEMP_ZP
    bcs LBF97
    sta OUTPUT_REM
    lda #$14
    sta OUTPUT_QUOT
    jmp LBFC8
LBF97:
    sta OUTPUT_REM
    ldx #$00
    stx OUTPUT_QUOT
LBF9F:
    lda TEMP_ZP
    asl a
    bcs LBFAB
    cmp OUTPUT_REM
    bcc LBFEC
    beq LBFEC
LBFAB:
    lda OUTPUT_REM
LBFAE:
    cmp TEMP_ZP
    bcc LBFB4
    sbc TEMP_ZP
LBFB4:
    rol OUTPUT_QUOT
    lsr TEMP_ZP
    dex
    bpl LBFAE
    sta OUTPUT_REM
    lda OUTPUT_QUOT
    clc
    adc #$14
    sta OUTPUT_QUOT
LBFC8:
    lda INPUT_NUM
    bmi LBFD3
    eor INPUT_DIV
    bmi LBFE1
    rts
LBFD3:
    lda #$00
    sec
    sbc OUTPUT_REM
    sta OUTPUT_REM
    lda INPUT_DIV
    bmi LBFEA
LBFE1:
    lda #$00
    sec
    sbc OUTPUT_QUOT
    sta OUTPUT_QUOT
LBFEA:
    clc
    rts
LBFEC:
    sta TEMP_ZP
    inx
    bne LBF9F
    brk
