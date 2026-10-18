# Signed 24-bit DIV/MOD: absolute quotient-zero hot path

**Research candidate, not an automatic speed promotion.** The operation-first
builder retains the original 325-byte `link:portable-zerozp` shared signed
24/24 Q/R producer and adds `link:abs-qzero-guard` for `SDIV24` and
`SMOD24`. Both share their own physical producer between DIV and MOD,
each with zero ZP and 7 call-exclusive RAM scratch bytes.

The original restoring core performs all 24 iterations even when
`abs(N24) < abs(D24)` (nonzero divisor): then the quotient must be zero and
the signed remainder must equal the original numerator. The candidate first
sign-normalizes numerator and divisor as before, compares their unsigned
24-bit absolute magnitudes, and returns Q=0/R=N/C=0 immediately in that
domain. For every other divisor it runs the **unchanged** 24-round restoring
kernel. Divisor zero, 24-bit signed overflow, high Q/R sentinel bytes and
N/D preservation retain the original public ABI. Decimal mode must be clear.

## Fair performance evaluation

```sh
python3 -m unittest discover -s tools -p 'test_selective_sdiv24_qzero.py' -v
```

The CPU-model gate executes identical signed edge, uniform random, explicit
quotient-zero, high-quotient and zero-divisor input pairs for both sources at
$8000/$C000 and $7123/$C040. It validates public Q/R/C, stack, input and
high-byte sentinels, and records matched public-entry-through-RTS cycle deltas.
Each true Q0 case must improve, while aggregate gains may coexist with a
small overhead on non-Q0 calls. Baseline and candidate cycle distributions
are **not** historical V1-V5 profiles; this does not claim to replace those
sources. Both variants must remain selectable on RAM and latency trade-offs.

```sh
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 tools/native_selective_sdiv24_qzero.py
```

The native gate runs both source-built versions on an identical 96-case
public ABI corpus, two relocations each, verifies Q/R/C and all byte
sentinels, then checks identical result-image hashes (**384 native public
calls**). CI assembles the pinned VICE r46284 upstream submodule.

Next: after independent CI qualification, compare source variants against
source-authenticated historical V1-V5 and OptiSearch signed 24-bit producers
on the *same* caller ABI and frame trace. The selector should use measured
per-frame call weights and tail latency only after that historical
comparison. Do not choose this candidate by the number of lines of assembly.
