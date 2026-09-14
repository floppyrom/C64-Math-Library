; ============================================================================
; Firemonger C64 Math API v3 REU-Pareto composable + batch-turbo profile
; ============================================================================
; Same public operand/result geometry and entry addresses as v1/v2.
; Requires a 512 KiB REU loaded with c64_math_v3_512k.reu.
;
; Selection rule: use the measured speed/size knee, not the huge Extreme tier.
; The normal initialized profile reserves 55 ZP bytes ($02-$38): UMUL32 $02-$20
; and persistent UMUL24 $21-$38. REU-native UMUL8/UMUL16 need no persistent
; ZP of their own; UMUL16 uses $10-$15 transiently inside the shared union.
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

; Exact normal-RAM launch wrapper for the UMUL32 record kernel.
; The 135-byte stack-free executable body is swapped into $000a-$0090 by REU.
*=$1000
!bin "bin/turbo_umul32_wrapper.bin"

; Turbo overlays are assembled against the already-resident v2 UMUL32
; quarter-square planes at $7000/$7200/$7400/$7600. No duplicate turbo
; table bank is needed in C64 RAM.

*=$3000
api_public_code_start:
math_umul8:
        ; v3 default: two one-byte REU lookups (product low/high).
        jmp reu_umul8_public
!if * > $3020 { !error "math_umul8 wrapper overflow" }
*=$3020
math_umul16:
        ; v3 default: four REU 8x8 products, no resident UMUL16 table/kernel.
        jmp reu_umul16_public
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
        ; v3 default: quotient/remainder direct from REU banks 2/3.
        jmp reu_udiv8_public
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
        ; v3 default: remainder direct from REU bank 3.
        jmp reu_umod8_public
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
        ; REU v3 replaces the resident public UMUL8 and UMUL16 paths, so
        ; $39-$3D are no longer persistent state.
        jsr reu_lookup_init
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

; ============================================================================
; REU v3 transport/adapters
; ============================================================================
; REC register map at $DF00-$DF0A. I/O must be visible in the C64 memory map.
REU_STATUS  = $df00
REU_COMMAND = $df01
REU_C64_LO  = $df02
REU_C64_HI  = $df03
REU_REU_LO  = $df04
REU_REU_HI  = $df05
REU_BANK    = $df06
REU_LEN_LO  = $df07
REU_LEN_HI  = $df08
REU_IMR     = $df09
REU_ACR     = $df0a
REU_CMD_FETCH = $81        ; Execute + REU -> C64
REU_CMD_SWAP  = $82        ; Execute + SWAP
REU_ACR_FIX_BOTH = $c0     ; one-byte lookup: hold C64 and REU addresses fixed

*=$3800
math_reu_umul16_begin:
        ; Swap exact 113-byte Firemonger kernel into $003e-$00ae while saving
        ; the application's previous bytes into REU bank 4.
        lda #$3e
        sta REU_C64_LO
        lda #$00
        sta REU_C64_HI
        sta REU_REU_LO
        sta REU_REU_HI
        lda #4
        sta REU_BANK
        lda #113
        sta REU_LEN_LO
        lda #0
        sta REU_LEN_HI
        sta REU_ACR
        lda #REU_CMD_SWAP
        sta REU_COMMAND
        clc
        rts
math_reu_umul16_begin_end:

*=$3840
math_reu_umul16:
        ; Valid only between BEGIN/END.  The A=x1 entry saves 3 native cycles.
        ; x0/x1/y1 are SMC/immediate operands inside the active ZP overlay.
        lda math_x0
        sta $54
        lda math_x1
        sta $62
        lda math_y1
        sta $72
        ldy math_y0
        lda math_x1
        jsr $0040              ; relocated umult_ax1
        sta math_z2
        stx math_z1
        sty math_z3
        lda $ae
        sta math_z0
        clc
        rts
math_reu_umul16_call_end:

*=$3880
math_reu_umul16_end:
        ; Same SWAP restores the exact pre-overlay ZP image and returns the
        ; modified-but-valid kernel to REU bank 4 for the next batch.
        jsr math_reu_umul16_begin
        jmp reu_lookup_init
math_reu_umul16_end_end:

*=$38c0
math_reu_umul32_begin:
        ; Swap the exact 135-byte stack-free record-family kernel into $000a-$0090.
        lda #$0a
        sta REU_C64_LO
        lda #$00
        sta REU_C64_HI
        sta REU_REU_LO
        sta REU_REU_HI
        lda #5
        sta REU_BANK
        lda #241
        sta REU_LEN_LO
        lda #0
        sta REU_LEN_HI
        sta REU_ACR
        lda #REU_CMD_SWAP
        sta REU_COMMAND
        clc
        rts
math_reu_umul32_begin_end:

*=$3900
math_reu_umul32:
        ; Valid only between BEGIN/END. Feed all SMC input bytes explicitly,
        ; use the validated A=x3 launch at $1002, then normalize to public z0..z7.
        lda math_x0
        sta $1b
        lda math_x1
        sta $29
        lda math_x2
        sta $39
        lda math_x3
        sta $49
        lda math_y1
        sta $60
        lda math_y2
        sta $0d
        lda math_y3
        sta $15
        ldy math_y0
        lda math_x3
        jsr $1002
        sta math_z6
        stx math_z7
        lda $75
        sta math_z0
        lda $76
        sta math_z1
        lda $77
        sta math_z2
        lda $72
        sta math_z3
        lda $73
        sta math_z4
        lda $74
        sta math_z5
        clc
        rts
math_reu_umul32_call_end:

*=$3960
math_reu_umul32_end:
        jsr math_reu_umul32_begin
        jmp reu_lookup_init
math_reu_umul32_end_end:

*=$39a0
reu_lookup_init:
        ; Configure a fixed C64 scratch byte, one-byte length and fixed-address
        ; mode. Each lookup then needs only REU offset/bank + Execute.
        lda #<MATH_REU_BYTE
        sta REU_C64_LO
        lda #>MATH_REU_BYTE
        sta REU_C64_HI
        lda #1
        sta REU_LEN_LO
        lda #0
        sta REU_LEN_HI
        lda #REU_ACR_FIX_BOTH
        sta REU_ACR
        rts
reu_lookup_init_end:

*=$39c0
reu_umul8_public:
        lda math_x0
        sta REU_REU_LO
        lda math_y0
        sta REU_REU_HI
        lda #0
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta math_z0
        lda #1
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta math_z1
        clc
        rts
reu_umul8_public_end:

*=$3a00
reu_udiv8_public:
        lda math_n0
        sta REU_REU_LO
        lda math_d0
        beq reu_udiv8_zero
        sta REU_REU_HI
        lda #2
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta math_q0
        lda #3
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta math_r0
        clc
        rts
reu_udiv8_zero:  lda #0
        sta math_q0
        sta math_r0
        sec
        rts
reu_udiv8_public_end:

*=$3a40
reu_umod8_public:
        lda math_n0
        sta REU_REU_LO
        lda math_d0
        beq reu_umod8_zero
        sta REU_REU_HI
        lda #3
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta math_r0
        clc
        rts
reu_umod8_zero:  lda #0
        sta math_r0
        sec
        rts
reu_umod8_public_end:

*=$3a80
reu_umul16_public:
        ; Generic one-shot 16x16 using four direct REU 8x8 product lookups.
        ; X/Y keep operand bytes across the two DMA fetches for each partial.
        ; ZP $10-$15 is transient and lies inside the existing resident union.
        ldx math_x0
        ldy math_y0

        ; p00 = x0*y0 -> $10:$11
        stx REU_REU_LO
        sty REU_REU_HI
        lda #0
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta $10
        lda #1
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta $11
        lda #0
        sta $12
        sta $13

        ; p01 = x0*y1, shifted by 8.
        ldy math_y1
        stx REU_REU_LO
        sty REU_REU_HI
        lda #0
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta $14
        lda #1
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta $15
        clc
        lda $11
        adc $14
        sta $11
        lda $12
        adc $15
        sta $12
        lda $13
        adc #0
        sta $13

        ; p10 = x1*y0, shifted by 8.
        ldx math_x1
        ldy math_y0
        stx REU_REU_LO
        sty REU_REU_HI
        lda #0
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta $14
        lda #1
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta $15
        clc
        lda $11
        adc $14
        sta $11
        lda $12
        adc $15
        sta $12
        lda $13
        adc #0
        sta $13

        ; p11 = x1*y1, shifted by 16.
        ldy math_y1
        stx REU_REU_LO
        sty REU_REU_HI
        lda #0
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta $14
        lda #1
        sta REU_BANK
        lda #REU_CMD_FETCH
        sta REU_COMMAND
        lda MATH_REU_BYTE
        sta $15
        clc
        lda $12
        adc $14
        sta $12
        lda $13
        adc $15
        sta $13

        lda $10
        sta math_z0
        lda $11
        sta math_z1
        lda $12
        sta math_z2
        lda $13
        sta math_z3
        clc
        rts
reu_umul16_public_end:

; Resident binary slices.
*=$420c
!bin "bin/udiv16_code.bin"
*=$4800
!bin "bin/udiv24_code.bin"
*=$4e00
!bin "bin/udiv32_16_outer.bin"
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
*=$7000
!bin "bin/umul32_sqr_lo.bin"
*=$7200
!bin "bin/umul32_sqr_hi.bin"
*=$7400
!bin "bin/umul32_neg_lo.bin"
*=$7600
!bin "bin/umul32_neg_hi.bin"
