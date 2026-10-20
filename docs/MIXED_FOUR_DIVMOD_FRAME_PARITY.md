# Joint signed + unsigned 32-bit DIV/MOD frame Pareto (four public APIs)

The preceding signed and unsigned DIV/MOD performance studies measured
*separate* project plans. A game/demo using **both** number domains
cannot legitimately add their individual peak-frame timings or source RAM.
This research measures a **single four-operation linked image**:
`MATH_UDIV32_32`, `MATH_UMOD32_32`, `MATH_SDIV32_32`,
and `MATH_SMOD32_32`.

Each unsigned pair shares one quotient/remainder source; each signed
pair shares a separate source. Four complete plans are evaluated:

| Plan | Unsigned source | Signed source |
|---|---|---|
| both-compact-zerozp | aligned shared zero-ZP | portable shared zero-ZP |
| unsigned-v2-signed-compact | V2 hybrid shared, 12-ZP | portable shared zero-ZP |
| unsigned-compact-signed-v2 | aligned shared zero-ZP | V2 signed hybrid, 12-ZP |
| both-v2-hybrid | V2 hybrid shared, 12-ZP | V2 signed hybrid, 12-ZP |

The source linker allocates the combined resources, including **one
physical producer for each sign domain**, with separately linked
I/O and scratch layouts. **Both V2 shared sources reuse a single
12-byte ZP scratch allocation**, rather than summing to 24 bytes,
provided the public routines run sequentially (not reentrantly). Identical signed and unsigned
32-bit dividends/divisors are exercised across 150 deterministic
public calls and 24 synthetic frames at both qualified relocations.
The signed remainder follows truncation-toward-zero quotient semantics,
and the benchmark checks output Q/R, zero-divisor carry, input
preservation, stack, source SHA and exact linked PRG SHA. The generic
Pareto summarizer compares **whole-image RAM, total ZP and worst
frame math cycles** rather than summing isolated operation metrics.

```sh
python3 -m unittest discover -s tools -p 'test_mixed_four_divmod_frame_parity.py' -v
python3 tools/mixed_four_divmod_frame_parity.py --out build/mixed-four/linked-report.json
python3 tools/mixed_frame_frontier.py \
  --in-report build/mixed-four/linked-report.json \
  --ram-budget 12000 --zp-budget 31 \
  --out build/mixed-four/frontier.json
```

**Offline evidence only.** This is a fourth potential deterministic
frame-producer corpus, not yet independently replay-registered for the
production opt-in `--objective frame`. The other registered workloads
cannot certify this *mixed* four-API frame profile, and neither
CPU-model math cycles nor native functional VICE checks establish
the actual PAL bus/IRQ/SID/REU peak-frame budget. Historical V1–V5
and hardware REU bundles remain unchanged.
