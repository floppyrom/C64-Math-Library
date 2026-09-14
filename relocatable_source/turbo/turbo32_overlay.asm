; Turbo32 stack-free 135-byte ZP overlay.
; Derived from the fully-qualified umul32_ram135 record-family implementation.
; Qualification source: UMUL16_UMUL32_LOW_ZP_IMPROVEMENTS (2026-09-10).
; Native candidate result: 614.275858 measured mean cycles on 67,108,864 pairs.
; This library adaptation keeps the candidate's executable/data ZP geometry but
; relocates its two ordinary-RAM helper blocks to REG_LOW and REG_LOW+$0100 and
; reuses the resident quarter-square planes at REG_TABLE+$1000/$1200/$1400/$1600.
; It reserves no hardware-stack-page bytes. BEGIN/END swap exactly 135 ZP bytes.
; TURBO32_ZP_BASE may be $02..$79; $00-$01 remain reserved for the 6510 port.

sqr_lo=REG_TABLE+$1000
sqr_hi=REG_TABLE+$1200
neg_lo=REG_TABLE+$1400
neg_hi=REG_TABLE+$1600
summation=REG_LOW+$0100
z00=TURBO32_ZP_BASE+$00
z10=TURBO32_ZP_BASE+$01
z20=TURBO32_ZP_BASE+$02
z30=TURBO32_ZP_BASE+$03
z01=TURBO32_ZP_BASE+$04
z11=TURBO32_ZP_BASE+$05
z21=TURBO32_ZP_BASE+$06
z31=TURBO32_ZP_BASE+$07
z02=TURBO32_ZP_BASE+$08
z12=TURBO32_ZP_BASE+$09
z22=TURBO32_ZP_BASE+$0a
z32=TURBO32_ZP_BASE+$0b
z03=TURBO32_ZP_BASE+$0c
z13=TURBO32_ZP_BASE+$0d
z23=TURBO32_ZP_BASE+$0e
z33=TURBO32_ZP_BASE+$0f
z14=TURBO32_ZP_BASE+$10
z24=TURBO32_ZP_BASE+$11
z34=TURBO32_ZP_BASE+$12
y0=TURBO32_ZP_BASE+$00
y1=TURBO32_ZP_BASE+$01
y2=TURBO32_ZP_BASE+$02
r0=TURBO32_ZP_BASE+$00
r1=TURBO32_ZP_BASE+$01
r2=TURBO32_ZP_BASE+$02
r3=TURBO32_ZP_BASE+$03
r7=TURBO32_ZP_BASE+$12

* = TURBO32_ZP_BASE
!byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00
* = TURBO32_ZP_BASE+$13
cg_zp_code_start
p1_carry:
        clc
                adc (NL1),y
                sta+1 z01-1,x
                lda #1
                adc (SH1),y
                adc (NH1),y
                adc (SL2),y
                bcc p2_hot
p2_carry:
        clc
                adc (NL2),y
                sta+1 z02-1,x
                lda #1
                adc (SH2),y
                adc (NH2),y
                adc (SL3),y
                bcc p3_hot
p3_carry:
        clc
                adc (NL3),y
                sta+1 z03-1,x
                lda #1
                adc (SH3),y
                adc (NH3),y
                dex
                beq sum_trampoline
loop:
        sta+1 z14-1,x
                ldy+1 y0-1,x

umult32x8_same_x
x0=*+1
        lda sqr_lo,y
NL0=*+1
        adc neg_lo,y
                sta+1 z00-1,x
SH0=*+1
        lda sqr_hi,y
NH0=*+1
        adc neg_hi,y
x1=*+1
        adc sqr_lo,y
                bcs p1_carry
p1_hot:
NL1=*+1
        adc neg_lo,y
                sta+1 z01-1,x
SH1=*+1
        lda sqr_hi,y
NH1=*+1
        adc neg_hi,y
x2=*+1
SL2=*+1
        adc sqr_lo,y
                bcs p2_carry
p2_hot:
NL2=*+1
        adc neg_lo,y
                sta+1 z02-1,x
SH2=*+1
        lda sqr_hi,y
NH2=*+1
        adc neg_hi,y
x3=*+1
SL3=*+1
        adc sqr_lo,y
                bcs p3_carry
p3_hot:
NL3=*+1
        adc neg_lo,y
                sta+1 z03-1,x
SH3=*+1
        lda sqr_hi,y
NH3=*+1
        adc neg_hi,y
                dex
                bne loop

sum_trampoline
                jmp summation
cg_zp_end
