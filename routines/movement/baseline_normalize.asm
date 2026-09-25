; Baseline for comparison: "move toward target" built on the shipped library,
; the way MATH_VEC2_NORMALIZE_Q8_8 would be used for it.
;
;   init:  (dx,dy) -> MATH_VEC2_NORMALIZE_Q8_8 -> Q1.15 unit vector
;          v = unit * speed via two MATH_SMUL16_SHR8 calls (Q8.8 px/frame)
;   step:  x (Q16.8) += vx, y (Q8.8) += vy
;
; The raw pixel delta is passed as the Q8.8 input; normalization is scale
; invariant, so this uses the whole signed 16-bit input range.
;
; init_arrive additionally computes a frame count for arrival:
;   len = isqrt(dx*dx + dy*dy)  (2x MATH_SMUL16, MATH_ISQRT32)
;   frames = ceil((len<<8) / speed)   (MATH_UDIV16_SHL8)
; and step_arrive counts it down and snaps to the target when it expires.
; Without that, a unit-vector mover has no way to know it has arrived.
;
; Speed here is Euclidean (px/frame along the direction of travel).
;
; Library entries/IO come from the V1 reference build (see benchmark.py).

ORG = $0800
IO  = $0B80
ST  = $0C00
MX = $C000
MY = $C004
MZ = $C008
MN = $C010
MD = $C014
MQ = $C018
NORM = $5E39
SMUL16_SHR8 = $5E0F
SMUL16 = $3BB0
ISQRT32 = $5E30
UDIV16_SHL8 = $5E18

IN_X0L = IO + 0
IN_X0H = IO + 1
IN_Y0  = IO + 2
IN_X1L = IO + 3
IN_X1H = IO + 4
IN_Y1  = IO + 5
IN_SPL = IO + 6
IN_SPH = IO + 7
SLOT   = IO + 8
UYL    = IO + 9
UYH    = IO + 10
DXL    = IO + 11
DXH    = IO + 12
DYL    = IO + 13
DYH    = IO + 14
SQ0    = IO + 15         ; 4 bytes dx*dx

PXF = ST + 0
PXL = ST + 8
PXH = ST + 16
PYF = ST + 24
PY  = ST + 32
VXL = ST + 40
VXH = ST + 48
VXS = ST + 56
VYL = ST + 64
VYH = ST + 72
FRL = ST + 80
FRH = ST + 88
TXL = ST + 96
TXH = ST + 104
TY  = ST + 112

* = ORG

b_init:
        stx SLOT
        lda #$80                ; start at the pixel centre
        sta PXF,x
        sta PYF,x
        lda IN_X0L
        sta PXL,x
        lda IN_X0H
        sta PXH,x
        lda IN_Y0
        sta PY,x
        lda IN_X1L
        sta TXL,x
        lda IN_X1H
        sta TXH,x
        lda IN_Y1
        sta TY,x
        lda IN_X1L
        sec
        sbc IN_X0L
        sta MX
        sta DXL
        lda IN_X1H
        sbc IN_X0H
        sta MX+1
        sta DXH
        lda IN_Y1
        sec
        sbc IN_Y0
        sta MY
        sta DYL
        lda #0
        sbc #0
        sta MY+1
        sta DYH
        jsr NORM
        lda MZ+2
        sta UYL
        lda MZ+3
        sta UYH
        lda MZ+0
        sta MX
        lda MZ+1
        sta MX+1
        lda IN_SPL
        sta MY
        lda IN_SPH
        sta MY+1
        jsr SMUL16_SHR8         ; Z = (ux*speed)>>8; v = Z>>7
        ldx SLOT
        lda MZ+0
        asl
        lda MZ+1
        rol
        sta VXL,x
        lda MZ+2
        rol
        sta VXH,x
        jsr sext
        sta VXS,x
        lda UYL
        sta MX
        lda UYH
        sta MX+1
        jsr SMUL16_SHR8
        ldx SLOT
        lda MZ+0
        asl
        lda MZ+1
        rol
        sta VYL,x
        lda MZ+2
        rol
        sta VYH,x
        clc
        rts

b_init_arrive:
        jsr b_init
        lda DXL                 ; dx*dx
        sta MX
        sta MY
        lda DXH
        sta MX+1
        sta MY+1
        jsr SMUL16
        lda MZ+0
        sta SQ0
        lda MZ+1
        sta SQ0+1
        lda MZ+2
        sta SQ0+2
        lda MZ+3
        sta SQ0+3
        lda DYL                 ; dy*dy
        sta MX
        sta MY
        lda DYH
        sta MX+1
        sta MY+1
        jsr SMUL16
        lda MZ+0
        clc
        adc SQ0
        sta MN
        lda MZ+1
        adc SQ0+1
        sta MN+1
        lda MZ+2
        adc SQ0+2
        sta MN+2
        lda MZ+3
        adc SQ0+3
        sta MN+3
        jsr ISQRT32
        lda MZ+0
        sta MN
        lda MZ+1
        sta MN+1
        lda IN_SPL
        sta MD
        lda IN_SPH
        sta MD+1
        jsr UDIV16_SHL8         ; Q = (len<<8)/speed, R = remainder
        ldx SLOT
        lda MQ+0
        sta FRL,x
        lda MQ+1
        sta FRH,x
        lda MQ+4                ; R low | high != 0 -> round up
        ora MQ+5
        beq bia_exact
        inc FRL,x
        bne bia_exact
        inc FRH,x
bia_exact:
        lda FRL,x
        ora FRH,x
        bne bia_moving
        sec                     ; zero-length move: arrived
        rts
bia_moving:
        clc
        rts

b_step:
        lda PXF,x
        clc
        adc VXL,x
        sta PXF,x
        lda PXL,x
        adc VXH,x
        sta PXL,x
        lda PXH,x
        adc VXS,x
        sta PXH,x
        lda PYF,x
        clc
        adc VYL,x
        sta PYF,x
        lda PY,x
        adc VYH,x
        sta PY,x
        clc
        rts

b_step_arrive:
        lda FRL,x
        bne bsa_lo
        lda FRH,x
        beq bsa_snap
        dec FRH,x
bsa_lo:
        dec FRL,x
        bne b_step
        lda FRH,x
        bne b_step
bsa_snap:
        lda TXL,x
        sta PXL,x
        lda TXH,x
        sta PXH,x
        lda TY,x
        sta PY,x
        sec
        rts

; 8-bit-x variants for the 8-bit corpus: x is Q8.8, the high byte is unused.
b8_step:
        lda PXF,x
        clc
        adc VXL,x
        sta PXF,x
        lda PXL,x
        adc VXH,x
        sta PXL,x
        lda PYF,x
        clc
        adc VYL,x
        sta PYF,x
        lda PY,x
        adc VYH,x
        sta PY,x
        clc
        rts

b8_step_arrive:
        lda FRL,x
        bne b8a_lo
        lda FRH,x
        beq b8a_snap
        dec FRH,x
b8a_lo:
        dec FRL,x
        bne b8_step
        lda FRH,x
        bne b8_step
b8a_snap:
        lda TXL,x
        sta PXL,x
        lda TY,x
        sta PY,x
        sec
        rts

sext:
        bmi sext_neg
        lda #0
        rts
sext_neg:
        lda #$FF
        rts
