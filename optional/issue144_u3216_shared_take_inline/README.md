# Issue #144: unrestricted shared-take 32/16 division (opt-in source)

Independently authored NMOS 6502/6510 research alternative. **Not** a change to any shipped binary or default builder. The 16-step low-word portion of the original split producer shares accepted/overflow subtraction paths. Every nonzero 16-bit divisor is supported, and the original 8-bit-divisor and D=0 branches remain unchanged. Public Q32/R16/C outputs and input preservation were tested.

To evaluate, in a disposable worktree copy `udiv32_16_split_direct_shared.inc` to `relocatable_source/division/udiv32_16_split_direct.inc`, then run `python tools/assemble_sources.py --profile all --config-kind reference` and `python tools/validate_source_build.py all --build build_source/reference`. Do not overwrite release artifacts or the original source in a production installation. It uses the existing U3216 entry, ZP, main placement and D8 base.

## Local same-input research benchmark, 15 October 2026

| Workload | Calls | Mean cycles saved | Worst cycles saved | Slowdowns |
|---|---:|---:|---:|---:|
| All public calls | 10,735 | 6.3371 | −1 | 108 |
| Uniform 32-bit N / 16-bit D | 5,000 | 6.7192 | −1 | 56 |
| D from 256 to 32767 | 2,500 | 9.4984 | +3 | 0 |
| D from 32768 to 65535 | 2,500 | 3.9620 | −1 | 52 |
| 8-bit divisor | 400 | 0 | 0 | 0 |
| D=0 | 50 | 0 | 0 | 0 |

The source-built V2 general tail decreases from **685 to 493 bytes** (192 bytes saved). All four directly assembled profiles V1–V4 passed the existing 21,678-call full API validator (**86,712 machine-code calls**). Actual VICE 3.13.2 x64sc public DIV/MOD calls passed with 16 calls per profile: V2, V3 plus 512-KiB REU, V4 plus 16-MiB REU (**48 calls**). No released PRGs/REUs were modified.

These small improvements do **not** meet the 5% general-production performance research threshold, and 108 high-D calls lose one modeled cycle. V5 hybrid integration, IRQ/NMI reentrancy, and physical VIC/REU timing are not certified. This is **research-only**, not a default replacement. The archived source corpus used for local tests had the identical U3216 common include as current main. See `validation/review/ISSUE144_U3216_SHARED_INLINE_OPTIN_2026-10-15.json`.
