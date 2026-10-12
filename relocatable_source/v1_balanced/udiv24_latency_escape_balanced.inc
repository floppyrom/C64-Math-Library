; Issue #39 V1 Balanced 24/8 exact short-divisor engine.
; The DU24B_low_d2 branch reaches V1LAT_GATE iff N2>0,D2=0,D>0;
; the earlier q=0/q=1 cases retain their original zero/short paths.
; D1!=0 preserves the original direct Repose tail, byte-for-byte.
* = REG_TABLE+$1FA0
V1LAT_GATE:
    lda MATH_D+1
    bne V1LAT_ORIGINAL
    jmp V1LAT_24_BY_8
V1LAT_ORIGINAL:
    jmp DU24B_low_tail0

; For 0<D<256, hold the partial remainder in just one byte;
; C from ROL represents bit 8, and the subtraction must always set Q-bit.
; The quotient is shifted through its destination bytes (not a ZP copy).
; Exactly 24 iterations, R0 after subtraction is always <D0.
; No new ZP, stack use, or adjustment to N/D/other input bytes.
; V5 substitutes its own V2 24-bit code and uses this REG_LOW slice
; for a separate 32/32 narrow-divisor helper; its builder scrubs V1-only code.
* = REG_LOW+$0D00
V1LAT_24_BY_8:
    lda MATH_N+0
    sta MATH_Q+0
    lda MATH_N+1
    sta MATH_Q+1
    lda MATH_N+2
    sta MATH_Q+2
    lda MATH_D+0
    sta V1LAT_CMP+1
    sta V1LAT_SBC+1
    lda #0
    ; Accumulator carries the 8-bit partial remainder across all 24 bits.
    ; Ninth bit is in carry from ROL A; CMP supplies the subtraction carry.
    ldx #24
V1LAT_8_LOOP:
    asl MATH_Q+0
    rol MATH_Q+1
    rol MATH_Q+2
    rol a
    bcs V1LAT_8_SUB
V1LAT_CMP:
    cmp #$00
    bcc V1LAT_8_NEXT
V1LAT_8_SUB:
V1LAT_SBC:
    sbc #$00
    inc MATH_Q+0
V1LAT_8_NEXT:
    dex
    bne V1LAT_8_LOOP
    sta MATH_R+0
    lda #0
    sta MATH_R+1
    sta MATH_R+2
    clc
    rts
    ; Preserve the entire 84-byte source-owned V1 island.
    ; The 68-byte RAM SMC engine leaves 16 explicitly zero-filled trailing bytes.
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
