# Stock-C64 read-only signed 8×8 quarter-square alternative

The `SMUL8` public ABI reads X8 and Y8, returns signed16 Z0..Z1,
preserves public input bytes, Z2..Z3, unrelated memory and stack, and
clears C. A/X/Y are volatile and decimal mode must be disabled.

## Two historical-compatible candidates

| Option | Code + lookup bytes | Reserved RAM scratch | ZP | Writable code |
|---|---:|---:|---:|---|
| `link:v1-resident-smc` | 46 B code + 2,044 B tables | 0 B | 0 B | Yes |
| `link:qs-readonly` | 73 B code + 1,022 B tables + 64 B signed adapter slot | 2 B | 0 B | No |

The V1 source is **not modified**. It remains an original 46-byte
self-modifying kernel using the four original 511-entry pages, with a
page-aligned source-linked region. The new candidate source-links
the verified no-SMC unsigned UMUL8 quarter-square kernel and its
two exact 511-byte low/high planes, then applies the signed correction
to the high result byte. This is exact modulo 2^16:

```
signed(X8)*signed(Y8) = unsigned(X8)*unsigned(Y8)
                      - (X8_sign ? unsigned(Y8)<<8 : 0)
                      - (Y8_sign ? unsigned(X8)<<8 : 0)
```

The new image reserves 1,159 bytes of executable source plus immutable
tables, two scratch bytes, 0 ZP, and the common 32-byte public I/O
region. It is relocatable across two disjoint code and I/O origins.
No REU, SMC, hardware-specific ROM preloading, or initialization is
needed.

The new alternative is **not yet declared faster** than the canonical
SMC source. Qualification includes exhaustive 256×256 signed operand
pairs, unchanged-source checks, two memory maps, native VICE r46284,
a 512-pair same-public-call CPU-model comparison of mean/p95/max
cycles, a separate 150-call/24-frame busiest-math-frame comparison,
source provenance and RAM-budget enforcement. Neither trace is physical
PAL/VIC-II/IRQ timing; the new read-only source need not be the fastest. The operation-first builder now supports an authenticated-source speed
comparison for both candidates: 512 identical complete public calls,
including signed correction and SMC behavior, determine which fastest
candidate fits actual RAM/ZP budgets. This remains provisional until
complete source-model, native VICE and package qualification passes;
resident-only historical timings are never substituted.

The operation-first builder still needs a generalized accounting
mechanism to share tables when UMUL8 and the read-only SMUL8 are
selected together; independent source images are not automatically
equivalent to globally shared tables. The five original profiles,
their native SMC source and the old table bytes must remain available.
