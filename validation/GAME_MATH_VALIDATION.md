# Game-math validation status

The prior FINAL validation corpus covered, per profile: 4,240 repaired-SMUL16 calls; 33,444 unsigned and 33,444 signed 32/32 divisions plus alias checks; 4,240 per signedness for 16-bit multiply-shift; 2,724 per signedness for 32-bit multiply-shift; 4,240 per signedness for shifted divide; exhaustive 65,536-divisor reciprocal; exhaustive 256-phase trig; exhaustive 65,536-pair atan2; exhaustive 65,536-input ISQRT16; a 4,130-case deterministic ISQRT32 corpus; and exhaustive 65,536-pair runs for each distance kernel.

In this optimized reviewed release ISQRT32 is the ISQRT16-seeded eight-step hybrid. The fast-kernel delta audit proves that all resident bytes outside its documented target/support ranges are unchanged, so the prior exhaustive results remain valid for all unchanged routines. The new ISQRT32 has separate current validation: 5,097 correctness/input-preservation cases per profile and a new measurement on the same 4,130-case performance corpus.

For the current release evidence map, read `REVIEWED_RELEASE_VALIDATION.md`.
