; C64 Math Library Issue #144: V2-only exclusive UMUL32_SHR16 batch overlay.
; RESEARCH/OPT-IN ONLY. Not a replacement for the ordinary resident library.
;
; Preconditions:
;  * Exact stock V2 public resident image, SHA verified by the builder
;  * MATH_INIT already called; C64 RAM visible at $5805-$594A and $C4E3
;  * No call to MATH_UMUL32 or anything sharing its producer until END
;  * No IRQ/NMI/other task invokes the shared producer during the patch
;
; BEGIN and END patch 13 existing executable bytes. They use no ZP,
; preserve the processor stack and never touch public input bytes.
; For ordinary $5E12 MATH_UMUL32_SHR16, the altered common producer
; writes the six requested bytes directly into $C008-$C00D.
; This implementation's ordinary UMUL32 core is NOT valid while installed.
;
; Exact source/byte verification and reproducible CPU-model/native checks:
; tools/issue144_shr16_direct_slice_overlay_research.py
; tools/qualify_issue144_v2_shr16_batch.py
; tools/native_issue144_shr16_overlay.py
;
; The caller may relocate ORG if $0900 is occupied.
!cpu 6510
* = $0900

MUL32_SHR16_BEGIN:
    lda #$ea
    sta $586e
    sta $586f
    sta $5870
    sta $58c8
    sta $58c9
    lda #$18
    sta $58c7
    lda #$4c
    sta $c4e3
    lda #$08
    sta $587f
    lda #$09
    sta $5894
    lda #$0a
    sta $58a8
    lda #$0b
    sta $58b5
    lda #$0c
    sta $58bc
    lda #$0d
    sta $58c3
    rts

MUL32_SHR16_END:
    lda #$8d
    sta $586e
    sta $58c7
    lda #$09
    sta $586f
    lda #$08
    sta $58c8
    lda #$c0
    sta $5870
    sta $58c9
    lda #$20
    sta $c4e3
    lda #$0a
    sta $587f
    lda #$0b
    sta $5894
    lda #$0c
    sta $58a8
    lda #$0d
    sta $58b5
    lda #$0e
    sta $58bc
    lda #$0f
    sta $58c3
    rts
