# Issue144 D — source-only SEEK16_INIT inlined accumulator V1–V5

**Optional source, not a production resident substitution or universal Pareto improvement.**

The ordinary SEEK16_INIT repeats a Bresenham accumulator helper with JSR/RTS
overhead for each integer speed quantum, then invokes the same helper for
the fractional component. The alternative uses the exact public source
mirror, copies only its INIT island into caller-owned RAM, **inlines the
first helper** (V1–V5), and replaces the second JSR/RTS with a JMP/JMP
continuation at a separately placed instance. The original helpers,
normal SEEK16_STEP routines, original executable bytes and lookup/state
arrays are never modified. Absolute external branch/helper addresses are
preserved, local control-flow labels are reassembled by the real 6510 assembler.

## Same-input CPU-model public-call results (4,080 INIT + STEP pairs/profile)

| Profile | Before | Source opt-in | Saved | Worst saved | Executable bytes |
|---|---:|---:|---:|---:|---:|
| v1_balanced | 737.995 | 715.889 | 22.105 | -1 | 399 |
| v2_pareto_fast | 662.755 | 637.304 | 25.451 | +0 | 328 |
| v3_reu_512k | 661.008 | 637.304 | 23.704 | +0 | 328 |
| v4_reu_16m | 661.008 | 637.304 | 23.704 | +0 | 328 |
| v5_hybrid_lowzp | 737.995 | 715.889 | 22.105 | -1 | 399 |

These are 408 canonical movement paths × ten major/Euclidean speed
classes = 4,080 comparisons per profile; **20,400 matched INIT calls**
in total, each followed by a normal SEEK16_STEP and comparison of the
complete public SEEK state arrays plus carry, X and stack.
The V1/V5 inline expansion needs two complemented long branches;
this can cost **one extra CPU-model cycle on certain degenerate moves**.
Do not erase this minor worst-case regression when reporting means.
The V2–V4 candidate has no measured slower call in that corpus.

Native real x64sc validates **seven baseline and seven candidate**
SEEK16_INIT speed/mode scenarios per profile (70 total INIT calls)
and 112 baseline + 112 candidate SEEK16_STEP frames/profile
(1,120 total frame-step calls) with identical positions, carry, X,
SP and post-arrival behavior. V3 and V4 load their actual REU images.
Native VICE correctness is certified, **native cycle timing is not**.

The source example places the relocated main code and helper copies
into caller-owned low RAM **$0D00–$0F8B**. The occupied foreign byte
$19F0 and V1/V5 live table $1A00, plus V2–V4 $90E0..$91FF SEEK
object state, remain untouched. This RAM is NOT automatically free
in every application, loader or memory map. The code is not IRQ/NMI
reentrant because the original math helpers and state/ZP are shared.
For direct opt-in JSR use the candidate source entry at $0D00;
alternatively, redirect ONLY the installed public JMP $5E48 in
application-owned writable memory while no caller/interrupt can enter.
Do not silently install into ordinary resident PRGs or REU payloads.

Verified reproduction: tools/issue144_seek16_accum_all_profiles_v2.py
Native x64sc: tools/native_issue144_seek16_accum_all_profiles.py
Machine-readable model: validation/review/ISSUE144_SEEK16_ACCUM_INLINE_ALL_MODEL.json
Machine-readable native: validation/review/ISSUE144_SEEK16_ACCUM_NATIVE_VICE.json
Five individually accessible ASM sources: optional/issue144_seek16_accum_inline_all/<profile>.asm
No private OptiSearch code is published.
