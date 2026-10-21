# Matched UDIV8 historical versus operation-first speed replay

This experiment directly compares the **original V1–V5 resident PRGs**
with both operation-first source-linkable `UDIV8` variants. It uses the
identical 1,000-input corpus already qualified by
`tools/selective_speed_udiv8.py`, including zero divisors, structured
edges, randomly sampled inputs and small-divisor stress.

Each complete public call is checked for 8-bit quotient, remainder,
Carry, unchanged numerator/divisor, and stack restoration. It measures
full CPU-model entry-through-RTS cycles, and reports mean, p95, minimum
and maximum separately. Both selective implementations are assembled
at **two distinct code/I/O/ZP placements**.

```sh
python3 tools/benchmark_historical_selective_udiv8.py --out build/matched-udiv8/report.json
python3 -m unittest discover -s tools -p 'test_benchmark_historical_selective_udiv8.py' -v
```

The original five resident PRG SHA values and associated historical
REU image SHA values are verified against the frozen package manifest.

**Limitations:** CPU-model only, not hardware-native 6510/VIC/REU bus
timings. No profile winner from a different operand distribution is
silently treated as comparable. This proves a direct UDIV8 comparison,
not full historical parity for 56 public operations. The new builder
and its default source-selection policy are unchanged.
