# Issue #144 — unrestricted UDIV32/16 shared-subtraction source trial

This is an **opt-in source-only trial**, not a change to the five shipped resident PRGs, REU images, ABI, or the default builder. It is independently authored and keeps private OptiSearch source out of this repository.

The candidate is a complete copy of the common V2/V3/V4 split-direct UDIV32/16 source. Sixteen repeated tail digit blocks share the subtraction path between the ordinary accepted comparison and the 17-bit-overflow-forced subtraction. Each step explicitly sets carry after a successful take. Original output, divide-by-zero, byte-divisor routing, highword division, and public alias behavior remain unchanged.

Research on an archived 8 October source snapshot: 10,735 paired full public V2 calls, alternating `MATH_UDIV32_16` and `MATH_UMOD32_16`, correctly produced Q32/R16/C and preserved N/D. The mean saving was **6.3371 cycles** over all test calls and **6.7192 cycles** on 5,000 unrestricted uniform calls; worst observed slowdown **1 cycle**. The unrolled routine removes 192 compiled bytes from the main tail in the isolated model, but **normal five-profile footprint, production binary reproducibility and live current-main native VICE integration remain separate gates**.

A V2 full-public 16-call native VICE proof on the archived source-build passed. It is not evidence of full current-main promotion; the dedicated CI workflow below rebuilds V2–V4 reference and alternate maps from the current repository for reproducible public-ABI verification.

To reproduce locally **in a disposable checkout**, replace `relocatable_source/division/udiv32_16_split_direct.inc` with `optional/issue144_u3216_sharedtake_fullwidth/udiv32_16_sharedtake.inc`, then execute:

```bash
make reference alternate
python3 tools/validate_udiv32_16_integrated.py
```

Never modify the default compiled binaries without complete five-profile ABI, resource, mixed-call, REU and reproducible benchmark qualification, plus regenerated release artifacts. See issue #144 family B.
