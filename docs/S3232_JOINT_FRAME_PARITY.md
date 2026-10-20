# Signed 32/32 public DIV/MOD whole-frame source qualification

This research measures `MATH_SDIV32_32` + `MATH_SMOD32_32` as **complete
linked public Q32/R32/C operations**, not isolated resident-kernel cycles.
Both operations can call the same physical quotient/remainder source.

We retain **two contrasting configurations**:

| Plan | Shared source | Zero-page | Why it matters |
|---|---|---|---|
| signed-portable-shared-zerozp | Restoring portable signed Q/R | 0 B | Compact code / no zero-page requirement |
| signed-v2-hybrid-shared | Source-authenticated V2 signed hybrid | 12 B | Performance option when larger executable and ZP are acceptable |

The research checks **150 deterministic calls in 24 synthetic frames**, at
two code/I/O/ZP relocations. Cases include negative numerators, negative
divisors, divide by zero and 32-bit signed overflow boundaries. For
both APIs it verifies exact truncating quotient/remainder semantics,
zero-divisor carry, N/D operand preservation and balanced stack, then
records full linked PRG and source SHA-256 hashes, RAM/ZP, one physical
shared source and peak/p95/total math-only frame cycles.

```sh
python3 tools/s3232_joint_frame_parity.py --out build/s3232/linked-frames.json
python3 tools/mixed_frame_frontier.py \
  --in-report build/s3232/linked-frames.json \
  --ram-budget 12000 --zp-budget 12 --out build/s3232/frontier.json
```

**Offline research only:** this workload has not yet been registered as
a replay producer for `math_builder.py --objective frame`. It is
insufficient to qualify arbitrary 56-operation projects or even a
mixed signed/unsigned four-operation project; both require new
identical-input source-linked benchmarking. Mean CPU cycles and
synthetic math-frame peaks are not actual PAL/VIC-II/IRQ/SID/REU
frame timing. Historical V1–V5 PRGs and original V3/V4 REU service
bundles are left untouched.
