# Issue #39 — V1 24/8 shared-subtraction release (2026-10-12)

The V1 Balanced exact 24-by-8 kernel at REG_LOW+$0D00 now shares a carry-aware subtraction path. It shrinks from **84 to 69 bytes** (15 unused bytes zero-filled). No additional ZP/stack, API address, or resident size growth. V2–V5 executables are unchanged.

On the official same-input corpus: **UDIV24 170.726699 → 170.238165**, **UMOD24 248.317450 → 246.822279** mean 6502 instruction cycles. The independent public-entry 48,388-call old/new comparison, including the D8 stress and wide-divisor control workloads, had **zero slower calls** and checked Q/R/C, input sentinels and stack balance. Full validation: 822,050 unsigned, 364,533 signed, 136,335 comparable and 53,760 workload-conditioned calls, all correct. A separate native x64sc old/new campaign successfully checked **256 public calls** for Q/R/C; no native timing claim. Refer to the preserved standalone test procedure and Issue #39 screening PR #77 for reproducing the public paired timings.

Source: relocatable_source/v1_balanced/udiv24_latency_escape_balanced.inc. Generated canonical source, V1 binary and standalone mirrors are released together. This is one improvement; Issue #39 unsigned DIV/MOD campaign **remains open**.
