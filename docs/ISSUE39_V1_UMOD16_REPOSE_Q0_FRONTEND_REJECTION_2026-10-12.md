# Issue #39 — V1 UMOD16 quotient-zero shortcut: API-complete no-gain screen

**12 October 2026** · **Decision: reject both experimental front ends.**
The unsigned DIV/MOD family remains open. No shipped routine bytes or source
are modified by this screen.

## Why this experiment matters

Following Repose's 11 October OptiSearch challenge, two manually designed,
ephemeral V1 modulo front ends were tested at the unchanged public
`MATH_UMOD16=$3220` entry, forwarding non-zero quotients to the existing
323-byte, shared V1 divider at $4200. The experimental code was placed only
in an *in-memory* copy of the unused $1E80 region; no resource ownership
claim or permanently free allocation is inferred from zero bytes alone.

The 34-byte **loose** variant returns correct remainder and carry on
quotient-zero inputs while omitting quotient writes. The 42-byte **strict**
variant writes Q16 and R16 as the current V1 alias does. V1's
`USER_MANUAL.md` describes `MATH_UMOD16` as a UDIV16 alias that produces
both Q and R. **Do not erase that existing V1 behavior merely to improve
a remainder-only benchmark.** V2–V5 use separately qualified remainder-only
modulo front ends in some profiles; their documented contracts and resource
envelopes must be evaluated individually, not assumed identical to V1.

## Public entry 6502 performance on the official identical-input corpus

Each variant was measured against the current merged PR #68 V1 resident,
SHA-256 `cae2afdf0271da338d110f2104a8530374214ef915d88a803c508bce9679bb4f`. All three variants received
**exactly 1,705 identical (N16,D16) pairs**.

| Candidate | Mean delta vs shipped V1 | Faster | Slower | Q output mismatches |
|---|---:|---:|---:|---:|
| Loose remainder-only | -2.397654 cycles | 768 | 937 | 768 |
| Strict V1 Q16+R16 | +2.106745 cycles | 85 | 1620 | 0 |

Negative deltas mean faster. Loose candidate remainder, carry, N and D were
correct on every sampled pair; it nevertheless violated the V1 quotient
side effect **768 times**. Strict candidate corrected every such output
difference, but averaged **2.106745 extra cycles**
and allocated eight more bytes than loose for the missing Q writes.

## Additional input classes and verdict

The executable screen also covers the seven fixed 256-pair workloads from
`tools/audit_issue39_unsigned_small_workloads.py`: uniform, small-divisor,
quotient-zero, quotient-one, quotient-2–7, power-of-two divisor, and divide
by zero. Total **11,259** original/loose/strict V1 public calls, including
768 unchanged `MATH_UDIV16` comparison calls. All strict arithmetic,
Q/R, carry, preserved-input, and out-of-range sentinel checks pass; this
is therefore a **performance/resource no-gain**, not an arithmetic failure.

The strict gate is slower on the quotient-zero workload too (mean
+0.976562
cycles), because correctly writing Q nullifies the nominal low-byte-copy
saving. Other quotient workloads also incur fallback dispatch penalties.
No public speed/size Pareto improvement exists in this tested architecture.

**OptiSearch context:** Repose's `umod16_biased` and `umod16_direct`
implementations were assessed separately and had success-case carry
violations under C64ML's public contract. The new screen is a *manual*
architecture derived from that finding, not a copied private OptiSearch
generator, and does not attribute the original package's cycles to itself.

The next credible unsigned family work must target the internal 16-bit
short-quotient arithmetic or the 24/32-bit quotient-class tails, and preserve
the fixed profile's actual public outputs, relocation and RAM ownership.
Report: `validation/review/ISSUE39_V1_UMOD16_Q0_FASTPATH_REJECTED.json`. Generator: `tools/screen_issue39_v1_umod16_q0_rejection.py`.
