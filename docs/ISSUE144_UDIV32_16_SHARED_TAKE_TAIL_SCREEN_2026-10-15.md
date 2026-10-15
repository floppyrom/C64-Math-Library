# Issue #144 B — full-width 32/16 producer shared-subtraction research (15 October 2026)

**Research-only source and test cases. No shipped math implementation, resident PRG, REU image, default ZP, public entry, or PERFORMANCE record is replaced.**

## Mechanism

The V2–V4 fast 32-bit numerator / 16-bit divisor unsigned producer reuses the 16/16 high-word quotient/remainder core and then consumes the remaining 16 numerator bits. The unrolled low-word continuation previously duplicated subtraction for both the overflow-forced and ordinary comparison-accepted cases. Both paths enter subtraction with carry=1. A single shared subtraction body and explicit final `SEC` can compute the same quotient and residual with fewer code bytes.

The experiment is a **source transplant**, not an input-domain guard: there is no full-width dispatch overhead. The production code itself remains unchanged.

## Independently executable evidence

**Isolated low-word continuation:** `python tools/issue144_u3216_shared_take_tail_research.py`. 7,554 same-input nonzero-D16 pairs. Correct quotient-low16 and remainder16 for baseline and candidate; standalone fragment 684→492 bytes at $2070; mean tail cycles 494.890→487.379 (7.511 saved), 0 slower cases in the isolated test. The high-word residual here is oracle-seeded, and public carry/D=0 are not included. Model CI: [Actions 38722317028](https://github.com/floppyrom/C64-Math-Library/actions/runs/38722317028).

**Complete public entries, V2/V3/V4:** `python tools/issue144_u3216_fullcall_source_transplant_screen.py`. Temporary edits apply ONLY inside the test checkout; the script restores the original common .inc on exit. Generated reference and alternate resident images are compared against the unchanged shipped PRGs, **1,280 identical mixed operands × 2 APIs × 3 profiles × 2 maps**. Q32, R16, C, inputs and SP pass, including ordinary unrestricted full-width inputs, narrow D and divisor zero. Each public API on each profile/map saves **6.591796875 modeled CPU cycles on 512 uniform full-width N32 cases**, and **4.7578125 cycles on all 1,280 cases**: 878 faster / 389 tied / 13 slower (worst −1 cycle), best +18. The reference and alternate results agree. Corpus SHA256 `873a7f093e844d9ea9493cad2f6ae95a8d48707915174d39bcb70db0dac6ae4b`. Model certification: [Actions 38724485006](https://github.com/floppyrom/C64-Math-Library/actions/runs/38724485006).

**Real native x64sc:** `python tools/issue144_u3216_fullcall_native.py` after source transplant in the same job. Checksum-pinned VICE 3.10 r46274 ran **288 native baseline/candidate full-public calls**, 24 original and 24 changed per API/profile. All public Q32/R16/carry, input and stack snapshots matched for V2/V3/V4. Native correctness **PASS** in [Actions 38725574165](https://github.com/floppyrom/C64-Math-Library/actions/runs/38725574165); **physical native cycles were not measured**. V1/V5 and mixed-call interleaving in the integrated replacement have not been independently qualified. Do not conflate this pinned VICE 3.10 CI proof with the separately preserved local VICE package.

## Resource, performance and promotion decision

The common source text changes 13,036 → 10,704 **characters**, which is not a resident-code byte measurement. The separate isolated executable saves 192 bytes; actual installed placement/branch geometry and existing live islands would require their own release qualification. No extra normal ZP is used by the isolated experiment, but a full producer replacement must pass complete resource/ABI proof before any claim of zero ZP growth.

The gain is only around **1% on the ordinary 650-cycle full-width public call**, far below the intended ≥5% general-producer threshold, with 13 one-cycle regressions on the mixed corpus. **Do not promote to default**: keep researching architecture changes that materially improve the entire all-input quotient/remainder producer. Existing narrow-numerator opt-in guards remain workload-specific and are not a solution for uniformly full-width inputs.

All bundled sources are publicly reproducible and independently authored; **private OptiSearch implementation/source is not published**. Issue #144 remains open. The original library binaries, source generator's committed core, and benchmark leaderboards are unchanged.
