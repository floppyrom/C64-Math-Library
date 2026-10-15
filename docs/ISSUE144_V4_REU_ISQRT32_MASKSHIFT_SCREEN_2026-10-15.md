# Issue144: V4 REU ISQRT32 maskshift canonical-source trial (not a binary release)

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

All 256 possible input bytes were exhaustively screened **after** the existing `AND #$03`. The computed result, carry and N/Z flags match six ASLs for all cases; neither sequence modifies overflow V. Candidate instruction footprint changes from 6 to 5 bytes, and theoretical NMOS CPU cost changes from 12 to 8 cycles per occurrence; **8 cycles total were saved on every measured public call in the completed source-assembled CPU-model test**.

`tools/issue144_v4_isqrt_maskshift_source_native_qualify.py` builds exact reference/alternate layouts from original and candidate (in temporary checkouts), calls the ordinary V4 public ISQRT32 with existing 16 MiB REU data on thousands of deterministic 32-bit inputs, checks identical arithmetic/status/input/scratch and compares model cycles, then executes 24+24 real x64sc calls using the actual REU payload. It does not mutate reference PRGs/REUs, the canonical source or the production PERFORMANCE.md. Source integration is currently a qualified research trial: the unchanged fast-four source is pinned beside it for baseline qualification; source/public ABI and package gates are required before promotion.

No private OptiSearch source is included.

## Machine-assembled source and VICE proof

[Dedicated GitHub Actions run #38794656495](https://github.com/floppyrom/C64-Math-Library/actions/runs/38794656495) PASS: **2,109 paired unrestricted public V4 ISQRT32 calls**, exact results, exactly **8 modeled cycles saved** each (min/mean/p95), no slower cases, no volatile V flag change and preserved tracked state; reference/alternate V4 source builds PASS; **48 native VICE calls** with the original 16 MiB REU image PASS with byte-identical captured status/outputs. This trial now stages the improvement in **canonical source** with a pinned fast-four baseline; it is not a new PRG/REU binary release, and physical REU/VIC bus timing is not established.
