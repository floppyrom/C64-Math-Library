# Issue #39: constrained UDIV16 / UMOD16 branch transplant

**Status:** qualified source-level micro-optimization; this does **not** complete the unsigned DIV/MOD family campaign.

## Provenance and scope

A private OptiSearch P40 constrained native-code postpass identified the source sequence at `$B867` in V3:

```asm
    sec
    bcc unreachable   ; impossible because SEC sets carry
    jmp chain_start
```

It replaces the branch/JMP pair with `jmp chain_start; nop; nop`, retaining the exact six-byte footprint including SEC, all addresses, page layout and cycle/flag semantics. The two NOPs are unreachable on the new jump path and preserve all following addresses. No public-entry or zero-page contract changes. V2, V3 and V4 share the same symbolic producer, and V5 inherits the V2 code. V1 uses a distinct Balanced producer and remains untouched.

**Attribution qualification:** The tiny rewrite was human-guided in the private P40 exploration; the generic optimizer did not independently discover a superior arithmetic engine. This is an OptiSearch-*assisted* native-code transplant, not proof of superior generic-search output.

## Exact paired public-entry measurements

4,753 deterministic UDIV16 and 1,553 independent UMOD16 calls per profile. The corpora are the same seeds and call orders used by the regular unsigned-family validation. No added ZP, no PRG growth, no slowed calls. Mean cycles include RTS and exclude caller setup.

| Profile | UDIV16 before → after | Faster / 4,753 | UMOD16 before → after | Faster / 1,553 |
|---|---:|---:|---:|---:|
| V2 | 127.773827 → 127.754892 | 45 | 195.951706 → 195.931101 | 16 |
| V3 | 125.423943 → 125.408794 | 36 | 196.414681 → 196.392788 | 17 |
| V4 | 125.625710 → 125.605512 | 48 | 195.529942 → 195.511912 | 14 |
| V5 | 126.385862 → 126.362297 | 56 | 199.918867 → 199.898261 | 16 |

Across **25,224 paired public calls**, all arithmetic outputs/carry and stable inputs agree, **zero slower calls**, at most two cycles saved on any call. Gains are only **0.015–0.024 cycles/call**, so this is deliberately reported as a minor gain, not a major new division record.

## Static and relocation qualification

Current `main` baselines used were the 2026-10-11 merged #47 residents (not the old P40 PRG hashes). Exactly five resident bytes at `$B868–$B86C` change per profile, while V1 remains byte-identical. Reference source rebuild and alternate-map all-API validator passed locally for V1–V4 (56 entries, 21,678 calls per profile). V5 inherits the change in source-built hybrid. The shared `DU16F___relax_3` label has no external incoming reference and the new unconditional transfer preserves carry/register contents.

Candidate SHA-256:

- V2: `016b620bf3f4228238f0377e4b3128c2cc1ec4211a1f69f560f7f2d4bbc520fb`
- V3: `77c39d522c7a58856179f4a45187871fcbd940967c055095bc614a065da98425`
- V4: `7488a1f93a3237190be40626ac9945801620e86bc7cfeba76fd41fd06f196b70`
- V5: `7a843a703a51f402ec51a6e66f589cff020725784fff9f9cc0d9ef7b9bfbe91b`

The full release publication workflow additionally regenerates all-profile unsigned/signed validation and indexes, standalone native source mirrors, hashes and package audits. VICE x64sc 3.13.2 and its complete shared-library runtime are available for separate hardware-oriented emulator qualification; instruction-cycle means here are from the deterministic Python 6502 emulator, not real-hardware bus timings.

**Remaining issue #39 unsigned tasks:** independent manual and OptiSearch passes / no-gain determinations for UDIV8/UMOD8, UDIV24/UMOD24, UDIV32/16 with modulo, UDIV32/32 with modulo across the compatible resource classes, and any additional 16-bit architecture candidates. The wider family checklist stays unchecked until fully qualified and published.
