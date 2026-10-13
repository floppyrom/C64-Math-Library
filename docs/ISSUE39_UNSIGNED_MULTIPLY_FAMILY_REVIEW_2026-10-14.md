# Issue #39 — Unsigned multiply family completion review (14 October 2026)

**Scope:** MATH_UMUL8, MATH_UMUL16, MATH_UMUL24, MATH_UMUL32, MATH_UMUL32_READY. This review closes the **basic unsigned multiplication implementation family only after** the production candidate's exact-head and post-merge main checks pass. It does not certify the separately scheduled REU Turbo16/Turbo32 or V4 QS16 optimization families, signed multiply, or shifted-output multipliers.

**Completion certification (14 October 2026):** The basic unsigned multiply implementation family is complete. The merged V1/V5 rare-carry change, independent full-source five-profile family gate, checksummed package and post-merge main library/performance checks passed. Issue #39 stays open for remaining families.

## Compatible source/ABI decisions

| Family | Release selection and evidence | Resolution |
| --- | --- | --- |
| UMUL8 | V1/V5 production direct-output source is 6 CPU-model cycles faster on each of 65,536 input pairs per profile; 11 substitutions, zero extra normal ZP/resident bytes, 256 native public calls. V2 public direct-output produces 72.494140625 CPU-model mean on the 65,536-pair 8-bit domain; V3/V4 use their retained faster choice. | Integrated; preserve all public entry addresses and source exports. |
| UMUL16 | Public source-built 10,169-input corpus in *both* relocation maps: V1/V5 273.980037, V2/V3/V4 216.980037 cycles. Existing V1/V5 tail JMP, V2–V4 direct low-byte result and fused quarter-square structures are already selected. | No compatible new reduction established; retain existing profiles, Pareto and standalone records. |
| UMUL24 | Current matched 10,324-input ref/alternate corpus: V1/V5 465.042329, V2/V3/V4 417.783224 cycles. V2–V4 no-carry return removes CLC (7,789 save 2, 2,535 tie). V1/V5 rare-carry carry-flow saves 1 on **all** 10,324 pairs, no byte/ZP growth. Reference and alternate maps agree. | Merge only after complete PR native/checksum/main gates; 384 production x64sc unsigned/signed old/new calls passed. |
| UMUL32 | 2,409-pair common corpus: V1/V5 normal 712.235367; V2/V3/V4 normal 690.235367 CPU-model cycles. Preserve the ordinary-entry pointer-high repair in V1/V5. | Retain qualified full public ABI. No verified normal-entry compatible simplification. |
| UMUL32_READY | *Same* 2,409 operands, prepared pointer state: V1/V5 690.235367, exactly 22 cycles cheaper than normal; V2/V3/V4 690.235367, zero saving. V1/V5 14 prior APIs × 4 states × 26 pairs: 1,456 normal calls/profile correct; 312 READY calls/profile incorrect after pointer clobbers from UMUL24, SMUL16, SMUL24. | READY is explicitly stateful, not an unconditional substitute. Never delete its caller-state precondition or silently alias normal to READY. |

**Timing:** All figures above are CPU-model public-entry totals, including RTS but excluding the caller JSR and input setup, unless specifically identified as native correctness probes. Native VICE executes the binaries but **does not measure their cycles**. Do not compare legacy numbers measured on different input distributions as though they are paired.

## OptiSearch review and rejected transplants

The private near-page UMUL16 code is correct on the 10,169 matching operand pairs in its own emulator, reported 156.385485 model cycles, but it requires **95 executable ZP bytes ($80–$DE), 81 stack-page executable bytes, four quarter-square tables totaling 2,044 bytes**, stable undocumented instruction behavior, self-modification and a nonstandard register ABI. These constraints are not covered by the normal public-profile ownership contract, and no source-compatible adapter has demonstrated a full-call paired speedup. Its speed and the public 216.980037-cycle full-call value are **not comparable** because timing models/ABIs differ. Preserve this private result as an isolated resource-class candidate, not shipped code.

The retained OptiSearch native UMUL24 record reports 27 ZP bytes, 311 code bytes and a noncomparable 361.041715-cycle figure. The public FAST24 record already uses 24 ZP bytes, 307 code bytes and reports 357.041715 under a different provenance. It retains Y's top partial-product, an INY merge-carry transfer, direct column merge, and high-byte carry propagation. There is no grounded additional public-compatible win to transplant from the private record. V1/V5 public producer/consumer tailcall and two profile-specific carry cleanups were explicitly screened and integrated. No private OptiSearch source is redistributed.

## Evidence and executable audit

Run `python3 tools/issue39_unsigned_multiply_completion_audit.py --exercise --output /tmp/issue39-unsigned-multiply-family.json` to verify all five profile resident SHA-256s, source-built reference/alternate inputs and results, READY shared-corpus mean and dirty-pointer witnesses, OptiSearch resource-class rejection, and package integrity. The job checks exact source-generated public binaries, not an arbitrary fastest native candidate. Prior standalone, mixed-call, signed multiply and released x64sc evidence are retained in the repository, as are fully SHA-pinned historical DIV/MOD parents.

Qualification does **not** assume the same ZP for all variants: V1/V5 FAST24 has the 24-ZP carry producer; V2–V4 use their source-backed fast public implementation, and V5 uses the hybrid donor envelope. Custom Pareto records continue available as individual code options. REU Turbo and QS overlays are reserved for their dedicated step.

### Completion criterion

This document is the technical decision record. Mark Issue #39's unsigned multiply checkbox only when the integrated V1/V5 rare-carry release and the family gate pass exact PR-head validation, comparable unsigned performance, SHA256SUMS, PACKAGE_AUDIT, native x64sc and post-merge `main` checks. Keep Issue #39 open for signed multiply, shifted outputs, REU multiply, trig, distance and seek.
