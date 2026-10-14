# Issue #39: completed SEEK8/16 public-family audit

**Audit PASS, without an additional qualified production optimization.**
This is not a claim that no faster algorithm exists.

The existing source-integrated SEEK16_INIT Euclidean scaling optimization
(PR #135) remains published. The V1/V5 UDIV32/16 and SEEK-state overlap
(Issue #136) remains repaired. No new binary, API, REU or ZP changes
were made in this final family audit.

## Official public-entry 408-move CPU-model mean cycles

| Profile | SEEK8 INIT | STEP | STEP_INT | STEP1 | SEEK16 INIT | STEP | STEP_INT | STEP1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v1_balanced | 601.747 | 87.137 | 70.993 | 65.954 | 783.094 | 118.277 | 103.655 | 98.183 |
| v2_pareto_fast | 543.965 | 87.137 | 70.993 | 65.954 | 702.606 | 118.689 | 103.655 | 98.183 |
| v3_reu_512k | 544.687 | 87.137 | 70.993 | 65.954 | 700.937 | 118.277 | 103.655 | 98.183 |
| v4_reu_16m | 544.687 | 87.137 | 70.993 | 65.954 | 700.937 | 118.277 | 103.655 | 98.183 |
| v5_hybrid_lowzp | 601.747 | 87.137 | 70.993 | 65.954 | 783.094 | 118.277 | 103.655 | 98.183 |

These are CPU-model cycles; native VICE cycle timing was not measured.

## Explicit resource screen: SEEK16 integer-speed-one shortcut

| Profile | Stock INIT bytes | Verified available island bytes | Candidate bytes | Fits |
|---|---:|---:|---:|---|
| v1_balanced | 311 | 312 | 337 | no |
| v2_pareto_fast | 270 | 270 | 291 | no |
| v3_reu_512k | 270 | 273 | 291 | no |
| v4_reu_16m | 270 | 273 | 291 | no |
| v5_hybrid_lowzp | 311 | 312 | 337 | no |

The proposed shortcut is larger than every safely occupied code
island. Importantly, the V2 SEEK16_INIT ends at $19EF but $19F0
already contains an unrelated resident byte and the initialized
table at $1A00 must not be overwritten. The separate trial in
PR #142 correctly failed public validation when extended to $1A04.
That candidate is rejected; neither performance gain nor native
correctness has been claimed for it. A relocation-based specialist
would require a separate, independently qualified architectural
study rather than silently changing stable resources.

## Exact public-family tests

- Five profiles, both source relocations, eight live SEEK objects:
  480 INIT calls and 246,480 public STEPs covering 86,960 reference
  movement frames with full unrelated-slot isolation (PR #139).
- Native x64sc with real V3/V4 REU images: 40 INIT and 640 STEP
  public calls, including fractional, integer, Euclidean and
  post-arrival paths (PR #140). No native cycle timing measured.
- Mixed safety: 18,280 UDIV/UMOD public calls and 13,580 SEEK
  calls with full 408-byte movement-state preservation; placement PASS.

OptiSearch P40 raw-delta kernels have distinct speed/state contracts
and cannot be ranked as drop-in replacements for the public Q8.8
SEEK family. Its private source is not part of this release.

Existing per-frame STEP/STEP_INT/STEP1 paths remain because no
additional publicly compatible winner was validated under the
fixed resource budgets. This ends the Issue #39 SEEK audit, subject
to a successful post-merge main CI closeout.

Evidence: validation/review/ISSUE39_SEEK_FAMILY_FINAL_AUDIT_2026-10-14.json
Official benchmark: validation/movement/SEEK_PROFILE_BENCHMARK.json
Native proof: validation/review/ISSUE39_SEEK_ALL_MODES_NATIVE_VICE_2026-10-14.json
All-slot proof: validation/review/ISSUE39_SEEK_ALL_SLOTS_RESEARCH_2026-10-14.json

## Independently verified main post-merge closeout

All existing Issue #39 optimization families have now been audited, with released improvements and no additional qualified SEEK specialist. This is not a global proof of algorithmic optimality. The following push-triggered post-merge main runs passed on commit d296ace693543025f8aba582a0c933c867939a3a:

- full_library: https://github.com/floppyrom/C64-Math-Library/actions/runs/38633755150
- comparable_unsigned: https://github.com/floppyrom/C64-Math-Library/actions/runs/38633755164
- fixed_multiply: https://github.com/floppyrom/C64-Math-Library/actions/runs/38633754914

Final certificate: validation/review/ISSUE39_SEEK_FAMILY_POSTMERGE_MAIN_CERT_2026-10-14.json
