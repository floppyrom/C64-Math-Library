; C64ML Issue144 signed SHR16 direct-slice EXCLUSIVE overlay: v2_pareto_fast
; Exact stock resident required; 49 shared producer bytes modified.
; BEGIN/END must not be interrupted by code calling signed math.
; NO ordinary SMUL32, READY or overlapping IRQ/NMI math while enabled.
; Requires MATH_INIT; no additional normal zero page or data tables.
; User must verify example $0900 installer RAM actually available.
; Overlay conflicts with any other optional $0900 batch installer.
; Normal SHR16 public address $5E15 unchanged, all signed inputs valid.
!cpu 6510
* = $0900

SMUL32_SHR16_EXCLUSIVE_BEGIN:
    lda #$08
    sta $357F
    sta $39F7
    sta $557B
    sta $CAB0
    lda #$09
    sta $3592
    sta $3A17
    sta $559B
    sta $CAC3
    lda #$0A
    sta $35A2
    sta $3A71
    sta $55F5
    sta $CAD3
    lda #$0B
    sta $35AC
    sta $3A77
    sta $55FC
    sta $CADD
    lda #$0C
    sta $35B3
    sta $3A7E
    sta $5604
    sta $CAE4
    lda #$0D
    sta $35BA
    sta $3A85
    sta $560C
    sta $CAEB
    lda #$4C
    sta $C50C
    lda #$EA
    sta $356E
    sta $356F
    sta $3570
    sta $35BE
    sta $35BF
    sta $35C0
    sta $39E9
    sta $39EA
    sta $39EB
    sta $3A89
    sta $3A8A
    sta $3A8B
    sta $556D
    sta $556E
    sta $556F
    sta $5610
    sta $5611
    sta $5612
    sta $CA9F
    sta $CAA0
    sta $CAA1
    sta $CAEF
    sta $CAF0
    sta $CAF1
    rts

SMUL32_SHR16_EXCLUSIVE_END:
    lda #$08
    sta $35BF
    sta $3A8A
    sta $5611
    sta $CAF0
    lda #$09
    sta $356F
    sta $39EA
    sta $556E
    sta $CAA0
    lda #$0A
    sta $357F
    sta $39F7
    sta $557B
    sta $CAB0
    lda #$0B
    sta $3592
    sta $3A17
    sta $559B
    sta $CAC3
    lda #$0C
    sta $35A2
    sta $3A71
    sta $55F5
    sta $CAD3
    lda #$0D
    sta $35AC
    sta $3A77
    sta $55FC
    sta $CADD
    lda #$0E
    sta $35B3
    sta $3A7E
    sta $5604
    sta $CAE4
    lda #$0F
    sta $35BA
    sta $3A85
    sta $560C
    sta $CAEB
    lda #$20
    sta $C50C
    lda #$8D
    sta $356E
    sta $35BE
    sta $39E9
    sta $3A89
    sta $556D
    sta $5610
    sta $CA9F
    sta $CAEF
    lda #$C0
    sta $3570
    sta $35C0
    sta $39EB
    sta $3A8B
    sta $556F
    sta $5612
    sta $CAA1
    sta $CAF1
    rts
