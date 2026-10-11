# V1 zero-ZP UDIV32/32 and UMOD32/32 prechecked gate (issue #39)

**Status: source-integrated candidate; publication and CI finalization pending.**

The V1 early Q=0/Q=1 gate already establishes whether D=0 or N>D. The new D=0 path jumps to the existing Q=R=0 carry-set handler at `REG_GAME+$0122`; the N>D path bypasses the second zero check by calling the existing nonzero continuation at `REG_GAME+$0150` instead of `REG_GAME+$013E`.

No stable ABI addresses, private-RAM envelope, zero-page allocation, or resident PRG length change. N and D remain preserved. The zero-divisor path no longer performs the undocumented private scratch copy.

| API | Previous mean | Candidate mean | Delta |
|---|---:|---:|---:|
| MATH_UDIV32_32 | 428.554036 | 416.861197 | −11.692839 cycles |
| MATH_UMOD32_32 | 552.220863 | 541.401803 | −10.819060 cycles |

The figures use existing deterministic public-entry corpora (6,801 and 1,553 calls), not full 2^64 input-pair coverage or physical hardware timing.

**Local qualification on the candidate:** 21,508 paired before/after calls with no mismatches or slowdowns; 164,410 V1 unsigned and 97,329 V1 signed family calls with zero errors; reference relocation builds produce the exact candidate SHA-256 `00ea3816ee39fac3ee3c04ae05c276bde43f05e3073fbdcc12f7f2fa74f97ad0`; alternate source layout passes 56 entries / 21,678 calls. VICE 3.13.2 files were recovered, but that runtime could not start in the current environment because of missing shared libraries.

This is one two-routine optimization, **not** completion of the entire unsigned DIV/MOD campaign. Private OptiSearch remains outside the repository.
