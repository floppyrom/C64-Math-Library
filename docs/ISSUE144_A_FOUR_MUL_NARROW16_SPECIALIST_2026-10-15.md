# Issue #144 A — four source-only upper-word-zero multiply specialists

**Explicit operand-domain Pareto alternatives; NOT installed resident replacements.**

PRECONDITION: BOTH 32-bit input operands $C000–$C003/$C004–$C007
have ZERO upper 16-bit words. Low 16 bits can be any unsigned
value 0..65535, including bit15 set. This is still nonnegative in
signed 32-bit arithmetic; do NOT confuse with signed 16-bit multiply.

The separately assembled 6510 source at caller-owned $0E60
uses the existing public resident unsigned MATH_UMUL16 entry $3020.
It constructs the full 64-bit product with zero upper 32 bits or
the exact 48-bit product shifted by 16, for four operation names.
No new normal ZP, tables, installed call-site addresses or REU use.
Requires MATH_INIT and resident tables; mutually exclusive use of
shared scratch from interrupts; not reentrant.

## Paired CPU-model baseline/alternative (1,145 operand pairs per op/profile)

| Profile | Operation | Stock cycles | Optional cycles | Saved cycles |
|---|---|---:|---:|---:|
| v1_balanced | MATH_UMUL32 | 674.147 | 305.438 | 368.709 |
| v1_balanced | MATH_SMUL32 | 682.147 | 308.438 | 373.709 |
| v1_balanced | MATH_UMUL32_SHR16 | 737.147 | 321.438 | 415.709 |
| v1_balanced | MATH_SMUL32_SHR16 | 745.147 | 324.438 | 420.709 |
| v2_pareto_fast | MATH_UMUL32 | 652.147 | 248.438 | 403.709 |
| v2_pareto_fast | MATH_SMUL32 | 652.147 | 251.438 | 400.709 |
| v2_pareto_fast | MATH_UMUL32_SHR16 | 715.147 | 264.438 | 450.709 |
| v2_pareto_fast | MATH_SMUL32_SHR16 | 715.147 | 267.438 | 447.709 |
| v3_reu_512k | MATH_UMUL32 | 652.147 | 248.438 | 403.709 |
| v3_reu_512k | MATH_SMUL32 | 652.147 | 251.438 | 400.709 |
| v3_reu_512k | MATH_UMUL32_SHR16 | 715.147 | 264.438 | 450.709 |
| v3_reu_512k | MATH_SMUL32_SHR16 | 715.147 | 267.438 | 447.709 |
| v4_reu_16m | MATH_UMUL32 | 652.147 | 248.438 | 403.709 |
| v4_reu_16m | MATH_SMUL32 | 652.147 | 251.438 | 400.709 |
| v4_reu_16m | MATH_UMUL32_SHR16 | 715.147 | 264.438 | 450.709 |
| v4_reu_16m | MATH_SMUL32_SHR16 | 715.147 | 267.438 | 447.709 |
| v5_hybrid_lowzp | MATH_UMUL32 | 674.147 | 305.438 | 368.709 |
| v5_hybrid_lowzp | MATH_SMUL32 | 682.147 | 308.438 | 373.709 |
| v5_hybrid_lowzp | MATH_UMUL32_SHR16 | 737.147 | 321.438 | 415.709 |
| v5_hybrid_lowzp | MATH_SMUL32_SHR16 | 745.147 | 324.438 | 420.709 |

22,900 model before/after pairs across five public profiles and four
signed/unsigned operation signatures passed output 8 or 6 bytes,
carry=0, input preservation and stack. 960 native x64sc
baseline/optin calls also pass. These are public-ABI-shaped
direct-candidate calls with identical raw operands; the stock
public entries are NOT redirected in the shipped libraries.
Native emulator correctness is qualified, native cycle timing NOT.

Signed narrow16-domain calls deliberately reuse UNSIGNED UMUL16;
signed 16-bit multiplication gives incorrect results for values
$8000–$FFFF even though the 32-bit signed operand is positive.
Do not run on inputs with any upper 16-bit bit set; doing so
silently yields incorrect arithmetic.

The address $0E60 is not generally free: caller/builders must
check actual occupied RAM/loader/IRQ maps or reassemble to an
independently tested safe address. Shared scratch requires
strictly sequential calls, and callers cannot have IRQ/NMI math
operations overlap. Current production PRGs, REU payloads,
performance leaderboards and normal public ABI are unchanged.

Source: optional/issue144_four_mul_narrow16/four_u32_narrow16.asm
CPU-model proof: validation/review/ISSUE144_FOUR_MUL_NARROW16_<profile>.json
Native VICE proof: validation/review/ISSUE144_FOUR_MUL_NARROW16_NATIVE_VICE.json
Reproducer: tools/issue144_four_mul_narrow16_model.py
Native reproducer: tools/native_issue144_four_mul_narrow16.py
No private OptiSearch generator source is included.
