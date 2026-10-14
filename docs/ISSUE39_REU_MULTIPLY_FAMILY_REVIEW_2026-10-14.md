# Issue #39 — REU multiply family: Turbo16, Turbo32 and V4 QS16

**Public ABI and resource-screen date:** 14 October 2026. Source and resident profile review only; **native raster-exact timing is not measured**. The private OptiSearch source is not published.

**Final certification (14 October 2026):** The REU multiply family (Turbo16, Turbo32, and V4 QS16) is complete after real VICE REU-image validation, reference/alternate relocation tests and post-merge full-library and comparable checks. The V4 QS16 alternate-bank defect is corrected in the source generator, with reference binaries unchanged. Issue #39 remains open.

## Identical-input public-entry results

Every normal-vs-Turbo16 pair is the **same 2,097 inputs**; every normal-vs-Turbo32 pair is the **same 2,192 inputs**. V4 QS16 uses the identical Turbo16 corpus (2,097). The CPU model includes its deterministic REU DMA costs; entry to RTS includes the actual public wrapper, while caller JSR and input setup are excluded. Both V3 and V4 have identical measured Turbo/public vectors, as do both source relocation maps.

| Service | Normal public comparison | REU service | BEGIN + END | Break-even batch |
| --- | ---: | ---: | ---: | ---: |
| Turbo16 (V3/V4) | UMUL16 216.73391 cycles | 197.04626 cycles | 645 cycles | **33 calls** |
| Turbo32 (V3/V4) | UMUL32 693.45347 cycles | 676.18522 cycles | 697 cycles | **41 calls** |
| V4 QS16 | UMUL16 216.73391 cycles | 281.72675 cycles | 36 cycles | **None (slower every batch)** |

The batch crossover is strictly defined as the first integer `n` satisfying `BEGIN + n * REU_CALL + END < n * NORMAL_CALL`, without counting operand marshalling or caller JSR. V4 QS16 remains valuable as an architectural example of two REU table fetches implementing `Q(x+y)-Q(abs(x-y))`, **not** as a fast multiply tier. Do not compare these 2026-10-14 same-input means with older random-seed means as if benchmark populations were identical.

## Public interface, ownership, alternatives

- **Turbo16:** 122-byte self-modifying executable-ZP overlay, public wrapper binds x/y, writes the 32-bit result directly into public Z. It saves approximately 19.68766 model cycles per operation versus same-corpus normal UMUL16, but first needs a 300-cycle BEGIN and finishes with a 345-cycle END. These include deterministic REU SWAP cost. No stack-page executable reservation.
- **Turbo32:** 135-byte stack-free executable-ZP overlay, resident register bind and direct low/high result paths. Same-corpus 32-bit saving approximately 17.26825 cycles per call; BEGIN 326, END 371. It cannot be substituted for the normal entry outside BEGIN/END or run concurrently with ordinary math sharing its ZP. Avoid equating a privately benchmarked unwrapped 614-cycle kernel with the public ~676-cycle REU CALL.
- **V4 QS16:** four-byte REU record AUTOLOAD, with 2× four-byte lookups for each product. Although BEGIN/END cost only 18 cycles each, per-call time is higher than the direct public route; the current 16 MiB table and 24-bit REU address requirements also constrain hardware compatibility.

For **each** Turbo mode, the audit checks signed-free unsigned products, carry C=0, preserved X/Y buffers, stack balance, 122/135 ZP byte ownership, exact ZP restoration, and successful second-batch reinstallation of the modified overlay. It also confirms that ordinary calls after END remain valid because the real resident ZP state is restored (not invented sentinel bytes). For QS16, it verifies that END restores the ordinary one-byte REU mode. There is no blanket license to call normal math routines inside a Turbo overlay interval.

### Relocation and comparison coverage

The new audit exercises **57,759 installed/source-built public product calls** over V3 and V4, published/reference/alternate builds. The prior independent relocation certificate already qualified 17,164 products plus 32 lifecycle calls, and the origin/bank boundary sweep qualified 3,556 additional products. Reference/alternate Turbo cycle vectors, BEGIN/END cycles and output contract must match bit-for-bit. ZP origins $02-$85 (Turbo16) and $02-$79 (Turbo32), and 512 KiB/16 MiB bank endpoints, remain distinct tested resource classes.

### OptiSearch transplantation decision

The normal multiply-family optimization already screened OptiSearch native quarter-square, sign-lifetime and 32-bit low-resource records. REU overlays are another ABI/resource class: native unwrapped fastest records or stack-page-dependent candidates are not valid substitute public CALL implementations without full binder, overlay lifetime, REU transfer, ZP ownership and mixed-call proof. No additional compatible REU-mode architecture beating the selected current Turbo16/32 paths has been established by the current evidence. This is a **documented no-gain audit**, not a claim of exhaustive optimization search.

### Publication criterion

This research review and same-input CPU proof do not by themselves certify native REU behaviour. Keep Issue #39's REU multiply checkbox **open until** native x64sc V3/V4 and QS16 mode proof, exact-head full CI and comparable benchmarks, checksum seal and postmerge main qualification have passed. Remaining trig/distance/seek families remain open irrespective of REU completion.

## Native VICE x64sc proof

The published V3 512-KiB and V4 16-MiB REU images passed **120 real x64sc public product calls**, each inside the required BEGIN/CALL/END lifecycle. Turbo16/32 passed in both profiles; V4 QS16 passed in the installed reference map. The native smoke test checks public products, carry, input/stack preservation and sentinel output bytes. Native cycles were **not** measured. The V4 QS16 *alternate* map is source-built and CPU-model-qualified on all 2,097 same operands; its relocation fixes symbolic public I/O, ZP scratch and the REU quarter-square base bank, while the installed reference-mode PRG/REU images remain byte-for-byte unchanged.

**Next qualification:** independent exact-head full-library, comparable unsigned and Turbo32 checks; post-merge main checks before checking off REU multiply in Issue #39.
