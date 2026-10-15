# Optional V4 REU ISQRT32 fast-four-step prototype

See `v4_reu_16m.asm` for separately accessible source. In a throwaway clone, substitute this for `relocatable_source/v4_reu_16m/isqrt32_reu_prefix.asm` and assemble V4 reference and alternate maps. Never overwrite shipped resident binaries or mix this experimental source into other profiles. See `docs/ISSUE144_V4_REU_ISQRT32_FAST4_REFINEMENT_2026-10-15.md`. The required immediate REU DMA command `$91` is **already in current main**; the research change only optimizes root-refinement steps.
