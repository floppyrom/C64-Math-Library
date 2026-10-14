# V2/V3/V4 unsigned SHR16 exclusive batch

This optional assembly source is SHA-pinned to the installed V2/V3/V4 resident binaries. Assemble overlay_begin_end.asm in free RAM, call MATH_INIT, then MUL32_SHR16_BEGIN; make at least four MATH_UMUL32_SHR16 calls; finish with MUL32_SHR16_END. During the active interval normal UMUL32, UMUL32_READY and any shared-producer clients, including IRQ/NMI callers, MUST NOT run. The patch changes shared executable bytes and is non-reentrant. No default public profile is changed. See ../../docs/ISSUE144_V234_SHR16_EXCLUSIVE_BATCH_2026-10-15.md.
