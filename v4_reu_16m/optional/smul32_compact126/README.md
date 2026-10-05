# Optional compact126 SMUL32 overlay — V4 REU 16M

This directory exposes the exact validated compact126 signed 32x32 -> 64 kernel for V4 as an **exclusive overlay source**. It is not selected by the fixed resident 54-entry API.

V4 is a natural host because its Turbo modes already establish explicit ownership intervals and its resident UMUL32 quarter-square tables use the same $7000/$7200/$7400/$7600 geometry. A production BEGIN/END wrapper must additionally preserve and restore the compact126 page-$01 range ($0100-$017D) and any ordinary-RAM overlay used for the signed wrapper.

Do not install this persistently over $80-$F3: that range contains the MATH_INIT-installed native SMUL16 executable-ZP image in the ordinary resident profile.

See ../../../docs/SMUL32_COMPACT126.md and ../../../validation/records/SMUL32_COMPACT126_2026-10-05.json.
