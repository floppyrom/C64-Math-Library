# Direct-core MUL_DIV handoff notes

The first fused candidate still called the **public** `MATH_UMUL16` entry and then reloaded the full 32-bit product from `Z[0..3]`. That already beat public composition, but it left a second layer of avoidable marshalling.

For V2 Pareto-Fast, the selected native UMUL16 core exposes a much better handoff point. Its validated native contract is:

```text
entry       $53EC
input X0    $21
input X1    $29
input Y0    CPU Y
input Y1    immediate operand at $541A

result byte0  $31
result byte1  CPU X
result byte2  CPU A
result byte3  CPU Y
```

The direct MUL_DIV candidate binds operands exactly as the V2 public wrapper does, calls `$53EC`, then immediately moves the four live product bytes into the bounded divider's quotient/remainder state. This avoids publishing the complete product to `MATH_Z` and then loading it again.

The measured effect on the 5,000-case uniform bounded corpus is:

```text
public composition   1027.605 cycles
public-mul fused      859.405 cycles
direct-core fused     815.900 cycles
```

So **about 43.5 additional cycles** disappear simply by choosing a better internal handoff. No arithmetic approximation is involved.

For byte-sized multiplicands, a second specialization is much more important. If product bytes 2 and 3 are both zero, the numerator is only 16 bits and the native V2 UDIV16 core is a better algorithm than the fixed 16-step constrained tail, especially because it has dedicated q=0/q=1 fast exits. The direct hybrid therefore dispatches:

```text
native UMUL16
    |
    +-- high16 == 0 --> native UDIV16
    |
    `-- high16 != 0 --> bounded constrained tail
```

On the 5,000-case `game8` corpus this changes the mean from 897.260 cycles for public composition to **336.085 cycles** with zero errors, a **62.54% reduction**.

This does **not** mean the hybrid should replace the direct general path. On uniformly distributed bounded 16-bit operands, almost no products fit in 16 bits, so the dispatch becomes overhead and the plain direct-core candidate remains faster (815.900 vs 824.427 cycles).

The current research conclusion is therefore a Pareto split rather than a single winner:

```text
general bounded 16-bit work    -> direct-core + constrained tail
byte/small-product work        -> direct-core hybrid with UDIV16 fast path
```

The next step is deeper fusion: determine whether product formation itself can leave the partial/high state in a form that removes more setup from the divide phase, and whether quotient-class prechecks can reduce the general path below a fixed 16-step tail.
