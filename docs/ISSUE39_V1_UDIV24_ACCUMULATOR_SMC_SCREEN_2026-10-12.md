# Issue #39 — RAM-only 24÷8 self-modifying specialist

**Research candidate only, not a shipped resident implementation.** PR #81 released the 61-byte **non-self-modifying** V1 engine. The optional 68-byte RAM-only engine patches its own immediate operands for `CMP #imm` and `SBC #imm` during each call. This saves loop cycles at the cost of writable executable RAM and non-reentrancy.

**Precondition:** N2>0, D1=D2=0, 0<D0<256. This is not a generic 24÷24 divider or a safe zero-divisor replacement. The caller must guard all other inputs; never run this code from ROM or when interrupts may enter it. It requires zero extra ordinary ZP or stack scratch.

The original screen against the **superseded PR #78 69-byte** core passed 48,388 paired full public entries, with means UDIV24 165.228277, UMOD24 231.489375, D8 stress 927.934314 cycles for the SMC variant. The correct *current-release* comparison is against the PR #81 61-byte image, not PR #78, and is published from the updated reproducible screen.

Sources: `tools/candidates/issue39_v1_24by8_accumulator_selfmod.asm` (exact V1 RAM candidate) and `routines/standalone_lab/portable/div_u24_by_u8_selfmod.asm` (independently liftable source with configurable placement), backed by `tools/screen_issue39_v1_24by8_accumulator_selfmod.py` and `tools/verify_issue39_v1_24by8_accumulator_selfmod_portable.py`. Preserve the 61-byte ROM-safe and 68-byte RAM-only alternatives side-by-side; do not replace any V1–V5 resident or close issue #39.
