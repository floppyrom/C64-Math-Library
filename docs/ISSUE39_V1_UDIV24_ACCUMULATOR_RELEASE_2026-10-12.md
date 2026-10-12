# Issue #39: integrated V1 61-byte accumulator-resident 24÷8 DIV/MOD

**2026-10-12. Source-backed release.** The V1 bounded 24÷8 engine now keeps the
partial 8-bit remainder in A during 24 shift/subtract steps and writes R0 once
on completion. Exactly **69→61 executable bytes**, while the original 84-byte
source-owned island stays reserved with 23 trailing zero bytes. The new engine
uses zero additional ZP or stack, leaves N/D unchanged, and preserves stable
public addresses, output flags and full resident size.

Source: `relocatable_source/v1_balanced/udiv24_latency_escape_balanced.inc`;
candidate: `tools/candidates/issue39_v1_24by8_accumulator.asm`.
Release resident SHA256: `cdc2ca502d664055f896d7ad1601e8dd994b61be33e24bde3e25fc0dcbee1cdd`; previous PR78 V1 SHA: `28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0`.
V5 SHA remains `5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222`; V2/V3/V4 unchanged.

### Same-input complete-public-entry comparison

| API | PR78 baseline | Installed accumulator | Difference |
|---|---:|---:|---:|
| UDIV24 (4,753 samples) | 170.238165 | 166.190196 | -4.047969 |
| UMOD24 (1,553 samples) | 246.822279 | 234.433355 | -12.388924 |

The standalone research screen checked **48,388 paired prior/new full public
6502 calls**, with zero wrong Q/R/C, no input/stack clobber, and no slower
calls. The D8 4,080-case stress mean went 1202.660784→976.350000.
A separate native VICE x64sc old/new **isolated** kernel test passed 128
calls; do not misrepresent this as native full-resident coverage or timing.
Current resident source builds at reference/alternate maps, full five-profile
822050 unsigned and 364533
signed calls, and 136335 same-input profile calls all pass.
The previous PR78 84→69-byte historical test is SHA-reconstructed and retains
its original certificate, rather than claiming its old metrics are the new ones.

This release is **part of** issue #39; the family-wide audit/no-gain review
and later ISQRT/UMUL/SMUL/etc campaign remain open.
