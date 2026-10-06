; Turbo32 resident fast public binder/summation for V3/V4.
; The active REU overlay owns TURBO32_ZP_BASE..+135 (136 bytes).
; This resident side binds X directly from MATH_IO, lets the overlay fetch Y
; directly from MATH_Y, writes result bytes 1..3 at the point they become final,
; and leaves only z0/z4..z7 for the public wrapper to marshal.
!cpu 6510

T32_MATH_X = MATH_IO
T32_MATH_Y = MATH_IO+$04
T32_MATH_Z = MATH_IO+$08

; 136-byte overlay layout. The direct-MATH_Y LDY abs,X adds one byte relative
; to the former 135-byte overlay, shifting the table-operand SMC fields by one.
T32_z00 = TURBO32_ZP_BASE+$00
T32_z10 = TURBO32_ZP_BASE+$01
T32_z20 = TURBO32_ZP_BASE+$02
T32_z30 = TURBO32_ZP_BASE+$03
T32_z01 = TURBO32_ZP_BASE+$04
T32_z11 = TURBO32_ZP_BASE+$05
T32_z21 = TURBO32_ZP_BASE+$06
T32_z31 = TURBO32_ZP_BASE+$07
T32_z02 = TURBO32_ZP_BASE+$08
T32_z12 = TURBO32_ZP_BASE+$09
T32_z22 = TURBO32_ZP_BASE+$0A
T32_z32 = TURBO32_ZP_BASE+$0B
T32_z03 = TURBO32_ZP_BASE+$0C
T32_z13 = TURBO32_ZP_BASE+$0D
T32_z23 = TURBO32_ZP_BASE+$0E
T32_z33 = TURBO32_ZP_BASE+$0F
T32_z14 = TURBO32_ZP_BASE+$10
T32_z24 = TURBO32_ZP_BASE+$11
T32_r0  = TURBO32_ZP_BASE+$00
T32_r7  = TURBO32_ZP_BASE+$12

T32_core = TURBO32_ZP_BASE+$44
T32_x0  = TURBO32_ZP_BASE+$45
T32_NL0 = TURBO32_ZP_BASE+$48
T32_SH0 = TURBO32_ZP_BASE+$4D
T32_NH0 = TURBO32_ZP_BASE+$50
T32_x1  = TURBO32_ZP_BASE+$53
T32_NL1 = TURBO32_ZP_BASE+$58
T32_SH1 = TURBO32_ZP_BASE+$5D
T32_NH1 = TURBO32_ZP_BASE+$60
T32_x2  = TURBO32_ZP_BASE+$63
T32_NL2 = TURBO32_ZP_BASE+$68
T32_SH2 = TURBO32_ZP_BASE+$6D
T32_NH2 = TURBO32_ZP_BASE+$70
T32_x3  = TURBO32_ZP_BASE+$73
T32_NL3 = TURBO32_ZP_BASE+$78
T32_SH3 = TURBO32_ZP_BASE+$7D
T32_NH3 = TURBO32_ZP_BASE+$80

; BEGIN swaps the exact 136-byte active overlay.
* = MATH_REU_UMUL32_BEGIN
        lda #<TURBO32_ZP_BASE
        sta $DF02
        lda #>TURBO32_ZP_BASE
        sta $DF03
        lda #$00
        sta $DF04
        sta $DF05
        lda #REU_TURBO32_BANK
        sta $DF06
        lda #136
        sta $DF07
        lda #0
        sta $DF08
        sta $DF0A
        lda #$82
        sta $DF01
        clc
        rts

; Public CALL. The native core now writes Z1..Z3 directly during summation.
* = MATH_REU_UMUL32
        jsr t32_bind_public
        sta T32_MATH_Z+$06
        stx T32_MATH_Z+$05
        sty T32_MATH_Z+$04
        lda T32_r0
        sta T32_MATH_Z+$00
        lda T32_r7
        sta T32_MATH_Z+$07
        clc
        rts

; Direct column summation. Z1/Z2/Z3 cease being live partials exactly where
; these stores occur, so write their stable-ABI destinations immediately.
* = REG_LOW+$0100
t32_summation:
        tay
        clc
        lda T32_z01
        adc T32_z10
        sta T32_MATH_Z+$01
        lda T32_z20
        adc T32_z11
        bcc t32_s1110
        inx
        clc
t32_s1110:
        adc T32_z02
        sta T32_MATH_Z+$02
        lda T32_z03
        adc T32_z12
        bcc t32_s1128
        iny
        cpx #$01
        adc T32_z30
        bcc t32_s112f
        clc
        iny
        bne t32_s112f
        jmp t32_helper_c3_over
t32_s1128:
        adc T32_z30
        bcc t32_s112d
        iny
t32_s112d:
        cpx #$01
t32_s112f:
        adc T32_z21
        sta T32_MATH_Z+$03
        tya
        ldx T32_z14
        adc T32_z13
        bcs t32_s1168
        adc T32_z31
        bcc t32_s1142
        inx
        beq t32_s1171
t32_s1141:
        clc
t32_s1142:
        adc T32_z22
        tay
        txa
        adc T32_z32
        bcs t32_s1159
        adc T32_z23
        tax
        lda T32_z24
        adc T32_z33
        bcs t32_s1156
        rts
t32_s1154:
        adc #0
t32_s1156:
        inc T32_r7
        rts
t32_s1159:
        clc
        adc T32_z23
        tax
        lda T32_z24
        adc T32_z33
        bcs t32_s1154
        adc #1
        bcs t32_s1156
        rts
t32_s1168:
        inx
        clc
        adc T32_z31
        bcc t32_s1142
        inx
        bne t32_s1141
t32_s1171:
        jmp t32_helper_c4_over

; Bind the four X bytes directly from the stable public input block. This
; replaces the old stage-to-SMC + reload sequence. Y3 is loaded here; Y2..Y0
; are fetched directly by the active overlay loop.
* = REG_LOW+$0180
t32_bind_public:
        lda T32_MATH_X+$00
        sta T32_x0
        sta T32_SH0
        eor #$FF
        sta T32_NL0
        sta T32_NH0

        lda T32_MATH_X+$01
        sta T32_x1
        sta T32_SH1
        eor #$FF
        sta T32_NL1
        sta T32_NH1

        lda T32_MATH_X+$02
        sta T32_x2
        sta T32_SH2
        eor #$FF
        sta T32_NL2
        sta T32_NH2

        lda T32_MATH_X+$03
        sta T32_x3
        sta T32_SH3
        eor #$FF
        sta T32_NL3
        sta T32_NH3

        ldy T32_MATH_Y+$03
        ldx #4
        sec
        jmp T32_core

t32_helper_c3_over:
        inc T32_z32
        bne t32_helper_c3_done
        inc T32_z33
        bne t32_helper_c3_done
        inc T32_r7
t32_helper_c3_done:
        clc
        jmp t32_s112f

t32_helper_c4_over:
        inc T32_z33
        bne t32_helper_c4_done
        inc T32_r7
t32_helper_c4_done:
        jmp t32_s1141
