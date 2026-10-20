# First matched full-source 32/32 DIV/MOD synthetic frame qualification

The earlier **three-operation** frame benchmark qualified multiply and
integer-square-root combinations. This research adds a distinct full-public
**unsigned 32-bit division/remainder** workload, where standalone
`UDIV32_32` and `UMOD32_32` source alternatives may reuse *one*
physical quotient/remainder producer.

## Directly compared source-linked complete images

| Plan | Division | Modulo | Reason to retain |
|---|---|---|---|
| aligned-shared-zerozp | shared aligned restoring | same shared image | 0 ZP, one physical Q/R producer |
| aligned-independent-zerozp | separate aligned DIV | separate aligned MOD | fallback and two-source cost control |
| v2-lowdivisor-shared | V2 unrestricted low-divisor hybrid | same V2 producer | faster candidate with 12 ZP |
| zptail-div+aligned-mod | compact 4-ZP DIV tail | 0-ZP aligned MOD | alternative zero-page / executable trade-off |

Each option is linked through the **normal operation-first builder**
with exact source pins and real code/tables/scratch/ZP accounting.
Each runs an *identical, independently indexed* 150-call
public `MATH_UDIV32_32` / `MATH_UMOD32_32` scenario, in 24
synthetic frames at both `$8000/$C000/$50` and
`$7123/$C040/$70` code/I/O/ZP relocations. Cases cover divisor
zero, high-word divisors and low-divisor hybrid triggers.

The benchmark checks quotient (on DIV calls), full 32-bit remainder,
zero-divisor carry status, preservation of both 32-bit operands
and stack pointer after complete public entry-through-RTS calls.
The actual linked PRG checksum, source digests, physical
producer-sharing count, RAM, ZP, full frame peaks/p95/total cycles
are recorded. `frame_cycle_budget.score` accounts for six caller
JSR cycles per call. The existing **generic offline source-linked**
multi-operation frontier scores the measured plans without
extrapolating from isolated average division and modulo timings.

```sh
python3 -m unittest discover -s tools -p 'test_u3232_joint_frame_parity.py' -v
python3 tools/u3232_joint_frame_parity.py --out build/u3232/frame-parity.json
python3 tools/mixed_frame_frontier.py \
  --in-report build/u3232/frame-parity.json \
  --ram-budget 12000 --zp-budget 12 \
  --out build/u3232/frame-frontier.json
```

**Important integration limitation:** this is offline qualification of a
*new* benchmark producer. The production opt-in frame objective is
currently replay-gated to the explicitly registered signed/unsigned
multiply + ISQRT16 workload. This research must not be accepted by that
installer before adding a matching registered deterministic replay
producer and source-integrity tests.

**Physical timing limitation:** the full-API 6510 CPU-model workload
includes measured arithmetic plus caller JSR, but excludes actual
PAL VIC-II memory stealing, IRQ/SID service, REU DMA and any
application code. It does not prove a 50 Hz real frame is possible.
The original V1–V5, their reference PRGs and V3/V4 REU lifecycle
bundles remain unchanged.
