# Issue144: V4 REU ISQRT32 masked-rotate source screen (research only)

This screen starts from the independently qualified canonical fast-four V4 REU ISQRT32 source and substitutes a single NMOS 6510 optimization **at exactly two** six-ASL address-index sites:

```asm
; After AND #$03 has clamped A to [0,3], replace
asl
asl
asl
asl
asl
asl
; with
lsr
ror
ror
and #$C0
```

All 256 possible input bytes were exhaustively screened **after** the existing `AND #$03`. The computed result, carry and N/Z flags match six ASLs for all cases; neither sequence modifies overflow V. Candidate instruction footprint changes from 6 to 5 bytes, and theoretical NMOS CPU cost changes from 12 to 8 cycles per occurrence; **8 cycles total is a hypothesis until the real source assembler, complete public call and VICE are tested**.

`tools/issue144_v4_isqrt_maskshift_source_native_qualify.py` builds exact reference/alternate layouts from original and candidate (in temporary checkouts), calls the ordinary V4 public ISQRT32 with existing 16 MiB REU data on thousands of deterministic 32-bit inputs, checks identical arithmetic/status/input/scratch and compares model cycles, then executes 24+24 real x64sc calls using the actual REU payload. It does not mutate reference PRGs/REUs, the canonical source or the production PERFORMANCE.md. Any gain is research-only until independent resource/layout/native qualification.

No private OptiSearch source is included.
