# Issue #144 D — normal-footprint SEEK16 INIT with compact UDIV32/16 code island

**Opt-in research only. No production PRG, REU, API address or normal zero-page allocation is changed.** The source examples are independently usable for V2, V3 and V4. They intentionally depend on the separately qualified compact full-domain U3216 shared-take include from PR #169.

## Architecture

The shared-subtraction 32/16 producer shrinks its ordinary low-word tail by **192 bytes**, leaving part of its formerly occupied resident code region available. Each alternative moves the SEEK16 Euclidean-scaling code and the fractional remainder-accumulator update into that reclaimed island at `U3216_MAIN_END`. It inlines the repeated integer-speed accumulator into the original INIT path; the fractional operation uses a JMP/JMP pair rather than JSR/RTS. All arithmetic and divide-by-zero semantics remain unchanged.

This is **not** an application-RAM overlay. The three independently accessible, full source alternatives are:

- `optional/issue144_seek_inhole_shared/v2_pareto_fast/seek_dda.asm`
- `optional/issue144_seek_inhole_shared/v3_reu_512k/seek_dda.asm`
- `optional/issue144_seek_inhole_shared/v4_reu_16m/seek_dda.asm`

To evaluate, in a disposable checkout install `optional/issue144_u3216_shared_take_inline/udiv32_16_split_direct_shared.inc` over `relocatable_source/division/udiv32_16_split_direct.inc`, then install the corresponding alternative `seek_dda.asm` over each matching `<profile>/resident/movement/native/seek_dda.asm`. Assemble and qualify as usual; do not overwrite shipped images without completing production gates. The combined U3216+SEEK placement is necessary: using these SEEK alternatives without the compact division core may overwrite other resident code.

## Same-input CPU-model public-entry benchmark (16 October 2026 research checkpoint)

| Profile | Paired INIT calls | Mean cycles saved | Worst saved | Slower | Follow-up STEP |
| --- | ---: | ---: | ---: | ---: | --- |
| V2 practical fast | 1,920 | 22.1448 | 0 | 0 | Identical |
| V3 512 KiB REU | 1,920 | 20.4781 | 0 | 0 | Identical |
| V4 16 MiB REU | 1,920 | 20.4781 | 0 | 0 | Identical |

Corpus covers 160 deterministic edge/random movements, six speed classes including 0.5 and 1.5 px/frame, and both major-axis and Euclidean modes. Every INIT and following STEP preserves complete $90E8–$91DF SEEK16 state, C, X and stack pointer.

All three combined source builds and the existing **56-entry / 21,678-call source validator** passed (**65,034 calls total**). These local benchmarks were obtained against archived source that retains the same SEEK arithmetic structure; `tools/issue144_seek_inhole_shared_qualify.py` independently rebuilds the current repository checkout in CI and rechecks layouts, signatures and paired public calls.

Real x64sc 3.13.2 independently passed 16 original + 16 candidate INIT calls per profile and matching subsequent STEP calls; 384 native captured status/state bytes matched in each profile. V3/V4 used actual 512 KiB / 16 MiB REUs, and source-built REU images were byte-identical to reference images. Real **native cycle timing**, VIC contention and physical DMA time are not part of these measurements.

## Limitations and promotion policy

V1 and V5 have different low-ZP resident layouts, so they are unchanged by this research. Performance savings depend on speed workload and are below the campaign's heuristic 5% mean in some mixes, despite no slower calls in this corpus. General IRQ/NMI reentrancy and mixed arbitrary-API concurrency have not been proven. No builder default or PERFORMANCE.md baseline has been updated. Complete a fresh current-main, reference/alternate, all-profile native and publication qualification before any production promotion.

Run `python3 tools/issue144_seek_inhole_shared_qualify.py --moves 160`. With a validated native VICE executable, set `VICE_WRAPPER=/path/to/x64sc` and add `--native`. This tool stages everything inside a disposable checkout and never modifies source or release artifacts in the working tree. No private OptiSearch implementation is published.
