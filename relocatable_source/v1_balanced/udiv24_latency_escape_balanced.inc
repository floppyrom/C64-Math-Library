; Issue #39 V1 Balanced narrow-divisor latency escape.
; Only N2>0,D2=0 reaches this helper: the original N2=0 small-quotient
; paths go directly to DU24B_low_tail0 without a new dispatch penalty.
; DU24B_div_u24 starts with LAX MATH_N+2. X=N2 is still live here.
; V5 reserves $7678-$7F78 for signed source donors; the $7FA0
; placement is intentionally beyond that code and inside the V1 REG_TABLE.
* = REG_TABLE+$1FA0
V1LAT_GATE:
    lda MATH_D+1
    bne V1LAT_ORIGINAL
    cpx MATH_D+0
    bcc V1LAT_ORIGINAL
    jmp V1LAT_NARROW
V1LAT_ORIGINAL:
    jmp DU24B_low_tail0
V1LAT_NARROW:
    ; V1 public UDIV32/16 already accepts the narrow full dividend.
    ; Preserve the fourth N byte, not owned by 24-bit ABI; clear R2.
    lda MATH_N+3
    pha
    lda #0
    sta MATH_N+3
    jsr MATH_UDIV32_16
    pla
    sta MATH_N+3
    lda #0
    sta MATH_R+2
    rts
