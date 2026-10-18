# Issue #285 — exact shared-component lower bounds for 56-operation resource selection

Scope: size / balanced / zero-page objectives in the operation-first C64 library. The arithmetic kernels, historical resident binaries, ABI, cycle benchmarks, and source catalogs remain unchanged.

## Reproduction and diagnosis

The slow case selected all 56 operations under 18,000 bytes of RAM and four ZP bytes, at unaligned code origin $4321, explicitly pinning ISQRT16 to its square-table variant. The original branch-and-bound used the largest individual minimum cost within each group of APIs that might share a producer. This is a safe but weak lower bound when a group needs several incompatible code images.

## Implementation

For each producer-sharing component, the solver now computes the exact minimum union of raw source-code bytes for the remaining APIs. A memoized dynamic program uses remaining API indices and previously installed shared identities. This accounts for real producer sharing while allowing different implementation choices. Components have disjoint shared identities, so their minimum incremental code sizes can safely be added to obtain a lower bound. Final page alignment, data tables, scratch, state and ZP are still checked with the original exact layout and score model.

An initially feasible greedy full selection may provide an upper-bound incumbent, but the exact search continues and may replace it. This heuristic never substitutes for proof. Individually impossible ZP variants are discarded before search.

## Regression gate

The smaller-frontier exhaustive reference tests remain authoritative for correctness of the selected score and tie-breaking. A new deterministic 56-operation test covers unpinned and explicitly pinned square-table ISQRT16, three resource objectives (size, balanced, zp), and both $2000 and $4321 code origins under 18,000 RAM / 4 ZP. It validates actual aligned code, ordinary scratch, persistent state and producer sharing. It prints elapsed time but has no brittle wall-clock assertion in shared CI.

Issue #285 should remain open until pinned $4321 no longer stalls, the regression matrix finishes on CI, and the full builder and publication gates pass at the exact PR head. This does not prove native VICE frame timing or change arithmetic producer correctness.
