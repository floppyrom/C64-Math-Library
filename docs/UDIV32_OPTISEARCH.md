# Four-ZP UDIV32 replacement

V2/V3/V4 use Repose OptiSearchV2's live-high quotient-state division with a
four-byte shifted-divisor workspace. V1/V5 retain their zero-ZP implementation.
UMOD32 retains its remainder-only front end and enters the new divider on fallback.

The source is adapted from `src/optisearchv2/targets/mos6502/live_high_division.py`
and `zp_aligned_division.py` in the uploaded `OptiSearchV2-2026-10-06(1).zip`
(SHA256 `f5a6a9f0e8728186f91a95c1112a70488cf943fc99b2380c52272424e44455eb`).
Generator strategy: `division.live-high-quotient-state-zp-tail-unsigned`, threshold 1.
Credit: Repose. The integrated symbolic assembly requires no external generator.

The donor report `docs/status/C64_DIVMOD_LEARNING_2026-09-25.md` compares
739 bytes / 4 ZP / 181.035 mean cycles with 869 bytes / 8 ZP / 376.381 cycles
on its 512-case SplitMix64 corpus. That explains the reported 195-cycle and
130-byte savings. Those are historical corpus-specific figures.

The current raw threshold-2 generator is smaller still, but its aligned loop
regresses badly for narrow divisors. This integration preserves our 32/8 and
32/16 restoring loops, reading preserved N directly rather than copying it to
ZP. An equality exit avoids running a full narrow loop for N=D. Normal returns
clear carry; zero divisors return zero Q/R and set carry. Decimal mode must be
clear, as in the existing ABI. Only documented 6502 instructions are used.

## Paired measurements against c29612a

Public-entry cycles include RTS and exclude caller JSR/input stores. All three
profiles produce the same results. Seed 0x32D1F, Python Random; groups consume
one sequential stream after the 23-by-23 edge cross product.

| Corpus | Pairs | Old mean | New mean | Slower pairs |
|---|---:|---:|---:|---:|
| Structured edges | 529 | 809.716 | 747.181 | 0 |
| Uniform 32-bit N/nonzero D | 30,000 | 368.906 | 191.169 | 1,198 |
| 16-bit nonzero D | 2,000 | 1576.294 | 1485.330 | 0 |
| 8-bit nonzero D | 2,000 | 1896.827 | 1814.827 | 0 |

The PR #27 live-high replacement by itself reduced the reachable public graph from **869 to 793 bytes** and its live-high workspace from **8 to 4 ZP bytes**. Item-6 latency bounding now deliberately makes the shared UDIV32/16 narrow-divisor engine and the dedicated 17-bit-divisor tail reachable from the public UDIV32/32 entry. The finalized whole-call graph therefore measures **2,755 reachable code bytes and 14 ZP bytes**, with **0 persistent stack-page bytes**. Wide divisors still execute the four-ZP live-high core; the larger static footprint reflects the newly reachable bounded fallbacks, not extra hot-path scratch. The resident PRG load span is unchanged.

This is an average-speed/resource improvement, not an all-input speed guarantee.
The worst sampled uniform regression is 882 cycles (N=2711414585, D=88257).
Uniform-corpus maxima are 1778 old / 2412 new; these are sampled, not theoretical
worst cases. Narrow sampled inputs improve by 82–91 cycles.

`validation/review/UDIV32_LIVE_HIGH_COMPARISON.json` preserves the paired baseline
measurements. `tools/validate_udiv32_live_high.py` exercises both incoming carry
states, quotient boundaries, zero/equal operands, preserved inputs, balanced
stack, sampled full-memory write guards, independent UMOD calls, and exact
reference/alternate cycle parity. The regular unsigned-family validator covers
all five profiles. Deterministic builds reproduce the bundled PRGs.

An independent Reduced6502 run matches Python results and mini6502 cycles on
4,625 structured/random pairs. Binary scope checks confirm the other 52 public
executable graphs are unchanged in both maps. The broad alternate-map suite
currently fails V2 SMUL8(0,0), returning $AF00; the saved c29612a baseline fails
identically. This replacement does not claim a new all-library certification.
