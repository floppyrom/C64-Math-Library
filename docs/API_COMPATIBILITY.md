# API compatibility

The release retains the authoritative **45-entry stable signed/unsigned/game-math API** in all four profiles. `PUBLIC_API_COMPLETE.csv` remains authoritative for that common surface. Normal operations use the configured public memory geometry and preserve the documented input semantics.

V2–V4 require `MATH_INIT`. `MATH_UMOD32_32` and `MATH_SMOD32_32` remain ABI aliases because their division kernels already produce quotient and remainder.

## REU Turbo extension

V3/V4 additionally expose six stateful batch lifecycle entries:

- `MATH_REU_UMUL16_BEGIN`
- `MATH_REU_UMUL16`
- `MATH_REU_UMUL16_END`
- `MATH_REU_UMUL32_BEGIN`
- `MATH_REU_UMUL32`
- `MATH_REU_UMUL32_END`

These are intentionally documented separately from the 45 stable calls because `BEGIN` installs an executable ZP overlay and temporarily owns the configured Turbo ZP range until `END`. They are now **source/build-time relocatable** but remain stateful/non-composable while active. No normal/game-math call is permitted between Turbo BEGIN and END.

Generated `math_api.inc` files for V3/V4 contain the six Turbo entry symbols plus the configured Turbo ZP/bank symbols. See `TURBO_API.csv` and `TURBO_RELOCATION.md`.
