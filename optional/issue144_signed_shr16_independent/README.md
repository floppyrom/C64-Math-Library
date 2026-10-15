# Signed 32x32 SHR16 independent mixed-call-safe source

See ../../docs/ISSUE144_SIGNED_SHR16_INDEPENDENT_MIXED_2026-10-15.md. Loader must reserve caller RAM for the emitted islands, initialise the resident library, and optionally repoint only the public $5E15 JMP target after protecting against concurrent calls. Original SMUL32/UMUL32 routines coexist for sequential mixed calls; shared ZP prevents IRQ/NMI reentrancy.
