# Issue #39 — live X-register high-byte reuse in UDIV24 / UMOD24 (2026-10-11)

**Status:** source-backed candidate requiring full release CI, not completion of the whole unsigned DIV/MOD campaign.

## Manual post-OptiSearch optimization

Both the V1 Balanced 24-bit divider and the V2–V4 Repose-derived direct Q0/t13/k13 divider contain a high-byte-equality fast path. Immediately before the `*_high_equal` target, `LAX MATH_N+2` loads both A and X with N2, and `CMP MATH_D+2; BEQ *_high_equal` certifies N2 = D2. The previous code then reloads D2 from memory using `LDA MATH_D+2` (4 cycles, 3 bytes). `TXA` restores the identical high byte in A (2 cycles, 1 byte) without changing carry and without allocating ZP or introducing a new dependency. Subsequent `BEQ` receives identical Z/N input; X is retained.

The source-level rewrite removes two bytes of selected code, shifting private branch destinations. It is not a fixed-offset binary patch: reference and alternate relocations must be rebuilt from symbolic source, and the new resident images compared to freshly validated machine-code execution. Public ABI entry addresses, input preservation, zero-divisor semantics, scratch ownership, and full PRG file sizes stay fixed. V5 inherits the updated V1 native block and optimized V2 donor 24-bit divider.

This improvement came from a **manual post-OptiSearch register-lifetime pass**. It is not evidence that the generic OptiSearch search independently discovered a faster complete 24-bit divider. Earlier OptiSearch/Repose-derived architectures remain important substrates.

## Paired deterministic machine-code measurement

Each profile uses the same 4,753-call UDIV24 corpus and 1,553-call UMOD24 corpus in both versions. Across **31,530 paired calls**, results, carry, input preservation and relevant ABI state matched exactly; **no call slowed**. Table means count 6502 instruction cycles, not C64 bus/DMA/physical-hardware time.

| Profile | UDIV24 mean old → candidate | Faster / 4,753 | UMOD24 mean old → candidate | Faster / 1,553 |
|---|---:|---:|---:|---:|
| V1 | 194.156322 → 194.032611 | 294 | 303.233097 → 302.877656 | 276 |
| V2 | 154.338944 → 154.218178 | 287 | 205.325821 → 205.325821 | 0 |
| V3 | 161.653272 → 161.533347 | 285 | 207.136510 → 207.136510 | 0 |
| V4 | 158.507048 → 158.385020 | 290 | 205.247263 → 205.247263 | 0 |
| V5 | 157.776141 → 157.655376 | 287 | 211.248551 → 210.894398 | 275 |

2 cycles saved on each of **1,994** improved calls and none slower. V2/V3/V4 UMOD24 uses its separate remainder-only frontend, so is unaffected by the changed 24-bit quotient backend on these corpora.

## Exact expected source-generated reference resident SHA-256

- V1: `759ca1e9d683eba2b56f818e9f3f4f36f5322a832daadf06493380d610f8f0b5`
- V2: `e1e828a2748099b6f05b224b98ca26960d120f8ba886c4906e8b52bdb8b4fbcd`
- V3: `026243976c2156b68ddc7527c6b1f1a4420cd4973026dd90d60cd4fef04f77bc`
- V4: `61d2f5bc88e5394035c51a7be9cf6b99e329dfea37419ae7f1c72d97262470b7`
- V5: `e875c010f1eef2bbf90e6678faf79d3ef641a8e59f3073ccb6b4700e271b1f5c`

## Validation and remaining limitations

Initial alternate-map V1–V4 common-API validation passed all 56 public entry points / 21,678 calls **per profile**. A genuine VICE 3.13.2 x64sc native spot check exercised old and candidate PRGs for each V1–V5, with 8 chosen divisor pairs per profile and both UDIV24/UMOD24 entries (**80 calls per side**, all correct). V3/V4 used the original 512 KiB / 16 MiB REU images; V5 used RAM under BASIC ROM and a correctly initialized CPU-port DDR.

Final promotion requires refreshed all-profile unsigned and signed family checks, reference and alternate source rebuild, V5 hybrid parity, standalone source mirrors, public performance and catalog tables, README/user manual, both changelogs, release hashes and sealed package audit, two green PR workflows, merge and green main CI.

The remaining 8/16/24/32 dividend/divisor resource-class searches and per-family no-gain decisions under issue #39 are still **open**. Nothing in this document authorizes ticking off the entire unsigned DIV/MOD family.