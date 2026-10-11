# Issue #39 — V2 Pareto Fast guarded UMOD8 public remainder

**Date:** 2026-10-11. **Status:** source-backed V2-only deployment, with other profiles preserved. Overall unsigned DIV/MOD campaign remains open.

V2 already has a dedicated UMOD8 magnitude core, but its public entry always stages N/D into zero-page scratch. V1 and V5 gained a source-backed **77-byte remainder-only guarded implementation** in PR #63. This PR transplants the exact same bounded algorithm into the V2 resource class: for nonzero D≥32, Q≤7, so an inline seven-subtraction accumulator chain writes R and returns carry clear without touching the existing public Q bytes or ZP. For D<32, including D=0, an LDA N and JMP back into the original unchanged V2 wrapper after the first LDA preserves prior magnitude semantics. Public ABI and normal-ZP allocation unchanged; code resides at a previously empty `REG_LOW+$0E00` block, within the resident PRG's original span.

## Exact full-domain timing

Exhaustive old/new V2 source-executed audit: **65,536 input pairs × two executable residents = 131,072 public machine-code calls**. Reconstruct the exact previous V2 merged PR #63 resident with SHA256 `e1e828a2748099b6f05b224b98ca26960d120f8ba886c4906e8b52bdb8b4fbcd`; the new V2 resident SHA256 is `2df096598ae5f046272472f08add0ade079a8a16ab43dc7b6cdd41aea7e80dad`. Numerator/denominator bytes, high sentinels, four Q bytes, high R bytes, carry and full remainder match the mathematical oracle for every possible input.

| Public V2 UMOD8 | Previous | Candidate |
|---|---:|---:|
| Exhaustive mean CPU cycles | 64.819153 | **52.835800** |
| Mean reduction | — | **18.49%** |
| D≥32, faster / same / slower | — | **57,060 / 284 / 0** |
| D<32 extra dispatch | — | **+14 cycles each of 8,192 pairs** |

The gain is workload-dependent: **not** universal Pareto dominance, since every D<32 call pays 14 cycles. CPU instruction cycles do not account for physical REU DMA bus latency in the unchanged V3/V4 profiles. V3/V4 retain their REU algorithms; no attempt is made to overwrite their different public wrappers.

**Native VICE x64sc:** 80 input pairs executed in both complete old and new V2 residents = **160 native calls**, all output/carry/quotient-preservation checks passed. The executable reported VICE 3.10 despite the saved archive name mentioning 3.13.2.

## V5 hybrid isolation

V5 already has this same guard from PR #63. V5 imports the V2 UMOD8 small-divisor fallback and its magnitude core, while retaining its own source-backed guard at the *same symbolic low-memory island*. The hybrid builder is updated to accept the V2 public wrapper whether its first instruction is the former LDA N or its newly optimized JMP to the **identical** guard; after the copy, V5's public and guard bytes remain unchanged. V5 reference SHA256 must remain **byte-identical to `bed1ee986857d045d452036d78d0d6cbdc078dbc3407f8a860a8fd54f8395fa2`**. V1 unchanged too. Alternate V2/V5 relocation and V5 mixed-call lifetime checks are mandatory.

## Bounded no-gain and OptiSearch companion

Exhaustively generated V1 UDIV8 quotient-prefix 4,6,8,10,12 candidates (327,680 machine calls), constrained to the existing occupied `$4000–$4125` source island. The shipped K12 path is fastest average among these **in-place variants**, with no compatibility-safe further in-place gain. Larger chain variants could be faster on selected workloads but collide with other resident code and would need a new ownership/relocation proof. This is not global cycle optimality or an assertion that OptiSearch cannot find another algorithm. Separate native OptiSearch 8/16/24 strategies were previously screened and did not constitute public-ABI-equivalent replacements. The V2 UMOD8 implementation is a manual transplant under public ABI/resource constraints, not a claim of native OptiSearch-generated superiority.

## Publication requirements

Full release gates: 822,050 all-profile unsigned + 364,533 signed public calls, 136,335 common-input, 53,760 seven-class, the new **131,072** paired V2 calls, PR63 V1/V5 **262,144** paired calls, historical 32/16 and 32/32 certificates, and full source/reference/alternate reassemblies. Update both CHANGELOG.md and CSDB_CHANGELOG.txt, README/manual, performance and best-profile tables, release status, source mirrors, SHA256 package seal and final post-merge main CI. Keep issue #39 unsigned DIV/MOD checkbox unchecked until the remaining 16/24/32-bit architecture/no-gain records are complete.
