**Post-merge final certification (14 October 2026):** PR #130 merged as `44fc91813d945c05194d2f4962bb89f9d5f88449`; all four independent main validation workflows passed. Both DIST8 public APIs are now released in V1–V5. Normalization and seek are still open.

# Issue #39 — source-backed DIST8 shared ordering optimization

DIST8_FAST and DIST8_ACCURATE reuse a magnitude-ordering exchange. The old stack-based PHA/PLA swap has been replaced by TAX/LDA/STA/STX/an early RTS with fixed-width NOP padding; the no-swap BCC still targets the previous RTS. Four architecture-specific relocatable modules cover V1/V5 absolute scratch and V2/V3/V4 zero page.

Exhaustive signed-byte paired old/new emulator proof: 655,360 input/API/profile pairs (1,310,720 executions), preserving public inputs, result, flags, stack and scratch bytes. New distributed images were benchmarked on an additional 655,360 calls. Reference/alternate generated source testing covered 119,220 calls and native x64sc baseline/source parity covered 480 public calls. Native cycle timing was not measured. The published PRGs change only 8 or 10 bytes within the original swap body, with identical lengths and no added ZP, REU, code area or stack-page reservation.

| Profile | Mean FAST CPU cycles | Mean ACCURATE CPU cycles |
|---|---:|---:|
| v1_balanced | 81.550583 | 87.550583 |
| v2_pareto_fast | 75.538910 | 81.538910 |
| v3_reu_512k | 75.038910 | 81.038910 |
| v4_reu_16m | 75.038910 | 81.038910 |
| v5_hybrid_lowzp | 81.550583 | 87.550583 |

Source, public standalone mirrors, performance data, SHA256 and the release status have been synchronized. **Independent PR/main CI must still pass; this is not the completion of the DIST8+NORMALIZE family.**
