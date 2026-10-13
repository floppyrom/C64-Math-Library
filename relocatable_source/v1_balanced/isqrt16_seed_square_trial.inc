; Profile-owned ISQRT16 code/seed experiment (not promoted).
; New code and 256-byte table must fit before REG_GAME+$0924.
IS16_FAST_BASE = REG_GAME+$07DB
IS16_FAST_LIMIT = REG_GAME+$0924
!source "../game_math/isqrt16_seed_square_trial.inc"
