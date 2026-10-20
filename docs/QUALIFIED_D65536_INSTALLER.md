# Optional D=$00010000 fast-path variants in the operation-first installer

The operation-first source-selecting linker now exposes
`link:d65536-hybrid` as an **independently linkable, source-authenticated,
opt-in Pareto alternative** for `MATH_UDIV32_32`, `MATH_UMOD32_32`,
`MATH_SDIV32_32` and `MATH_SMOD32_32`. The signed and unsigned pairs
share one physical source image within each pair; they are independently
instantiable, and retain the historical V2 producers and portable variants.

For exact **unsigned magnitude** divisor `$00010000`, the producer sets
`Q=N>>16`, `R=N&$FFFF` and carry clear. Signed operations normalize
N/D and restore the quotient/remainder signs. All other divisors retain
the original source-qualified V2 32/16 narrow-divisor and unrestricted
32/32 fallback arithmetic. Divisor zero maintains the original C=1 and
Q/R contract. The entire 32-bit Q32/R32/C and N/D preservation are checked
for each public call at two relocations.

## Example explicit selection

Only use the additional RAM when that trade-off is actually worthwhile.
Pin the variant on all four APIs for the native PAL seven-operation example:

```sh
python3 tools/math_builder.py \
  --operation UDIV32_32,UMOD32_32,SDIV32_32,SMOD32_32 \
  --objective size --zp-budget 12 --ram-budget 10000 \
  --pin UDIV32_32=link:d65536-hybrid \
  --pin UMOD32_32=link:d65536-hybrid \
  --pin SDIV32_32=link:d65536-hybrid \
  --pin SMOD32_32=link:d65536-hybrid \
  --validate-sources --build \
  --out build/d65536/selection_manifest.json
```

Install with the normal linker, retaining source SHA verification,
resource budgets and public ABI. The old V2 options remain independently
selectable; do not unconditionally select the new larger producer.

## Quantified decision

Prior merged [PR #357](https://github.com/floppyrom/C64-Math-Library/pull/357)
measured the original seven-operation, 24-independent-synthetic-frame
native PAL/VIC-II workload in pinned x64sc r46284:

| Metric | Original V2 | D65536 experimental source |
|---|---:|---:|
| Worst VIC-visible burst, frame 8 | 19,883 PAL slots | 17,618 PAL slots |
| Nominal worst-burst margin | −227 | +2,038 |
| Over-budget isolated bursts | 1/24 | 0/24 |
| Mixed-project linked RAM | 8,957 B | 9,213 B |
| Zero page | 31 B | 31 B |

The candidate's single worst-case signed-modulo input
`N=$80000001`, `D=$00010000` took 2,842 versus 485 native CIA slots,
but other divisor inputs can become slightly slower. The larger variant
adds **96 source bytes per independently linked signed/unsigned producer**;
the fully linked seven-operation benchmark grows by **256 bytes**,
including layout/alignment. The builder must retain these Pareto choices
rather than promote a universal faster routine.

This change does not itself certify a continuous 50 Hz PAL game/demo:
those tests intentionally exclude SID playback, actual raster IRQ,
REU DMA and other rendering/effect tasks. The native linked-instance
check in `tools/native_registered_d65536.py` independently revalidates
all four *production installer-selected* public entries at both physical
relocations in pinned x64sc, rather than using the older research-only
manually assembled kernels.

All five historical profiles, REU/Turbo/QS16 images and the original V2
source routines are unchanged.
