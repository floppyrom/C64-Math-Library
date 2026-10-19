# Historical quarter-square signed 16-bit Q8.8 scaled multiply

Status: **research**, dependent on signed full-width quarter-square PR #312.
This retains the portable 184-byte implementation and changes no V1–V5
historical binaries or REU/Turbo services.

`MATH_SMUL16_SHR8` reads signed X16 and signed Y16. It computes their exact
signed 32-bit product, performs an arithmetic right shift of eight bits,
and writes the low 24 result bits at Z0..Z2. X/Y, high Z4..Z7, and the
stack must remain intact. Z3 is intermediate and outside the public SHR8
output. C=0, A/X/Y volatile, decimal mode off.

| Alternative | Code + tables | Zero page | Ordinary scratch |
|---|---:|---:|---:|
| `link:compact-zerozp` | 184 bytes | 0 | 6 bytes |
| `link:qs-signed-shr8-public` | 1,383 bytes | 0 | 4 bytes |

The fast candidate links exactly the canonical unsigned quarter-square
16x16 producer (233-byte code and two 511-byte planes), then the same
bounded signed high-word correction used by `SMUL16`, and finally a
private 32-byte slot for a signed Q24 byte-slice entry. No REU,
self-modifying stores, special I/O, initialization, or zero-page bytes.
This is an independent image, not yet a coalesced shared-code owner
across UMUL16, SMUL16 and SMUL16_SHR8.

Qualification includes 512 identical signed public input pairs at two
independent code origins; public output, input/sentinel preservation and
stack tests; matched mean, p95 and max cycles; RAM-budget fallback to
the compact kernel; a 150-call / 24-frame busy math trace; and 192
native VICE r46284 calls at two layouts. The frame trace is **not**
physical PAL/VIC-II/IRQ timing.

Before profile retirement, further work must establish complete mixed
operation speed and static/dynamic sharing of the quarter-square tables.
