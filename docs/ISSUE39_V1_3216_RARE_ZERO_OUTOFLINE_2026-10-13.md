# Issue #39 — V1 32÷16 rare divide-by-zero handler relocation (13 October 2026)

**Disposition: qualified research candidate; NOT promoted to a resident default.**
No released binary, public ABI entry, profile allocation, or stable routine has been changed by this screen. Keep [issue #39](https://github.com/floppyrom/C64-Math-Library/issues/39) open and its unsigned DIV/MOD family unchecked.

## Exact mechanism

The shipped V1 `UDIV32_16` producer begins with `JSR` into the shared 16-bit high-word divider, then `BCC` around a 7-byte divide-by-zero cleanup. On all successful calls this taken branch costs three cycles.

The candidate copies that cold cleanup to **$44F0–$44F6** (verified unoccupied in the exact released V1 image), changes the original `BCC` to a backward `BCS` and shifts the **111-byte** low-word continuation seven bytes earlier so successful calls fall through. It verifies **10** intra-body relative branches and adjusts the sole live unrolled-loop backlink **$1B6A: JMP $4573 → JMP $456C**. Existing high-word and low-word unroll islands remain in place. Program load address and image size do not change. Extra normal zero page: **0 bytes**. No extra stack frame or input classifier.

The old full resident is SHA-256-pinned to
`2567dccbc4e01f3d606e80126c8150c58e4f30b8b726ff38e116c6aaec644178`.
The patch is **in-memory for testing only**, not a shippable blind binary patch. Other versions and later resident hashes must not be silently treated as equivalent.

## Same-input CPU-model screen

Reproducible tool: `python3 tools/screen_issue39_v1_3216_outofline_zero.py --out /tmp/issue39_v1_3216_zero_ool.json`.

Independent [research-screen run](https://github.com/floppyrom/C64-Math-Library/actions/runs/38367332665): **15,826 matched input pairs / 31,652 real 6502-model public-entry calls**, zero tested Q32/R16/carry/divide-zero/N/D/high-remainder/sentinel/stack differences.

| V1 API | Official input cases | Mean candidate − released cycles | Faster / slower |
| --- | ---: | ---: | ---: |
| `MATH_UDIV32_16` | 2,729 | **−0.834005** | 2,578 / 151 |
| `MATH_UMOD32_16` | 1,705 | **−0.734311** | 1,554 / 151 |

Every tested valid-divisor call across the six independently seeded workload categories and four additional numerator/divisor strata saved **exactly 1 instruction cycle**; every tested divisor-zero call cost **2 extra cycles**. The 151 slower official cases for each API are divisor-zero observations, **not hidden arithmetic failures**. This is a small, explicit latency tradeoff, not strict all-case Pareto dominance. Timing means are deterministic opcode counts, not VIC/REU bus-inclusive or hardware wall time.

## Real native VICE qualification

Independent [native x64sc workflow](https://github.com/floppyrom/C64-Math-Library/actions/runs/38367874761) downloaded official headless VICE r46274 and checked pinned SHA-256 `5d85ab7b73e9b32007ac7f844603e101fdd7009c47d1898216bfff4b2a44996a` before running it. It executed **192 actual complete V1 resident public calls**: 48 deterministic 32×16 operands × 2 resident images × both aliases. All returned exact Q32, R16, carry, N32/D16 and memory sentinels, with identical original/candidate output dump hashes. VICE **did not measure CPU cycles**.

Reproduce with `python3 tools/native_issue39_v1_3216_outofline_zero.py --out /tmp/issue39_v1_3216_native_vice.json` with `VICE_WRAPPER` set to the pinned x64sc binary.

## Production gate not yet met

Promotion requires owning the new $44F0 cold slot in the canonical V1 source (not relying on zero-filled RAM), relocating its branch and $1B6A unroll backlink in **reference and alternate maps**, source-regenerating a byte-identical reference resident, rebuilding V5 from the actual donor without clobbering hybrid allocations, full signed/unsigned/mixed-call and standalone/package audits, native VICE on the installed resulting source-built images, both changelogs/performance/release metadata/checksums and independent PR/post-merge main CI. No benefit to V2–V5 is claimed.

This work neither includes nor publishes confidential OptiSearch source; its next role is to screen further source-owned 32÷16 continuations under the established ABI/resource limits.
