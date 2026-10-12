; Source-backed standalone copy of div_u32_aligned_nozp.asm (Repose / OptiSearch donor).
; Independent relocation experiment: edit the constants below to choose a new map.
; Keep code, buffers and scratch disjoint, with the 6510 memory configuration
; exposing RAM in those regions. This file requires caller-owned machine-code RAM; validated via emulator and native x64sc.
; Decimal mode clear (CLD); success C=0, zero-divisor C=1.
; 325-byte core at KERNEL_CODE; 251-byte aligned tail at KERNEL_AUX; 0 ZP; four-byte TEMP_RAM scratch owned by caller.
!cpu 6510

KERNEL_CODE = $8000
KERNEL_AUX = $9000


INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_RAM = $C020



; segment $0600 (325 bytes)
* = KERNEL_CODE
FAST_UDIV32_PUBLIC:
    lda  INPUT_NUM+3
    cmp  INPUT_DIV+3
    bcc  L0628
    bne  L064F
    lda  INPUT_NUM+2
    cmp  INPUT_DIV+2
    bcc  L0628
    bne  L064F
    lda  INPUT_NUM+1
    cmp  INPUT_DIV+1
    bcc  L0628
    bne  L064F
    lda  INPUT_NUM
    cmp  INPUT_DIV
    bcc  L0628
    bcs  L064F
L0628:
    lda  #$00
    sta  OUTPUT_QUOT
    sta  OUTPUT_QUOT+1
    sta  OUTPUT_QUOT+2
    sta  OUTPUT_QUOT+3
    lda  INPUT_NUM
    sta  OUTPUT_REM
    lda  INPUT_NUM+1
    sta  OUTPUT_REM+1
    lda  INPUT_NUM+2
    sta  OUTPUT_REM+2
    lda  INPUT_NUM+3
    sta  OUTPUT_REM+3
    rts  
L064F:
    lda  INPUT_DIV+3
    bne  L0662
    lda  INPUT_DIV
    ora  INPUT_DIV+1
    ora  INPUT_DIV+2
    bne  L0662
    jmp  L072A
L0662:
    sec  
    lda  INPUT_NUM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    lda  INPUT_NUM+1
    sbc  INPUT_DIV+1
    sta  OUTPUT_REM+1
    lda  INPUT_NUM+2
    sbc  INPUT_DIV+2
    sta  OUTPUT_REM+2
    lda  INPUT_NUM+3
    sbc  INPUT_DIV+3
    cmp  INPUT_DIV+3
    bcc  L06EE
    beq  L06AE
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    lda  OUTPUT_REM+1
    sbc  INPUT_DIV+1
    sta  OUTPUT_REM+1
    lda  OUTPUT_REM+2
    sbc  INPUT_DIV+2
    sta  OUTPUT_REM+2
    tya  
    sbc  INPUT_DIV+3
    jmp  L0702
L06AE:
    tax  
    lda  OUTPUT_REM+2
    cmp  INPUT_DIV+2
    bcc  L06ED
    bne  L06CD
    lda  OUTPUT_REM+1
    cmp  INPUT_DIV+1
    bcc  L06ED
    bne  L06CD
    lda  OUTPUT_REM
    cmp  INPUT_DIV
    bcc  L06ED
    bne  L06CD
L06CD:
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    lda  OUTPUT_REM+1
    sbc  INPUT_DIV+1
    sta  OUTPUT_REM+1
    lda  OUTPUT_REM+2
    sbc  INPUT_DIV+2
    sta  OUTPUT_REM+2
    lda  #$00
    jmp  L0702
L06ED:
    txa  
L06EE:
    sta  OUTPUT_REM+3
    lda  #$01
    sta  OUTPUT_QUOT
    lda  #$00
    sta  OUTPUT_QUOT+1
    sta  OUTPUT_QUOT+2
    sta  OUTPUT_QUOT+3
    rts  
L0702:
    sta  OUTPUT_REM+3
    jsr  L2000
    clc  
    lda  OUTPUT_QUOT
    adc  #$02
    sta  OUTPUT_QUOT
    lda  OUTPUT_QUOT+1
    adc  #$00
    sta  OUTPUT_QUOT+1
    lda  OUTPUT_QUOT+2
    adc  #$00
    sta  OUTPUT_QUOT+2
    lda  OUTPUT_QUOT+3
    adc  #$00
    sta  OUTPUT_QUOT+3
    rts  
L072A:
    lda  #$00
    sta  OUTPUT_QUOT
    sta  OUTPUT_QUOT+1
    sta  OUTPUT_QUOT+2
    sta  OUTPUT_QUOT+3
    sta  OUTPUT_REM
    sta  OUTPUT_REM+1
    sta  OUTPUT_REM+2
    sta  OUTPUT_REM+3
    rts  

; segment $2000 (251 bytes)
* = KERNEL_AUX
FAST_UDIV32_ALIGNED_TAIL:
L2000:
    lda  INPUT_DIV
    sta  TEMP_RAM
    lda  INPUT_DIV+1
    sta  TEMP_RAM+1
    lda  INPUT_DIV+2
    sta  TEMP_RAM+2
    lda  INPUT_DIV+3
    sta  TEMP_RAM+3
    lda  #$00
    sta  OUTPUT_QUOT
    sta  OUTPUT_QUOT+1
    sta  OUTPUT_QUOT+2
    sta  OUTPUT_QUOT+3
    ldx  #$01
L2028:
    bit  TEMP_RAM+3
    bmi  L206F
    asl  TEMP_RAM
    rol  TEMP_RAM+1
    rol  TEMP_RAM+2
    rol  TEMP_RAM+3
    lda  OUTPUT_REM+3
    cmp  TEMP_RAM+3
    bcc  L2063
    bne  L205F
    lda  OUTPUT_REM+2
    cmp  TEMP_RAM+2
    bcc  L2063
    bne  L205F
    lda  OUTPUT_REM+1
    cmp  TEMP_RAM+1
    bcc  L2063
    bne  L205F
    lda  OUTPUT_REM
    cmp  TEMP_RAM
    bcc  L2063
L205F:
    inx
    jmp  L2028
L2063:
    lsr  TEMP_RAM+3
    ror  TEMP_RAM+2
    ror  TEMP_RAM+1
    ror  TEMP_RAM
L206F:
    ldy  OUTPUT_REM+3
L2072:
    cpy  TEMP_RAM+3
    bcc  L20D8
    bne  L20B5
    lda  OUTPUT_REM+2
    cmp  TEMP_RAM+2
    bcc  L20D8
    bne  L2095
    lda  OUTPUT_REM+1
    cmp  TEMP_RAM+1
    bcc  L20D8
    bne  L2095
    lda  OUTPUT_REM
    cmp  TEMP_RAM
    bcc  L20D8
L2095:
    lda  OUTPUT_REM
    sbc  TEMP_RAM
    sta  OUTPUT_REM
    lda  OUTPUT_REM+1
    sbc  TEMP_RAM+1
    sta  OUTPUT_REM+1
    lda  OUTPUT_REM+2
    sbc  TEMP_RAM+2
    sta  OUTPUT_REM+2
    ldy  #$00
    jmp  L20D9
L20B5:
    lda  OUTPUT_REM
    sbc  TEMP_RAM
    sta  OUTPUT_REM
    lda  OUTPUT_REM+1
    sbc  TEMP_RAM+1
    sta  OUTPUT_REM+1
    lda  OUTPUT_REM+2
    sbc  TEMP_RAM+2
    sta  OUTPUT_REM+2
    tya
    sbc  TEMP_RAM+3
    tay
    jmp  L20D9
L20D8:
    clc
L20D9:
    rol  OUTPUT_QUOT
    rol  OUTPUT_QUOT+1
    rol  OUTPUT_QUOT+2
    rol  OUTPUT_QUOT+3
    dex
    beq  L20F7
    lsr  TEMP_RAM+3
    ror  TEMP_RAM+2
    ror  TEMP_RAM+1
    ror  TEMP_RAM
    jmp  L2072
L20F7:
    sty  OUTPUT_REM+3
    rts
