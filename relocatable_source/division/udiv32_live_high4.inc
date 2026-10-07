; Repose OptiSearchV2 live-high quotient-state division, threshold 1, guarded narrow divisors.
; Adapted for the C64 Math Library public ABI: N,D preserved; Q,R output;
; Decimal mode must be clear; C=1 and zero Q/R on divisor zero, C=0 otherwise.
; Derived from Repose OptiSearchV2 live_high_division.py and zp_aligned_division.py.
; See docs/UDIV32_OPTISEARCH.md for provenance and measured tradeoffs.
; Four bytes hold the shifted divisor only during the aligned tail.
; No SMC, tables, init requirement or persistent stack-page storage.
UD32_SHIFT = ZP_MAIN+$51
* = MATH_UDIV32_32
    jmp UD32_L0600
; Retain the private entry used by the existing remainder-only fallback.
* = REG_GAME
    jmp UD32_L0600
* = REG_GAME+$FE
; Quotient 0/1 prefix and zero guard.
UD32_L0600:
    lda MATH_N+$03
UD32_L0603:
    cmp MATH_D+$03
UD32_L0606:
    bcc UD32_L0628
UD32_L0608:
    bne UD32_L064F
UD32_L060A:
    lda MATH_N+$02
UD32_L060D:
    cmp MATH_D+$02
UD32_L0610:
    bcc UD32_L0628
UD32_L0612:
    bne UD32_L064F
UD32_L0614:
    lda MATH_N+$01
UD32_L0617:
    cmp MATH_D+$01
UD32_L061A:
    bcc UD32_L0628
UD32_L061C:
    bne UD32_L064F
UD32_L061E:
    lda MATH_N+$00
UD32_L0621:
    cmp MATH_D+$00
UD32_L0624:
    bcc UD32_L0628
UD32_L0626:
    bne UD32_L064F
    jmp UD32_EQUAL
UD32_L0628:
    lda #$00
UD32_L062A:
    sta MATH_Q+$00
UD32_L062D:
    sta MATH_Q+$01
UD32_L0630:
    sta MATH_Q+$02
UD32_L0633:
    sta MATH_Q+$03
UD32_L0636:
    lda MATH_N+$00
UD32_L0639:
    sta MATH_R+$00
UD32_L063C:
    lda MATH_N+$01
UD32_L063F:
    sta MATH_R+$01
UD32_L0642:
    lda MATH_N+$02
UD32_L0645:
    sta MATH_R+$02
UD32_L0648:
    lda MATH_N+$03
UD32_L064B:
    sta MATH_R+$03
UD32_L064E:
    clc
    rts
; Keep the proven narrow-divisor restoring loops.
UD32_L064F:
    lda MATH_D+3
    ora MATH_D+2
    bne UD32_L0662
    lda MATH_D+0
    sta UD32_SHIFT
    lda MATH_D+1
    sta UD32_SHIFT+1
    beq UD32_CHECK_D8
    jmp UD32_OLD_C28A
UD32_CHECK_D8:
    lda UD32_SHIFT
    bne UD32_GO_D8
    jmp UD32_L072A
UD32_GO_D8:
    jmp UD32_OLD_C23D
UD32_L0662:
    sec
UD32_L0663:
    lda MATH_N+$00
UD32_L0666:
    sbc MATH_D+$00
UD32_L0669:
    sta MATH_R+$00
UD32_L066C:
    lda MATH_N+$01
UD32_L066F:
    sbc MATH_D+$01
UD32_L0672:
    sta MATH_R+$01
UD32_L0675:
    lda MATH_N+$02
UD32_L0678:
    sbc MATH_D+$02
UD32_L067B:
    sta MATH_R+$02
UD32_L067E:
    lda MATH_N+$03
UD32_L0681:
    sbc MATH_D+$03
UD32_L0684:
    cmp MATH_D+$03
UD32_L0687:
    bcc UD32_L06EE
UD32_L0689:
    beq UD32_L06AE
UD32_L068B:
    tay
UD32_L068C:
    lda MATH_R+$00
UD32_L068F:
    sbc MATH_D+$00
UD32_L0692:
    sta MATH_R+$00
UD32_L0695:
    lda MATH_R+$01
UD32_L0698:
    sbc MATH_D+$01
UD32_L069B:
    sta MATH_R+$01
UD32_L069E:
    lda MATH_R+$02
UD32_L06A1:
    sbc MATH_D+$02
UD32_L06A4:
    sta MATH_R+$02
UD32_L06A7:
    tya
UD32_L06A8:
    sbc MATH_D+$03
UD32_L06AB:
    jmp UD32_L0702
UD32_L06AE:
    tax
UD32_L06AF:
    lda MATH_R+$02
UD32_L06B2:
    cmp MATH_D+$02
UD32_L06B5:
    bcc UD32_L06ED
UD32_L06B7:
    bne UD32_L06CD
UD32_L06B9:
    lda MATH_R+$01
UD32_L06BC:
    cmp MATH_D+$01
UD32_L06BF:
    bcc UD32_L06ED
UD32_L06C1:
    bne UD32_L06CD
UD32_L06C3:
    lda MATH_R+$00
UD32_L06C6:
    cmp MATH_D+$00
UD32_L06C9:
    bcc UD32_L06ED
UD32_L06CB:
    bne UD32_L06CD
UD32_L06CD:
    lda MATH_R+$00
UD32_L06D0:
    sbc MATH_D+$00
UD32_L06D3:
    sta MATH_R+$00
UD32_L06D6:
    lda MATH_R+$01
UD32_L06D9:
    sbc MATH_D+$01
UD32_L06DC:
    sta MATH_R+$01
UD32_L06DF:
    lda MATH_R+$02
UD32_L06E2:
    sbc MATH_D+$02
UD32_L06E5:
    sta MATH_R+$02
UD32_L06E8:
    lda #$00
UD32_L06EA:
    jmp UD32_L0702
UD32_L06ED:
    txa
UD32_L06EE:
    sta MATH_R+$03
UD32_L06F1:
    lda #$01
UD32_L06F3:
    sta MATH_Q+$00
UD32_L06F6:
    lda #$00
UD32_L06F8:
    sta MATH_Q+$01
UD32_L06FB:
    sta MATH_Q+$02
UD32_L06FE:
    sta MATH_Q+$03
UD32_L0701:
    clc
    rts
UD32_L0702:
    sta MATH_R+$03
UD32_L0705:
    jsr UD32_L2000
UD32_L0708:
    clc
UD32_L0709:
    lda MATH_Q+$00
UD32_L070C:
    adc #$02
UD32_L070E:
    sta MATH_Q+$00
UD32_L0711:
    lda MATH_Q+$01
UD32_L0714:
    adc #$00
UD32_L0716:
    sta MATH_Q+$01
UD32_L0719:
    lda MATH_Q+$02
UD32_L071C:
    adc #$00
UD32_L071E:
    sta MATH_Q+$02
UD32_L0721:
    lda MATH_Q+$03
UD32_L0724:
    adc #$00
UD32_L0726:
    sta MATH_Q+$03
UD32_L0729:
    clc
    rts
UD32_L072A:
    lda #$00
UD32_L072C:
    sta MATH_Q+$00
UD32_L072F:
    sta MATH_Q+$01
UD32_L0732:
    sta MATH_Q+$02
UD32_L0735:
    sta MATH_Q+$03
UD32_L0738:
    sta MATH_R+$00
UD32_L073B:
    sta MATH_R+$01
UD32_L073E:
    sta MATH_R+$02
UD32_L0741:
    sta MATH_R+$03
UD32_L0744:
    sec
    rts
; General aligned long-division tail; divisor already known nonzero.
UD32_L2000:
    lda MATH_D+$00
UD32_L2003:
    sta UD32_SHIFT+$00
UD32_L2005:
    lda MATH_D+$01
UD32_L2008:
    sta UD32_SHIFT+$01
UD32_L200A:
    lda MATH_D+$02
UD32_L200D:
    sta UD32_SHIFT+$02
UD32_L200F:
    lda MATH_D+$03
UD32_L2012:
    sta UD32_SHIFT+$03
UD32_L2014:
    lda #$00
UD32_L2016:
    sta MATH_Q+$00
UD32_L2019:
    sta MATH_Q+$01
UD32_L201C:
    sta MATH_Q+$02
UD32_L201F:
    sta MATH_Q+$03
UD32_L2022:
    ldx #$01
UD32_L2024:
    bit UD32_SHIFT+$03
UD32_L2026:
    bmi UD32_L205E
UD32_L2028:
    asl UD32_SHIFT+$00
UD32_L202A:
    rol UD32_SHIFT+$01
UD32_L202C:
    rol UD32_SHIFT+$02
UD32_L202E:
    rol UD32_SHIFT+$03
UD32_L2030:
    lda MATH_R+$03
UD32_L2033:
    cmp UD32_SHIFT+$03
UD32_L2035:
    bcc UD32_L2056
UD32_L2037:
    bne UD32_L2052
UD32_L2039:
    lda MATH_R+$02
UD32_L203C:
    cmp UD32_SHIFT+$02
UD32_L203E:
    bcc UD32_L2056
UD32_L2040:
    bne UD32_L2052
UD32_L2042:
    lda MATH_R+$01
UD32_L2045:
    cmp UD32_SHIFT+$01
UD32_L2047:
    bcc UD32_L2056
UD32_L2049:
    bne UD32_L2052
UD32_L204B:
    lda MATH_R+$00
UD32_L204E:
    cmp UD32_SHIFT+$00
UD32_L2050:
    bcc UD32_L2056
UD32_L2052:
    inx
UD32_L2053:
    jmp UD32_L2024
UD32_L2056:
    lsr UD32_SHIFT+$03
UD32_L2058:
    ror UD32_SHIFT+$02
UD32_L205A:
    ror UD32_SHIFT+$01
UD32_L205C:
    ror UD32_SHIFT+$00
UD32_L205E:
    ldy MATH_R+$03
UD32_L2061:
    cpy UD32_SHIFT+$03
UD32_L2063:
    bcc UD32_L20BC
UD32_L2065:
    bne UD32_L209D
UD32_L2067:
    lda MATH_R+$02
UD32_L206A:
    cmp UD32_SHIFT+$02
UD32_L206C:
    bcc UD32_L20BC
UD32_L206E:
    bne UD32_L2080
UD32_L2070:
    lda MATH_R+$01
UD32_L2073:
    cmp UD32_SHIFT+$01
UD32_L2075:
    bcc UD32_L20BC
UD32_L2077:
    bne UD32_L2080
UD32_L2079:
    lda MATH_R+$00
UD32_L207C:
    cmp UD32_SHIFT+$00
UD32_L207E:
    bcc UD32_L20BC
UD32_L2080:
    lda MATH_R+$00
UD32_L2083:
    sbc UD32_SHIFT+$00
UD32_L2085:
    sta MATH_R+$00
UD32_L2088:
    lda MATH_R+$01
UD32_L208B:
    sbc UD32_SHIFT+$01
UD32_L208D:
    sta MATH_R+$01
UD32_L2090:
    lda MATH_R+$02
UD32_L2093:
    sbc UD32_SHIFT+$02
UD32_L2095:
    sta MATH_R+$02
UD32_L2098:
    ldy #$00
UD32_L209A:
    jmp UD32_L20BD
UD32_L209D:
    lda MATH_R+$00
UD32_L20A0:
    sbc UD32_SHIFT+$00
UD32_L20A2:
    sta MATH_R+$00
UD32_L20A5:
    lda MATH_R+$01
UD32_L20A8:
    sbc UD32_SHIFT+$01
UD32_L20AA:
    sta MATH_R+$01
UD32_L20AD:
    lda MATH_R+$02
UD32_L20B0:
    sbc UD32_SHIFT+$02
UD32_L20B2:
    sta MATH_R+$02
UD32_L20B5:
    tya
UD32_L20B6:
    sbc UD32_SHIFT+$03
UD32_L20B8:
    tay
UD32_L20B9:
    jmp UD32_L20BD
UD32_L20BC:
    clc
UD32_L20BD:
    rol MATH_Q+$00
UD32_L20C0:
    rol MATH_Q+$01
UD32_L20C3:
    rol MATH_Q+$02
UD32_L20C6:
    rol MATH_Q+$03
UD32_L20C9:
    dex
UD32_L20CA:
    beq UD32_L20D7
UD32_L20CC:
    lsr UD32_SHIFT+$03
UD32_L20CE:
    ror UD32_SHIFT+$02
UD32_L20D0:
    ror UD32_SHIFT+$01
UD32_L20D2:
    ror UD32_SHIFT+$00
UD32_L20D4:
    jmp UD32_L2061
UD32_L20D7:
    sty MATH_R+$03
UD32_L20DA:
    rts
UD32_OLD_C28A:
    lda MATH_N+$00
UD32_OLD_C28C:
    sta MATH_Q+$00
UD32_OLD_C28F:
    lda MATH_N+$01
UD32_OLD_C291:
    sta MATH_Q+$01
UD32_OLD_C294:
    lda MATH_N+$02
UD32_OLD_C296:
    sta MATH_Q+$02
UD32_OLD_C299:
    lda #$00
UD32_OLD_C29B:
    sta MATH_Q+$03
UD32_OLD_C29E:
    lda MATH_N+$03
UD32_OLD_C2A0:
    sta MATH_Q+$04
UD32_OLD_C2A3:
    lda #$00
UD32_OLD_C2A5:
    sta MATH_Q+$05
UD32_OLD_C2A8:
    sta MATH_Q+$06
UD32_OLD_C2AB:
    sta MATH_Q+$07
UD32_OLD_C2AE:
    ldx #$18
UD32_OLD_C2B0:
    asl MATH_Q+$00
UD32_OLD_C2B3:
    rol MATH_Q+$01
UD32_OLD_C2B6:
    rol MATH_Q+$02
UD32_OLD_C2B9:
    rol MATH_Q+$04
UD32_OLD_C2BC:
    rol MATH_Q+$05
UD32_OLD_C2BF:
    bcs UD32_OLD_C2D1
UD32_OLD_C2C1:
    lda MATH_Q+$05
UD32_OLD_C2C4:
    cmp UD32_SHIFT+$01
UD32_OLD_C2C6:
    bcc UD32_OLD_C2E5
UD32_OLD_C2C8:
    bne UD32_OLD_C2D1
UD32_OLD_C2CA:
    lda MATH_Q+$04
UD32_OLD_C2CD:
    cmp UD32_SHIFT+$00
UD32_OLD_C2CF:
    bcc UD32_OLD_C2E5
UD32_OLD_C2D1:
    sec
UD32_OLD_C2D2:
    lda MATH_Q+$04
UD32_OLD_C2D5:
    sbc UD32_SHIFT+$00
UD32_OLD_C2D7:
    sta MATH_Q+$04
UD32_OLD_C2DA:
    lda MATH_Q+$05
UD32_OLD_C2DD:
    sbc UD32_SHIFT+$01
UD32_OLD_C2DF:
    sta MATH_Q+$05
UD32_OLD_C2E2:
    inc MATH_Q+$00
UD32_OLD_C2E5:
    dex
UD32_OLD_C2E6:
    bne UD32_OLD_C2B0
UD32_OLD_C2E8:
    clc
UD32_OLD_C2E9:
    rts
UD32_MAIN_END:
* = REG_KERNEL+$1957
UD32_OLD_C23D:
    lda MATH_N+$00
UD32_OLD_C23F:
    sta MATH_Q+$00
UD32_OLD_C242:
    lda MATH_N+$01
UD32_OLD_C244:
    sta MATH_Q+$01
UD32_OLD_C247:
    lda MATH_N+$02
UD32_OLD_C249:
    sta MATH_Q+$02
UD32_OLD_C24C:
    lda MATH_N+$03
UD32_OLD_C24E:
    sta MATH_Q+$03
UD32_OLD_C251:
    lda #$00
UD32_OLD_C253:
    sta MATH_Q+$04
UD32_OLD_C256:
    sta MATH_Q+$05
UD32_OLD_C259:
    sta MATH_Q+$06
UD32_OLD_C25C:
    sta MATH_Q+$07
UD32_OLD_C25F:
    ldx #$20
UD32_OLD_C261:
    asl MATH_Q+$00
UD32_OLD_C264:
    rol MATH_Q+$01
UD32_OLD_C267:
    rol MATH_Q+$02
UD32_OLD_C26A:
    rol MATH_Q+$03
UD32_OLD_C26D:
    rol MATH_Q+$04
UD32_OLD_C270:
    bcs UD32_OLD_C279
UD32_OLD_C272:
    lda MATH_Q+$04
UD32_OLD_C275:
    cmp UD32_SHIFT+$00
UD32_OLD_C277:
    bcc UD32_OLD_C285
UD32_OLD_C279:
    sec
UD32_OLD_C27A:
    lda MATH_Q+$04
UD32_OLD_C27D:
    sbc UD32_SHIFT+$00
UD32_OLD_C27F:
    sta MATH_Q+$04
UD32_OLD_C282:
    inc MATH_Q+$00
UD32_OLD_C285:
    dex
UD32_OLD_C286:
    bne UD32_OLD_C261
UD32_OLD_C288:
    clc
UD32_OLD_C289:
    rts
; Leading equal compare leaves A=N0=D0; OR the remaining divisor bytes.
UD32_EQUAL:
    ora MATH_D+1
    ora MATH_D+2
    ora MATH_D+3
    beq UD32_EQUAL_ZERO
    ldx #0
    lda #1
    sta MATH_Q
    stx MATH_Q+1
    stx MATH_Q+2
    stx MATH_Q+3
    stx MATH_R
    stx MATH_R+1
    stx MATH_R+2
    stx MATH_R+3
    clc
    rts
UD32_EQUAL_ZERO:
    jmp UD32_L072A
UD32_END:
; Must remain below the SMUL8 public adapter at REG_GAME+$03B5.
