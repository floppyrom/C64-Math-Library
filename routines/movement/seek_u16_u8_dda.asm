; seek_u16_u8_dda: exact "move object toward target" stepper (bulk Bresenham DDA)
;
; For the common game case "move this object to (tx,ty) at a given speed" this
; replaces normalize -> scale -> integrate. No unit vector, square root,
; general multiply or large table is needed, and the object lands on the target
; pixel exactly: every frame's position lies on the Bresenham line from the
; start to the target (within 0.5 px of the true line).
;
; Coordinates: x unsigned 16-bit (e.g. sprite X 0..511), y unsigned 8-bit.
; |dx| <= 32767.
;
; Speed is unsigned Q8.8 pixels per frame, integer part <= 126.
;   seek_init        speed along the MAJOR axis (classic Bresenham/Chebyshev:
;                    a 45 degree move covers sqrt(2) x the distance per frame)
;   seek_init_euclid speed along the direction of travel (constant Euclidean
;                    speed, within 0.7%); the major-axis speed is derived with a
;                    5-bit slope index, a 32-byte table and a 16x8 multiply
;
; Each frame advances the major axis by k = floor or ceil of the speed (the
; fraction is carried per slot) and the minor axis by exactly the Bresenham
; amount for those k pixels. The k-pixel error update is folded into one
; precomputed step: err -= rem_k and minor += whole_k (+1 on wrap), where
; k*dmin = whole_k*dmaj + rem_k. The result after every frame is identical to
; running k single-pixel Bresenham steps.
;
; Calling:
;   Put the object's start position in POS_XL/POS_XH/POS_Y (slot X); these
;   arrays are the object's position and are what you draw.
;   seek_init / seek_init_euclid:
;       X = slot, IN_X1L/IN_X1H/IN_Y1 = target, IN_SPL/IN_SPH = speed.
;       Returns C=1 if already on the target, else C=0.
;   seek_step:
;       X = slot. Call once per frame. Returns C=1 on the frame the target is
;       reached and on every later call (position stays on it), else C=0.
;   seek_step_int:
;       as seek_step, but ignores the speed fraction (moves the integer part
;       every frame); use it with seek_init and a whole-pixel speed.
;   All preserve X; A/Y volatile; D=0 required. Not reentrant: init uses the
;   IO scratch and overwrites IN_SPL/IN_SPH. The steppers use no scratch at
;   all, so they may be called for any number of slots in any order.
;
; Configure before assembly:
;   ORG  code origin
;   IO   16 bytes of input/scratch (zero page recommended)
;   ST   256 bytes of per-slot state; this file is laid out for NSLOT=8
;        (fields are 8 bytes apart; the KK/REM planes are 2x8 and the V planes
;        4x8 bytes)
;
; Per-slot fields (struct-of-arrays, index X = slot):
;   POS_XL/POS_XH/POS_Y  current position (public)
;   TGT_XL/TGT_XH/TGT_Y  target, used to snap on the arrival frame
;   N_L/N_H              major pixels remaining minus one; borrow = arrival
;   ERR_L/ERR_H          Bresenham error, invariant 0 <= err < dmaj
;   DMAJ_L/DMAJ_H        major-axis delta
;   BUD, KF              speed fraction accumulator and speed fraction
;   KK[2]                pixels per frame without/with fractional carry
;   REM_L[2]/REM_H[2]    k*dmin mod dmaj for both k values
;   VXL[4]/VXH[4]/VY[4]  per-frame deltas; plane = set + 2*wrap, stored with
;                        the step's known carries folded in (see put_nowrap)
;
ORG = $8000
IO  = $00F0
ST  = $9000

; IO block
IN_X1L = IO + 0
IN_X1H = IO + 1
IN_Y1  = IO + 2
IN_SPL = IO + 3          ; speed fraction (1/256 px)
IN_SPH = IO + 4          ; speed integer part, 0..126
T_DMAJL = IO + 5
T_DMAJH = IO + 6
T_DMIN  = IO + 7
T_MMAJ  = IO + 8         ; $00 / $FF major direction mask
T_MMIN  = IO + 9         ; $00 / $FF minor direction mask
T_REML  = IO + 10
T_REMH  = IO + 11
T_WHOLE = IO + 12
T_TMP   = IO + 13
T_MODE  = IO + 14        ; bit 7 set: y is the major axis
T_VY    = IO + 15

; Slot state, NSLOT = 8
POS_XL = ST + 0
POS_XH = ST + 8
POS_Y  = ST + 16
TGT_XL = ST + 24
TGT_XH = ST + 32
TGT_Y  = ST + 40
N_L    = ST + 48
N_H    = ST + 56
ERR_L  = ST + 64
ERR_H  = ST + 72
DMAJ_L = ST + 80
DMAJ_H = ST + 88
BUD    = ST + 96
KF     = ST + 104
KK     = ST + 112        ; [2]
REM_L  = ST + 128        ; [2]
REM_H  = ST + 144        ; [2]
VXL    = ST + 160        ; [4]
VXH    = ST + 192        ; [4]
VY     = ST + 224        ; [4] ends at ST+255

* = ORG

; ---------------------------------------------------------------------------
; seek_step: one frame of movement for slot X.
; ---------------------------------------------------------------------------
seek_step:
        lda BUD,x               ; speed fraction; carry selects k0 or k0+1
        clc
        adc KF,x
        sta BUD,x
        bcc seek_step_int
        txa                     ; Y = slot + 8 (k0+1 plane)
        adc #7
        tay
        bcc step_n              ; always (C=0)
; seek_step_int: integer speeds only (ignores KF/BUD, always moves k0).
seek_step_int:
        txa
        tay
step_n:
        lda N_L,x               ; remaining-1 -= k; borrow past zero = arrival
        sec
        sbc KK,y
        sta N_L,x
        bcc step_borrow
step_move:                      ; C=1
        lda ERR_L,x             ; err -= rem_k
        sbc REM_L,y
        sta ERR_L,x
        lda ERR_H,x
        sbc REM_H,y
        sta ERR_H,x
        bcs step_nowrap         ; C=1: no-wrap planes are stored pre-biased
        lda ERR_L,x             ; wrapped: err += dmaj, use wrap plane (+16)
        adc DMAJ_L,x
        sta ERR_L,x
        lda ERR_H,x
        adc DMAJ_H,x
        sta ERR_H,x
        tya                     ; C=1 (true sum >= 0)
        adc #15                 ; +16, leaves C=0
        tay
step_nowrap:                    ; carry-in is part of the stored deltas
        lda POS_XL,x
        adc VXL,y
        sta POS_XL,x
        lda POS_XH,x
        adc VXH,y
        sta POS_XH,x
        lda POS_Y,x             ; VY absorbs the carry out of the x add
        adc VY,y
        sta POS_Y,x
        clc
        rts
step_borrow:
        dec N_H,x
        bmi step_arrive
        sec
        bcs step_move           ; always
step_arrive:
        lda TGT_XL,x            ; land exactly on the target
        sta POS_XL,x
        lda TGT_XH,x
        sta POS_XH,x
        lda TGT_Y,x
        sta POS_Y,x
arrived_state:
        lda #0                  ; N = 0 and k >= 1 in both planes: every later
        sta N_L,x               ; call borrows into N_H and snaps again
        sta N_H,x
        lda #1
        sta KK,x
        sta KK+8,x
        sec
        rts

; ---------------------------------------------------------------------------
; seek_init_euclid: as seek_init, but IN_SP is the speed along the path.
; major speed = speed * cos(theta) = speed - speed*d/256, d from a 32-entry
; table indexed by floor(32*dmin/dmaj).
; ---------------------------------------------------------------------------
seek_init_euclid:
        jsr seek_geometry
        bcc eu_moving
        rts
eu_moving:
        lda T_DMAJH             ; bring dmaj below 256 for an 8-bit ratio
        sta T_REMH
        lda T_DMAJL
        ldy T_DMIN
        sty T_REML
        ldy T_REMH
eu_scale:
        beq eu_div              ; Z from T_REMH
        lsr T_REMH
        ror
        lsr T_REML
        ldy T_REMH
        jmp eu_scale
eu_div:
        sta T_WHOLE             ; scaled dmaj (>= 1; >= 128 if it was shifted)
        lda #$08                ; quotient sentinel: 5 rols push it into C
        sta T_TMP
        lda T_REML              ; scaled dmin <= scaled dmaj
eu_dloop:
        asl
        bcs eu_dsub
        cmp T_WHOLE
        bcc eu_dskip
eu_dsub:
        sbc T_WHOLE
        sec
eu_dskip:
        rol T_TMP
        bcc eu_dloop
        ldy T_TMP               ; q = min(31, floor(32*dmin/dmaj))
        ; P = (speed * d) >> 8, d = cos_d[q] <= 74, in T_REMH:A.
        ; d is shifted out LSB first with a sentinel in bit 7: 8 iterations.
        lda cos_d,y
        sec
        ror
        sta T_TMP
        lda #0
        sta T_REMH
eu_mloop:
        bcc eu_mskip
        clc
        adc IN_SPL
        tay
        lda T_REMH
        adc IN_SPH
        sta T_REMH
        tya
eu_mskip:
        ror T_REMH
        ror
        lsr T_TMP
        bne eu_mloop
        sta T_TMP               ; speed -= P
        lda IN_SPL
        sec
        sbc T_TMP
        sta IN_SPL
        lda IN_SPH
        sbc T_REMH
        sta IN_SPH
        jmp seek_rates

; ---------------------------------------------------------------------------
; seek_init: start moving slot X from POS_* to IN_X1/IN_Y1.
; ---------------------------------------------------------------------------
seek_init:
        jsr seek_geometry
        bcc seek_rates
        rts

; Per-frame rates for k0 = IN_SPH and k0+1; KF = IN_SPL.
seek_rates:
        lda IN_SPL
        sta KF,x
        lda #0
        sta T_REML
        sta T_REMH
        sta T_WHOLE
        ; rem = k0*dmin by repeated addition
        ldy IN_SPH
        beq rt_div
rt_mul:
        lda T_REML
        clc
        adc T_DMIN
        sta T_REML
        bcc rt_mul_nc
        inc T_REMH
rt_mul_nc:
        dey
        bne rt_mul
        ; whole = rem / dmaj, rem = rem mod dmaj (whole <= k0)
rt_div:
        lda T_REML
        cmp T_DMAJL
        lda T_REMH
        sbc T_DMAJH
        bcc rt_div_done
        sta T_REMH
        lda T_REML
        sbc T_DMAJL
        sta T_REML
        inc T_WHOLE
        jmp rt_div
rt_div_done:
        lda IN_SPH
        sta KK,x
        lda T_REML
        sta REM_L,x
        lda T_REMH
        sta REM_H,x
        ldy T_WHOLE
        ; set 1: rem += dmin, at most one more wrap
        lda T_REML
        clc
        adc T_DMIN
        sta T_REML
        bcc rt_s1_nc
        inc T_REMH
rt_s1_nc:
        cmp T_DMAJL
        lda T_REMH
        sbc T_DMAJH
        bcc rt_s1_store
        sta T_REMH
        lda T_REML
        sbc T_DMAJL
        sta T_REML
        inc T_WHOLE
rt_s1_store:
        lda T_REML
        sta REM_L+8,x
        lda T_REMH
        sta REM_H+8,x
        lda IN_SPH
        clc
        adc #1
        sta KK+8,x
        ; signed deltas: v = (m eor k) - m; minor wrap variant adds (m or 1)
        eor T_MMAJ
        sec
        sbc T_MMAJ
        sta T_DMAJH             ; vmaj1 (DMAJ temps are no longer needed)
        lda IN_SPH
        eor T_MMAJ
        sec
        sbc T_MMAJ
        sta T_DMAJL             ; vmaj0
        lda T_WHOLE
        eor T_MMIN
        sec
        sbc T_MMIN
        sta T_REMH              ; vmin1
        tya
        eor T_MMIN
        sec
        sbc T_MMIN
        sta T_REML              ; vmin0
        lda T_MMIN
        ora #1
        sta T_TMP               ; minor unit, +1 or -1
        txa                     ; set 0 planes: Y = slot (and slot+16)
        tay
        lda T_DMAJL
        ldx T_REML
        jsr rt_set
        tya                     ; set 1 planes: Y = slot+8 (and slot+24)
        clc
        adc #8
        tay
        lda T_DMAJH
        ldx T_REMH
        jsr rt_set
        tya
        sec
        sbc #8
        tax                     ; restore slot
        clc
        rts

; Write the no-wrap plane Y and the wrap plane Y+16 for one k.
; A = signed major delta, X = signed minor delta (no wrap); Y preserved.
;
; seek_step adds VXL/VXH with a known carry-in (C=1 on the no-wrap path,
; C=0 on the wrap path) and then adds VY with the carry out of that 16-bit
; add, which is 1 exactly when the stored VXH is $FF. So:
;   no-wrap plane: VX = vx-1, VY = vy + VXH
;   wrap plane:    VX = vx,   VY = vy + VXH
rt_set:
        bit T_MODE
        bmi rt_set_y
        stx T_VY                ; x major: vx = vmaj, vy = vmin (+unit on wrap)
        sta T_WHOLE
        sta VXL+16,y
        ora #$7F
        bmi rt_x_wn
        lda #0
rt_x_wn:
        sta VXH+16,y
        clc
        adc T_VY
        clc
        adc T_TMP
        sta VY+16,y
        lda T_WHOLE
        sec
        sbc #1
        sta VXL,y
        ora #$7F
        bmi rt_x_nn
        lda #0
rt_x_nn:
        sta VXH,y
        clc
        adc T_VY
        sta VY,y
        rts
rt_set_y:
        sta T_VY                ; y major: vy = vmaj, vx = vmin (+unit on wrap)
        stx T_WHOLE
        txa
        clc
        adc T_TMP
        sta VXL+16,y
        ora #$7F
        bmi rt_y_wn
        lda #0
rt_y_wn:
        sta VXH+16,y
        clc
        adc T_VY
        sta VY+16,y
        lda T_WHOLE
        sec
        sbc #1
        sta VXL,y
        ora #$7F
        bmi rt_y_nn
        lda #0
rt_y_nn:
        sta VXH,y
        clc
        adc T_VY
        sta VY,y
        rts

; ---------------------------------------------------------------------------
; seek_geometry: deltas, major/minor, err, N, target. C=1 if dmaj = 0.
; ---------------------------------------------------------------------------
seek_geometry:
        lda #0
        sta BUD,x
        lda IN_Y1
        sta TGT_Y,x
        sec
        sbc POS_Y,x
        ldy #0
        bcs geo_dy_pos
        eor #$FF
        adc #1                  ; C=0
        dey
geo_dy_pos:
        sta T_DMIN
        sty T_MMIN
        ldy #0
        lda IN_X1L
        sta TGT_XL,x
        sec
        sbc POS_XL,x
        sta T_DMAJL
        lda IN_X1H
        sta TGT_XH,x
        sbc POS_XH,x            ; Z/N/C from the high byte
        bcs geo_dx_pos
        dey
        eor #$FF                ; negate 16-bit: -(h:l) = ~(h:l)+1
        sta T_DMAJH
        lda T_DMAJL
        eor #$FF
        clc
        adc #1
        sta T_DMAJL
        bcc geo_dx_neg_done
        inc T_DMAJH
geo_dx_neg_done:
        lda T_DMAJH
geo_dx_pos:
        sta T_DMAJH
        sty T_MMAJ
        bne geo_xmajor
        lda T_DMAJL
        cmp T_DMIN
        bcs geo_xmajor
        ldy T_DMIN              ; y major: swap magnitudes and masks
        sta T_DMIN
        sty T_DMAJL
        lda T_MMAJ
        ldy T_MMIN
        sta T_MMIN
        sty T_MMAJ
        lda #$80
        sta T_MODE
        bne geo_common
geo_xmajor:
        lda #0
        sta T_MODE
geo_common:
        lda T_DMAJH             ; err = dmaj/2
        sta DMAJ_H,x
        lsr
        sta ERR_H,x
        lda T_DMAJL
        sta DMAJ_L,x
        ror
        sta ERR_L,x
        lda T_DMAJL             ; N = dmaj-1
        sec
        sbc #1
        sta N_L,x
        lda T_DMAJH
        sbc #0
        sta N_H,x
        bcc geo_zero
        clc
        rts
geo_zero:
        jmp arrived_state       ; sets the arrived state; returns C=1 to seek_init*

; Euclidean correction: cos_d[q] = round(256*(1-cos(atan((q+0.5)/32))))
cos_d:
        !byte 0, 0, 1, 2, 2, 4, 5, 7
        !byte 9, 11, 13, 15, 18, 20, 23, 26
        !byte 28, 31, 34, 37, 40, 44, 47, 50
        !byte 53, 56, 59, 62, 65, 68, 71, 74
