; ============================================================================
; Firemonger C64 Math API v1 — composable resident reference image
; ============================================================================
; This top-level file is a sparse validation/link image. Algorithm sources are
; under resident/modules/. The !bin slices are rebuilt byte-for-byte from those
; commented sources by tools/rebuild_resident.py.
;
; Memory model:
;   $02-$0D  persistent UMUL32 pointer-high state after math_init
;   $0E-$20  UMUL32 transient state; other primitives use subsets of $10-$20
;   $3000... public wrappers and composition helpers
;   $4000... resident arithmetic kernels (sparse, fixed/tuned placement)
;   $8000... page-aligned quarter-square table bank
;   $C000-$C01F public operand/result vectors (not emitted by this image)
;
; The library is sequential/non-reentrant: do not invoke it from an IRQ while a
; foreground math call is active. UMUL24/UMUL32 patch operands in writable RAM.
; Decimal mode must be clear. $0000/$0001 are never used.
; ============================================================================

!cpu 6510
!source "math_api.inc"

; Internal resident kernel addresses.
I_UDIV8       = $4006
I_UDIV16      = $4200
I_UDIV24      = $4300
I_UDIV32_16   = $4500
I_UMOD8       = $4612
I_UMUL8       = $4700
I_UMUL16      = $4800
I_UMUL24      = $4a00
I_UMUL32      = $4c00

; ---------------------------------------------------------------------------
; Public wrappers. Inputs live at $c000 and are preserved.
; Multiply wrappers normalize C=0. Divide/mod return C=0 success, C=1 d=0.
; ---------------------------------------------------------------------------
*=$3000
api_public_code_start:
math_umul8:
        ; UMUL8 balanced uses two ZP pointers whose high bytes are normally
        ; initialized by its standalone image. Rebuild them because ZP is shared.
        lda #$80
        sta $11
        lda #$82
        sta $13
        ldx math_x0
        ldy math_y0
        jsr I_UMUL8
        sta math_z1
        lda $14
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
        lda math_x0
        sta $10
        lda math_x1
        sta $11
        lda math_x2
        sta $12
        lda math_y0
        sta $19
        lda math_y1
        sta $1a
        lda math_y2
        sta $1b
        jsr I_UMUL24
        sta math_z5
        lda $10
        sta math_z0
        lda $11
        sta math_z1
        lda $12
        sta math_z2
        lda $13
        sta math_z3
        lda $14
        sta math_z4
        clc
        rts
!if * > $30b0 { !error "math_umul24 wrapper overflow" }
*=$30b0
math_umul32:
        ; Zero-assumption public entry: rebuild the persistent pointer-high
        ; block before every call, then fall into the composable ready entry.
        lda #$90                  ; >umul32_neg_sqr_lo
        sta $03
        sta $07
        sta $0b
        lda #$8e                  ; >umul32_sqr_hi
        sta $05
        sta $09
        sta $0d
math_umul32_ready:
        ; After math_init, $02-$0d survives every other resident public call.
        ; This entry therefore remains valid across arbitrary UMUL/UDIV/UMOD
        ; sequencing and saves the six pointer-high stores on each UMUL32.
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
!if * > $3120 { !error "math_umul32 wrapper overflow" }

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

; Derived wide modulo entries. They deliberately update q as a side effect;
; the remainder/status contract is identical to UDIV.
*=$3220
math_umod16:
        jmp math_udiv16
math_umod24:
        jmp math_udiv24
math_umod32_16:
        jmp math_udiv32_16

; Composition helpers.
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
.zn:
        lda math_z0,x
        sta math_n0,x
        dex
        bpl .zn
        rts
*=$3260
math_q32_to_x32:
        ldx #3
.qx:
        lda math_q0,x
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

; ---------------------------------------------------------------------------
; Resident code modules. These are byte-exact extracts of relocated validated
; kernels, except UMUL16 which is the new portable resident-profile core.
; ---------------------------------------------------------------------------

; ---------------------------------------------------------------------------
; Optional one-time resident initialization.
; Initializes the persistent UMUL32 pointer-high block used by
; math_umul32_ready. Safe to call again at any time.
; ---------------------------------------------------------------------------
*=$3280
math_init:
        lda #$90
        sta $03
        sta $07
        sta $0b
        lda #$8e
        sta $05
        sta $09
        sta $0d
        clc
        rts

*=$4000
!bin "bin/udiv8_code.bin"
*=$4200
!bin "bin/udiv16_code.bin"
*=$4300
!bin "bin/udiv24_code.bin"
*=$4400
!bin "bin/udiv32_16_core.bin"
*=$4500
!bin "bin/udiv32_16_outer.bin"
*=$4600
!bin "bin/umod8_code.bin"
*=$4700
!bin "bin/umul8_code.bin"
*=$4800
!bin "bin/umul16_code.bin"
*=$4a00
!bin "bin/umul24_code.bin"
*=$4c00
!bin "bin/umul32_code.bin"

; ---------------------------------------------------------------------------
; Shared table bank. Page geometry is preserved from the validated kernels.
; ---------------------------------------------------------------------------
*=$8000
!bin "bin/umul8_sqr_lo.bin"
*=$8200
!bin "bin/umul8_sqr_hi.bin"
*=$8400
!bin "bin/umul24_sqr_lo.bin"
*=$8600
!bin "bin/umul24_sqr_hi.bin"
*=$8800
!bin "bin/umul24_neg_lo.bin"
*=$8a00
!bin "bin/umul24_neg_hi.bin"
*=$8c00
!bin "bin/umul32_sqr_lo.bin"
*=$8e00
!bin "bin/umul32_sqr_hi.bin"
*=$9000
!bin "bin/umul32_neg_lo.bin"
*=$9200
!bin "bin/umul32_neg_hi.bin"

; ---------------------------------------------------------------------------
; Assembly-level composition proofs / useful fused call sequences.
; ---------------------------------------------------------------------------
*=$3300
math_chain_umul16_udiv32_16:
        jsr math_umul16
        jsr math_z32_to_n32
        jmp math_udiv32_16

*=$3330
math_chain_udiv16_umul16:
        jsr math_udiv16
        bcs chain16_done
        lda math_q0
        sta math_x0
        lda math_q1
        sta math_x1
        lda math_d0
        sta math_y0
        lda math_d1
        sta math_y1
        jsr math_umul16
chain16_done:
        rts

*=$3360
math_chain_udiv24_umul24:
        jsr math_udiv24
        bcs chain24_done
        lda math_q0
        sta math_x0
        lda math_q1
        sta math_x1
        lda math_q2
        sta math_x2
        lda math_d0
        sta math_y0
        lda math_d1
        sta math_y1
        lda math_d2
        sta math_y2
        jsr math_umul24
chain24_done:
        rts

*=$33a0
math_chain_udiv32_16_umul32:
        jsr math_udiv32_16
        bcs chain3216_done
        lda math_q0
        sta math_x0
        lda math_q1
        sta math_x1
        lda math_q2
        sta math_x2
        lda math_q3
        sta math_x3
        lda math_d0
        sta math_y0
        lda math_d1
        sta math_y1
        lda #0
        sta math_y2
        sta math_y3
        jsr math_umul32
chain3216_done:
        rts
api_public_code_end:
