; Repose OptiSearch 32-bit aligned remainder kernel, specialized standalone.
; Public carry adapter by C64ML. Zero ZP bytes; 4 scratch RAM bytes and nested JSR.
; Check available RAM/code ranges; C=1 on divide by zero, C=0 on success.
!cpu 6510

KERNEL_CODE = $8000
KERNEL_AUX = $9000
KERNEL_ADAPTER = $8400
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_RAM = $C020


; donor segment $0600 (250 bytes)
* = KERNEL_CODE
FAST_UMOD32_ALIGNED_CORE:
    lda  INPUT_NUM+3
    cmp  INPUT_DIV+3
    bcc  L0628
    bne  L0641
    lda  INPUT_NUM+2
    cmp  INPUT_DIV+2
    bcc  L0628
    bne  L0641
    lda  INPUT_NUM+1
    cmp  INPUT_DIV+1
    bcc  L0628
    bne  L0641
    lda  INPUT_NUM
    cmp  INPUT_DIV
    bcc  L0628
    bcs  L0641
L0628:
    lda  INPUT_NUM
    sta  OUTPUT_REM
    lda  INPUT_NUM+1
    sta  OUTPUT_REM+1
    lda  INPUT_NUM+2
    sta  OUTPUT_REM+2
    lda  INPUT_NUM+3
    sta  OUTPUT_REM+3
    rts  
L0641:
    lda  INPUT_DIV+3
    bne  L0654
    lda  INPUT_DIV
    ora  INPUT_DIV+1
    ora  INPUT_DIV+2
    bne  L0654
    jmp  L06EB
L0654:
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
    bcc  L06E0
    beq  L06A0
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
    jmp  L06E4
L06A0:
    tax  
    lda  OUTPUT_REM+2
    cmp  INPUT_DIV+2
    bcc  L06DF
    bne  L06BF
    lda  OUTPUT_REM+1
    cmp  INPUT_DIV+1
    bcc  L06DF
    bne  L06BF
    lda  OUTPUT_REM
    cmp  INPUT_DIV
    bcc  L06DF
    bne  L06BF
L06BF:
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
    jmp  L06E4
L06DF:
    txa  
L06E0:
    sta  OUTPUT_REM+3
    rts  
L06E4:
    sta  OUTPUT_REM+3
    jsr  L2000
    rts  
L06EB:
    lda  #$00
    sta  OUTPUT_REM
    sta  OUTPUT_REM+1
    sta  OUTPUT_REM+2
    sta  OUTPUT_REM+3
    rts  

; donor segment $2000 (225 bytes)
* = KERNEL_AUX
FAST_UMOD32_ALIGNED_TAIL:
L2000:
    lda  INPUT_DIV
    sta  TEMP_RAM
    lda  INPUT_DIV+1
    sta  TEMP_RAM+1
    lda  INPUT_DIV+2
    sta  TEMP_RAM+2
    lda  INPUT_DIV+3
    sta  TEMP_RAM+3
    ldx  #$01
L201A:
    bit  TEMP_RAM+3
    bmi  L2061
    asl  TEMP_RAM
    rol  TEMP_RAM+1
    rol  TEMP_RAM+2
    rol  TEMP_RAM+3
    lda  OUTPUT_REM+3
    cmp  TEMP_RAM+3
    bcc  L2055
    bne  L2051
    lda  OUTPUT_REM+2
    cmp  TEMP_RAM+2
    bcc  L2055
    bne  L2051
    lda  OUTPUT_REM+1
    cmp  TEMP_RAM+1
    bcc  L2055
    bne  L2051
    lda  OUTPUT_REM
    cmp  TEMP_RAM
    bcc  L2055
L2051:
    inx  
    jmp  L201A
L2055:
    lsr  TEMP_RAM+3
    ror  TEMP_RAM+2
    ror  TEMP_RAM+1
    ror  TEMP_RAM
L2061:
    ldy  OUTPUT_REM+3
L2064:
    cpy  TEMP_RAM+3
    bcc  L20CA
    bne  L20A7
    lda  OUTPUT_REM+2
    cmp  TEMP_RAM+2
    bcc  L20CA
    bne  L2087
    lda  OUTPUT_REM+1
    cmp  TEMP_RAM+1
    bcc  L20CA
    bne  L2087
    lda  OUTPUT_REM
    cmp  TEMP_RAM
    bcc  L20CA
L2087:
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
    jmp  L20CB
L20A7:
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
    jmp  L20CB
L20CA:
    clc  
L20CB:
    dex  
    beq  L20DD
    lsr  TEMP_RAM+3
    ror  TEMP_RAM+2
    ror  TEMP_RAM+1
    ror  TEMP_RAM
    jmp  L2064
L20DD:
    sty  OUTPUT_REM+3
    rts  

; Public 21-byte C64 Math Library-compatible carry gate.
* = KERNEL_ADAPTER
FAST_UMOD32_ALIGNED_PUBLIC:
    jsr FAST_UMOD32_ALIGNED_CORE
    lda INPUT_DIV
    ora INPUT_DIV+1
    ora INPUT_DIV+2
    ora INPUT_DIV+3
    beq aligned_zero
    clc
    rts
aligned_zero:
    sec
    rts
