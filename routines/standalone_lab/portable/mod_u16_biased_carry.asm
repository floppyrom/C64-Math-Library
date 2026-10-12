; Source-backed standalone copy of mod_u16_biased_carry.asm (Repose / OptiSearch donor).
; Independent relocation experiment: edit the constants below to choose a new map.
; Keep code, buffers and scratch disjoint, with the 6510 memory configuration
; exposing RAM in those regions. This file remains emulator-qualified only.
; Decimal mode clear (CLD); success C=0, zero-divisor C=1.
; 244-byte core at KERNEL_CODE; 18-byte entry/adapter at KERNEL_ADAPTER; ZP TEMP_ZP must be exclusively owned.
!cpu 6510

KERNEL_CODE = $8000
KERNEL_ADAPTER = $8400


INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_ZP = $50



; segment $0610 (244 bytes)
* = KERNEL_CODE
FAST_UMOD16_BIASED:
    lax  INPUT_NUM+1
    cmp  INPUT_DIV+1
    bcs  L0622
L0618:
    lda  INPUT_NUM
    sta  OUTPUT_REM
    stx  OUTPUT_REM+1
    rts  
L0622:
    bne  L064F
    lda  INPUT_NUM
    sbc  INPUT_DIV
    bcc  L0618
    sta  OUTPUT_REM
    txa  
    bne  L063F
    lda  INPUT_DIV
    beq  L0645
    stx  OUTPUT_REM+1
    ldx  #$FC
    jmp  L0696
L063F:
    anc  #$00
    sta  OUTPUT_REM+1
    rts  
L0645:
    ldx  #$00
    stx  OUTPUT_REM
    stx  OUTPUT_REM+1
    sec  
    rts  
L064F:
    lda  INPUT_NUM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    txa  
    sbc  INPUT_DIV+1
    cmp  INPUT_DIV+1
    bcc  L066D
    bne  L0673
    tax  
    lda  OUTPUT_REM
    cmp  INPUT_DIV
    bcs  L0672
    txa  
L066D:
    sta  OUTPUT_REM+1
    rts  
L0671:
    rts  
L0672:
    txa  
L0673:
    ldx  INPUT_DIV+1
    bne  L067D
    ldx  INPUT_DIV
    beq  L0645
L067D:
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
    sta  OUTPUT_REM+1
    cmp  INPUT_DIV+1
    bcs  L0694
    rts  
L0694:
    ldx  #$FD
L0696:
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    tay  
    lda  OUTPUT_REM+1
    sbc  INPUT_DIV+1
    bcc  L0671
    sta  OUTPUT_REM+1
    sty  OUTPUT_REM
    inx  
    bmi  L0696
    cmp  INPUT_DIV+1
    bcc  L0671
    bne  L06BD
    lda  OUTPUT_REM
    cmp  INPUT_DIV
    bcc  L0671
L06BD:
    lda  INPUT_DIV
    sta  TEMP_ZP
    lda  INPUT_DIV+1
    sta  TEMP_ZP+1
    ldy  OUTPUT_REM+1
L06CA:
    asl  TEMP_ZP
    rol  TEMP_ZP+1
    cpy  TEMP_ZP+1
    bcc  L06E3
    bne  L06DB
    lda  OUTPUT_REM
    cmp  TEMP_ZP
    bcc  L06E3
L06DB:
    inx  
    bit  TEMP_ZP+1
    bpl  L06CA
    inx  
    bpl  L06E8
L06E3:
    lsr  TEMP_ZP+1
    inx  
L06E6:
    ror  TEMP_ZP
L06E8:
    sec  
    lda  OUTPUT_REM
    sbc  TEMP_ZP
    tay  
    lda  OUTPUT_REM+1
    sbc  TEMP_ZP+1
    bcc  L06FC
    sta  OUTPUT_REM+1
    sty  OUTPUT_REM
L06FC:
    dex  
    beq  L0703
    lsr  TEMP_ZP+1
    bpl  L06E6
L0703:
    rts  

; 15-byte public ABI adapter: carry set if and only if divisor is zero.
; Entry for standalone callers: FAST_UMOD16_CARRYFIX at $0800.
; This uses one extra JSR frame (2 stack bytes) over the donor code.
* = KERNEL_ADAPTER
FAST_UMOD16_CARRYFIX:
    jsr FAST_UMOD16_BIASED
    lda INPUT_DIV
    ora INPUT_DIV+1
    beq carry_divzero
    clc
    rts
carry_divzero:
    sec
    rts

; Optional 3-byte profile-style public jump for apples-to-apples benchmarks.
* = KERNEL_ADAPTER+$0f
FAST_UMOD16_PUBLIC:
    jmp FAST_UMOD16_CARRYFIX
