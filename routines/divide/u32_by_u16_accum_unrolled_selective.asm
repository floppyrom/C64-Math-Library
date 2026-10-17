; Experimental *zero-ZP* public 32/16 shared quotient/remainder producer.
; 32 iterations of the qualified accumulator-remainder core are statically
; unrolled, eliminating all 32 loop counter decrements and back-branches.
; There is no core algorithm change, no table, no SMC, no extra private RAM.
; Source-only research until native VICE + fair 384-input benchmarks qualify.
; Zero-ZP shared public 32/16 DIV/MOD using A as remainder high byte.
; Independent RAM-only candidate, NOT the historical resident speed producer.
; 32/16 unsigned N/D preserved. Both entries write Q32 and R16.
; On D=0: Q32=R16=0, C=1. Otherwise C=0. D=0 (CLD) required.
; One byte TEMP_RAM stores low remainder; high is kept live in A.
; Does not use tables, REU, undocumented opcodes or self-modifying code.
!cpu 6510
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
TEMP_RAM = $C020
R0 = TEMP_RAM
* = KERNEL_CODE
FAST_UDIV32_16_ACCUM:
FAST_UMOD32_16_ACCUM:
    lda INPUT_DIV
    ora INPUT_DIV+1
    bne DIV_NONZERO
    jmp DIV_ZERO
DIV_NONZERO:
    lda INPUT_NUM+0
    sta OUTPUT_QUOT+0
    lda INPUT_NUM+1
    sta OUTPUT_QUOT+1
    lda INPUT_NUM+2
    sta OUTPUT_QUOT+2
    lda INPUT_NUM+3
    sta OUTPUT_QUOT+3
    lda #0
    sta R0
DIV_LOOP_0:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_0
    cmp INPUT_DIV+1
    bcc DIV_SKIP_0
    bne DIV_TAKE_0
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_0
DIV_TAKE_0:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_0:
DIV_LOOP_1:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_1
    cmp INPUT_DIV+1
    bcc DIV_SKIP_1
    bne DIV_TAKE_1
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_1
DIV_TAKE_1:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_1:
DIV_LOOP_2:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_2
    cmp INPUT_DIV+1
    bcc DIV_SKIP_2
    bne DIV_TAKE_2
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_2
DIV_TAKE_2:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_2:
DIV_LOOP_3:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_3
    cmp INPUT_DIV+1
    bcc DIV_SKIP_3
    bne DIV_TAKE_3
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_3
DIV_TAKE_3:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_3:
DIV_LOOP_4:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_4
    cmp INPUT_DIV+1
    bcc DIV_SKIP_4
    bne DIV_TAKE_4
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_4
DIV_TAKE_4:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_4:
DIV_LOOP_5:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_5
    cmp INPUT_DIV+1
    bcc DIV_SKIP_5
    bne DIV_TAKE_5
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_5
DIV_TAKE_5:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_5:
DIV_LOOP_6:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_6
    cmp INPUT_DIV+1
    bcc DIV_SKIP_6
    bne DIV_TAKE_6
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_6
DIV_TAKE_6:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_6:
DIV_LOOP_7:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_7
    cmp INPUT_DIV+1
    bcc DIV_SKIP_7
    bne DIV_TAKE_7
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_7
DIV_TAKE_7:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_7:
DIV_LOOP_8:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_8
    cmp INPUT_DIV+1
    bcc DIV_SKIP_8
    bne DIV_TAKE_8
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_8
DIV_TAKE_8:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_8:
DIV_LOOP_9:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_9
    cmp INPUT_DIV+1
    bcc DIV_SKIP_9
    bne DIV_TAKE_9
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_9
DIV_TAKE_9:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_9:
DIV_LOOP_10:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_10
    cmp INPUT_DIV+1
    bcc DIV_SKIP_10
    bne DIV_TAKE_10
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_10
DIV_TAKE_10:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_10:
DIV_LOOP_11:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_11
    cmp INPUT_DIV+1
    bcc DIV_SKIP_11
    bne DIV_TAKE_11
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_11
DIV_TAKE_11:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_11:
DIV_LOOP_12:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_12
    cmp INPUT_DIV+1
    bcc DIV_SKIP_12
    bne DIV_TAKE_12
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_12
DIV_TAKE_12:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_12:
DIV_LOOP_13:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_13
    cmp INPUT_DIV+1
    bcc DIV_SKIP_13
    bne DIV_TAKE_13
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_13
DIV_TAKE_13:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_13:
DIV_LOOP_14:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_14
    cmp INPUT_DIV+1
    bcc DIV_SKIP_14
    bne DIV_TAKE_14
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_14
DIV_TAKE_14:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_14:
DIV_LOOP_15:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_15
    cmp INPUT_DIV+1
    bcc DIV_SKIP_15
    bne DIV_TAKE_15
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_15
DIV_TAKE_15:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_15:
DIV_LOOP_16:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_16
    cmp INPUT_DIV+1
    bcc DIV_SKIP_16
    bne DIV_TAKE_16
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_16
DIV_TAKE_16:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_16:
DIV_LOOP_17:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_17
    cmp INPUT_DIV+1
    bcc DIV_SKIP_17
    bne DIV_TAKE_17
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_17
DIV_TAKE_17:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_17:
DIV_LOOP_18:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_18
    cmp INPUT_DIV+1
    bcc DIV_SKIP_18
    bne DIV_TAKE_18
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_18
DIV_TAKE_18:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_18:
DIV_LOOP_19:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_19
    cmp INPUT_DIV+1
    bcc DIV_SKIP_19
    bne DIV_TAKE_19
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_19
DIV_TAKE_19:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_19:
DIV_LOOP_20:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_20
    cmp INPUT_DIV+1
    bcc DIV_SKIP_20
    bne DIV_TAKE_20
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_20
DIV_TAKE_20:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_20:
DIV_LOOP_21:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_21
    cmp INPUT_DIV+1
    bcc DIV_SKIP_21
    bne DIV_TAKE_21
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_21
DIV_TAKE_21:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_21:
DIV_LOOP_22:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_22
    cmp INPUT_DIV+1
    bcc DIV_SKIP_22
    bne DIV_TAKE_22
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_22
DIV_TAKE_22:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_22:
DIV_LOOP_23:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_23
    cmp INPUT_DIV+1
    bcc DIV_SKIP_23
    bne DIV_TAKE_23
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_23
DIV_TAKE_23:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_23:
DIV_LOOP_24:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_24
    cmp INPUT_DIV+1
    bcc DIV_SKIP_24
    bne DIV_TAKE_24
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_24
DIV_TAKE_24:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_24:
DIV_LOOP_25:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_25
    cmp INPUT_DIV+1
    bcc DIV_SKIP_25
    bne DIV_TAKE_25
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_25
DIV_TAKE_25:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_25:
DIV_LOOP_26:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_26
    cmp INPUT_DIV+1
    bcc DIV_SKIP_26
    bne DIV_TAKE_26
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_26
DIV_TAKE_26:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_26:
DIV_LOOP_27:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_27
    cmp INPUT_DIV+1
    bcc DIV_SKIP_27
    bne DIV_TAKE_27
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_27
DIV_TAKE_27:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_27:
DIV_LOOP_28:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_28
    cmp INPUT_DIV+1
    bcc DIV_SKIP_28
    bne DIV_TAKE_28
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_28
DIV_TAKE_28:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_28:
DIV_LOOP_29:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_29
    cmp INPUT_DIV+1
    bcc DIV_SKIP_29
    bne DIV_TAKE_29
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_29
DIV_TAKE_29:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_29:
DIV_LOOP_30:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_30
    cmp INPUT_DIV+1
    bcc DIV_SKIP_30
    bne DIV_TAKE_30
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_30
DIV_TAKE_30:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_30:
DIV_LOOP_31:
    clc
    rol OUTPUT_QUOT+0
    rol OUTPUT_QUOT+1
    rol OUTPUT_QUOT+2
    rol OUTPUT_QUOT+3
    rol R0
    rol a
    bcs DIV_TAKE_31
    cmp INPUT_DIV+1
    bcc DIV_SKIP_31
    bne DIV_TAKE_31
    tay
    lda R0
    cmp INPUT_DIV
    tya
    bcc DIV_SKIP_31
DIV_TAKE_31:
    tay
    lda R0
    sbc INPUT_DIV
    sta R0
    tya
    sbc INPUT_DIV+1
    inc OUTPUT_QUOT+0
DIV_SKIP_31:
    ldx #0
    sta OUTPUT_REM+1
    lda R0
    sta OUTPUT_REM+0
    clc
    rts
DIV_ZERO:
    lda #0
    sta OUTPUT_QUOT+0
    sta OUTPUT_QUOT+1
    sta OUTPUT_QUOT+2
    sta OUTPUT_QUOT+3
    sta OUTPUT_REM+0
    sta OUTPUT_REM+1
    sec
    rts
