; Issue39: reference-byte-identical, fully relocatable public V4 QS16.
; Source-derived from shipped standalone BEGIN/CALL/END disassembly.
; Address/data/REU-bank operands are symbolic. The old generated monolith
; retains raw reference bytes, overwritten at these precise addresses.
; V4 REU_QS16_BASE_BANK is 8-bank aligned and can move from $10 to $30.
; Stable signed/unsigned API contracts, original branch encodings and
; fixed module lengths must be proven with both source maps before release.

* = REG_API+$0A80
mul_u16_u16_u32_qs16_begin:
MATH_REU_QS16_BEGIN:
    lda #$04                           
    sta $DF07                          
    lda #$00                           
    sta $DF0A                          
    rts

* = REG_API+$0A8B
mul_u16_u16_u32_qs16:
MATH_REU_QS16:
    clc                                
    lda MATH_IO                          
    adc MATH_IO+$04                          
    sta ZP_MAIN+$0E                            
    lda MATH_IO+$01                          
    adc MATH_IO+$05                          
    sta ZP_MAIN+$0F                            
    lda #$00                           
    adc #$00                           
    sta ZP_MAIN+$10                            
    lda MATH_IO+$01                          
    cmp MATH_IO+$05                          
    bcc L3ACC                          
    bne L3AB4                          
    lda MATH_IO                          
    cmp MATH_IO+$04                          
    bcc L3ACC                          
L3AB4:
    sec                                
    lda MATH_IO                          
    sbc MATH_IO+$04                          
    sta ZP_MAIN+$11                            
    lda MATH_IO+$01                          
    sbc MATH_IO+$05                          
    sta ZP_MAIN+$12                            
    lda #$00                           
    sta ZP_MAIN+$13                            
    jmp L3AE1                          
L3ACC:
    sec                                
    lda MATH_IO+$04                          
    sbc MATH_IO                          
    sta ZP_MAIN+$11                            
    lda MATH_IO+$05                          
    sbc MATH_IO+$01                          
    sta ZP_MAIN+$12                            
    lda #$00                           
    sta ZP_MAIN+$13                            
L3AE1:
    asl ZP_MAIN+$0E                            
    rol ZP_MAIN+$0F                            
    rol ZP_MAIN+$10                            
    asl ZP_MAIN+$0E                            
    rol ZP_MAIN+$0F                            
    rol ZP_MAIN+$10                            
    lda ZP_MAIN+$0E                            
    sta $DF04                          
    lda ZP_MAIN+$0F                            
    sta $DF05                          
    lda ZP_MAIN+$10                            
    ora #REU_QS16_BASE_BANK                           
    sta $DF06                          
    lda #$B1                           
    sta $DF01                          
    lda REU_SCRATCH                          
    sta ZP_MAIN+$1A                            
    lda REU_SCRATCH+$01                          
    sta ZP_MAIN+$1B                            
    lda REU_SCRATCH+$02                          
    sta ZP_MAIN+$1C                            
    lda REU_SCRATCH+$03                          
    sta ZP_MAIN+$1D                            
    asl ZP_MAIN+$11                            
    rol ZP_MAIN+$12                            
    rol ZP_MAIN+$13                            
    asl ZP_MAIN+$11                            
    rol ZP_MAIN+$12                            
    rol ZP_MAIN+$13                            
    lda ZP_MAIN+$11                            
    sta $DF04                          
    lda ZP_MAIN+$12                            
    sta $DF05                          
    lda ZP_MAIN+$13                            
    ora #REU_QS16_BASE_BANK                           
    sta $DF06                          
    lda #$B1                           
    sta $DF01                          
    sec                                
    lda ZP_MAIN+$1A                            
    sbc REU_SCRATCH                          
    sta MATH_IO+$08                          
    lda ZP_MAIN+$1B                            
    sbc REU_SCRATCH+$01                          
    sta MATH_IO+$09                          
    lda ZP_MAIN+$1C                            
    sbc REU_SCRATCH+$02                          
    sta MATH_IO+$0A                          
    lda ZP_MAIN+$1D                            
    sbc REU_SCRATCH+$03                          
    sta MATH_IO+$0B                          
    clc                                
    rts

* = REG_API+$0B5C
mul_u16_u16_u32_qs16_end:
MATH_REU_QS16_END:
    lda #$01                           
    sta $DF07                          
    lda #$C0                           
    sta $DF0A                          
    rts
