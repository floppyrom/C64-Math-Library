; Self-contained *fixed-map* NMOS 6510 executable kernel from Repose OptiSearch.
; Generated source, not a source mirror of the full C64 Math Library resident.
; The fixed code / buffers / ZP are owned entirely by the caller. It is not
; a universal relocate-at-will module; update memory ownership before reuse.
; Original generator strategy: division.live-high-quotient-state-zp-tail-unsigned
; No tables, ROM calls, library resident, or REU needed.
!cpu 6510

INPUT_NUM = $0300
INPUT_DIV = $0320
OUTPUT_QUOT = $0540
OUTPUT_REM = $0560
TEMP_ZP = $10


; segment $0600 (325 bytes)
* = $0600
FAST_UDIV32_ZPTAIL_T1:
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

; segment $2000 (219 bytes)
* = $2000
FAST_UDIV32_INTERNAL_TAIL:
L2000:
    lda  INPUT_DIV
    sta  TEMP_ZP
    lda  INPUT_DIV+1
    sta  TEMP_ZP+1
    lda  INPUT_DIV+2
    sta  TEMP_ZP+2
    lda  INPUT_DIV+3
    sta  TEMP_ZP+3
    lda  #$00
    sta  OUTPUT_QUOT
    sta  OUTPUT_QUOT+1
    sta  OUTPUT_QUOT+2
    sta  OUTPUT_QUOT+3
    ldx  #$01
L2024:
    bit  TEMP_ZP+3
    bmi  L205E
    asl  TEMP_ZP
    rol  TEMP_ZP+1
    rol  TEMP_ZP+2
    rol  TEMP_ZP+3
    lda  OUTPUT_REM+3
    cmp  TEMP_ZP+3
    bcc  L2056
    bne  L2052
    lda  OUTPUT_REM+2
    cmp  TEMP_ZP+2
    bcc  L2056
    bne  L2052
    lda  OUTPUT_REM+1
    cmp  TEMP_ZP+1
    bcc  L2056
    bne  L2052
    lda  OUTPUT_REM
    cmp  TEMP_ZP
    bcc  L2056
L2052:
    inx  
    jmp  L2024
L2056:
    lsr  TEMP_ZP+3
    ror  TEMP_ZP+2
    ror  TEMP_ZP+1
    ror  TEMP_ZP
L205E:
    ldy  OUTPUT_REM+3
L2061:
    cpy  TEMP_ZP+3
    bcc  L20BC
    bne  L209D
    lda  OUTPUT_REM+2
    cmp  TEMP_ZP+2
    bcc  L20BC
    bne  L2080
    lda  OUTPUT_REM+1
    cmp  TEMP_ZP+1
    bcc  L20BC
    bne  L2080
    lda  OUTPUT_REM
    cmp  TEMP_ZP
    bcc  L20BC
L2080:
    lda  OUTPUT_REM
    sbc  TEMP_ZP
    sta  OUTPUT_REM
    lda  OUTPUT_REM+1
    sbc  TEMP_ZP+1
    sta  OUTPUT_REM+1
    lda  OUTPUT_REM+2
    sbc  TEMP_ZP+2
    sta  OUTPUT_REM+2
    ldy  #$00
    jmp  L20BD
L209D:
    lda  OUTPUT_REM
    sbc  TEMP_ZP
    sta  OUTPUT_REM
    lda  OUTPUT_REM+1
    sbc  TEMP_ZP+1
    sta  OUTPUT_REM+1
    lda  OUTPUT_REM+2
    sbc  TEMP_ZP+2
    sta  OUTPUT_REM+2
    tya  
    sbc  TEMP_ZP+3
    tay  
    jmp  L20BD
L20BC:
    clc  
L20BD:
    rol  OUTPUT_QUOT
    rol  OUTPUT_QUOT+1
    rol  OUTPUT_QUOT+2
    rol  OUTPUT_QUOT+3
    dex  
    beq  L20D7
    lsr  TEMP_ZP+3
    ror  TEMP_ZP+2
    ror  TEMP_ZP+1
    ror  TEMP_ZP
    jmp  L2061
L20D7:
    sty  OUTPUT_REM+3
    rts  
