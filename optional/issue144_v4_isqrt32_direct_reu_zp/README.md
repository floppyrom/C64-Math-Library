# Issue #144 C — direct REU-to-zero-page ISQRT32 record, experimental

**Not installed in canonical V4.** Existing canonical source, frozen PRGs/REUs and `PERFORMANCE.md` are unchanged.

## Idea

The V4 prefix lookup yields four ordered bytes: `root_lo, root_hi, residual_lo, residual_hi`. The installed source sends this REU record to `REU_SCRATCH` (`$C020` on the reference map), then spends four C64-side load/store pairs copying them into ISQRT32's existing zero-page workspace.

The candidate keeps **the same eight normal-ZP bytes** (`ZP_MAIN+$52..+$59`), but changes which root/residual fields occupy each address so the prefix lookup can DMA directly to `IS32_ROOT0`. The existing third residual byte and three trial bytes remain within that eight-byte envelope.

**Important:** other public REU routines may assume the established C64 destination. The candidate explicitly restores the REU C64 address registers `$DF02/$DF03` back to `REU_SCRATCH` after the four-byte transfer, before the arithmetic refinement. No additional ZP, caller RAM, REU table size or private OptiSearch code is required.

## Expected improvement and rejection criteria

The direct DMA removes four absolute-LDA/ZP-STA pairs (approximately 28 base CPU cycles); reprogramming the REU C64-side destination after DMA costs about 12 cycles. The **hypothesis** is roughly 16 CPU cycles saved per ordinary ISQRT32 call, subject to true machine-code and native VICE measurement. **Do not call this a win until confirmed.**

Run `python3 tools/issue144_v4_reu_direct_zp_screen.py` to construct disposable baseline and candidate full V4 images from source in **reference and alternate** configurations, compare full-input same-operand ISQRT32 public-call cycles, root, N32, carry and ordinary registers/stack, verify that the REU C64 destination registers are restored, and run the existing full 56-entry source validator on candidate images. With `VICE_WRAPPER` set, replay 24 native x64sc baseline and 24 candidate root calls with an actual emulated 16 MiB REU image.

Differences in transient internal zero-page scratch bytes after return are **expected** when the workspace is permuted; these bytes are not public state. A full mixed-call, interrupt-lifetime and real PAL/NTSC VIC/REU hardware timing audit is still needed before potential default promotion. Any native mismatch, wrong output/carry, unsafe REU state, slower workload class, source-space collision or ZP growth rejects promotion.

The existing [Issue144 source-release candidate](ISSUE144_ISQRT32_SOURCE_RELEASE_CANDIDATE_2026-10-16.md) remains the published baseline.
