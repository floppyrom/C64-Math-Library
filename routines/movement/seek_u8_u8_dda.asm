; seek_u8_u8_dda: exact "move object toward target" for 8-bit coordinates
;
; The 8-bit counterpart of seek_u16_u8_dda, following Repose's observation
; that game coordinates are small: x and y are both unsigned bytes (0..255;
; use x/2 for full-width sprite X, as many games already do). Every delta is
; then at most 255, so the Bresenham error, the remaining-distance counter and
; both positions are single bytes and one frame costs about 70 cycles.
;
; Every frame's position lies on the Bresenham line from the start to the
; target (within 0.5 px of the true line) and the object lands exactly on the
; target.
;
; Speed is unsigned Q8.8 pixels per frame, integer part <= 126.
;   seek8_init        speed along the MAJOR axis (classic Bresenham: a 45
;                     degree move covers sqrt(2) x the distance per frame)
;   seek8_init_euclid speed along the path (constant Euclidean speed, within
;                     0.7%); 5-bit slope index, 32-byte table, 16x8 multiply
;   seek8_step        one frame, fractional speeds
;   seek8_step_int    one frame, integer speeds only (ignores the fraction)
;
; Each frame moves the major axis by k = floor or ceil of the speed and the
; minor axis by exactly the Bresenham amount for those k pixels, precomputed
; at init as k*dmin = whole_k*dmaj + rem_k: err -= rem_k, minor += whole_k,
; and +1 more on wrap. Identical to k single-pixel Bresenham steps. No
; multiply or divide is needed for this: init runs k0+1 add/compare rounds.
;
; The speed fraction and the distance still to go share one 16-bit counter,
; R = dmaj*256 - 1 - (sum of speeds so far): the borrow out of its low byte
; says whether this frame moves k0 or k0+1 pixels, and the borrow out of its
; high byte says the object has arrived.
;
;   seek8_step1       one frame at exactly 1 px/frame (uses the NMOS DCP opcode)
;
; Calling:
;   Put the start position in POS_X/POS_Y (slot X); these arrays are the
;   object's position and are what you draw.
;   seek8_init / seek8_init_euclid:
;       X = slot, IN_X1/IN_Y1 = target, IN_SPL/IN_SPH = speed (Q8.8).
;       Returns C=1 if already on the target, else C=0.
;   seek8_step / seek8_step_int:
;       X = slot, once per frame. Returns C=1 on the frame the target is
;       reached and on every later call (position stays on it), else C=0.
;       Use one stepper for a given move; seek8_step_int needs a speed of
;       at least 1.0 and moves exactly IN_SPH pixels per frame; seek8_step1
;       needs a speed of $01xx and moves exactly 1 pixel per frame.
;   All preserve X; A/Y volatile; D=0 required. Init uses the IO scratch and
;   overwrites IN_SPL/IN_SPH; the steppers use no scratch at all.
;
; Configure before assembly:
;   ORG  code origin
;   IO   16 bytes of input/scratch (zero page recommended)
;   ST   160 bytes of per-slot state, laid out for NSLOT=8 (fields are 8 bytes
;        apart; REM is 2x8 and VX/VY 4x8 bytes)
;
; Per-slot fields (struct-of-arrays, index X = slot):
;   POS_X/POS_Y     current position (public)
;   TGT_X/TGT_Y     target, used to snap on the arrival frame
;   RL/RH           R = dmaj*256 - 1 - speeds so far (see above)
;   ERR, DMAJ       Bresenham error (0 <= err < dmaj) and major delta
;   KF, KI          speed fraction and integer part
;   REM[2]          k*dmin mod dmaj for k0 and k0+1
;   VX[4]/VY[4]     per-frame deltas, plane = set + 2*wrap. The steppers add
;                   VX with C=1 and then VY with the carry out of that add,
;                   so VX = vx-1 and VY = vy-[vx<=0]
;
!cpu 6510                ; seek8_step1 uses DCP
ORG = $8000
IO  = $00F0
ST  = $9000

; IO block
IN_X1   = IO + 0
IN_Y1   = IO + 1
IN_SPL  = IO + 2         ; speed fraction (1/256 px)
IN_SPH  = IO + 3         ; speed integer part, 0..126
T_DMAJ  = IO + 4
T_DMIN  = IO + 5
T_MMAJ  = IO + 6         ; $00 / $FF major direction mask
T_MMIN  = IO + 7         ; $00 / $FF minor direction mask
T_MODE  = IO + 8         ; bit 7 set: y is the major axis
T_WHOLE = IO + 9
T_A0    = IO + 10        ; signed major delta for k0 / k0+1
T_A1    = IO + 11
T_B0    = IO + 12        ; signed minor delta for k0 / k0+1 (no wrap)
T_B1    = IO + 13
T_U     = IO + 14        ; minor unit, +1 or -1; also a multiply temp
T_VY    = IO + 15

; Slot state, NSLOT = 8
POS_X  = ST + 0
POS_Y  = ST + 8
TGT_X  = ST + 16
TGT_Y  = ST + 24
RL     = ST + 32
RH     = ST + 40
ERR    = ST + 48
DMAJ   = ST + 56
KF     = ST + 64
KI     = ST + 72
REM    = ST + 80         ; [2]
VX     = ST + 96         ; [4]
VY     = ST + 128        ; [4] ends at ST+159

* = ORG

; ---------------------------------------------------------------------------
; seek8_step: one frame, fractional speed. Falls into seek8_step_int for the
; common k0 frame; the k0+1 frame has its own copy using the +8 planes.
; ---------------------------------------------------------------------------
seek8_step:
        lda RL,x
        sec
        sbc KF,x
        sta RL,x
        bcc st1                 ; borrow: this frame moves k0+1
; seek8_step_int: one frame of k0 pixels.
seek8_step_int:
        sec
        lda RH,x
        sbc KI,x
        sta RH,x
        bcc st_arrive
st0_move:
        lda ERR,x               ; C=1
        sbc REM,x
        bcc st0_wrap
        sta ERR,x
        lda POS_X,x             ; C=1 into both planes, see VX/VY above
        adc VX,x
        sta POS_X,x
        lda POS_Y,x
        adc VY,x
        sta POS_Y,x
        clc
        rts
st0_wrap:
        adc DMAJ,x              ; err += dmaj; the true sum is >= 0, so C=1
        sta ERR,x
        lda POS_X,x
        adc VX+16,x
        sta POS_X,x
        lda POS_Y,x
        adc VY+16,x
        sta POS_Y,x
        clc
        rts
; seek8_step1: one frame at exactly 1 px/frame along the major axis (init
; with speed $0100). DCP decrements R's high byte and compares it with $FF in
; one instruction: Z=1 when it wraps (arrival) and C=1 for the error update.
seek8_step1:
        lda #$FF
        dcp RH,x
        bne st0_move
st_arrive:
        lda TGT_X,x             ; land exactly on the target
        sta POS_X,x
        lda TGT_Y,x
        sta POS_Y,x
arrived_state:
        lda #0                  ; R = 0 and k >= 1: every later call borrows
        sta RH,x                ; out of RH and snaps again
        lda #1
        sta KI,x
        sec
        rts

st1:
        lda RH,x                ; C=0: subtracts k0+1
        sbc KI,x
        sta RH,x
        bcc st_arrive
        lda ERR,x
        sbc REM+8,x
        bcc st1_wrap
        sta ERR,x
        lda POS_X,x
        adc VX+8,x
        sta POS_X,x
        lda POS_Y,x
        adc VY+8,x
        sta POS_Y,x
        clc
        rts
st1_wrap:
        adc DMAJ,x
        sta ERR,x
        lda POS_X,x
        adc VX+24,x
        sta POS_X,x
        lda POS_Y,x
        adc VY+24,x
        sta POS_Y,x
        clc
        rts
; ---------------------------------------------------------------------------
; seek8_init_euclid: IN_SP is the speed along the path.
; major speed = speed * cos(theta) = speed - speed*d/256, d = cos_d[q],
; q = min(31, floor(32*dmin/dmaj)).
; ---------------------------------------------------------------------------
seek8_init_euclid:
        jsr seek8_geometry
        bcc eu_moving
        rts
eu_moving:
        lda #$08                ; quotient sentinel: 5 rols push it into C
        sta T_U
        lda T_DMIN
eu_dloop:
        asl
        bcs eu_dsub
        cmp T_DMAJ
        bcc eu_dskip
eu_dsub:
        sbc T_DMAJ
        sec
eu_dskip:
        rol T_U
        bcc eu_dloop
        ldy T_U
        ; P = (speed * d) >> 8 in T_WHOLE:A. d leaves LSB first; the sentinel
        ; in bit 7 ends the loop after 8 shifts.
        lda cos_d,y
        sec
        ror
        sta T_U
        lda #0
        sta T_WHOLE
eu_mloop:
        bcc eu_mskip
        clc
        adc IN_SPL
        tay
        lda T_WHOLE
        adc IN_SPH
        sta T_WHOLE
        tya
eu_mskip:
        ror T_WHOLE
        ror
        lsr T_U
        bne eu_mloop
        sta T_U                 ; speed -= P
        lda IN_SPL
        sec
        sbc T_U
        sta IN_SPL
        lda IN_SPH
        sbc T_WHOLE
        sta IN_SPH
        jmp seek8_rates

; ---------------------------------------------------------------------------
; seek8_init: start moving slot X from POS_X/POS_Y to IN_X1/IN_Y1.
; ---------------------------------------------------------------------------
seek8_init:
        jsr seek8_geometry
        bcc seek8_rates
        rts

seek8_rates:
        lda IN_SPL
        sta KF,x
        lda IN_SPH
        sta KI,x
        ; rem0 = k0*dmin mod dmaj, whole0 = k0*dmin div dmaj (k0 rounds)
        lda #0
        sta T_WHOLE
        ldy IN_SPH
        beq rt0_done
rt0_loop:
        clc
        adc T_DMIN
        bcs rt0_sub
        cmp T_DMAJ
        bcc rt0_next
rt0_sub:
        sbc T_DMAJ              ; C=1 on both paths
        inc T_WHOLE
rt0_next:
        dey
        bne rt0_loop
rt0_done:
        sta REM,x
        ldy T_WHOLE             ; Y = whole0
        clc                     ; one more round for k0+1
        adc T_DMIN
        bcs rt1_sub
        cmp T_DMAJ
        bcc rt1_done
rt1_sub:
        sbc T_DMAJ
        inc T_WHOLE
rt1_done:
        sta REM+8,x
        ; signed deltas: v = (k eor m) - m, and k0+1 = k0 + (m or 1)
        lda T_MMAJ
        ora #1
        sta T_U
        lda IN_SPH
        eor T_MMAJ
        sec
        sbc T_MMAJ
        sta T_A0
        clc
        adc T_U
        sta T_A1
        lda T_MMIN
        ora #1
        sta T_U                 ; minor unit
        tya
        eor T_MMIN
        sec
        sbc T_MMIN
        sta T_B0
        lda T_WHOLE
        eor T_MMIN
        sec
        sbc T_MMIN
        sta T_B1
        ; Planes: VX = vx-1 and VY = vy + sign(vx-1), where sign = $FF/$00.
        bit T_MODE
        bmi rt_ymajor
        ; x major: vx = A_k in both wrap planes, vy = B_k (+unit on wrap)
        lda T_A0
        sec
        sbc #1
        sta VX,x
        sta VX+16,x
        ora #$7F
        bmi rt_x0
        lda #0
rt_x0:
        clc
        adc T_B0
        sta VY,x
        clc
        adc T_U
        sta VY+16,x
        lda T_A1                ; |vx| = k0+1 >= 1: sign(vx-1) = major mask
        sec
        sbc #1
        sta VX+8,x
        sta VX+24,x
        lda T_MMAJ
        clc
        adc T_B1
        sta VY+8,x
        clc
        adc T_U
        sta VY+24,x
        clc
        rts
rt_ymajor:
        ; y major: vy = A_k, vx = B_k (+unit on wrap)
        lda T_B0
        sec
        sbc #1
        sta VX,x
        ora #$7F
        bmi rt_y0
        lda #0
rt_y0:
        clc
        adc T_A0
        sta VY,x
        lda T_B0
        clc
        adc T_U
        sec
        sbc #1
        sta VX+16,x
        ora #$7F
        bmi rt_y1
        lda #0
rt_y1:
        clc
        adc T_A0
        sta VY+16,x
        lda T_B1
        sec
        sbc #1
        sta VX+8,x
        ora #$7F
        bmi rt_y2
        lda #0
rt_y2:
        clc
        adc T_A1
        sta VY+8,x
        lda T_B1
        clc
        adc T_U
        sec
        sbc #1
        sta VX+24,x
        ora #$7F
        bmi rt_y3
        lda #0
rt_y3:
        clc
        adc T_A1
        sta VY+24,x
        clc
        rts

; ---------------------------------------------------------------------------
; seek8_geometry: target, deltas, major/minor, err and R. C=1 if dmaj = 0.
; ---------------------------------------------------------------------------
seek8_geometry:
        lda #$FF
        sta RL,x
        ldy #0
        lda IN_Y1
        sta TGT_Y,x
        sec
        sbc POS_Y,x
        bcs geo_dy_pos
        eor #$FF
        adc #1                  ; C=0
        dey
geo_dy_pos:
        sta T_DMIN
        sty T_MMIN
        ldy #0
        lda IN_X1
        sta TGT_X,x
        sec
        sbc POS_X,x
        bcs geo_dx_pos
        eor #$FF
        adc #1
        dey
geo_dx_pos:
        sty T_MMAJ
        cmp T_DMIN
        bcs geo_xmajor
        ldy T_DMIN              ; y major: swap magnitudes and masks
        sta T_DMIN
        sty T_DMAJ
        lda T_MMAJ
        ldy T_MMIN
        sta T_MMIN
        sty T_MMAJ
        lda #$80
        sta T_MODE
        lda T_DMAJ
        bne geo_common          ; dmaj >= 1 here
geo_xmajor:
        sta T_DMAJ
        ldy #0
        sty T_MODE
geo_common:
        sta DMAJ,x
        lsr
        sta ERR,x
        lda T_DMAJ              ; RH = dmaj-1
        sec
        sbc #1
        sta RH,x
        bcc geo_zero
        clc
        rts
geo_zero:
        jmp arrived_state       ; C=1

; Euclidean correction: cos_d[q] = round(256*(1-cos(atan((q+0.5)/32))))
cos_d:
        !byte 0, 0, 1, 2, 2, 4, 5, 7
        !byte 9, 11, 13, 15, 18, 20, 23, 26
        !byte 28, 31, 34, 37, 40, 44, 47, 50
        !byte 53, 56, 59, 62, 65, 68, 71, 74
