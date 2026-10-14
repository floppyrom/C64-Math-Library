# SEEK16 Euclidean INIT release, Issue #39

Source-backed conditional-loop optimization for V1–V5. Native x64sc old/new: 240 public calls, real REU images for V3/V4; no hardware cycles timed. Official 408-move per-profile corpus confirms every frame, unchanged other SEEK operations and non-Euclidean INIT; same public ABI/ZP/resources.

Issue #136 safety repair: V1/V5 UDIV32/16 low-round code was moved from $1900-$1B6C to shared free $4D80-$4FEC, preserving public SEEK position arrays and all API addresses. Full 408-byte movement state survived 18,280 interleaved DIV/MOD public calls and 13,580 SEEK steps in the CPU-model regression (not native timing).

Transitive V1 division timing changes on the same-input corpus: {"MATH_UDIV16_SHL8": {"delta_cycles": 0.0010993037742537126, "new_mean_cycles": 729.262733602052, "old_mean_cycles": 729.2616342982777, "profile": "v1_balanced"}, "MATH_UDIV32_16": {"delta_cycles": 0.0010993037742537126, "new_mean_cycles": 825.0410406742396, "old_mean_cycles": 825.0399413704654, "profile": "v1_balanced"}, "MATH_UDIV32_32": {"delta_cycles": 0.010260168559909744, "new_mean_cycles": 335.7610846463906, "old_mean_cycles": 335.7508244778307, "profile": "v1_balanced"}, "MATH_UMOD32_16": {"delta_cycles": 0.0240469208210925, "new_mean_cycles": 842.9196480938416, "old_mean_cycles": 842.8956011730205, "profile": "v1_balanced"}, "MATH_UMOD32_32": {"delta_cycles": 0.01642228739001439, "new_mean_cycles": 399.57360703812316, "old_mean_cycles": 399.55718475073314, "profile": "v1_balanced"}}

| Profile | Before Euclidean INIT | After | Saved cycles |
|---|---:|---:|---:|
| v1_balanced | 1036.462418 | 1036.246732 | 0.215686 |
| v2_pareto_fast | 925.805556 | 925.589869 | 0.215686 |
| v3_reu_512k | 925.133987 | 923.920752 | 1.213235 |
| v4_reu_16m | 925.133987 | 923.920752 | 1.213235 |
| v5_hybrid_lowzp | 1036.462418 | 1036.246732 | 0.215686 |

Production stage requires full PR/main green CI. SEEK family audit and OptiSearch candidate review remain open.
