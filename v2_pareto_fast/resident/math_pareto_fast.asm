; ============================================================================
; Firemonger C64 Math API v1-PF — Pareto-Fast composable profile
; ============================================================================
; Same public operand/result geometry and entry addresses as v1.
;
; Selection rule: use the measured speed/size knee, not the huge Extreme tier.
; The initialized profile reserves 60 ZP bytes ($02-$3D): UMUL32 $02-$20,
; persistent UMUL24 $21-$38, and persistent UMUL8 $39-$3D. Divisions reuse
; UMUL32 transient bytes $10+, but preserve its six pointer-high bytes below $10.
;
; Public input vectors at $C000 are preserved. A/X/Y are volatile. D=0.
; UMUL returns C=0. UDIV/UMOD return C=0 success, C=1 divisor zero.
; Routines are sequential/non-reentrant; do not call from an IRQ concurrently.
; ============================================================================
!cpu 6510
!source "math_api.inc"
I_UDIV8=$4006
I_UDIV16=$420c
I_UDIV24=$480b
I_UDIV32_16=$4e00
I_UMOD8=$5212
I_UMUL8=$5300
I_UMUL16=$5400
I_UMUL24=$5600
I_UMUL24_Y1=$5645
I_UMUL24_Y2=$566f
I_UMUL24_Z0=$571e
I_UMUL32=$5800

*=$3000
api_public_code_start:
math_umul8:
        ; math_init installed the two isolated UMUL8 pointer highs once.
        ldx math_x0
        ldy math_y0
        jsr I_UMUL8
        sta math_z1
        lda $3d
        sta math_z0
        clc
        rts
!if * > $3020 { !error "math_umul8 wrapper overflow" }
*=$3020
math_umul16:
        jmp I_UMUL16
!if * > $3060 { !error "math_umul16 wrapper overflow" }
*=$3060
math_umul24:
        ; Public entry address stays compatible; the larger adapter is out of line.
        jmp pareto_umul24_public
!if * > $30b0 { !error "math_umul24 stub overflow" }
*=$30b0
math_umul32:
        ; Pareto-Fast initialized entry. math_init is mandatory for this profile.
        jmp pareto_umul32_public
!if * > $30c0 { !error "math_umul32 stub overflow" }
*=$30c0
math_umul32_ready:
        ; Address-compatible alias for loops that want to state the ready contract.
        jmp pareto_umul32_public
!if * > $30d0 { !error "math_umul32_ready stub overflow" }
*=$30d0
math_umul32_safe:
        ; Recovery entry if external code has overwritten the persistent highs.
        lda #$74
        sta $03
        sta $07
        sta $0b
        lda #$72
        sta $05
        sta $09
        sta $0d
        jmp pareto_umul32_public
!if * > $3120 { !error "math_umul32_safe overflow" }
*=$3120
math_udiv8:
        lda math_n0
        sta $10
        lda math_d0
        sta $11
        jsr I_UDIV8
        lda $12
        sta math_q0
        lda $13
        sta math_r0
        rts
!if * > $3140 { !error "math_udiv8 wrapper overflow" }
*=$3140
math_udiv16:
        lda math_n0
        sta $10
        lda math_n1
        sta $11
        lda math_d0
        sta $12
        lda math_d1
        sta $13
        jsr I_UDIV16
        lda $14
        sta math_q0
        lda $15
        sta math_q1
        lda $16
        sta math_r0
        lda $17
        sta math_r1
        rts
!if * > $3170 { !error "math_udiv16 wrapper overflow" }
*=$3170
math_udiv24:
        lda math_n0
        sta $10
        lda math_n1
        sta $11
        lda math_n2
        sta $12
        lda math_d0
        sta $13
        lda math_d1
        sta $14
        lda math_d2
        sta $15
        jsr I_UDIV24
        lda $16
        sta math_q0
        lda $17
        sta math_q1
        lda $18
        sta math_q2
        lda $19
        sta math_r0
        lda $1a
        sta math_r1
        lda $1b
        sta math_r2
        rts
!if * > $31b0 { !error "math_udiv24 wrapper overflow" }
*=$31b0
math_udiv32_16:
        lda math_n0
        sta $18
        lda math_n1
        sta $19
        lda math_n2
        sta $10
        lda math_n3
        sta $11
        lda math_d0
        sta $12
        lda math_d1
        sta $13
        jsr I_UDIV32_16
        lda $1a
        sta math_q0
        lda $1b
        sta math_q1
        lda $14
        sta math_q2
        lda $15
        sta math_q3
        lda $16
        sta math_r0
        lda $17
        sta math_r1
        rts
!if * > $3200 { !error "math_udiv32_16 wrapper overflow" }
*=$3200
math_umod8:
        lda math_n0
        sta $10
        lda math_d0
        sta $11
        jsr I_UMOD8
        sta math_r0
        rts
!if * > $3220 { !error "math_umod8 wrapper overflow" }
*=$3220
math_umod16: jmp math_udiv16
math_umod24: jmp math_udiv24
math_umod32_16: jmp math_udiv32_16
*=$3230
math_z16_to_n32:
        lda math_z0
        sta math_n0
        lda math_z1
        sta math_n1
        lda #0
        sta math_n2
        sta math_n3
        rts
*=$3250
math_z32_to_n32:
        ldx #3
.zn:    lda math_z0,x
        sta math_n0,x
        dex
        bpl .zn
        rts
*=$3260
math_q32_to_x32:
        ldx #3
.qx:    lda math_q0,x
        sta math_x0,x
        dex
        bpl .qx
        rts
*=$3270
math_r16_to_x16:
        lda math_r0
        sta math_x0
        lda math_r1
        sta math_x1
        rts
*=$3280
math_init:
        ; UMUL32 persistent table highs.
        lda #$74
        sta $03
        sta $07
        sta $0b
        lda #$72
        sta $05
        sta $09
        sta $0d
        ; UMUL24 isolated pointer highs ($21-$38).
        lda #$60
        sta $22
        sta $24
        sta $26
        lda #$62
        sta $28
        sta $2a
        sta $2c
        lda #$64
        sta $2e
        sta $30
        sta $32
        lda #$66
        sta $34
        sta $36
        sta $38
        ; UMUL8 isolated practical pointer highs ($39-$3D).
        lda #$68
        sta $3a
        lda #$6a
        sta $3c
        clc
        rts
api_public_code_end:

; Composition helpers are kept at the same public addresses as v1.
*=$3300
api_chain_code_start:
math_chain_umul16_udiv32_16:
        jsr math_umul16
        jsr math_z32_to_n32
        jmp math_udiv32_16
*=$3330
math_chain_udiv16_umul16:
        jsr math_udiv16
        bcs chain_div16_mul_ret
        lda math_q0
        sta math_x0
        lda math_q1
        sta math_x1
        lda math_d0
        sta math_y0
        lda math_d1
        sta math_y1
        jsr math_umul16
chain_div16_mul_ret: rts
*=$3360
math_chain_udiv24_umul24:
        jsr math_udiv24
        bcs chain_div24_mul_ret
        ldx #2
.cp1:   lda math_q0,x
        sta math_x0,x
        lda math_d0,x
        sta math_y0,x
        dex
        bpl .cp1
        jsr math_umul24
chain_div24_mul_ret: rts
*=$33a0
math_chain_udiv32_16_umul32:
        jsr math_udiv32_16
        bcs chain_div3216_mul_ret
        ldx #3
.cp2:   lda math_q0,x
        sta math_x0,x
        dex
        bpl .cp2
        lda math_d0
        sta math_y0
        lda math_d1
        sta math_y1
        lda #0
        sta math_y2
        sta math_y3
        jsr math_umul32
chain_div3216_mul_ret: rts
api_chain_code_end:

; Out-of-line initialized public adapter for UMUL32.
*=$3420
api_umul32_adapter_start:
pareto_umul32_public:
        lda math_x1
        sta $04
        lda math_x2
        sta $08
        lda math_x3
        sta $0c
        lda math_y0
        sta $0e
        lda math_y1
        sta $0f
        lda math_y2
        sta $10
        ldy math_y3
        lda math_x0
        jsr I_UMUL32
        sta math_z6
        stx math_z4
        sty math_z5
        lda $0e
        sta math_z0
        lda $0f
        sta math_z1
        lda $10
        sta math_z2
        lda $11
        sta math_z3
        lda $1c
        sta math_z7
        clc
        rts
api_umul32_adapter_end:

; Out-of-line public adapter for UMUL24.
*=$34c0
api_umul24_adapter_start:
pareto_umul24_public:
        ; math_init installed all twelve pointer high bytes in isolated $21-$38.
        ; Assisted ABI mirrors x0/x1/x2 into the p_sqr_lo pointer lows even
        ; though x0/x2 are also supplied in X/A.
        lda math_x0
        sta $21
        lda math_x1
        sta $23
        lda math_x2
        sta $25
        lda math_y1
        sta I_UMUL24_Y1
        lda math_y2
        sta I_UMUL24_Y2
        lda math_x2
        ldx math_x0
        ldy math_y0
        jsr I_UMUL24
        sta math_z5
        lda I_UMUL24_Z0
        sta math_z0
        lda $2f
        sta math_z1
        lda $31
        sta math_z2
        lda $33
        sta math_z3
        lda $35
        sta math_z4
        clc
        rts
api_umul24_adapter_end:

; Resident binary slices.
*=$4000
!bin "bin/udiv8_code.bin"
*=$420c
!bin "bin/udiv16_code.bin"
*=$4800
!bin "bin/udiv24_code.bin"
*=$4e00
!bin "bin/udiv32_16_outer.bin"
*=$5200
!bin "bin/umod8_code.bin"
*=$5300
!bin "bin/umul8_code.bin"
*=$5400
!bin "bin/umul16_code.bin"
*=$5600
!bin "bin/umul24_code.bin"
*=$5800
!bin "bin/umul32_code.bin"

; Table banks. UMUL24 and UMUL8/32 use different quarter-square biases.
*=$6000
!bin "bin/umul24_sqr_lo.bin"
*=$6200
!bin "bin/umul24_sqr_hi.bin"
*=$6400
!bin "bin/umul24_neg_lo.bin"
*=$6600
!bin "bin/umul24_neg_hi.bin"
*=$6800
!bin "bin/umul8_sqr_lo.bin"
*=$6a00
!bin "bin/umul8_sqr_hi.bin"
*=$6c00
!bin "bin/umul8_diff_lo.bin"
*=$6d00
!bin "bin/umul8_diff_hi.bin"
*=$7000
!bin "bin/umul32_sqr_lo.bin"
*=$7200
!bin "bin/umul32_sqr_hi.bin"
*=$7400
!bin "bin/umul32_neg_lo.bin"
*=$7600
!bin "bin/umul32_neg_hi.bin"
