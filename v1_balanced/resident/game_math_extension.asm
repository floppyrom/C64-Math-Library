; C64 GAME MATH EXTENSION — generated release source
; Extension body uses documented NMOS 6502 opcodes. Selected inherited fast DIV kernels may use stable NMOS undocumented opcodes.
; Target: NMOS 6510/6502 semantics. D=0 required. A/X/Y volatile.
; Inputs in the stable $C000 vectors are preserved unless explicitly documented.

MATH_UDIV32_32 = $5E00
MATH_UMOD32_32 = $5E03
MATH_SDIV32_32 = $5E06
MATH_SMOD32_32 = $5E09
MATH_UMUL16_SHR8 = $5E0C
MATH_SMUL16_SHR8 = $5E0F
MATH_UMUL32_SHR16 = $5E12
MATH_SMUL32_SHR16 = $5E15
MATH_UDIV16_SHL8 = $5E18
MATH_SDIV16_SHL8 = $5E1B
MATH_URECIP16_Q16 = $5E1E
MATH_SIN8 = $5E21
MATH_COS8 = $5E24
MATH_SINCOS8 = $5E27
MATH_ATAN2_8 = $5E2A
MATH_ISQRT16 = $5E2D
MATH_ISQRT32 = $5E30
MATH_DIST8_FAST = $5E33
MATH_DIST8_ACCURATE = $5E36
X0 = $C000
X1 = $C001
X2 = $C002
X3 = $C003
Y0 = $C004
Y1 = $C005
Y2 = $C006
Y3 = $C007
Z0 = $C008
Z1 = $C009
Z2 = $C00A
Z3 = $C00B
Z4 = $C00C
Z5 = $C00D
Z6 = $C00E
Z7 = $C00F
N0 = $C010
N1 = $C011
N2 = $C012
N3 = $C013
D0 = $C014
D1 = $C015
D2 = $C016
D3 = $C017
Q0 = $C018
Q1 = $C019
Q2 = $C01A
Q3 = $C01B
R0 = $C01C
R1 = $C01D
R2 = $C01E
R3 = $C01F
S0 = $C040
S1 = $C041
S2 = $C042
S3 = $C043
S4 = $C044
S5 = $C045
S6 = $C046
S7 = $C047
S8 = $C048
S9 = $C049
S10 = $C04A
S11 = $C04B
S12 = $C04C
S13 = $C04D
S14 = $C04E
S15 = $C04F
S16 = $C050
S17 = $C051
S18 = $C052
S19 = $C053
S20 = $C054
S21 = $C055
S22 = $C056
S23 = $C057
SINTAB = $9400
COSTAB = $9500
LOGTAB = $9600
ATANTAB = $9700
SQLOTAB = $9800
SQHITAB = $9900
DISTATAB = $9A00
DISTBTAB = $9B00
OLD_UMUL16 = $3020
OLD_UMUL32 = $30B0
OLD_SMUL16 = $3BB0
OLD_SMUL32 = $3C40
OLD_UDIV24 = $3170
OLD_SDIV24 = $3DE0
OLD_UDIV32_16 = $31B0
OLD_SDIV32_16 = $3EE0

; Stable extension ABI: 3-byte JMP slots. Modulo aliases return both q and r.
.org $5E00
math_udiv32_32: jmp udiv32_public
math_umod32_32: jmp udiv32_public
math_sdiv32_32: jmp sdiv32_public
math_smod32_32: jmp sdiv32_public
math_umul16_shr8: jmp umul16_shr8
math_smul16_shr8: jmp smul16_shr8
math_umul32_shr16: jmp umul32_shr16
math_smul32_shr16: jmp smul32_shr16
math_udiv16_shl8: jmp udiv16_shl8
math_sdiv16_shl8: jmp sdiv16_shl8
math_urecip16_q16: jmp urecip16_q16
math_sin8: jmp sin8
math_cos8: jmp cos8
math_sincos8: jmp sincos8
math_atan2_8: jmp atan2_8
math_isqrt16: jmp isqrt16
math_isqrt32: jmp isqrt32_fast
math_dist8_fast: jmp dist8_fast
math_dist8_accurate: jmp dist8_accurate

.org $C100


; ---------------------------------------------------------------------------
; 32/32 unsigned and signed division.
; Private magnitude core uses a 32/16 32-step knee when d<65536 and a
; 16-step high-divisor path when d>=65536 (then q is provably <=16 bits).
; S0..S3 = |n|, S4..S7 = |d|, S8 quotient-sign, S9 remainder-sign.
; ---------------------------------------------------------------------------
udiv32_public:
    lda N0
    sta S0
    lda N1
    sta S1
    lda N2
    sta S2
    lda N3
    sta S3
    lda D0
    sta S4
    lda D1
    sta S5
    lda D2
    sta S6
    lda D3
    sta S7
    jsr div32_mag_core
    rts

sdiv32_public:
    lda D0
    ora D1
    ora D2
    ora D3
    bne sd32_nonzero
    jsr zero_qr_error
    rts
sd32_nonzero:
    lda N3
    eor D3
    and #$80
    sta S8
    lda N3
    and #$80
    sta S9
    ; magnitude numerator
    lda N0
    sta S0
    lda N1
    sta S1
    lda N2
    sta S2
    lda N3
    sta S3
    bpl sd32_nmag_done
    sec
    lda #0
    sbc S0
    sta S0
    lda #0
    sbc S1
    sta S1
    lda #0
    sbc S2
    sta S2
    lda #0
    sbc S3
    sta S3
sd32_nmag_done:
    lda D0
    sta S4
    lda D1
    sta S5
    lda D2
    sta S6
    lda D3
    sta S7
    bpl sd32_dmag_done
    sec
    lda #0
    sbc S4
    sta S4
    lda #0
    sbc S5
    sta S5
    lda #0
    sbc S6
    sta S6
    lda #0
    sbc S7
    sta S7
sd32_dmag_done:
    jsr div32_mag_core
    bcs sd32_return
    lda S8
    beq sd32_q_done
    sec
    lda #0
    sbc Q0
    sta Q0
    lda #0
    sbc Q1
    sta Q1
    lda #0
    sbc Q2
    sta Q2
    lda #0
    sbc Q3
    sta Q3
sd32_q_done:
    lda S9
    beq sd32_success
    sec
    lda #0
    sbc R0
    sta R0
    lda #0
    sbc R1
    sta R1
    lda #0
    sbc R2
    sta R2
    lda #0
    sbc R3
    sta R3
sd32_success:
    clc
sd32_return:
    rts

zero_qr_error:
    lda #0
    sta Q0
    sta Q1
    sta Q2
    sta Q3
    sta R0
    sta R1
    sta R2
    sta R3
    sec
    rts

div32_mag_core:
    lda S4
    ora S5
    ora S6
    ora S7
    bne d32_nonzero
    jsr zero_qr_error
    rts
d32_nonzero:
    ; Four quotient-width knees selected from the divisor's leading byte.
    ; d<2^8:  32 quotient bits, 8-bit remainder.
    ; d<2^16: 24 quotient bits, preloaded top numerator byte.
    ; d<2^24: 16 quotient bits, preloaded top numerator word.
    ; else:     8 quotient bits, preloaded top three numerator bytes.
    lda S7
    beq d32_check_s6
    jmp d32_wide8
d32_check_s6:
    lda S6
    beq d32_check_s5
    jmp d32_wide16
d32_check_s5:
    lda S5
    beq d32_narrow8
    jmp d32_mid24
d32_narrow8:

    ; 32 / 8 magnitude path.
    lda S0
    sta Q0
    lda S1
    sta Q1
    lda S2
    sta Q2
    lda S3
    sta Q3
    lda #0
    sta R0
    sta R1
    sta R2
    sta R3
    ldx #32
d32_8_loop:
    asl Q0
    rol Q1
    rol Q2
    rol Q3
    rol R0
    bcs d32_8_sub
    lda R0
    cmp S4
    bcc d32_8_nosub
d32_8_sub:
    sec
    lda R0
    sbc S4
    sta R0
    inc Q0
d32_8_nosub:
    dex
    bne d32_8_loop
    clc
    rts

d32_mid24:
    ; d>=256 => q<2^24. Top numerator byte is a valid initial remainder.
    lda S0
    sta Q0
    lda S1
    sta Q1
    lda S2
    sta Q2
    lda #0
    sta Q3
    lda S3
    sta R0
    lda #0
    sta R1
    sta R2
    sta R3
    ldx #24
d32_24_loop:
    asl Q0
    rol Q1
    rol Q2
    rol R0
    rol R1
    bcs d32_24_sub
    lda R1
    cmp S5
    bcc d32_24_nosub
    bne d32_24_sub
    lda R0
    cmp S4
    bcc d32_24_nosub
d32_24_sub:
    sec
    lda R0
    sbc S4
    sta R0
    lda R1
    sbc S5
    sta R1
    inc Q0
d32_24_nosub:
    dex
    bne d32_24_loop
    clc
    rts

d32_wide8:
    ; d>=2^24 => q<256. Early compare handles the common n<=d cases.
    lda S3
    cmp S7
    bcc d32_wide8_less
    bne d32_wide8_greater
    lda S2
    cmp S6
    bcc d32_wide8_less
    bne d32_wide8_greater
    lda S1
    cmp S5
    bcc d32_wide8_less
    bne d32_wide8_greater
    lda S0
    cmp S4
    bcc d32_wide8_less
    bne d32_wide8_greater
    lda #1
    sta Q0
    lda #0
    sta Q1
    sta Q2
    sta Q3
    sta R0
    sta R1
    sta R2
    sta R3
    clc
    rts
d32_wide8_less:
    lda #0
    sta Q0
    sta Q1
    sta Q2
    sta Q3
    lda S0
    sta R0
    lda S1
    sta R1
    lda S2
    sta R2
    lda S3
    sta R3
    clc
    rts
d32_wide8_greater:
    lda S0
    sta Q0
    lda #0
    sta Q1
    sta Q2
    sta Q3
    lda S1
    sta R0
    lda S2
    sta R1
    lda S3
    sta R2
    lda #0
    sta R3
    ldx #8
d32_wide8_loop:
    asl Q0
    rol R0
    rol R1
    rol R2
    rol R3
    bcs d32_wide8_sub
    lda R3
    cmp S7
    bcc d32_wide8_nosub
    bne d32_wide8_sub
    lda R2
    cmp S6
    bcc d32_wide8_nosub
    bne d32_wide8_sub
    lda R1
    cmp S5
    bcc d32_wide8_nosub
    bne d32_wide8_sub
    lda R0
    cmp S4
    bcc d32_wide8_nosub
d32_wide8_sub:
    sec
    lda R0
    sbc S4
    sta R0
    lda R1
    sbc S5
    sta R1
    lda R2
    sbc S6
    sta R2
    lda R3
    sbc S7
    sta R3
    inc Q0
d32_wide8_nosub:
    dex
    bne d32_wide8_loop
    clc
    rts

d32_wide16:
    ; Early n<d / n=d knees.
    lda S3
    cmp S7
    bcc d32_less
    bne d32_greater
    lda S2
    cmp S6
    bcc d32_less
    bne d32_greater
    lda S1
    cmp S5
    bcc d32_less
    bne d32_greater
    lda S0
    cmp S4
    bcc d32_less
    bne d32_greater
    lda #1
    sta Q0
    lda #0
    sta Q1
    sta Q2
    sta Q3
    sta R0
    sta R1
    sta R2
    sta R3
    clc
    rts
d32_less:
    lda #0
    sta Q0
    sta Q1
    sta Q2
    sta Q3
    lda S0
    sta R0
    lda S1
    sta R1
    lda S2
    sta R2
    lda S3
    sta R3
    clc
    rts
d32_greater:
    ; This label is reached only from the 16-bit-quotient wide path.
    ; Since d>=2^16 and n<2^32, q<2^16.
    lda S0
    sta Q0
    lda S1
    sta Q1
    lda #0
    sta Q2
    sta Q3
    lda S2
    sta R0
    lda S3
    sta R1
    lda #0
    sta R2
    sta R3
    ldx #16
d32_wide_loop:
    asl Q0
    rol Q1
    rol R0
    rol R1
    rol R2
    rol R3
    bcs d32_wide_sub
    lda R3
    cmp S7
    bcc d32_wide_nosub
    bne d32_wide_sub
    lda R2
    cmp S6
    bcc d32_wide_nosub
    bne d32_wide_sub
    lda R1
    cmp S5
    bcc d32_wide_nosub
    bne d32_wide_sub
    lda R0
    cmp S4
    bcc d32_wide_nosub
d32_wide_sub:
    sec
    lda R0
    sbc S4
    sta R0
    lda R1
    sbc S5
    sta R1
    lda R2
    sbc S6
    sta R2
    lda R3
    sbc S7
    sta R3
    inc Q0
d32_wide_nosub:
    dex
    bne d32_wide_loop
    clc
    rts

; ---------------------------------------------------------------------------
; Byte-aligned fixed-point multiply shifts. These deliberately reuse the
; profile's selected state-of-the-art integer producer; the post-product shift
; is just byte selection, not a general shift loop.
; ---------------------------------------------------------------------------
umul16_shr8:
    jsr OLD_UMUL16
    lda Z1
    sta Z0
    lda Z2
    sta Z1
    lda Z3
    sta Z2
    clc
    rts
smul16_shr8:
    jsr OLD_SMUL16
    lda Z1
    sta Z0
    lda Z2
    sta Z1
    lda Z3
    sta Z2
    clc
    rts
umul32_shr16:
    jsr OLD_UMUL32
    lda Z2
    sta Z0
    lda Z3
    sta Z1
    lda Z4
    sta Z2
    lda Z5
    sta Z3
    lda Z6
    sta Z4
    lda Z7
    sta Z5
    clc
    rts
smul32_shr16:
    jsr OLD_SMUL32
    lda Z2
    sta Z0
    lda Z3
    sta Z1
    lda Z4
    sta Z2
    lda Z5
    sta Z3
    lda Z6
    sta Z4
    lda Z7
    sta Z5
    clc
    rts

; ---------------------------------------------------------------------------
; Exact (n16 << 8) / d16 fixed-point division.
; Launch the profile's already-selected 32/16 divider rather than maintaining a
; slower second division engine.  Only the numerator geometry changes; the
; public input vectors are restored after the call without disturbing carry.
; ---------------------------------------------------------------------------
udiv16_shl8:
    lda N0
    sta S0
    lda N1
    sta S1
    lda N2
    sta S2
    lda N3
    sta S3
    lda #0
    sta N0
    lda S0
    sta N1
    lda S1
    sta N2
    lda #0
    sta N3
    jsr OLD_UDIV32_16
    lda S0
    sta N0
    lda S1
    sta N1
    lda S2
    sta N2
    lda S3
    sta N3
    rts

sdiv16_shl8:
    lda N0
    sta S0
    lda N1
    sta S1
    lda N2
    sta S2
    lda N3
    sta S3
    lda #0
    sta N0
    lda S0
    sta N1
    lda S1
    sta N2
    bpl sfx_positive_n
    lda #$ff
    bne sfx_store_sign
sfx_positive_n:
    lda #0
sfx_store_sign:
    sta N3
    jsr OLD_SDIV32_16
    lda S0
    sta N0
    lda S1
    sta N1
    lda S2
    sta N2
    lda S3
    sta N3
    rts

; ---------------------------------------------------------------------------
; Exact unsigned Q16 reciprocal: Q0:Q2=floor(65536/d) (17-bit).
; R is deliberately unspecified. d=1 is the sole 17-bit quotient special case.
; ---------------------------------------------------------------------------
urecip16_q16:
    ; Exact quotient-special ladder. For q=k, d is in
    ; floor(65536/(k+1))+1 .. floor(65536/k).
    ; q=1..15 covers 61,439 of 65,536 possible d values.
recip_q1_test:
    lda D1
    cmp #$80
    bcc recip_q2_test
    bne recip_q1_hit
    lda D0
    cmp #$01
    bcc recip_q2_test
recip_q1_hit:
    lda #$01
    jmp recip_small_return
recip_q2_test:
    lda D1
    cmp #$55
    bcc recip_q3_test
    bne recip_q2_hit
    lda D0
    cmp #$56
    bcc recip_q3_test
recip_q2_hit:
    lda #$02
    jmp recip_small_return
recip_q3_test:
    lda D1
    cmp #$40
    bcc recip_q4_test
    bne recip_q3_hit
    lda D0
    cmp #$01
    bcc recip_q4_test
recip_q3_hit:
    lda #$03
    jmp recip_small_return
recip_q4_test:
    lda D1
    cmp #$33
    bcc recip_q5_test
    bne recip_q4_hit
    lda D0
    cmp #$34
    bcc recip_q5_test
recip_q4_hit:
    lda #$04
    jmp recip_small_return
recip_q5_test:
    lda D1
    cmp #$2A
    bcc recip_q6_test
    bne recip_q5_hit
    lda D0
    cmp #$AB
    bcc recip_q6_test
recip_q5_hit:
    lda #$05
    jmp recip_small_return
recip_q6_test:
    lda D1
    cmp #$24
    bcc recip_q7_test
    bne recip_q6_hit
    lda D0
    cmp #$93
    bcc recip_q7_test
recip_q6_hit:
    lda #$06
    jmp recip_small_return
recip_q7_test:
    lda D1
    cmp #$20
    bcc recip_q8_test
    bne recip_q7_hit
    lda D0
    cmp #$01
    bcc recip_q8_test
recip_q7_hit:
    lda #$07
    jmp recip_small_return
recip_q8_test:
    lda D1
    cmp #$1C
    bcc recip_q9_test
    bne recip_q8_hit
    lda D0
    cmp #$72
    bcc recip_q9_test
recip_q8_hit:
    lda #$08
    jmp recip_small_return
recip_q9_test:
    lda D1
    cmp #$19
    bcc recip_q10_test
    bne recip_q9_hit
    lda D0
    cmp #$9A
    bcc recip_q10_test
recip_q9_hit:
    lda #$09
    jmp recip_small_return
recip_q10_test:
    lda D1
    cmp #$17
    bcc recip_q11_test
    bne recip_q10_hit
    lda D0
    cmp #$46
    bcc recip_q11_test
recip_q10_hit:
    lda #$0A
    jmp recip_small_return
recip_q11_test:
    lda D1
    cmp #$15
    bcc recip_q12_test
    bne recip_q11_hit
    lda D0
    cmp #$56
    bcc recip_q12_test
recip_q11_hit:
    lda #$0B
    jmp recip_small_return
recip_q12_test:
    lda D1
    cmp #$13
    bcc recip_q13_test
    bne recip_q12_hit
    lda D0
    cmp #$B2
    bcc recip_q13_test
recip_q12_hit:
    lda #$0C
    jmp recip_small_return
recip_q13_test:
    lda D1
    cmp #$12
    bcc recip_q14_test
    bne recip_q13_hit
    lda D0
    cmp #$4A
    bcc recip_q14_test
recip_q13_hit:
    lda #$0D
    jmp recip_small_return
recip_q14_test:
    lda D1
    cmp #$11
    bcc recip_q15_test
    bne recip_q14_hit
    lda D0
    cmp #$12
    bcc recip_q15_test
recip_q14_hit:
    lda #$0E
    jmp recip_small_return
recip_q15_test:
    lda D1
    cmp #$10
    bcc recip_fallback
    bne recip_q15_hit
    lda D0
    cmp #$01
    bcc recip_fallback
recip_q15_hit:
    lda #$0F
    jmp recip_small_return
recip_small_return:
    sta Q0
    lda #0
    sta Q1
    sta Q2
    clc
    rts
recip_fallback:
    ; Small-divisor tail: reuse the selected exact UDIV24 kernel
    ; on numerator $010000, while preserving public N and D2:D3.
    lda N0
    sta S14
    lda N1
    sta S15
    lda N2
    sta S16
    lda N3
    sta S17
    lda D2
    sta S20
    lda D3
    sta S21
    lda #0
    sta N0
    sta N1
    lda #1
    sta N2
    lda #0
    sta N3
    sta D2
    sta D3
    jsr OLD_UDIV24
    lda S14
    sta N0
    lda S15
    sta N1
    lda S16
    sta N2
    lda S17
    sta N3
    lda S20
    sta D2
    lda S21
    sta D3
    rts

; ---------------------------------------------------------------------------
; 8-bit phase trig. 0=$00, 90deg=$40, 180deg=$80, 270deg=$C0.
; Results are signed Q1.7-ish integers scaled to +/-127.
; ---------------------------------------------------------------------------
sin8:
    ldx X0
    lda SINTAB,x
    sta Z0
    clc
    rts
cos8:
    lda X0
    clc
    adc #64
    tax
    lda SINTAB,x
    sta Z0
    clc
    rts
sincos8:
    ldx X0
    lda SINTAB,x
    sta Z0
    txa
    clc
    adc #64
    tax
    lda SINTAB,x
    sta Z1
    clc
    rts

; ---------------------------------------------------------------------------
; ATAN2_8: signed dx=X0, dy=Y0 -> Z0 angle. Log2 difference reduces ratio to
; two 256-byte tables. Exhaustive release validation compares all 65,536 pairs.
; ---------------------------------------------------------------------------
atan2_8:
    lda X0
    bne atan_x_nonzero
    lda Y0
    beq atan_zero
    bmi atan_x0_neg_y
    lda #64
    jmp atan_store
atan_x0_neg_y:
    lda #192
    jmp atan_store
atan_zero:
    lda #0
    jmp atan_store
atan_x_nonzero:
    lda Y0
    bne atan_both_nonzero
    lda X0
    bmi atan_y0_neg_x
    lda #0
    jmp atan_store
atan_y0_neg_x:
    lda #128
    jmp atan_store
atan_both_nonzero:
    lda #0
    sta S12
    lda X0
    bpl atan_x_pos
    lda #1
    sta S12
    sec
    lda #0
    sbc X0
    sta S10
    jmp atan_y_sign
atan_x_pos:
    sta S10
atan_y_sign:
    lda Y0
    bpl atan_y_pos
    lda S12
    ora #2
    sta S12
    sec
    lda #0
    sbc Y0
    sta S11
    jmp atan_logs
atan_y_pos:
    sta S11
atan_logs:
    ldx S10
    lda LOGTAB,x
    ldx S11
    sec
    sbc ATANLOGTAB,x
    bcc atan_y_larger
    tax
    lda ATANTAB,x
    sta S13
    jmp atan_map
atan_y_larger:
    eor #$ff
    clc
    adc #1
    tax
    lda ATANTAB,x
    sta S13
    lda #64
    sec
    sbc S13
    sta S13
atan_map:
    lda S12
    beq atan_q0
    cmp #1
    beq atan_q1
    cmp #3
    beq atan_q2
    lda #0
    sec
    sbc S13
    jmp atan_store
atan_q2:
    lda #128
    clc
    adc S13
    jmp atan_store
atan_q1:
    lda #128
    sec
    sbc S13
    jmp atan_store
atan_q0:
    lda S13
atan_store:
    sta Z0
    clc
    rts

; ---------------------------------------------------------------------------
; ISQRT16: exact floor sqrt (profile-selected table/REU path).
; ISQRT32: exact 16-bit root using ISQRT16 seeding plus eight restoring base-4 refinement steps.
; ---------------------------------------------------------------------------
isqrt16:
    lda #0
    sta S19

    lda S19
    ora #$80
    tax
    lda SQHITAB,x
    cmp N1
    bcc sqrt16_accept0
    bne sqrt16_reject0
    lda SQLOTAB,x
    cmp N0
    bcc sqrt16_accept0
    beq sqrt16_accept0
    jmp sqrt16_reject0
sqrt16_accept0:
    stx S19
sqrt16_reject0:
    lda S19
    ora #$40
    tax
    lda SQHITAB,x
    cmp N1
    bcc sqrt16_accept1
    bne sqrt16_reject1
    lda SQLOTAB,x
    cmp N0
    bcc sqrt16_accept1
    beq sqrt16_accept1
    jmp sqrt16_reject1
sqrt16_accept1:
    stx S19
sqrt16_reject1:
    lda S19
    ora #$20
    tax
    lda SQHITAB,x
    cmp N1
    bcc sqrt16_accept2
    bne sqrt16_reject2
    lda SQLOTAB,x
    cmp N0
    bcc sqrt16_accept2
    beq sqrt16_accept2
    jmp sqrt16_reject2
sqrt16_accept2:
    stx S19
sqrt16_reject2:
    lda S19
    ora #$10
    tax
    lda SQHITAB,x
    cmp N1
    bcc sqrt16_accept3
    bne sqrt16_reject3
    lda SQLOTAB,x
    cmp N0
    bcc sqrt16_accept3
    beq sqrt16_accept3
    jmp sqrt16_reject3
sqrt16_accept3:
    stx S19
sqrt16_reject3:
    lda S19
    ora #$08
    tax
    lda SQHITAB,x
    cmp N1
    bcc sqrt16_accept4
    bne sqrt16_reject4
    lda SQLOTAB,x
    cmp N0
    bcc sqrt16_accept4
    beq sqrt16_accept4
    jmp sqrt16_reject4
sqrt16_accept4:
    stx S19
sqrt16_reject4:
    lda S19
    ora #$04
    tax
    lda SQHITAB,x
    cmp N1
    bcc sqrt16_accept5
    bne sqrt16_reject5
    lda SQLOTAB,x
    cmp N0
    bcc sqrt16_accept5
    beq sqrt16_accept5
    jmp sqrt16_reject5
sqrt16_accept5:
    stx S19
sqrt16_reject5:
    lda S19
    ora #$02
    tax
    lda SQHITAB,x
    cmp N1
    bcc sqrt16_accept6
    bne sqrt16_reject6
    lda SQLOTAB,x
    cmp N0
    bcc sqrt16_accept6
    beq sqrt16_accept6
    jmp sqrt16_reject6
sqrt16_accept6:
    stx S19
sqrt16_reject6:
    lda S19
    ora #$01
    tax
    lda SQHITAB,x
    cmp N1
    bcc sqrt16_accept7
    bne sqrt16_reject7
    lda SQLOTAB,x
    cmp N0
    bcc sqrt16_accept7
    beq sqrt16_accept7
    jmp sqrt16_reject7
sqrt16_accept7:
    stx S19
sqrt16_reject7:

    lda S19
    sta Z0
    lda #0
    sta Z1
    clc
    rts

.org $CA24
sqrt32_byte:
    ldy #4
sqrt32_pair:
    txa
    asl a
    rol S1
    rol S2
    rol S3
    asl a
    rol S1
    rol S2
    rol S3
    tax
    asl S4
    rol S5
    lda S4
    asl a
    ora #1
    sta S6
    lda S5
    rol a
    sta S7
    bcc sqrt32_trial_hi0
    lda S3
    beq sqrt32_no_sub
    cmp #1
    bne sqrt32_do_sub
    beq sqrt32_compare16
sqrt32_trial_hi0:
    lda S3
    bne sqrt32_do_sub
sqrt32_compare16:
    lda S2
    cmp S7
    bcc sqrt32_no_sub
    bne sqrt32_do_sub
    lda S1
    cmp S6
    bcc sqrt32_no_sub
sqrt32_do_sub:
    sec
    lda S1
    sbc S6
    sta S1
    lda S2
    sbc S7
    sta S2
    lda S3
    sbc #0
    sta S3
    inc S4
sqrt32_no_sub:
    dey
    bne sqrt32_pair
    rts

.org $CACC
; ---------------------------------------------------------------------------
; DIST8 inputs are signed deltas X0,Y0 (-128..127), output Z0.
; FAST is max + floor(min/2). ACCURATE uses an exhaustively selected separable
; approximation round(243*max/256)+round(107*min/256).
; ---------------------------------------------------------------------------
dist_abs_order:
    lda X0
    bpl dist_x_pos
    sec
    lda #0
    sbc X0
dist_x_pos:
    sta S10
    lda Y0
    bpl dist_y_pos
    sec
    lda #0
    sbc Y0
dist_y_pos:
    sta S11
    cmp S10
    bcc dist_order_done
    lda S10
    pha
    lda S11
    sta S10
    pla
    sta S11
dist_order_done:
    ; S10=max, S11=min
    rts

dist8_fast:
    jsr dist_abs_order
    lda S11
    lsr a
    clc
    adc S10
    sta Z0
    clc
    rts

dist8_accurate:
    jsr dist_abs_order
    ldx S10
    lda DISTATAB,x
    ldx S11
    clc
    adc DISTBTAB,x
    sta Z0
    clc
    rts

.org $9400
SINTAB:
.byte $00,$03,$06,$09,$0C,$10,$13,$16,$19,$1C,$1F,$22,$25,$28,$2B,$2E
.byte $31,$33,$36,$39,$3C,$3F,$41,$44,$47,$49,$4C,$4E,$51,$53,$55,$58
.byte $5A,$5C,$5E,$60,$62,$64,$66,$68,$6A,$6B,$6D,$6F,$70,$71,$73,$74
.byte $75,$76,$78,$79,$7A,$7A,$7B,$7C,$7D,$7D,$7E,$7E,$7E,$7F,$7F,$7F
.byte $7F,$7F,$7F,$7F,$7E,$7E,$7E,$7D,$7D,$7C,$7B,$7A,$7A,$79,$78,$76
.byte $75,$74,$73,$71,$70,$6F,$6D,$6B,$6A,$68,$66,$64,$62,$60,$5E,$5C
.byte $5A,$58,$55,$53,$51,$4E,$4C,$49,$47,$44,$41,$3F,$3C,$39,$36,$33
.byte $31,$2E,$2B,$28,$25,$22,$1F,$1C,$19,$16,$13,$10,$0C,$09,$06,$03
.byte $00,$FD,$FA,$F7,$F4,$F0,$ED,$EA,$E7,$E4,$E1,$DE,$DB,$D8,$D5,$D2
.byte $CF,$CD,$CA,$C7,$C4,$C1,$BF,$BC,$B9,$B7,$B4,$B2,$AF,$AD,$AB,$A8
.byte $A6,$A4,$A2,$A0,$9E,$9C,$9A,$98,$96,$95,$93,$91,$90,$8F,$8D,$8C
.byte $8B,$8A,$88,$87,$86,$86,$85,$84,$83,$83,$82,$82,$82,$81,$81,$81
.byte $81,$81,$81,$81,$82,$82,$82,$83,$83,$84,$85,$86,$86,$87,$88,$8A
.byte $8B,$8C,$8D,$8F,$90,$91,$93,$95,$96,$98,$9A,$9C,$9E,$A0,$A2,$A4
.byte $A6,$A8,$AB,$AD,$AF,$B2,$B4,$B7,$B9,$BC,$BF,$C1,$C4,$C7,$CA,$CD
.byte $CF,$D2,$D5,$D8,$DB,$DE,$E1,$E4,$E7,$EA,$ED,$F0,$F4,$F7,$FA,$FD
.org $9600
ATANLOGTAB:
.byte $00,$00,$20,$32,$40,$4A,$52,$59,$60,$65,$6A,$6E,$72,$76,$79,$7D
.byte $80,$82,$85,$87,$8A,$8C,$8E,$90,$92,$94,$96,$98,$99,$9B,$9D,$9E
.byte $A0,$A1,$A2,$A4,$A5,$A6,$A7,$A9,$AA,$AB,$AC,$AD,$AE,$AF,$B0,$B1
.byte $B2,$B3,$B4,$B5,$B6,$B7,$B8,$B9,$B9,$BA,$BB,$BC,$BD,$BD,$BE,$BF
.byte $C0,$C0,$C1,$C2,$C2,$C3,$C4,$C4,$C5,$C6,$C6,$C7,$C7,$C8,$C9,$C9
.byte $CA,$CA,$CB,$CC,$CC,$CD,$CD,$CE,$CE,$CF,$CF,$D0,$D0,$D1,$D1,$D2
.byte $D2,$D3,$D3,$D4,$D4,$D5,$D5,$D5,$D6,$D6,$D7,$D7,$D8,$D8,$D9,$D9
.byte $D9,$DA,$DA,$DB,$DB,$DB,$DC,$DC,$DD,$DD,$DD,$DE,$DE,$DE,$DF,$DF
.byte $E0,$E0,$E0,$E1,$E1,$E1,$E2,$E2,$E2,$E3,$E3,$E3,$E4,$E4,$E4,$E5
.byte $E5,$E5,$E6,$E6,$E6,$E7,$E7,$E7,$E7,$E8,$E8,$E8,$E9,$E9,$E9,$EA
.byte $EA,$EA,$EA,$EB,$EB,$EB,$EC,$EC,$EC,$EC,$ED,$ED,$ED,$ED,$EE,$EE
.byte $EE,$EE,$EF,$EF,$EF,$EF,$F0,$F0,$F0,$F1,$F1,$F1,$F1,$F1,$F2,$F2
.byte $F2,$F2,$F3,$F3,$F3,$F3,$F4,$F4,$F4,$F4,$F5,$F5,$F5,$F5,$F5,$F6
.byte $F6,$F6,$F6,$F7,$F7,$F7,$F7,$F7,$F8,$F8,$F8,$F8,$F9,$F9,$F9,$F9
.byte $F9,$FA,$FA,$FA,$FA,$FA,$FB,$FB,$FB,$FB,$FB,$FC,$FC,$FC,$FC,$FC
.byte $FD,$FD,$FD,$FD,$FD,$FD,$FE,$FE,$FE,$FE,$FE,$FF,$FF,$FF,$FF,$FF
.org $9700
ATANTAB:
.byte $20,$20,$1F,$1F,$1E,$1E,$1D,$1D,$1C,$1C,$1C,$1B,$1B,$1A,$1A,$19
.byte $19,$19,$18,$18,$17,$17,$17,$16,$16,$15,$15,$15,$14,$14,$14,$13
.byte $13,$13,$12,$12,$12,$11,$11,$11,$10,$10,$10,$0F,$0F,$0F,$0E,$0E
.byte $0E,$0E,$0D,$0D,$0D,$0D,$0C,$0C,$0C,$0C,$0B,$0B,$0B,$0B,$0A,$0A
.byte $0A,$0A,$0A,$09,$09,$09,$09,$09,$08,$08,$08,$08,$08,$08,$07,$07
.byte $07,$07,$07,$07,$07,$06,$06,$06,$06,$06,$06,$06,$06,$05,$05,$05
.byte $05,$05,$05,$05,$05,$05,$04,$04,$04,$04,$04,$04,$04,$04,$04,$04
.byte $04,$04,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03,$03
.byte $03,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02
.byte $02,$02,$02,$02,$02,$02,$02,$02,$02,$01,$01,$01,$01,$01,$01,$01
.byte $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01
.byte $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01
.byte $01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$00,$00,$00,$00
.byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
.byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
.byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
.org $9800
SQLOTAB:
.byte $00,$01,$04,$09,$10,$19,$24,$31,$40,$51,$64,$79,$90,$A9,$C4,$E1
.byte $00,$21,$44,$69,$90,$B9,$E4,$11,$40,$71,$A4,$D9,$10,$49,$84,$C1
.byte $00,$41,$84,$C9,$10,$59,$A4,$F1,$40,$91,$E4,$39,$90,$E9,$44,$A1
.byte $00,$61,$C4,$29,$90,$F9,$64,$D1,$40,$B1,$24,$99,$10,$89,$04,$81
.byte $00,$81,$04,$89,$10,$99,$24,$B1,$40,$D1,$64,$F9,$90,$29,$C4,$61
.byte $00,$A1,$44,$E9,$90,$39,$E4,$91,$40,$F1,$A4,$59,$10,$C9,$84,$41
.byte $00,$C1,$84,$49,$10,$D9,$A4,$71,$40,$11,$E4,$B9,$90,$69,$44,$21
.byte $00,$E1,$C4,$A9,$90,$79,$64,$51,$40,$31,$24,$19,$10,$09,$04,$01
.byte $00,$01,$04,$09,$10,$19,$24,$31,$40,$51,$64,$79,$90,$A9,$C4,$E1
.byte $00,$21,$44,$69,$90,$B9,$E4,$11,$40,$71,$A4,$D9,$10,$49,$84,$C1
.byte $00,$41,$84,$C9,$10,$59,$A4,$F1,$40,$91,$E4,$39,$90,$E9,$44,$A1
.byte $00,$61,$C4,$29,$90,$F9,$64,$D1,$40,$B1,$24,$99,$10,$89,$04,$81
.byte $00,$81,$04,$89,$10,$99,$24,$B1,$40,$D1,$64,$F9,$90,$29,$C4,$61
.byte $00,$A1,$44,$E9,$90,$39,$E4,$91,$40,$F1,$A4,$59,$10,$C9,$84,$41
.byte $00,$C1,$84,$49,$10,$D9,$A4,$71,$40,$11,$E4,$B9,$90,$69,$44,$21
.byte $00,$E1,$C4,$A9,$90,$79,$64,$51,$40,$31,$24,$19,$10,$09,$04,$01
.org $9900
SQHITAB:
.byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
.byte $01,$01,$01,$01,$01,$01,$01,$02,$02,$02,$02,$02,$03,$03,$03,$03
.byte $04,$04,$04,$04,$05,$05,$05,$05,$06,$06,$06,$07,$07,$07,$08,$08
.byte $09,$09,$09,$0A,$0A,$0A,$0B,$0B,$0C,$0C,$0D,$0D,$0E,$0E,$0F,$0F
.byte $10,$10,$11,$11,$12,$12,$13,$13,$14,$14,$15,$15,$16,$17,$17,$18
.byte $19,$19,$1A,$1A,$1B,$1C,$1C,$1D,$1E,$1E,$1F,$20,$21,$21,$22,$23
.byte $24,$24,$25,$26,$27,$27,$28,$29,$2A,$2B,$2B,$2C,$2D,$2E,$2F,$30
.byte $31,$31,$32,$33,$34,$35,$36,$37,$38,$39,$3A,$3B,$3C,$3D,$3E,$3F
.byte $40,$41,$42,$43,$44,$45,$46,$47,$48,$49,$4A,$4B,$4C,$4D,$4E,$4F
.byte $51,$52,$53,$54,$55,$56,$57,$59,$5A,$5B,$5C,$5D,$5F,$60,$61,$62
.byte $64,$65,$66,$67,$69,$6A,$6B,$6C,$6E,$6F,$70,$72,$73,$74,$76,$77
.byte $79,$7A,$7B,$7D,$7E,$7F,$81,$82,$84,$85,$87,$88,$8A,$8B,$8D,$8E
.byte $90,$91,$93,$94,$96,$97,$99,$9A,$9C,$9D,$9F,$A0,$A2,$A4,$A5,$A7
.byte $A9,$AA,$AC,$AD,$AF,$B1,$B2,$B4,$B6,$B7,$B9,$BB,$BD,$BE,$C0,$C2
.byte $C4,$C5,$C7,$C9,$CB,$CC,$CE,$D0,$D2,$D4,$D5,$D7,$D9,$DB,$DD,$DF
.byte $E1,$E2,$E4,$E6,$E8,$EA,$EC,$EE,$F0,$F2,$F4,$F6,$F8,$FA,$FC,$FE
.org $9A00
DISTATAB:
.byte $00,$01,$02,$03,$04,$05,$06,$07,$08,$09,$09,$0A,$0B,$0C,$0D,$0E
.byte $0F,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$1A,$1B,$1C,$1C,$1D
.byte $1E,$1F,$20,$21,$22,$23,$24,$25,$26,$27,$28,$29,$2A,$2B,$2C,$2D
.byte $2E,$2F,$2F,$30,$31,$32,$33,$34,$35,$36,$37,$38,$39,$3A,$3B,$3C
.byte $3D,$3E,$3F,$40,$41,$41,$42,$43,$44,$45,$46,$47,$48,$49,$4A,$4B
.byte $4C,$4D,$4E,$4F,$50,$51,$52,$53,$54,$54,$55,$56,$57,$58,$59,$5A
.byte $5B,$5C,$5D,$5E,$5F,$60,$61,$62,$63,$64,$65,$66,$67,$67,$68,$69
.byte $6A,$6B,$6C,$6D,$6E,$6F,$70,$71,$72,$73,$74,$75,$76,$77,$78,$79
.byte $7A,$7A,$7B,$7C,$7D,$7E,$7F,$80,$81,$82,$83,$84,$85,$86,$87,$88
.byte $89,$8A,$8B,$8C,$8C,$8D,$8E,$8F,$90,$91,$92,$93,$94,$95,$96,$97
.byte $98,$99,$9A,$9B,$9C,$9D,$9E,$9F,$9F,$A0,$A1,$A2,$A3,$A4,$A5,$A6
.byte $A7,$A8,$A9,$AA,$AB,$AC,$AD,$AE,$AF,$B0,$B1,$B2,$B2,$B3,$B4,$B5
.byte $B6,$B7,$B8,$B9,$BA,$BB,$BC,$BD,$BE,$BF,$C0,$C1,$C2,$C3,$C4,$C4
.byte $C5,$C6,$C7,$C8,$C9,$CA,$CB,$CC,$CD,$CE,$CF,$D0,$D1,$D2,$D3,$D4
.byte $D5,$D6,$D7,$D7,$D8,$D9,$DA,$DB,$DC,$DD,$DE,$DF,$E0,$E1,$E2,$E3
.byte $E4,$E5,$E6,$E7,$E8,$E9,$EA,$EA,$EB,$EC,$ED,$EE,$EF,$F0,$F1,$F2
.org $9B00
DISTBTAB:
.byte $00,$00,$01,$01,$02,$02,$03,$03,$03,$04,$04,$05,$05,$05,$06,$06
.byte $07,$07,$08,$08,$08,$09,$09,$0A,$0A,$0A,$0B,$0B,$0C,$0C,$0D,$0D
.byte $0D,$0E,$0E,$0F,$0F,$0F,$10,$10,$11,$11,$12,$12,$12,$13,$13,$14
.byte $14,$14,$15,$15,$16,$16,$17,$17,$17,$18,$18,$19,$19,$19,$1A,$1A
.byte $1B,$1B,$1C,$1C,$1C,$1D,$1D,$1E,$1E,$1F,$1F,$1F,$20,$20,$21,$21
.byte $21,$22,$22,$23,$23,$24,$24,$24,$25,$25,$26,$26,$26,$27,$27,$28
.byte $28,$29,$29,$29,$2A,$2A,$2B,$2B,$2B,$2C,$2C,$2D,$2D,$2E,$2E,$2E
.byte $2F,$2F,$30,$30,$30,$31,$31,$32,$32,$33,$33,$33,$34,$34,$35,$35
.byte $36,$36,$36,$37,$37,$38,$38,$38,$39,$39,$3A,$3A,$3B,$3B,$3B,$3C
.byte $3C,$3D,$3D,$3D,$3E,$3E,$3F,$3F,$40,$40,$40,$41,$41,$42,$42,$42
.byte $43,$43,$44,$44,$45,$45,$45,$46,$46,$47,$47,$47,$48,$48,$49,$49
.byte $4A,$4A,$4A,$4B,$4B,$4C,$4C,$4C,$4D,$4D,$4E,$4E,$4F,$4F,$4F,$50
.byte $50,$51,$51,$52,$52,$52,$53,$53,$54,$54,$54,$55,$55,$56,$56,$57
.byte $57,$57,$58,$58,$59,$59,$59,$5A,$5A,$5B,$5B,$5C,$5C,$5C,$5D,$5D
.byte $5E,$5E,$5E,$5F,$5F,$60,$60,$61,$61,$61,$62,$62,$63,$63,$63,$64
.byte $64,$65,$65,$66,$66,$66,$67,$67,$68,$68,$68,$69,$69,$6A,$6A,$6B


.org $CB40
; ---------------------------------------------------------------------------
; Fast ISQRT32 hybrid.  The upper 16 bits determine the result high byte
; exactly: hi(root32) = floor(sqrt(N3:N2)).  Reuse the selected ISQRT16 path,
; form the exact residual (N3:N2 - r*r), then run only the eight remaining
; restoring base-4 digit steps over N1:N0.  N0..N3 are restored before return.
; ---------------------------------------------------------------------------
isqrt32_fast:
    lda N0
    sta S8
    lda N1
    sta S9
    lda N2
    sta N0
    lda N3
    sta N1
    jsr MATH_ISQRT16
    lda S8
    sta N0
    lda S9
    sta N1

    ldx Z0
    stx S4
    lda #0
    sta S5

    sec
    lda N2
    sbc SQLOTAB,x
    sta S1
    lda N3
    sbc SQHITAB,x
    sta S2
    lda #0
    sta S3

    ldx N1
    jsr sqrt32_byte
    ldx N0
    jsr sqrt32_byte

    lda S4
    sta Z0
    lda S5
    sta Z1
    clc
    rts
