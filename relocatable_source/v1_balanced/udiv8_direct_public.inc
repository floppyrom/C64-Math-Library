; V1 Balanced direct UDIV8, 256-class speed/space knee.
; Exhaustive unsigned core provenance; direct stable-memory ABI.
DU8B_n = MATH_N
DU8B_d = MATH_D
DU8B_q = MATH_Q
DU8B_r = MATH_R
DU8B_sd = ZP_MAIN+$0E

* = MATH_UDIV8
    jmp DU8B_div_u8

;ABI
;CPU: mos6502
;Operation: udiv
;Entry: DU8B_div_u8
;Input DU8B_n: uint8 = DU8B_n
;Input DU8B_d: uint8 = DU8B_d
;Output DU8B_q: uint8 = DU8B_q
;Remainder DU8B_r: uint8 = DU8B_r
;UDiv DU8B_zero remainder: DU8B_zero
;Region ZP: cg_zp_start..cg_zp_end
;Region Code: DU8B_cg_code_start..DU8B_cg_code_end
;End ABI
; ============================================================================
; FIREMONGER C64 DIVISION REFERENCE — PUBLICATION COPY
; Family       : udiv8
; Tier         : 256-class
; Target       : NMOS 6502/6510, decimal mode clear
; Measurement  : exhaustive 65,536-pair space; seed $C0FFEE where random
; Timing       : entry instruction through final RTS; caller JSR excluded
; Avg cycles   : 47.858444
; Min / Max    : 20 / 494
; Stddev       : 59.490569
; Resident     : 230 bytes (Code 230 + Data 0); ZP 5 bytes separate
; Validation   : 65536 cases, 0 errors
; Edge suite   : 603 cases in canonical run, 0 errors
; Architecture : Residual shifted-divisor DU8B_tail after a small quotient bias; strong sub-256-byte point.
;
; NOTE: this publication block is comments only and does not alter the exact
; assembled image that produced the result. Raw canonical JSON is supplied
; beside the source when available. See TECHNICAL_ASSESSMENT.md for caveats.
; ============================================================================
* = REG_KERNEL
DU8B_cg_code_start:
DU8B_zero:
 sta DU8B_q
 sta DU8B_r
 sec
 rts
DU8B_div_u8:
 lda DU8B_d
 beq DU8B_zero
 lda DU8B_n
 cmp DU8B_d
 bcs DU8B_cont0
 sta DU8B_r
 lda #0
 sta DU8B_q
 rts
DU8B_cont0:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont1
 sta DU8B_r
 lda #1
 sta DU8B_q
 rts
DU8B_cont1:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont2
 sta DU8B_r
 lda #2
 sta DU8B_q
 rts
DU8B_cont2:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont3
 sta DU8B_r
 lda #3
 sta DU8B_q
 rts
DU8B_cont3:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont4
 sta DU8B_r
 lda #4
 sta DU8B_q
 rts
DU8B_cont4:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont5
 sta DU8B_r
 lda #5
 sta DU8B_q
 rts
DU8B_cont5:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont6
 sta DU8B_r
 lda #6
 sta DU8B_q
 rts
DU8B_cont6:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont7
 sta DU8B_r
 lda #7
 sta DU8B_q
 rts
DU8B_cont7:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont8
 sta DU8B_r
 lda #8
 sta DU8B_q
 rts
DU8B_cont8:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont9
 sta DU8B_r
 lda #9
 sta DU8B_q
 rts
DU8B_cont9:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont10
 sta DU8B_r
 lda #10
 sta DU8B_q
 rts
DU8B_cont10:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_cont11
 sta DU8B_r
 lda #11
 sta DU8B_q
 rts
DU8B_cont11:
 sbc DU8B_d
 cmp DU8B_d
 bcs DU8B_tail
 sta DU8B_r
 lda #12
 sta DU8B_q
 rts
DU8B_tail:
 sta DU8B_r
 lda DU8B_d
 sta DU8B_sd
 ldx #0
 stx DU8B_q
DU8B_align:
 lda DU8B_sd
 asl
 bcs DU8B_aligned
 cmp DU8B_r
 bcc DU8B_take
 beq DU8B_take
DU8B_aligned:
 lda DU8B_r
DU8B_bits:
 cmp DU8B_sd
 bcc DU8B_no_sub
 sbc DU8B_sd
DU8B_no_sub:
 rol DU8B_q
 lsr DU8B_sd
 dex
 bpl DU8B_bits
 sta DU8B_r
 lda DU8B_q
 clc
 adc #12
 sta DU8B_q
 rts
DU8B_take:
 sta DU8B_sd
 inx
 bne DU8B_align
DU8B_cg_code_end:
