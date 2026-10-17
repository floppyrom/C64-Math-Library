; Selective V2-compatible ISQRT32 highword seed + 4+4 radix-4 refinement.
; Entry/highword seed derived from exact canonical V2 source:
; relocatable_source/v2_pareto_fast/isqrt32_direct_highword_normal.inc
; Step helper assembled from canonical V2 generated executable source:
; relocatable_source/v2_pareto_fast/math_relocatable.asm (LC968..LC9BB).
; Three square/seed pages are exact mathematical lookup tables, not copied PRG bytes.
; Preserves N32, X/Y and stack; floor sqrt in Z16, carry clear.
; Code is read-only, no init, no REU; seven scratch zero-page bytes. CLD required.
!cpu 6510
KERNEL_CODE = $8000
SQ_SQUARE_LO = $9000
SQ_SQUARE_HI = $9100
SQ_GUESS = $9200
INPUT_NUM = $C010
OUTPUT_Z = $C008
TEMP_ZP = $90
* = KERNEL_CODE
LCB40:
    txa
    pha
    tya
    pha
    jsr LC836
    ldx OUTPUT_Z
    stx TEMP_ZP+3
    lda #$00
    sta TEMP_ZP+4
    sec
    lda INPUT_NUM+2
    sbc SQ_SQUARE_LO,x
    sta TEMP_ZP+0
    lda INPUT_NUM+3
    sbc SQ_SQUARE_HI,x
    sta TEMP_ZP+1
    lda #$00
    sta TEMP_ZP+2
    ldx INPUT_NUM+1
    jsr SQ_STEP4
    ldx INPUT_NUM
    jsr SQ_STEP4
    lda TEMP_ZP+3
    sta OUTPUT_Z
    lda TEMP_ZP+4
    sta OUTPUT_Z+1
    pla
    tay
    pla
    tax
    clc
    rts

; Seed helper follows main entry, without its former fixed-address gap
LC836:
    ldx INPUT_NUM+3
    ldy SQ_GUESS,x
LC83C:
    lda INPUT_NUM+3
    cmp SQ_SQUARE_HI,y
    bcc LC858
    bne LC84E
    lda INPUT_NUM+2
    cmp SQ_SQUARE_LO,y
    bcc LC858
LC84E:
    sty OUTPUT_Z
    lda #$00
    sta OUTPUT_Z+1
    clc
    rts
LC858:
    dey
    jmp LC83C

SQ_STEP4:
    ldy #$04
LC968:
    txa
    asl
    rol TEMP_ZP+0
    rol TEMP_ZP+1
    rol TEMP_ZP+2
    asl
    rol TEMP_ZP+0
    rol TEMP_ZP+1
    rol TEMP_ZP+2
    tax
    asl TEMP_ZP+3
    rol TEMP_ZP+4
    lda TEMP_ZP+3
    asl
    ora #$01
    sta TEMP_ZP+5
    lda TEMP_ZP+4
    rol
    sta TEMP_ZP+6
    bcc LC994
    lda TEMP_ZP+2
    beq LC9BB
    cmp #$01
    bne LC9A6
    beq LC998
LC994:
    lda TEMP_ZP+2
    bne LC9A6
LC998:
    lda TEMP_ZP+1
    cmp TEMP_ZP+6
    bcc LC9BB
    bne LC9A6
    lda TEMP_ZP+0
    cmp TEMP_ZP+5
    bcc LC9BB
LC9A6:
    sec
    lda TEMP_ZP+0
    sbc TEMP_ZP+5
    sta TEMP_ZP+0
    lda TEMP_ZP+1
    sbc TEMP_ZP+6
    sta TEMP_ZP+1
    lda TEMP_ZP+2
    sbc #$00
    sta TEMP_ZP+2
    inc TEMP_ZP+3
LC9BB:
    dey
    bne LC968
    rts

* = SQ_SQUARE_LO
    !byte $00, $01, $04, $09, $10, $19, $24, $31, $40, $51, $64, $79, $90, $A9, $C4, $E1
    !byte $00, $21, $44, $69, $90, $B9, $E4, $11, $40, $71, $A4, $D9, $10, $49, $84, $C1
    !byte $00, $41, $84, $C9, $10, $59, $A4, $F1, $40, $91, $E4, $39, $90, $E9, $44, $A1
    !byte $00, $61, $C4, $29, $90, $F9, $64, $D1, $40, $B1, $24, $99, $10, $89, $04, $81
    !byte $00, $81, $04, $89, $10, $99, $24, $B1, $40, $D1, $64, $F9, $90, $29, $C4, $61
    !byte $00, $A1, $44, $E9, $90, $39, $E4, $91, $40, $F1, $A4, $59, $10, $C9, $84, $41
    !byte $00, $C1, $84, $49, $10, $D9, $A4, $71, $40, $11, $E4, $B9, $90, $69, $44, $21
    !byte $00, $E1, $C4, $A9, $90, $79, $64, $51, $40, $31, $24, $19, $10, $09, $04, $01
    !byte $00, $01, $04, $09, $10, $19, $24, $31, $40, $51, $64, $79, $90, $A9, $C4, $E1
    !byte $00, $21, $44, $69, $90, $B9, $E4, $11, $40, $71, $A4, $D9, $10, $49, $84, $C1
    !byte $00, $41, $84, $C9, $10, $59, $A4, $F1, $40, $91, $E4, $39, $90, $E9, $44, $A1
    !byte $00, $61, $C4, $29, $90, $F9, $64, $D1, $40, $B1, $24, $99, $10, $89, $04, $81
    !byte $00, $81, $04, $89, $10, $99, $24, $B1, $40, $D1, $64, $F9, $90, $29, $C4, $61
    !byte $00, $A1, $44, $E9, $90, $39, $E4, $91, $40, $F1, $A4, $59, $10, $C9, $84, $41
    !byte $00, $C1, $84, $49, $10, $D9, $A4, $71, $40, $11, $E4, $B9, $90, $69, $44, $21
    !byte $00, $E1, $C4, $A9, $90, $79, $64, $51, $40, $31, $24, $19, $10, $09, $04, $01
* = SQ_SQUARE_HI
    !byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
    !byte $01, $01, $01, $01, $01, $01, $01, $02, $02, $02, $02, $02, $03, $03, $03, $03
    !byte $04, $04, $04, $04, $05, $05, $05, $05, $06, $06, $06, $07, $07, $07, $08, $08
    !byte $09, $09, $09, $0A, $0A, $0A, $0B, $0B, $0C, $0C, $0D, $0D, $0E, $0E, $0F, $0F
    !byte $10, $10, $11, $11, $12, $12, $13, $13, $14, $14, $15, $15, $16, $17, $17, $18
    !byte $19, $19, $1A, $1A, $1B, $1C, $1C, $1D, $1E, $1E, $1F, $20, $21, $21, $22, $23
    !byte $24, $24, $25, $26, $27, $27, $28, $29, $2A, $2B, $2B, $2C, $2D, $2E, $2F, $30
    !byte $31, $31, $32, $33, $34, $35, $36, $37, $38, $39, $3A, $3B, $3C, $3D, $3E, $3F
    !byte $40, $41, $42, $43, $44, $45, $46, $47, $48, $49, $4A, $4B, $4C, $4D, $4E, $4F
    !byte $51, $52, $53, $54, $55, $56, $57, $59, $5A, $5B, $5C, $5D, $5F, $60, $61, $62
    !byte $64, $65, $66, $67, $69, $6A, $6B, $6C, $6E, $6F, $70, $72, $73, $74, $76, $77
    !byte $79, $7A, $7B, $7D, $7E, $7F, $81, $82, $84, $85, $87, $88, $8A, $8B, $8D, $8E
    !byte $90, $91, $93, $94, $96, $97, $99, $9A, $9C, $9D, $9F, $A0, $A2, $A4, $A5, $A7
    !byte $A9, $AA, $AC, $AD, $AF, $B1, $B2, $B4, $B6, $B7, $B9, $BB, $BD, $BE, $C0, $C2
    !byte $C4, $C5, $C7, $C9, $CB, $CC, $CE, $D0, $D2, $D4, $D5, $D7, $D9, $DB, $DD, $DF
    !byte $E1, $E2, $E4, $E6, $E8, $EA, $EC, $EE, $F0, $F2, $F4, $F6, $F8, $FA, $FC, $FE
* = SQ_GUESS
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
