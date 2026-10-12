# Issue #39: PR68 — V1 16-bit quotient-two branch re-layout

**Date:** 2026-10-12. **Status:** source-backed native-verified V1 323-byte
UDIV16/UMOD16 improvement. The larger unsigned DIV/MOD campaign is still open.

The V1 shared unsigned private division core at `REG_KERNEL+$0200`
(reference $4200..$4342) now places the quotient-2 exit before the rare
post-restoring quotient-bias tail. This brings the quotient-2 exit into the
6502 BCC relative-branch range, eliminating the prior absolute JMP.
Three unreachable alignment bytes follow a different RTS, preserving
the high-quotient shift/subtract loop's original page phases and placement.

### Verified measurement

- Initial independent OptiSearch Reduced6502 full-public-ABI paired screen:
  963 input pairs per API, 320 faster / 643 equal / zero slower;
  mean saving 0.332295 cycles.
- Independent wider stress: 13,559 identical structured/random and quotient-
  stratified pairs per API, 8,255 faster / 5,304 equal / zero slower,
  mean saving **0.608821 cycles per call**. Zero arithmetic, status, input or
  stack-state errors in 27,118 calls.
- Native VICE x64sc: complete V1 old/new residents (MATH_INIT, RAM banked in),
  256 operand pairs each for UDIV16 and UMOD16, 1,024 old+new public calls,
  no differences and no mathematical/flag errors. Evidence: `validation/review/ISSUE39_V1_U16_Q2_NATIVE_VICE.json`.
- Native VICE V5: 1,024 additional old/new UDIV16/UMOD16 public calls
  passed with no mathematical/flag differences. Evidence: `validation/review/ISSUE39_V5_INHERITED_U16_Q2_NATIVE_VICE.json`.
- Source assembly: independent 323-byte expected SHA-256 matches the rebuilt
  reference code at $4200..$4342; **57 changed bytes in that window, 0
  changed elsewhere**. Alternate relocation compiles successfully. Resident
  length, ordinary ZP, scratch ownership, stack, public jump addresses and
  all other profiles are unchanged.
- Source candidate SHA-256: `cae2afdf0271da338d110f2104a8530374214ef915d88a803c508bce9679bb4f`; pre-change SHA-256: `9afa30ffd24c1ce9566e7ef21e4032396fbdea7d4c3da5b68e137fc12ec41b62`.
- On the published 2,729-pair UDIV16 same-input corpus: old V1 **156.348479**,
  new V1 **156.087578** cycles.
- On the published 1,705-pair UMOD16 same-input corpus: old V1 **189.383578**,
  new V1 **189.127859** cycles.

### Release, provenance and future

Only V1's direct source changes. V5 imports the same V1 private 323-byte
core and inherits exactly the same size-neutral 57-byte change. V2/V3/V4
binaries remain byte-identical. The helper `tools/issue39_v1_u16_q2_parent.py`
restores the exact previous V1 bytes when auditing archived PR57-62 experiments
so frozen evidence does not silently drift to a later resident hash. No private
OptiSearch generator or unpublished Repose program was copied into the release.
This is a manual post-OptiSearch synthesis inspired by the comparator's page-
placement finding, with public-ABI resource and relocation checks.

The campaign's **Unsigned DIV/MOD family checkbox remains open** until all
widths/variants receive the same optimization/no-gain decision. This is not
claimed to be globally optimal.
