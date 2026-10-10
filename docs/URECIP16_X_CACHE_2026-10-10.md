# V3/V4 URECIP16_Q16 X-register caching (2026-10-11)

The public V3 and V4 REU-backed reciprocal routines now load the denominator's
high byte `D1` into volatile register X once and use `CPX` in all fifteen
quotient-threshold checks. Low-byte tie-breaks still use `LDA D0`/`CMP`.
The published API permits X to change. `D0/D1`, result `Q0/Q1/Q2`,
divide-by-zero carry convention and REU images are unchanged.

The implementation preserves API entry $5E1E, the return block at $C6F6,
fallback at $C703, and all subsequent code addresses. A 39-byte NOP pad
keeps the shortened island within its original allocation.

## Exhaustive result (CPU instruction model)

| Property | Earlier V3/V4 | Updated V3/V4 |
|---|---:|---:|
| Mean cycles (all 65,536 denominators) | 66.233795 | 57.331436 |
| Minimum cycles | 41 | 41 |
| Maximum cycles | 239 | 186 |
| Reachable code bytes | 430 | 391 |
| Extra ZP / REU tables / stack-page | 0 | 0 |

Net reduction: 8.902359 cycles (13.44%).
These figures count CPU instruction cycles through the public entry and RTS,
not physical REU bus/DMA timing. The denominator-zero convention is preserved.

The validated release was checked against every 16-bit denominator in both
profiles by a native machine-code instruction/REU model. Independently,
VICE x64sc ran the 4,095 REU-lookup inputs (d=2..4096) in V3 and V4,
original and modified, with matching checksums and completion markers.
Canonical assembly and PRG bytes matched after the existing immediate-DMA
correction; 8/8 deterministic rebuild checks, 1,617 standalone-source
checks, 320 public catalog checks, and 30 packaging checks passed locally.

This reciprocal change is **not** a completed audit of the whole unsigned
DIV/MOD family. The distinct V1/V2/V5 implementations remain unchanged.
See issue #39 for the remaining cross-profile optimization campaign.
