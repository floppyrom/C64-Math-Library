# Direct-core MUL_DIV handoff notes

The first fused candidate still called the **public** `MATH_UMUL16` entry and then reloaded the full 32-bit product from `Z[0..3]`. That already beat public composition, but it left a second layer of avoidable marshalling.

For V2 Pareto-Fast, the selected native UMUL16 core exposes a much better handoff point:

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

The direct MUL_DIV candidate binds operands exactly as the V2 wrapper does, calls `$53EC`, then consumes those live product bytes immediately. This avoids publishing the complete product to `MATH_Z` and loading it again.

On the 5,000-case uniform bounded corpus:

```text
public composition   1027.605 cycles
public-mul fused      859.405 cycles
direct-core fused     815.893 cycles
```

So **about 43.5 additional cycles** disappear simply by choosing a better internal handoff. No approximation is involved.

## Small-product specialization

For byte-sized multiplicands, product bytes 2 and 3 are zero. The numerator is therefore already 16 bits. The first direct hybrid routed these cases to the native V2 UDIV16 core and reached 336.085 cycles on `game8`.

The quotient distribution showed that another layer was worth fusing:

```text
q == 0     74.30%
q <= 1     86.58%
```

So the current direct hybrid resolves q=0 and q=1 **without calling any divider**:

```text
native UMUL16
    |
    +-- d == 0 --------------------> error immediately
    |
    +-- high16 == 0
    |      |
    |      +-- product < d --------> q=0, r=product
    |      |
    |      +-- product-d < d ------> q=1, r=product-d
    |      |
    |      `-- otherwise ----------> native UDIV16
    |
    `-- high16 != 0 ---------------> bounded constrained tail
```

That changes the 5,000-case `game8` result from:

```text
public composition       897.260 cycles
earlier direct hybrid    336.085 cycles
q0/q1 direct hybrid      294.563 cycles
```

or **67.17% below public composition**, with zero errors in the measured corpus and the 2,197-case structured edge suite.

This still does **not** make the hybrid the universal winner. On uniformly distributed bounded 16-bit operands, almost no products fit in 16 bits, so the plain direct-core path remains faster:

```text
direct           815.893 cycles
direct_hybrid    823.931 cycles
```

The current Pareto conclusion is therefore:

```text
general bounded 16-bit work
    -> direct-core + constrained 16-step tail

byte/small-product work
    -> direct-core + q0/q1 exits + native UDIV16 fallback
```

The next step is deeper fusion of the **general** path: either leave multiply state in a form that reduces divider setup further, or replace the fixed 16-step tail with a width/quotient strategy that wins without penalizing full-width cases.
