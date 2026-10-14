# Issue 144: signed 32×32 SHR16 specialist screen

**Nonnegative-domain opt-in only; no change to the normal signed library.**

When BOTH signed 32-bit operands have their sign bit clear, the signed
product equals the unsigned product exactly. After MATH_INIT and loading
the previously published unsigned independent clone at $0D05–$0E49,
source-assemble the signed enable/disable at $0C00 (or free RAM).
It temporarily redirects only the two JMP target bytes of the original
signed public entry $5E15, from $C50C to the clone at $0E03.
Both inputs MUST be nonnegative during the entire enabled period.

## Qualified nonnegative domain — matched public entry cycles

| Profile | Signed baseline | Specialist | Saving | % | Pairs |
|---|---:|---:|---:|---:|---:|
| v2_pareto_fast | 739.337 | 680.965 | 58.372 | 7.90% | 715 |
| v3_reu_512k | 739.337 | 680.965 | 58.372 | 7.90% | 715 |
| v4_reu_16m | 739.337 | 680.965 | 58.372 | 7.90% | 715 |

715 paired nonnegative 32-bit operand pairs per profile, 2,145 exact
model cases; 144 native x64sc baseline/candidate calls; 3-profile
source-assembled enable/disable with restored original public JMP,
input/output, carry and stack checks. Native cycles NOT measured.
The standard signed and unsigned full multiplication routines remain
available BETWEEN calls; code and ZP are shared and NONREENTRANT.

## General signed inputs — screened but not promoted

The exact sign-correction and the quadrant hybrid variants both pass
7,227 model cases and 216 baseline/candidate native x64sc calls;
however general correction has large worst-case regressions. The
hybrid speeds the mixed-sign corpus by only ~2.12% and also regresses
on negative-negative inputs. Neither replaces the default signed API.

| Profile | Stock signed mean | Hybrid mean | Saving | Worst regression |
|---|---:|---:|---:|---:|
| v2_pareto_fast | 774.643 | 758.205 | 16.438 | +18 |
| v3_reu_512k | 774.643 | 758.205 | 16.438 | +18 |
| v4_reu_16m | 774.643 | 758.205 | 16.438 | +18 |

Resource contract: V2/V3/V4 only; original quarter-square tables and
MATH_INIT; reserve $0D05–$0E49 for unsigned producer and $0C00
installer source, or relocate only after fresh proof. Shared regular ZP;
not safe to run concurrently from IRQ/NMI. JMP update not atomic:
disable interrupts/other callers while enabling or disabling.
Conditional nonnegative specialist does NOT need general signed
research code at $0E50–$0F18. Existing resident PRGs, REUs, public
entry address, normal ZP and regular PERFORMANCE rankings unchanged.

Source installer: optional/issue144_signed_shr16_hybrid/nonnegative_enable_disable.asm
Research general signed source (not default): optional/issue144_signed_shr16_hybrid/research_signed_shr16.asm
Proof model/native general: validation/review/ISSUE144_SIGNED_SHR16_HYBRID_RESEARCH.json ; validation/review/ISSUE144_SIGNED_SHR16_HYBRID_NATIVE_VICE.json
Proof model/native nonnegative: validation/review/ISSUE144_SIGNED_NONNEGATIVE_SHR16_OPTIN_MODEL.json ; validation/review/ISSUE144_SIGNED_NONNEGATIVE_SHR16_NATIVE_VICE.json
Installer proof: validation/review/ISSUE144_SIGNED_NONNEGATIVE_INSTALLER_MODEL.json
Private OptiSearch source is not included.
