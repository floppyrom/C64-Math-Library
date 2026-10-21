# Historical speed parity and native REU — engineering phase 1

**Status: reproducible source/ABI inventory and REU lifecycle-contract foundation only.** This does NOT declare historical speed parity or enable a REU kernel in the operation-first linker. The stock-C64 installer and all historical source, PRG, REU and benchmark artifacts remain unchanged.

## Historical parity — first qualification step

Run:

    python3 tools/historical_parity_triage.py --out build/historical-parity-triage.json

The report cross-checks all 56 public stock-C64 operations against their published historical best-profile records, independently verifies the historical source SHA-256, inventories all currently linkable source variants and their physical module resources, and identifies byte-identical historical donor files.

**Eleven unsigned DIV/MOD APIs** have authenticated five-profile historical identical-input corpora. Those comparisons do NOT automatically compare against the new builder's source benchmarks: each side may use a different input corpus, public-call adapter, origin and init contract. Neither a historical lowest mean nor a source SHA identity certifies builder performance parity.

Every operation is deliberately marked as lacking a certified historical-to-selective same-corpus speed comparison. The next transplant trials should prioritize the wide 24/32-bit division, modulo and multiplication families, with the exact same operands, complete public ABI, zero-divisor/overflow behavior, mean/p95/max and per-frame tail, at two memory maps. Preserve qualified slower variants when they offer genuine RAM/ZP/initialization/SMC trade-offs.

## Native operation-first REU — first integration step

Run:

    python3 tools/reu_selective_contract.py --reference-tier v3_reu_512k --family UMUL16 --out build/reu16-contract.json

Optionally pass --stock-manifest PATH to detect *known* conflicts between a frozen reference REU executable zero-page overlay and the caller's operation-first image or reserved application ZP.

The contract is extracted from the original V3/V4 API include files. It validates distinct ordered BEGIN, CALL and END entries and the hardware tier and bank contracts:

| REU service | Historical hardware | Exclusive ZP | Historical CPU-model guide |
| --- | --- | --- | --- |
| Turbo16 multiply | V3 512 KiB+ or V4 16 MiB | 122 bytes | Beneficial in large batches; historical crossover around 33 calls |
| Turbo32 multiply | V3 512 KiB+ or V4 16 MiB | 135 bytes | Beneficial in large batches; historical crossover around 41 calls |
| QS16 multiply | V4 16 MiB | 16 bytes, exact extent not yet extracted | Specialized functional choice; not always faster |

These crossover examples are historical same-corpus CPU-model estimates with BEGIN/END, not hardware raster or DMA timing guarantees. The report deliberately returns status CONTRACT_ONLY_NO_SELECTIVE_REU_BINARY and native_reu_backend_available=false. An overlap-free reference placement is NOT evidence that an independent modular REU service exists.

### Next executable REU milestone

1. Extract the V3/V4 Turbo16 DMA adapter and hot kernel as independently relocatable source, not by importing a whole resident image.
2. Extend global placement to reserve user-chosen REU banks, full lifecycle-owned executable ZP, required C64 RAM and DMA control state. Reject collisions before generating any PRG.
3. Implement BEGIN/CALL/END with exact save/restore of caller ZP, multiple batches, strict non-nesting, and no overlapping ordinary math calls.
4. Verify old/new whole-public-call Q/R/Carry, inputs and stack on identical corpora at two RAM maps; then run 512-KiB and 16-MiB native VICE REU/DMA qualification.
5. Only after full source, ABI, hardware and integration proof make an actual source variant selectable. Keep small/zero-ZP non-REU alternatives available.

QS16's exact writable state placement has **not** yet been established. No new REU service should be marked link-ready until it is.

Until then, continue using the immutable separate historical bundles described in [REU compatibility](REU_COMPAT_EXPORT.md). Never mix a frozen REU resident with a newly generated stock math PRG.

Regression command:

    python3 -m unittest discover -s tools -p 'test_historical_parity_reu_phase1.py' -v

This qualifies the *engineering inventory*, not a production REU backend.
