# Historical V3 signed 24/24 DIV/MOD: experimental independent source transplant

This is a source-linked transplant of the **exact historical V3 signed24
magnitude producer**, not a new wrapper around the slower portable restoring
divider. The donor is
`v3_reu_512k/standalone/div_s24_s24_s24_24.asm`,
SHA-256 `c34456837b5f9bd24265d7b3108d71ddb1d7a9575402ef49a58a82fb831ca11c`
(also the original V3 `MATH_SMOD24` alias). The original executable
mirror contains 819 reachable instructions, 1,894 machine-code bytes and
three distant code islands. The manually audited transplant compacts
those islands and adds the second public JMP entry, yielding an expected
**1,897-byte independent image**.

Unlike the stock zero-ZP portable kernels, the historical producer uses
**9 caller-exclusive zero-page bytes**, no ordinary RAM scratch, no REU
transfer/INIT and no external tables found in the statically reachable
source. It requires **writable code**: an original store to `$8802`
adjusts the immediate operand of the tail ADC instruction. This store
has been rewritten to `L8801_ADC_IMMEDIATE+1` to follow code relocation.
All 16 public I/O bytes have symbolic relocatable addresses, and the
NMOS 6510 LAX encodings have been preserved. Neither the original V3
profile PRG nor its source mirrors are modified.

The builder retains `link:portable-zerozp` (325 bytes code, 7 RAM
scratch, 0 ZP) and `link:abs-qzero-guard` (387 bytes, 7 RAM, 0 ZP)
alongside `link:v3-signed-magnitude`. It must not silently pick the
new donor until matched-input and native VICE gates pass and resource
requirements are accurately incorporated into Pareto selection.

## Qualification

The paired CPU-model test assembles both signed aliases as one physical
producer at `$8000/$C000` and `$7123/$C040`, with distinct ZP bases,
then exercises the same signed-edge, divisor-zero, uniform, and
quotient-zero-biased calls as the compact portable producer. Every call
checks mathematical Q/R, carry, public input preservation, high-byte
sentinels and balanced stack. It also checks that any runtime code
modification is confined to the single relocated historical ADC operand.
The test reports mean and worst public entry-through-RTS cycles and
worst regressions; source relocation can change branch/page timing.

Native VICE **r46284**, source-built from the pinned upstream submodule,
must independently exercise both exported entries on the same 96-call
public ABI set at two code/I/O relocations (**384 emulator calls**).

This is a **research branch only** pending exact-head CI. The new
`tools/native_all56_sdiv24_v3.py` qualifies the original historical
donor in an image with **all 56 builder operations resident** (both
signed24 public entries at two RAM relocations, 384 native calls), while
keeping the other 54 selected sources pinned. It is combined-image
compatibility, not execution coverage of all 56 public APIs. The regular
full-library checks and SHA256 package audit must also pass before
this resource-hungry donor is eligible for the builder.
The historical zero-page region cannot be assumed free in arbitrary
games. Donor timing must be compared on the same corpus, not against
unrelated V1-V5 published averages or real hardware elapsed time.


## Matched public-call CPU-model results

The first exact-code source qualification completed successfully on
**912 identical signed24 inputs per placement** (edge values, zero
divisors, signed sign quadrants, small divisors and explicit quotient
zero cases). Observed public-entry-through-RTS cycles were:

| Placement | Portable zero-ZP mean | V3 magnitude mean | Historical source code | Maximum V3 call | Worst call-level regression |
|---|---:|---:|---:|---:|---:|
| $8000/$C000 | 2,101.160 | **655.678** | 1,897 B | 3,358 | +867 cycles |
| $7123/$C040 | 2,100.639 | **648.091** | 1,897 B | 3,313 | +822 cycles |

The same input corpus shows an approximately **69% mean-cycle reduction**
from migrating the *actual arithmetic core* rather than only a wrapper.
This comes with a large code (+1,572 B) and zero-page (9 B) cost,
requires executable RAM, and sometimes loses on individual operands.
Thus it is a **fast/high-memory Pareto candidate**, not a replacement
for the existing low-ZP and compact alternatives. The worst-case
regression also means the busy-frame objective must use actual workload
calls before selecting the V3 donor by default.

This measurement is CPU-model data, not VICE frame elapsed time.
Native VICE and the global linked 56-operation qualification remain
separate acceptance gates.
