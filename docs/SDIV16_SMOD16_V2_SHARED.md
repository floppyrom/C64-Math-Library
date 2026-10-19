# Source-linked historical V2 signed 16/16 shared Q/R producer

Status: **draft research until exact-head VICE, complete CI and source checksum
validation are green**. No V1–V5 or REU/Turbo historical binary is changed.

The operation-first library's `SDIV16` and `SMOD16` are the same
signed 16-bit numerator/divisor producer. Both write **Q16 and R16**;
the quotient truncates toward zero and the remainder has the numerator's
sign. Divide-by-zero returns Q=R=0 and carry set. For `-32768/-1`, Q16
wraps modulo 2^16; C is clear. Input N/D, Q2/Q3, R2/R3, caller stack and
unrelated memory are preserved. Decimal mode is off; A/X/Y volatile.

## Two independent resource choices

| Implementation | Code | Ordinary scratch | Zero page |
|---|---:|---:|---:|
| `link:portable-zerozp` | 206 bytes | 3 bytes | 0 |
| `link:v2-signed-shared` | 1,705 bytes | 8 bytes | 0 |

Both options are one **shared physical image** for the pair SDIV16/SMOD16
when the project selects matching implementations, never two copies.
The original compact restoring code is retained without modification.

The V2-fast option source-links the unmodified canonical 1,481-byte
`udiv16_v2_zerozp.asm` source with its historical LAX/ANC strategy.
Its unsigned N/D/Q/R operands are rebound to an eight-byte private
ordinary-RAM workspace. A bounded 224-byte signed adapter handles
absolute magnitudes, two's-complement output correction and public
zero-divisor behavior. No self-modification, REU, initialization or
private zero-page is required.

## Matched public-call evidence

The initial two-origin 384-pair CPU model gave mean **473.94–473.99**
cycles for historical V2 versus **821.88** for portable, and maximum
**1,229** versus **1,366** cycles. However p95 was **1,138** versus
**1,120**: a small tail regression on this sample. Thus the default
speed objective optimizes the measured mean, while hard real-time users
should separately examine their corpus and worst-case frame.

Qualification also checks two placements, Q/R/C and all public
sentinels, the `-32768` boundary, source hash dependencies, exact
RAM-budget fallback, shared producer identity and preserved code
bytes. An identical 150-call/24-frame busy math trace checks the
maximum model frame. These are *not* claims about VIC-II badlines,
IRQ timing, physical PAL cycle budgets, or REU hardware behavior.
Pinned native VICE r46284 at two origins is the final execution gate.

This candidate adds **two more operations** with authentic
same-input speed selection, taking 37/56 to 39/56 **only after all
exact-head CI and publication checks pass**. Full profile retirement
also requires preserving the best resident fast variants, shared
resource accounting and the historical drive/REU feature surface.
