# Issue #144: V2/V3/V4 exclusive SHR16 direct-output batch

**Research/opt-in source, not the default public library.**
Original V2 experiment: PR #145. Extended V2/V3/V4 exact
installed core verification and native test: PR #146.

The unsigned multiplier still computes lower-column carries, but
the six final output bytes are written directly to shifted-result
destinations. BEGIN redirects six absolute stores, suppresses two
low-output stores and tail-dispatches the existing producer.
END restores the exact original executable bytes.

| Profile | Baseline CPU cycles | Exclusive CPU cycles | Saving | Pairs | Native calls |
|---|---:|---:|---:|---:|---:|
| v2_pareto_fast | 753.235 | 700.235 | 53 | 2,409 | 48 |
| v3_reu_512k | 753.235 | 700.235 | 53 | 2,409 | 48 |
| v4_reu_16m | 753.235 | 700.235 | 53 | 2,409 | 48 |

Every tested operand pair in each profile saved exactly 53
CPU-model public-entry cycles. Total: 7,227 matched pairs.
Both original and source-assembled BEGIN/CALL/END results were
verified in native x64sc, 144 calls total. Native instruction
cycles and REU DMA/bus timing were NOT measured.

BEGIN costs 76 cycles, END costs 80 cycles. Four shifted products
amortize the two setup calls including their caller JSR instructions.

Critical limitations: source targets only the exact released
V2/V3/V4 binaries. Call MATH_INIT first and place patch code in free
RAM. While BEGIN-END is active, do not call regular UMUL32,
UMUL32_READY, or any other transitively shared producer consumer;
the patch is non-reentrant and unsafe for interrupts using this
producer. V1/V5 have different code and cannot use this source.
There is no mixed-call-safe default API replacement here.

Production resident PRGs, REU payloads, normal ZP budgets, stable
API addresses, and PERFORMANCE.md are unchanged. No private
OptiSearch material has been published.

Source: optional/issue144_v234_umul32_shr16_exclusive/overlay_begin_end.asm
CPU-model evidence: validation/review/ISSUE144_V234_SHR16_BATCH_CPU_MODEL.json
Native x64sc evidence: validation/review/ISSUE144_V234_SHR16_BATCH_NATIVE_VICE.json
