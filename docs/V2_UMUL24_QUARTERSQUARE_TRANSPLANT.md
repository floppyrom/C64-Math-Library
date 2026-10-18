# Original V2 biased quarter-square UMUL24 public source transplant

This is the **actual V2 Pareto-Fast UMUL24 arithmetic core**, extracted from
`v2_pareto_fast/resident/modules/pareto_umul24.a` with a relocatable
public X24/Y24-to-Z48 wrapper. No resident binary is copied into the builder.

Original source notes report a 24-byte contiguous ZP pointer bank and
four 511-entry offset quarter-square planes. The implemented source retains
its carry-neutral parity offset **$CA (202)**, exactly the optimization
highlighted in Repose's CSDB discussion. It also keeps the original
carry-repair branches and row summation. Only page origins and a public ABI
adapter are changed.

The source-linked image reserves up to 512 bytes executable plus alignment
to 256 and four 512-byte quarter-square table slots. Twenty-four ZP bytes
are reserved. The wrapper seeds the high bytes of all table pointers and
patches two Y-row immediates on each call. The source modifies some
immediate operands and the stored low result byte inside executable RAM;
**writable code and non-reentrancy are explicit requirements**.

Run `python3 -m unittest discover -s tools -p
'test_research_v2_umul24.py' -v` to test the complete 48-bit product on
512 same-corpus calls at both $8000 and $7123, with X/Y preservation,
carry=0, stack balance and output sentinels.

The operation-first builder now exposes `link:v2-quarter-square` with exact
page-aligned RAM, 24 ZP, writable-code and canonical source provenance.
The speed objective compares **512 identical full public calls** against
the 156-byte portable source. It automatically picks the fastest qualified
feasible implementation, while preserving compact zero-ZP selection. The
final acceptance gate is native VICE r46284 and complete library CI at
two placements, plus full-page resource accounting.
A signed SMUL24 fast sibling may share the physical unsigned producer
after sign-correction qualification, but may not be assumed correct or fast.

The source extraction and native qualification remain under review until
all exact-head CI checks are green; no historical profile is modified.
