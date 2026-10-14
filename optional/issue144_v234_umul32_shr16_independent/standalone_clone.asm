; ISSUE144 generated original source assembly: relocatable private UMUL32
; Source mirror: v2_pareto_fast/standalone/mul_u32_u32_u48_shr16.asm
; Exclusive addresses $0D05..$0E49; entry $0E03.
; Pure independent code; original resident $5805..$5949 is preserved.
!cpu 6510
* = $0D05
L5805:
    clc
    adc ($3D),y
    sta $1D,x
    lda #$01
    adc ($3F),y
    bcc L5844
L5810:
    clc
    adc ($41),y
    sta $12,x
    lda #$01
    adc ($4F),y
    bcc L5852
L581B:
    clc
    adc ($51),y
    sta $16,x
    lda #$01
    adc ($68),y
    bcc L5860
L5826:
    sta $1A,x
    ldy $C004,x
L582B:
    lda $7000,y
    adc $7400,y
    sta $0E,x
    lda $7200,y
    adc $7600,y
    adc $7000,y
    bcs L5805
    adc ($3D),y
    sta $1D,x
    lda ($3F),y
L5844:
    adc $7600,y
    adc $7000,y
    bcs L5810
    adc ($41),y
    sta $12,x
    lda ($4F),y
L5852:
    adc $7600,y
    adc $7000,y
    bcs L581B
    adc ($51),y
    sta $16,x
    lda ($68),y
L5860:
    adc $7600,y
    dex
    bpl L5826
    tax
    ldy $1A
    clc
    lda $1D
    adc $0F
    nop
    nop
    nop
    lda $1E
    adc $10
    bcc L587C
    inc $11
    beq L58CB
    clc
L587C:
    adc $12
    sta $C008
    lda $13
    adc $16
    bcc L5889
    inx
    clc
L5889:
    adc $11
    bcc L5891
    inx
    beq L58CE
    clc
L5891:
    adc $1F
    sta $C009
    txa
    adc $17
    bcc L589D
    iny
    clc
L589D:
    adc $20
    bcc L58A5
    iny
    beq L58F1
    clc
L58A5:
    adc $14
    sta $C00A
    tya
    adc $15
    bcc L58B2
    inc $1B
    clc
L58B2:
    adc $18
    sta $C00B
    lda $19
    adc $1B
    sta $C00C
    lda $1C
    adc #$00
    sta $C00D
    lda $0E
    clc
    nop
    nop
    rts
L58CB:
    jmp L58D1
L58CE:
    jmp L58E3
L58D1:
    inc $20
    bne L58DF
    inc $15
    bne L58DF
    inc $19
    bne L58DF
    inc $1C
L58DF:
    clc
    jmp L587C
L58E3:
    inc $15
    bne L58ED
    inc $19
    bne L58ED
    inc $1C
L58ED:
    clc
    jmp L5891
L58F1:
    inc $19
    bne L58F7
    inc $1C
L58F7:
    clc
    jmp L58A5
* = $0E03
MATH_UMUL32_SHR16_CLONE:
L5903:
    lda $C003
    ldx #$03
    sec
    ldy $C007
    sta $68
    sta $0D56
    eor #$FF
    sta $51
    sta $0D61
    lda $C000
    sta $0D2C
    sta $0D34
    eor #$FF
    sta $0D2F
    sta $0D37
    lda $C001
    sta $3F
    sta $0D3A
    eor #$FF
    sta $3D
    sta $0D45
    lda $C002
    sta $4F
    sta $0D48
    eor #$FF
    sta $41
    sta $0D53
    jmp L582B
