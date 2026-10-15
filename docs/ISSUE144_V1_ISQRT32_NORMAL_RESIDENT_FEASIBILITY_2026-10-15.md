# Issue #144 C — V1 normal-resident ISQRT32 highword seed feasibility (15 October 2026)

**Research-only source screen, not canonical source promotion or a new PRG/REU release.**

The existing unrestricted direct-highword `ISQRT32` seed from PR #155 formerly lived in a `$0C00` application-RAM prototype. This study reassembles it at the **ordinary resident V1 root code** entry `REG_GAME+$0A40`, with its independent seed helper in a verified unoccupied region at `REG_GAME+$0AA8` (reference `$CBA8`). The prior helper candidates +$0A90, +$0A98 and +$0AA0 overlap other nonzero resident bytes and are rejected by source-assembler collision screening.

A full ordinary public-call, same-input CPU-model test checked **657 unrestricted 32-bit radicands in each of V1's reference and alternate layouts**: exactly **51 cycles saved per call**, zero slower cases, exact `math.isqrt`, carry clear, input and X/Y/SP preserved. Both source maps assembled and the public root trampoline remained fixed. No new normal ZP or caller-owned RAM was introduced.

Real [x64sc native workflow #38805584806](https://github.com/floppyrom/C64-Math-Library/actions/runs/38805584806) independently ran **96 calls** (24 baseline plus 24 candidate per layout). The root and captured full status bytes matched exactly; these tests establish actual NMOS 6510 correctness but do **not** measure real CPU/REU bus-time cycles.

**Important boundaries:** This work does not modify production V1 code or shipped V5. V5 inherits part of the V1 binary architecture, but its source-selected hybrid image, public ABI, relocation and mixed-call behaviors have **not** yet been qualified with this candidate. The next task is an explicit V1/V5 normal-source integration trial with full public ABI, mixed calls, VICE and resource gates. No private OptiSearch implementation is published.
