; Issue39 ISQRT16 candidate: INDEPENDENT MANUAL math/ABI architecture.
; Fit the high-byte ceiling seed and correction code INSIDE the retired
; eight-guess square-search code island. No new normal zero page.
; IS16_FAST_BASE is supplied by each profile's source wrapper.
; Existing SQLO/SQHI resident planes at REG_TABLE+$3800/$3900 are reused.
; No private OptiSearch code or generated data is included.
; EXPERIMENTAL until both maps/native VICE/public mixed-call proof.

* = IS16_FAST_BASE
IS16_FAST_START:
    ldx MATH_N+$01
    ldy IS16_FAST_SEED,x
    ; Tiny-N branch: for N<64 the exact root is in 0..7,
    ; otherwise N1=0 means root 8..15. This makes the maximum
    ; downward correction seven rather than fifteen.
    txa
    bne IS16_FAST_TRY
    lda MATH_N+$00
    cmp #$40
    bcs IS16_FAST_TRY
    ldy #$07
IS16_FAST_TRY:
    lda MATH_N+$01
    cmp REG_TABLE+$3900,y
    bcc IS16_FAST_DECREMENT
    bne IS16_FAST_STORE
    lda MATH_N+$00
    cmp REG_TABLE+$3800,y
    bcc IS16_FAST_DECREMENT
IS16_FAST_DECREMENT:
    dey
    bne IS16_FAST_TRY ; if Y reaches zero, sqrt(N)=0 is exact
IS16_FAST_STORE:
    sty MATH_Z+$00
    lda #$00
    sta MATH_Z+$01
    clc
    rts
IS16_FAST_SEED:
    !byte $0F, $16, $1B, $1F, $23, $27, $2A, $2D, $2F, $32, $35, $37, $39, $3B, $3D, $3F
    !byte $41, $43, $45, $47, $49, $4B, $4C, $4E, $4F, $51, $53, $54, $56, $57, $59, $5A
    !byte $5B, $5D, $5E, $5F, $61, $62, $63, $65, $66, $67, $68, $6A, $6B, $6C, $6D, $6E
    !byte $6F, $71, $72, $73, $74, $75, $76, $77, $78, $79, $7A, $7B, $7C, $7D, $7E, $7F
    !byte $80, $81, $82, $83, $84, $85, $86, $87, $88, $89, $8A, $8B, $8C, $8D, $8E, $8F
    !byte $8F, $90, $91, $92, $93, $94, $95, $96, $96, $97, $98, $99, $9A, $9B, $9B, $9C
    !byte $9D, $9E, $9F, $9F, $A0, $A1, $A2, $A3, $A3, $A4, $A5, $A6, $A7, $A7, $A8, $A9
    !byte $AA, $AA, $AB, $AC, $AD, $AD, $AE, $AF, $AF, $B0, $B1, $B2, $B2, $B3, $B4, $B5
    !byte $B5, $B6, $B7, $B7, $B8, $B9, $B9, $BA, $BB, $BB, $BC, $BD, $BD, $BE, $BF, $BF
    !byte $C0, $C1, $C1, $C2, $C3, $C3, $C4, $C5, $C5, $C6, $C7, $C7, $C8, $C9, $C9, $CA
    !byte $CB, $CB, $CC, $CC, $CD, $CE, $CE, $CF, $CF, $D0, $D1, $D1, $D2, $D3, $D3, $D4
    !byte $D4, $D5, $D6, $D6, $D7, $D7, $D8, $D9, $D9, $DA, $DA, $DB, $DB, $DC, $DD, $DD
    !byte $DE, $DE, $DF, $DF, $E0, $E1, $E1, $E2, $E2, $E3, $E3, $E4, $E5, $E5, $E6, $E6
    !byte $E7, $E7, $E8, $E8, $E9, $EA, $EA, $EB, $EB, $EC, $EC, $ED, $ED, $EE, $EE, $EF
    !byte $EF, $F0, $F1, $F1, $F2, $F2, $F3, $F3, $F4, $F4, $F5, $F5, $F6, $F6, $F7, $F7
    !byte $F8, $F8, $F9, $F9, $FA, $FA, $FB, $FB, $FC, $FC, $FD, $FD, $FE, $FE, $FF, $FF
IS16_FAST_END:
