; ============================================================================
; Firemonger C64 Math API v3 REU-Pareto — public symbols
; ============================================================================
; Target: NMOS 6502/6510, D=0.
; Public operand/result vectors live in ordinary RAM at MATH_IO_BASE ($C000 in
; the reference build).  Internal kernels use $02-$38 and are non-reentrant.
;
; Public status contract:
;   UMUL: C=0 on return.
;   UDIV/UMOD: C=0 success; C=1 divisor zero, result/remainder zero.
; A/X/Y are caller-clobbered. Public input vectors are preserved.
;
; IMPORTANT: MATH_INIT is mandatory. In addition to the v2 persistent multiplier
; state, it configures the REU one-byte lookup destination/length/address mode.
; v3 requires a 512 KiB-compatible REU image from reu/c64_math_v3_512k.reu.
; The normal API remains sequential/non-reentrant. Turbo overlay modes are explicit
; batch contracts and temporarily own their documented zero-page ranges.
; ============================================================================

; C64 Math API v3 REU-Pareto — public symbols
; Ordinary-RAM public IO; internal kernels use initialized ZP $02-$38 non-reentrantly.

MATH_IO_BASE = $c000

math_x0 = MATH_IO_BASE+$00
math_x1 = MATH_IO_BASE+$01
math_x2 = MATH_IO_BASE+$02
math_x3 = MATH_IO_BASE+$03
math_y0 = MATH_IO_BASE+$04
math_y1 = MATH_IO_BASE+$05
math_y2 = MATH_IO_BASE+$06
math_y3 = MATH_IO_BASE+$07
math_z0 = MATH_IO_BASE+$08
math_z1 = MATH_IO_BASE+$09
math_z2 = MATH_IO_BASE+$0a
math_z3 = MATH_IO_BASE+$0b
math_z4 = MATH_IO_BASE+$0c
math_z5 = MATH_IO_BASE+$0d
math_z6 = MATH_IO_BASE+$0e
math_z7 = MATH_IO_BASE+$0f
math_n0 = MATH_IO_BASE+$10
math_n1 = MATH_IO_BASE+$11
math_n2 = MATH_IO_BASE+$12
math_n3 = MATH_IO_BASE+$13
math_d0 = MATH_IO_BASE+$14
math_d1 = MATH_IO_BASE+$15
math_d2 = MATH_IO_BASE+$16
math_d3 = MATH_IO_BASE+$17
math_q0 = MATH_IO_BASE+$18
math_q1 = MATH_IO_BASE+$19
math_q2 = MATH_IO_BASE+$1a
math_q3 = MATH_IO_BASE+$1b
math_r0 = MATH_IO_BASE+$1c
math_r1 = MATH_IO_BASE+$1d
math_r2 = MATH_IO_BASE+$1e
math_r3 = MATH_IO_BASE+$1f

; Public entry points (filled by math_resident.asm layout)
MATH_UMUL8      = $3000
MATH_UMUL16     = $3020
MATH_UMUL24     = $3060
MATH_UMUL32     = $30b0
MATH_UMUL32_READY = $30c0
MATH_UDIV8      = $3120
MATH_UDIV16     = $3140
MATH_UDIV24     = $3170
MATH_UDIV32_16  = $31b0
MATH_UMOD8      = $3200
MATH_UMOD16     = $3220
MATH_UMOD24     = $3223
MATH_UMOD32_16  = $3226
MATH_Z16_TO_N32 = $3230
MATH_Z32_TO_N32 = $3250
MATH_Q32_TO_X32 = $3260
MATH_R16_TO_X16 = $3270
MATH_INIT        = $3280

MATH_ZP_FIRST = $02
MATH_ZP_LAST  = $38
MATH_ZP_BYTES = 55
MATH_CHAIN_UMUL16_UDIV32_16 = $3300
MATH_CHAIN_UDIV16_UMUL16    = $3330
MATH_CHAIN_UDIV24_UMUL24    = $3360
MATH_CHAIN_UDIV32_16_UMUL32 = $33a0

api_zp_start=$02
api_zp_end=$39

; --- REU v3 extensions -------------------------------------------------------
MATH_REU_UMUL16_BEGIN = $3800
MATH_REU_UMUL16       = $3840
MATH_REU_UMUL16_END   = $3880
MATH_REU_UMUL32_BEGIN = $38c0
MATH_REU_UMUL32       = $3900
MATH_REU_UMUL32_END   = $3960
MATH_REU_LOOKUP_INIT  = $39a0
MATH_REU_BYTE         = $c020
; Turbo16 owns $003e-$00ae while active. Resident wide calls that do not use
; the REU lookup transport may coexist; do not call default UMUL8/UMUL16,
; UDIV8, or UMOD8 until Turbo16 END restores lookup mode.
; Turbo32 owns the configured 135-byte ZP range (reference $000a-$0090) and is an exclusive math mode.

; ---------------------------------------------------------------------------
; Signed API extension (2026-09-05 complete release)
; Two's-complement signed values, same public I/O vectors as unsigned calls.
; Stable signed entry addresses; FINAL implementations are profile-specific native paths.
MATH_SMUL8       = $3b80
MATH_SMUL16      = $3bb0
MATH_SMUL24      = $3bf0
MATH_SMUL32      = $3c40
MATH_SDIV8       = $3ca0
MATH_SDIV16      = $3d20
MATH_SDIV24      = $3de0
MATH_SDIV32_16   = $3ee0
MATH_SMOD8       = $3fd4
MATH_SMOD16      = $3fd7
MATH_SMOD24      = $3fda
MATH_SMOD32_16   = $3fdd
MATH_SMUL32_READY = $3fe0
; Legacy compatibility-build aliases retained for source compatibility; FINAL native code does not use them.
MATH_SIGNED_SCRATCH_FIRST = $c040
MATH_SIGNED_SCRATCH_LAST  = $c049
MATH_SIGNED_SCRATCH_BYTES = 10


; ---------------------------------------------------------------------------
; Game / fixed-point math extension (2026-09-06)
; Stable 3-byte JMP ABI slots shared by V1-V4.
MATH_UDIV32_32       = $5e00
MATH_UMOD32_32       = $5e03
MATH_SDIV32_32       = $5e06
MATH_SMOD32_32       = $5e09
; Explicit divmod aliases: divide entries already return both Q and R.
MATH_UDIVMOD32_32    = MATH_UDIV32_32
MATH_SDIVMOD32_32    = MATH_SDIV32_32
MATH_UMUL16_SHR8     = $5e0c
MATH_SMUL16_SHR8     = $5e0f
MATH_UMUL32_SHR16    = $5e12
MATH_SMUL32_SHR16    = $5e15
MATH_UDIV16_SHL8     = $5e18
MATH_SDIV16_SHL8     = $5e1b
MATH_URECIP16_Q16    = $5e1e
MATH_SIN8             = $5e21
MATH_COS8             = $5e24
MATH_SINCOS8          = $5e27
MATH_ATAN2_8          = $5e2a
MATH_ISQRT16          = $5e2d
MATH_ISQRT32          = $5e30
MATH_DIST8_FAST       = $5e33
MATH_DIST8_ACCURATE   = $5e36
MATH_GAME_SCRATCH_FIRST = $53
MATH_GAME_SCRATCH_LAST  = $6a
MATH_GAME_SCRATCH_BYTES = 24
; $53-$6A is available in normal resident mode but lies inside Turbo16/Turbo32 overlay ownership.
; Do not call game-math entries between REU Turbo BEGIN and END.
