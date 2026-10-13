# Issue39 — V1 32/16 zero-handler source promotion (staging)

13 October 2026. This branch stages source-built V1 and V5 images, with both reference and alternate memory maps rebuilt.

The hot V1 code falls through into the 32/16 continuation after the 16/16 producer returns carry clear. The rare divide-by-zero handler is source-owned at REG_KERNEL+$04F0, the low-word continuation moves seven bytes earlier, and its unrolled backlink jumps to REG_KERNEL+$056C. No new scratch or public entry address.

Full 822,050 unsigned, 364,533 signed and 136,335 shared-input public calls passed, with identical resident lengths and unchanged REU layouts. Canonical source regeneration and V5 rebuild passed reference and alternate source maps.

| Entry | Previous V1 official mean | New V1 official mean |
|---|---:|---:|
| MATH_UDIV32_16 | 825.873946 | 825.039941 |
| MATH_UMOD32_16 | 843.629912 | 842.895601 |

**Native VICE release gate passed:** 384 complete V1/V5 original/candidate public calls in pinned x64sc, covering both 32/16 aliases. No native cycle timings measured. Remaining gates: independent PR CI and post-merge main CI. Do not close #39. The candidate is not global Pareto: divide-by-zero is 2 cycles slower, valid divisor is 1 faster.

## Historical proof compatibility after source promotion
Older 24/8 and UMOD8 replay scripts previously assumed only archived resident SHA values. The V1 24/8 replay now reverses the **exact known** V1 32/16 transformation and asserts the recovered pre-PR100 SHA before running its original comparisons. The V2 UMOD8 replay uses the SHA-pinned current V2 resident, reverses only the original 104-byte UMOD8 guard, and requires all other bytes to match. The V5 unchanged-source comparison short-circuits, avoiding unnecessary historical PR71 inversion. These changes do not modify production arithmetic or relax arbitrary-hash checks.
