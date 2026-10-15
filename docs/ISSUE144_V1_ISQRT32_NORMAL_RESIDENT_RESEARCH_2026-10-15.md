# Issue144 C - V1 normal resident ISQRT32 highword-seed feasibility

**Research only; no default source or reference image changes.** Independent V1-only in-memory source assembly replaces the slow `ISQRT16` seed delegation inside the already owned REG_GAME+$0A40..+$0AFF root section, translating the previously qualified highword-seed option to symbolic `MATH_IO`, `V1_SCRATCH`, `REG_TABLE` and `REG_GAME` addresses.

Both reference and alternate maps are tested on full unsigned 32-bit radicands and square boundaries with identical-input baseline/candidate public-entry model cycles, output/flags/input/SP/X/Y, `ISQRT16` interleaving and proof of unchanged memory outside the 192-byte owned slot. Native VICE and the V5 hybrid *have not* been validated by the current screen, regardless of the earlier 51-cycle caller-owned RAM option. Do not merge into the normal generator, change performance records or publish binary images without full native/public mixed-call qualification.

No private OptiSearch implementation is included.
