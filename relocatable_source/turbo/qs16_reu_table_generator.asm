; Source-built QS16 REU table generator and guarded service dispatcher.
; Only a separately qualified INSTALL call may populate the 8-bank table.
; State and buffer locations supplied by the independent packaging linker.
; Q(n) = floor(n*n/4) emitted in four byte planes, 256 records per block.
; 512 blocks * 1024 bytes = 8 complete 64KiB banks (final unused entry).
; Every block is DMA-written and DMA-read back for byte-for-byte verification.
; The historical V4 .reu image is never loaded or used as a table fixture.

* = Q16_SERVICE_BASE
Q16_SWAP_BEGIN:
        lda Q16_ACTIVE
        beq Q16_BEGIN_FREE
        sec
        rts
Q16_BEGIN_FREE:
        jsr MATH_REU_QS16_BEGIN
        lda #$00
        sta $DF08
        sta $DF09
        lda #$01
        sta Q16_ACTIVE
        clc
        rts
Q16_SWAP_CALL:
        lda Q16_ACTIVE
        bne Q16_CALL_ACTIVE
        sec
        rts
Q16_CALL_ACTIVE:
        jmp MATH_REU_QS16
Q16_SWAP_END:
        lda Q16_ACTIVE
        bne Q16_END_ACTIVE
        sec
        rts
Q16_END_ACTIVE:
        jsr MATH_REU_QS16_END
        lda #$00
        sta Q16_ACTIVE
        clc
        rts

* = Q16_GENERATOR_BASE
Q16_GENERATE_TABLE:
        lda Q16_BUF_PTR
        sta Q16_SAVE_PTR0
        lda Q16_BUF_PTR+1
        sta Q16_SAVE_PTR1
        lda #$00
        sta Q16_Q0
        sta Q16_Q1
        sta Q16_Q2
        sta Q16_Q3
        sta Q16_HALF_LO
        sta Q16_HALF_HI
        sta Q16_PARITY
        sta Q16_REU_HIGH
        sta Q16_BLOCK_LO
        sta Q16_BLOCK_HI
        lda #REU_QS16_BASE_BANK
        sta Q16_REU_BANK
Q16_NEXT_BLOCK:
        lda #<Q16_DATA_BUFFER
        sta Q16_BUF_PTR
        lda #>Q16_DATA_BUFFER
        sta Q16_BUF_PTR+1
        ldx #$04
Q16_RECORD_PAGE:
        ldy #$00
Q16_NEXT_RECORD:
        ; Interleave four little-endian bytes for each record, not
        ; four separate 256-byte value planes.
        lda Q16_Q0
        sta (Q16_BUF_PTR),y
        iny
        lda Q16_Q1
        sta (Q16_BUF_PTR),y
        iny
        lda Q16_Q2
        sta (Q16_BUF_PTR),y
        iny
        lda Q16_Q3
        sta (Q16_BUF_PTR),y
        iny
        ; Increment by floor((n+1)/2). On every second record increase
        ; the 16-bit half increment, then add it to the 32-bit Q(n).
        lda Q16_PARITY
        eor #$01
        sta Q16_PARITY
        bne Q16_HALF_READY
        inc Q16_HALF_LO
        bne Q16_HALF_READY
        inc Q16_HALF_HI
Q16_HALF_READY:
        clc
        lda Q16_Q0
        adc Q16_HALF_LO
        sta Q16_Q0
        lda Q16_Q1
        adc Q16_HALF_HI
        sta Q16_Q1
        lda Q16_Q2
        adc #$00
        sta Q16_Q2
        lda Q16_Q3
        adc #$00
        sta Q16_Q3
        tya
        beq Q16_PAGE_DONE
        jmp Q16_NEXT_RECORD
Q16_PAGE_DONE:
        inc Q16_BUF_PTR+1
        dex
        beq Q16_UPLOAD_BLOCK
        jmp Q16_RECORD_PAGE

Q16_UPLOAD_BLOCK:
        lda #<Q16_DATA_BUFFER
        sta $DF02
        lda #>Q16_DATA_BUFFER
        sta $DF03
        lda #$00
        sta $DF04
        lda Q16_REU_HIGH
        sta $DF05
        lda Q16_REU_BANK
        sta $DF06
        lda #$00
        sta $DF07
        lda #$04
        sta $DF08
        lda #$00
        sta $DF09
        sta $DF0A
        lda #$90
        sta $DF01

        ; Re-fetch the same REU region into a second, independently
        ; owned buffer to check the physical DMA and actual data bytes.
        lda #<Q16_VERIFY_BUFFER
        sta $DF02
        lda #>Q16_VERIFY_BUFFER
        sta $DF03
        lda #$00
        sta $DF04
        lda Q16_REU_HIGH
        sta $DF05
        lda Q16_REU_BANK
        sta $DF06
        lda #$00
        sta $DF07
        lda #$04
        sta $DF08
        lda #$00
        sta $DF09
        sta $DF0A
        lda #$91
        sta $DF01

        ldy #$00
Q16_VERIFY_NEXT:
        lda Q16_DATA_BUFFER,y
        cmp Q16_VERIFY_BUFFER,y
        bne Q16_VERIFY_FAILED
        lda Q16_DATA_BUFFER+$0100,y
        cmp Q16_VERIFY_BUFFER+$0100,y
        bne Q16_VERIFY_FAILED
        lda Q16_DATA_BUFFER+$0200,y
        cmp Q16_VERIFY_BUFFER+$0200,y
        bne Q16_VERIFY_FAILED
        lda Q16_DATA_BUFFER+$0300,y
        cmp Q16_VERIFY_BUFFER+$0300,y
        bne Q16_VERIFY_FAILED
        iny
        bne Q16_VERIFY_NEXT
        jmp Q16_NEXT_TRANSFER
Q16_VERIFY_FAILED:
        lda Q16_SAVE_PTR0
        sta Q16_BUF_PTR
        lda Q16_SAVE_PTR1
        sta Q16_BUF_PTR+1
        sec
        rts

Q16_NEXT_TRANSFER:
        clc
        lda Q16_REU_HIGH
        adc #$04
        sta Q16_REU_HIGH
        bcc Q16_BANK_OK
        inc Q16_REU_BANK
Q16_BANK_OK:
        inc Q16_BLOCK_LO
        bne Q16_DO_NEXT
        inc Q16_BLOCK_HI
        lda Q16_BLOCK_HI
        cmp #$02
        beq Q16_GENERATE_DONE
Q16_DO_NEXT:
        jmp Q16_NEXT_BLOCK

Q16_GENERATE_DONE:
        lda Q16_SAVE_PTR0
        sta Q16_BUF_PTR
        lda Q16_SAVE_PTR1
        sta Q16_BUF_PTR+1
        ; Original QS16 routine expects DMA C64 address at its 4-byte
        ; scratch area, and REU length high=0 for four-byte fetches.
        lda #<REU_SCRATCH
        sta $DF02
        lda #>REU_SCRATCH
        sta $DF03
        lda #$00
        sta $DF04
        sta $DF05
        sta $DF08
        sta $DF09
        sta $DF0A
        clc
        rts
