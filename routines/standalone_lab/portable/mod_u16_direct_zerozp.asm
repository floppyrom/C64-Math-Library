; Standalone memory-specialist unsigned 16/16 remainder (UMOD16).
; Repose OptiSearch direct-chain generated donor; C64ML: carry correction and Q preservation.
; Not a full-corpus speed winner. No zero-page bytes; requires 2 ordinary scratch bytes.
; NMOS 6510; CLD before call; original N/D unchanged; C=1 only on D=0.
; Call FAST_UMOD16_DIRECT_PUBLIC. Q untouched. R=0 on D=0.
; Table 16 bytes + donor 945 executable bytes + C64ML 15-byte adapter.
; The three code/data regions must not overlap or alias caller-owned RAM.
!cpu 6510
KERNEL_CODE = $8000
KERNEL_TABLE = $8400
KERNEL_ADAPTER = $8800
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_RAM = $C020

* = KERNEL_TABLE
FAST_UMOD16_DIRECT_CUTOFF_TABLE:
    !byte $00,$0B,$16,$21,$2C,$37,$42,$4D,$58,$63,$6E,$79,$84,$8F,$9A,$A5

* = KERNEL_CODE
FAST_UMOD16_DIRECT_CORE:
    lax  INPUT_NUM+1
    cmp  INPUT_DIV+1
    bcs  L0682
L0678:
    lda  INPUT_NUM
    sta  OUTPUT_REM
    stx  OUTPUT_REM+1
    rts  
L0682:
    bne  L069F
    lda  INPUT_NUM
    sbc  INPUT_DIV
    bcs  L068F
    jmp  L0678
L068F:
    cpx  #$00
    bne  L0696
    jmp  L09CF
L0696:
    sta  OUTPUT_REM
    lda  #$00
    sta  OUTPUT_REM+1
    rts  
L069F:
    lda  INPUT_NUM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    txa  
    sbc  INPUT_DIV+1
    sta  OUTPUT_REM+1
    cmp  INPUT_DIV+1
    bcc  L06E0
    bne  L06BE
    lda  OUTPUT_REM
    cmp  INPUT_DIV
    bcc  L06DD
L06BE:
    ldx  INPUT_DIV+1
    cpx  #$0F
    bcc  L06C8
    jmp  L06E1
L06C8:
    cpx  #$01
    bcc  L06DA
    lda  OUTPUT_REM+1
    cmp  FAST_UMOD16_DIRECT_CUTOFF_TABLE,x
    bcs  L06D7
    jmp  L06E1
L06D7:
    jmp  L0986
L06DA:
    jmp  L09CF
L06DD:
    lda  OUTPUT_REM+1
L06E0:
    rts  
L06E1:
    sec  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    lda  OUTPUT_REM+1
    sbc  INPUT_DIV+1
    cmp  INPUT_DIV+1
    bcc  L075A
    beq  L0748
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L0706:
    cmp  INPUT_DIV+1
    bcc  L0770
    beq  L075E
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L071B:
    cmp  INPUT_DIV+1
    bcc  L0786
    beq  L0774
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L0730:
    cmp  INPUT_DIV+1
    bcc  L079C
    beq  L078A
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
    jmp  L07A0
L0748:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L0759
    sta  OUTPUT_REM
    lda  #$00
    jmp  L0706
L0759:
    txa  
L075A:
    sta  OUTPUT_REM+1
    rts  
L075E:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L076F
    sta  OUTPUT_REM
    lda  #$00
    jmp  L071B
L076F:
    txa  
L0770:
    sta  OUTPUT_REM+1
    rts  
L0774:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L0785
    sta  OUTPUT_REM
    lda  #$00
    jmp  L0730
L0785:
    txa  
L0786:
    sta  OUTPUT_REM+1
    rts  
L078A:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L079B
    sta  OUTPUT_REM
    lda  #$00
    jmp  L07A0
L079B:
    txa  
L079C:
    sta  OUTPUT_REM+1
    rts  
L07A0:
    cmp  INPUT_DIV+1
    bcc  L0809
    beq  L07F7
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L07B5:
    cmp  INPUT_DIV+1
    bcc  L081F
    beq  L080D
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L07CA:
    cmp  INPUT_DIV+1
    bcc  L0835
    beq  L0823
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L07DF:
    cmp  INPUT_DIV+1
    bcc  L084B
    beq  L0839
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
    jmp  L084F
L07F7:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L0808
    sta  OUTPUT_REM
    lda  #$00
    jmp  L07B5
L0808:
    txa  
L0809:
    sta  OUTPUT_REM+1
    rts  
L080D:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L081E
    sta  OUTPUT_REM
    lda  #$00
    jmp  L07CA
L081E:
    txa  
L081F:
    sta  OUTPUT_REM+1
    rts  
L0823:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L0834
    sta  OUTPUT_REM
    lda  #$00
    jmp  L07DF
L0834:
    txa  
L0835:
    sta  OUTPUT_REM+1
    rts  
L0839:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L084A
    sta  OUTPUT_REM
    lda  #$00
    jmp  L084F
L084A:
    txa  
L084B:
    sta  OUTPUT_REM+1
    rts  
L084F:
    cmp  INPUT_DIV+1
    bcc  L08B8
    beq  L08A6
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L0864:
    cmp  INPUT_DIV+1
    bcc  L08CE
    beq  L08BC
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L0879:
    cmp  INPUT_DIV+1
    bcc  L08E4
    beq  L08D2
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L088E:
    cmp  INPUT_DIV+1
    bcc  L08FA
    beq  L08E8
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
    jmp  L08FE
L08A6:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L08B7
    sta  OUTPUT_REM
    lda  #$00
    jmp  L0864
L08B7:
    txa  
L08B8:
    sta  OUTPUT_REM+1
    rts  
L08BC:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L08CD
    sta  OUTPUT_REM
    lda  #$00
    jmp  L0879
L08CD:
    txa  
L08CE:
    sta  OUTPUT_REM+1
    rts  
L08D2:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L08E3
    sta  OUTPUT_REM
    lda  #$00
    jmp  L088E
L08E3:
    txa  
L08E4:
    sta  OUTPUT_REM+1
    rts  
L08E8:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L08F9
    sta  OUTPUT_REM
    lda  #$00
    jmp  L08FE
L08F9:
    txa  
L08FA:
    sta  OUTPUT_REM+1
    rts  
L08FE:
    cmp  INPUT_DIV+1
    bcc  L0952
    beq  L0940
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L0913:
    cmp  INPUT_DIV+1
    bcc  L0968
    beq  L0956
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
L0928:
    cmp  INPUT_DIV+1
    bcc  L097E
    beq  L096C
    tay  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    tya  
    sbc  INPUT_DIV+1
    jmp  L0982
L0940:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L0951
    sta  OUTPUT_REM
    lda  #$00
    jmp  L0913
L0951:
    txa  
L0952:
    sta  OUTPUT_REM+1
    rts  
L0956:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L0967
    sta  OUTPUT_REM
    lda  #$00
    jmp  L0928
L0967:
    txa  
L0968:
    sta  OUTPUT_REM+1
    rts  
L096C:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L097D
    sta  OUTPUT_REM
    lda  #$00
    jmp  L0982
L097D:
    txa  
L097E:
    sta  OUTPUT_REM+1
    rts  
L0982:
    sta  OUTPUT_REM+1
    rts  
L0986:
    lda  INPUT_NUM
    sta  TEMP_RAM
    lda  INPUT_NUM+1
    sta  OUTPUT_REM
    lda  #$00
    lsr  a
    ldy  #$08
L0997:
    rol  TEMP_RAM
    rol  OUTPUT_REM
    rol  a
    cmp  INPUT_DIV+1
    bcc  L09C8
    beq  L09B6
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    sta  OUTPUT_REM
    txa  
    sbc  INPUT_DIV+1
    jmp  L09C8
L09B6:
    tax  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    bcc  L09C7
    sta  OUTPUT_REM
    lda  #$00
    jmp  L09C8
L09C7:
    txa  
L09C8:
    dey  
    bne  L0997
    sta  OUTPUT_REM+1
    rts  
L09CF:
    lda  INPUT_DIV
    ora  INPUT_DIV+1
    bne  L09DA
    jmp  L0A17
L09DA:
    lda  INPUT_NUM
    sta  TEMP_RAM
    lda  INPUT_NUM+1
    sta  TEMP_RAM+1
    lda  #$00
    sta  OUTPUT_REM
    sta  OUTPUT_REM+1
    ldy  #$10
    clc  
L09F1:
    rol  TEMP_RAM
    rol  TEMP_RAM+1
    rol  OUTPUT_REM
    rol  OUTPUT_REM+1
    sec  
    lda  OUTPUT_REM
    sbc  INPUT_DIV
    tax  
    lda  OUTPUT_REM+1
    sbc  INPUT_DIV+1
    bcc  L0A13
    sta  OUTPUT_REM+1
    stx  OUTPUT_REM
L0A13:
    dey  
    bne  L09F1
    rts  
L0A17:
    lda  #$00
    sta  OUTPUT_REM
    sta  OUTPUT_REM+1
    sec  
    rts  

; The donor does not normalize carry, so call this 15-byte public adapter.
* = KERNEL_ADAPTER
FAST_UMOD16_DIRECT_PUBLIC:
    jsr FAST_UMOD16_DIRECT_CORE
    lda INPUT_DIV
    ora INPUT_DIV+1
    beq UMOD16_DIRECT_ZERO
    clc
    rts
UMOD16_DIRECT_ZERO:
    sec
    rts
