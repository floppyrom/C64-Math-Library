; Source-backed standalone copy of div_u16_biased.asm (Repose / OptiSearch donor).
; Independent relocation experiment: edit the constants below to choose a new map.
; Keep code, buffers and scratch disjoint, with the 6510 memory configuration
; exposing RAM in those regions. This file remains emulator-qualified only.
; Decimal mode clear (CLD); success C=0, zero-divisor C=1.
; 323-byte code at KERNEL_CODE; ZP TEMP_ZP must be exclusively owned.
!cpu 6510

KERNEL_CODE = $8000


INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_ZP = $50



; segment $0610 (323 bytes)
* = KERNEL_CODE
FAST_UDIV16_BIASED:
    lax  INPUT_NUM+1
    cmp  INPUT_DIV+1
    bcs  L062A
L0618:
    lda  #$00
    sta  OUTPUT_QUOT
    sta  OUTPUT_QUOT+1
    lda  INPUT_NUM
    sta  OUTPUT_REM
    stx  OUTPUT_REM+1
    rts  
L062A:
    bne  L0665
    lda  INPUT_NUM
    sbc  INPUT_DIV
    bcc  L0618
    sta  OUTPUT_REM
    txa  
    bne  L0647
    lda  INPUT_DIV
    beq  L0655
    stx  OUTPUT_REM+1
    ldx  #$FC
    jmp  L06CB
L0647:
    anc  #$00
    sta  OUTPUT_REM+1
    sta  OUTPUT_QUOT+1
    lda  #$01
    sta  OUTPUT_QUOT
    rts  
L0655:
    ldx  #$00
    stx  OUTPUT_QUOT
    stx  OUTPUT_QUOT+1
    stx  OUTPUT_REM
    stx  OUTPUT_REM+1
    sec  
    rts  
L0665:
    lda  INPUT_NUM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    txa  
    sbc  INPUT_DIV+1
    cmp  INPUT_DIV+1
    bcc  L0683
    bne  L069E
    tax  
    lda  OUTPUT_REM
    cmp  INPUT_DIV
    bcs  L069D
    txa  
L0683:
    sta  OUTPUT_REM+1
    lda  #$00
    sta  OUTPUT_QUOT+1
    lda  #$01
    sta  OUTPUT_QUOT
    rts  
L0691:
    txa  
    adc  #$05
    sta  OUTPUT_QUOT
    anc  #$00
    sta  OUTPUT_QUOT+1
    rts  
L069D:
    txa  
L069E:
    ldx  INPUT_DIV+1
    bne  L06A8
    ldx  INPUT_DIV
    beq  L0655
L06A8:
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
    sta  OUTPUT_REM+1
    cmp  INPUT_DIV+1
    bcs  L06C9
    lda  #$02
    sta  OUTPUT_QUOT
    anc  #$00
    sta  OUTPUT_QUOT+1
    rts  
L06C9:
    ldx  #$FD
L06CB:
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    tay  
    lda  OUTPUT_REM+1
    sbc  INPUT_DIV+1
    bcc  L0691
    sta  OUTPUT_REM+1
    sty  OUTPUT_REM
    inx  
    bmi  L06CB
    cmp  INPUT_DIV+1
    bcc  L0691
    bne  L06F2
    lda  OUTPUT_REM
    cmp  INPUT_DIV
    bcc  L0691
L06F2:
    lda  INPUT_DIV
    sta  TEMP_ZP
    lda  INPUT_DIV+1
    sta  TEMP_ZP+1
    stx  OUTPUT_QUOT
    stx  OUTPUT_QUOT+1
    ldy  OUTPUT_REM+1
L0705:
    asl  TEMP_ZP
    rol  TEMP_ZP+1
    cpy  TEMP_ZP+1
    bcc  L071E
    bne  L0716
    lda  OUTPUT_REM
    cmp  TEMP_ZP
    bcc  L071E
L0716:
    inx  
    bit  TEMP_ZP+1
    bpl  L0705
    inx  
    bpl  L0723
L071E:
    lsr  TEMP_ZP+1
    inx  
L0721:
    ror  TEMP_ZP
L0723:
    sec  
    lda  OUTPUT_REM
    sbc  TEMP_ZP
    tay  
    lda  OUTPUT_REM+1
    sbc  TEMP_ZP+1
    bcc  L0737
    sta  OUTPUT_REM+1
    sty  OUTPUT_REM
L0737:
    rol  OUTPUT_QUOT
    rol  OUTPUT_QUOT+1
    dex  
    beq  L0744
    lsr  TEMP_ZP+1
    bpl  L0721
L0744:
    lda  #$05
    adc  OUTPUT_QUOT
    sta  OUTPUT_QUOT
    bcc  L0752
    inc  OUTPUT_QUOT+1
    clc  
L0752:
    rts  
