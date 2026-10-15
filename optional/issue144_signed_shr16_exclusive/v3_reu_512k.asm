; C64ML Issue144 signed SHR16 direct-slice EXCLUSIVE overlay: v3_reu_512k
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
    sta $46F7
    sta $51B0
    sta $557B
    lda #$09
    sta $3592
    sta $4717
    sta $51C3
    sta $559B
    lda #$0A
    sta $35A2
    sta $4771
    sta $51D3
    sta $55F5
    lda #$0B
    sta $35AC
    sta $4777
    sta $51DD
    sta $55FC
    lda #$0C
    sta $35B3
    sta $477E
    sta $51E4
    sta $5604
    lda #$0D
    sta $35BA
    sta $4785
    sta $51EB
    sta $560C
    lda #$4C
    sta $C50C
    lda #$EA
    sta $356E
    sta $356F
    sta $3570
    sta $35BE
    sta $35BF
    sta $35C0
    sta $46E9
    sta $46EA
    sta $46EB
    sta $4789
    sta $478A
    sta $478B
    sta $519F
    sta $51A0
    sta $51A1
    sta $51EF
    sta $51F0
    sta $51F1
    sta $556D
    sta $556E
    sta $556F
    sta $5610
    sta $5611
    sta $5612
    rts

SMUL32_SHR16_EXCLUSIVE_END:
    lda #$08
    sta $35BF
    sta $478A
    sta $51F0
    sta $5611
    lda #$09
    sta $356F
    sta $46EA
    sta $51A0
    sta $556E
    lda #$0A
    sta $357F
    sta $46F7
    sta $51B0
    sta $557B
    lda #$0B
    sta $3592
    sta $4717
    sta $51C3
    sta $559B
    lda #$0C
    sta $35A2
    sta $4771
    sta $51D3
    sta $55F5
    lda #$0D
    sta $35AC
    sta $4777
    sta $51DD
    sta $55FC
    lda #$0E
    sta $35B3
    sta $477E
    sta $51E4
    sta $5604
    lda #$0F
    sta $35BA
    sta $4785
    sta $51EB
    sta $560C
    lda #$20
    sta $C50C
    lda #$8D
    sta $356E
    sta $35BE
    sta $46E9
    sta $4789
    sta $519F
    sta $51EF
    sta $556D
    sta $5610
    lda #$C0
    sta $3570
    sta $35C0
    sta $46EB
    sta $478B
    sta $51A1
    sta $51F1
    sta $556F
    sta $5612
    rts
