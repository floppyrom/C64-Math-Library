# Issue 39 — generic unsigned 24-bit high-quotient TXA source integration

13 October 2026. Source-backed staged resident candidate.

On N2>D2, earlier NMOS LAX N2 keeps N2 in X. Replacing LDA N2
with TXA directly before high-byte SBC saves two CPU cycles/two
instruction bytes without additional zero page or public ABI changes.
V1 and V2–V4 source files were separately edited; V5 hybrid imports
the rebuilt V2 dividend kernel from its relocated private ROM-underlay.

Both reference and alternate address-map builds passed with real
source-assembled PRGs and V3/V4 REU images. Every candidate public
UDIV24 and UMOD24 entry passed signed/unsigned cross-family ABI checks,
preserved N/D, quotient where promised, remainder, carry including D=0,
high sentinel and caller stack. The V2–V5 remainder-only frontend
can change branch phase, creating minor per-case modulo slowdowns.

| Profile | Parent SHA prefix | Candidate SHA prefix | Official UDIV24 mean | Official UMOD24 mean |
|---|---|---|---:|---:|
| v1_balanced | d6e013740a8c | 2567dccbc4e0 | 164.369661 | 230.804894 |
| v2_pareto_fast | 0510d469e1ff | c3c0898bc61a | 156.996423 | 207.493883 |
| v3_reu_512k | 00a64179f701 | 7ec22f5272b5 | 156.996423 | 207.493883 |
| v4_reu_16m | 595f9d655920 | 3e2b745e9cd8 | 156.996423 | 207.493883 |
| v5_hybrid_lowzp | 5191e44263c2 | 431824532ef2 | 156.996423 | 207.493883 |

Official mean uses exactly the same current library comparison corpus
for every V1–V5 resident, not an independent-seed profile-validator mean.
No size, REU bank or normal zero-page growth. Full 822,050 unsigned,
364,533 signed and 136,335 same-input public executions passed.

The exact reference/alternate qualified input/cycle vectors and
full SHA-pinned image evidence are retained in
validation/review/ISSUE39_U24_TXA_SOURCE_INTEGRATION.json.

**Native VICE verification is still a separate gate.** No emulator
native call or VIC/REU DMA timing is claimed by this staged proof.
Do not merge solely on this script if native evidence is required.

The other unsigned DIV/MOD classes and issue #39 remain OPEN.
