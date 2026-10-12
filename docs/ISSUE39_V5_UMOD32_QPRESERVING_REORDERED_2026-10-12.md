# Issue #39 — V5 UMOD32/32 quotient-preserving delayed-zero front end

**12 October 2026 — qualified V5 source-backed public-ABI improvement.**
The broader unsigned DIV/MOD campaign remains OPEN.

## Design and ABI

V5 historically exposes MATH_UMOD32_32 at $5E03 as an alias of its
quotient-producing MATH_UDIV32_32. Unlike the V2/V3/V4 remainder-only
front ends, V5's documented public API returns **Q32 and R32** even for
UMOD32_32. The candidate honors both outputs, success/divisor-zero carry,
input N/D ownership, and leaves MATH_UDIV32_32 unchanged.

A dedicated 147-byte NMOS 6510 private gate, generated from
`tools/v5_umod32_qpreserving_source.py`, is installed at $5E80 into a
checked empty resident island. Public $5E03 changes from JMP $5957 to
JMP $5E80, without moving any public symbol or increasing the PRG size.
Normal ZP stays 31 bytes.

The new 32-bit high-to-low comparison sends N<D directly to Q=0/R=N.
Only the rare equality test checks D=0. For N>D the original high-qone
helper receives the saved compare accumulator and carry; PHA/PLA protects
A/C during the D=0 check. Zero divisors still go to the original routine.
The alternate V5 configuration compiles from the same symbolic source.

## Measured, with explicit distribution caveat

V5 public-entry Reduced6502 A/B screen: **4,314 identical operand pairs**
on old/new complete resident images, with Q32/R32/C/N/D and external
sentinel exact on all. Overall weighted mean saving
**0.493278 cycles** (1,518 faster, 540 ties,
2,256 slower); this constructed stress mix is *not* an unbiased workload.
On the official 1,705 same-input UMOD32_32 corpus, mean saving
**2.770088 cycles** (official new V5 mean
**299.582991 cycles**, previous V5 **302.353079**).
Some divide-by-zero and N>D fallback cases slow down, up to their recorded
class maximum; no global cycle dominance is claimed.

Repose-derived exploration first screened two alternatives (127-byte
full-gate and 51-byte high-byte-only) that were +7.34 and +7.36 cycles
slower on the constructed 4,314-pair corpus. This is a hand-written source
synthesis, not a direct import of unpublished OptiSearch machine-code blobs.

Native VICE x64sc full-resident A/B completed **512 calls** (256 input
pairs, each original and candidate), with correct Q32/R32/carry including
divide-by-zero and quotient boundary cases. Evidence: `validation/review/ISSUE39_V5_UMOD32_NATIVE_VICE.json`.
It is a correctness validation, *not* cycle timing or REU DMA measurement.

Reference source assembly **exactly matches the VICE-tested candidate**
SHA-256 `5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222`, and alternate relocated source builds successfully.
Only $5E03–$5E05 and $5E80–$5F12 differ from the previous resident.
V1–V4 images are byte-identical. All five-profile unsigned and signed
correctness/cycle reports, paired unsigned common corpus and historical
SHA-frozen UMOD8/zero-high-bypass audits were rerun.

Next work: examine remaining quotient-tail DIV/MOD optimizations, then the
integer-root campaign. The unsigned campaign checkbox is **NOT** crossed.
