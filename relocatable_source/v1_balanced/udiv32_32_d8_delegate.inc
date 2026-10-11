; Issue39 V1 Balanced proven D8 denominator gate for 32/32 DIV/MOD.
; Reached after 32/32 public gate proves N>D, D!=0, D3=0.
; For D1=D2=0, reused V1 UDIV32/16 yields exact Q and two-byte R.
; Other D3=0 denominators incur a measured <=14-cycle guard cost.
; V5 reclaims this V1-only island and installs its own faster D16 helper.
* = REG_LOW+$0D80
V1_D3232_D8_GATE:
    lda MATH_D+2
    ora MATH_D+1
    bne V1_D3232_D8_OLD
    jsr MATH_UDIV32_16
    lda #0
    sta MATH_R+2
    sta MATH_R+3
    clc
    rts
V1_D3232_D8_OLD:
    jmp REG_GAME
