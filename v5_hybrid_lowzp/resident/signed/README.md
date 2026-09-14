# Native signed implementation map — v5_hybrid_lowzp

V5 is rebuilt from the V1 low-ZP base. All signed multiply/divide APIs therefore inherit the V1 **native signed executable paths**. The hybrid builder imports selected faster V2 **unsigned** divide/modulo and trig routines only; it does not replace the signed APIs.

Native means no signed entry executes the corresponding unsigned multiply/divide engine. Immutable tables may be shared. This is checked by `tools/validate_signed_layout.py` and by the dedicated multiply/divide arithmetic validators.
