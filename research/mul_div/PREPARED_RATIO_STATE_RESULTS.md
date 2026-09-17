# Prepared ratio state policy: safe vs fast

The first prepared-ratio prototype kept the Q0.16 multiplier directly bound into the V2 record UMUL16 core and used its `same_x` entry. That is the fastest APPLY path, but another UMUL16 call rebinds the native X operand and invalidates the prepared ratio.

This note measures a second **safe-state** policy that keeps the prepared multiplier in private ordinary RAM. Each APPLY reloads the two multiplier bytes and enters the native generic UMUL16 core, which rebuilds its own mirror bindings. Other multiply calls may therefore occur between ratio applications without destroying the prepared state.

Both policies keep the same arithmetic contract:

```text
m = round(|n|*65536/|d|), |n|<=|d|
result = trunc_toward_zero(y*sign(n/d)*m/65536)
max integer error vs exact y*n/d <= 1
```

## Code size

| PREP | State | PREP code | APPLY code | Total |
|---|---|---:|---:|---:|
| compact loop | fast bound | 221 B | 130 B | 351 B |
| compact loop | **safe RAM** | 207 B | 140 B | **347 B** |
| unrolled | fast bound | 889 B | 130 B | 1019 B |
| unrolled | **safe RAM** | 875 B | 140 B | **1015 B** |

Safe PREP is smaller because it stores only the final two-byte multiplier instead of installing all native UMUL16 X mirrors. Safe APPLY pays the rebind cost on every application.

## Quake64 near-clip stress corpus

Same 5,000 edge-pair corpus as `PREPARED_RATIO_V2_5000.json`:

```text
seed      $C0FFEE
ZCLIP     $0100
z0        [-8192, 255]
z1        [256, 8191]
X/Y delta [-8192, 8191]
```

Cycles below exclude the external caller JSR, matching the library's routine timing convention. The Quake current pair includes its 28-cycle four-PHA/four-PLA save/restore of the original ratio between X and Y.

| Path | PREP mean | APPLY mean | Pair mean | Pair min | Pair max | Gain vs Quake |
|---|---:|---:|---:|---:|---:|---:|
| compact fast | 952.231 | 216.144 | 1384.519 | 1199 | 1608 | 60.56% |
| compact **safe** | 932.231 | 258.144 | 1448.519 | 1263 | 1672 | 58.74% |
| unrolled fast | 744.538 | 216.144 | **1176.827** | 1022 | 1380 | **66.47%** |
| unrolled **safe** | **724.538** | 258.144 | **1240.827** | 1086 | 1444 | **64.65%** |
| Quake current | — | — | 3510.286 | 1863 | 3896 | baseline |

All prepared variants produced the same Q0.16 result contract, with:

```text
non-zero error vs exact y*n/d   1.57%
mean absolute integer error     0.0157
maximum absolute integer error  1
```

There were zero prepared-contract mismatches in the 10,000 component outputs.

## Interpretation

The cost of making the state robust is surprisingly small on the target workload:

```text
unrolled fast pair  1176.827
unrolled safe pair  1240.827
                    --------
extra                  64.000 cycles for two APPLY calls
```

That is only about **32 cycles per application** net after safe PREP's cheaper state installation offsets part of the generic-core rebind cost.

The safe version still reduces the Quake arithmetic pair by about **64.65%** on the stress corpus, while avoiding a fragile lifecycle dependency on the current UMUL16 binding.

This changes the likely public-API direction:

```text
public/default candidate:
    safe PREP + safe APPLY

profile/internal hot-loop option:
    bound PREP + same_x APPLY
```

The fast bound form remains useful when a caller can guarantee a short prepared-ratio batch with no intervening UMUL16 rebind, similar in spirit to the library's existing stateful Turbo lifecycle. The safe form is a better default contract because ordinary unrelated math calls do not silently corrupt the prepared ratio.

## Next gate

Before promotion, benchmark the safe variant inside an actual Quake64 near-clip integration, including caller marshalling and surrounding endpoint arithmetic. If that remains decisively below the existing path, the prepared ratio has a much stronger claim to a stable API slot than general `UMULDIV16`.
