# Issue #144 B — unrolled 32/16 low-word shared-take experiment

**Research only. No installed arithmetic changes, and not a callable replacement for `MATH_UDIV32_16` or `MATH_UMOD32_16`.**

## Hypothesis

The shipped V2–V5 fast 32÷16 producer uses the certified 16÷16 high-word divider followed by sixteen quotient/remainder steps. In the low-word tail, the overflow-forced subtraction and the normal compare-accepted subtraction are duplicated. Both branches reach subtraction with carry set. The candidate shares one subtract body and explicitly sets carry after it to inject the accepted quotient bit.

The standalone experimental generator in `tools/issue144_u3216_shared_take_tail_research.py` uses the **public** mini6502 CPU/assembler. It models precisely the lower 16 quotient bits and 16-bit remainder, with the high dividend's residual seeded by the mathematical oracle. The scratch addresses `$30-$35` are independent research allocations, **not public resident ABI addresses**.

## Preliminary screen — 15 October 2026

A first independent placed NMOS 6502 model screened **7,554 identical (N32,D16) pairs with D!=0** at origin `$2070`; 7,554/7,554 matched exact lower quotient and full remainder, baseline and candidate. The fragment shrank **684 → 492 machine bytes**, while tail-only mean cycles changed **494.890 → 487.379** (saving **7.511 cycles**), with **0 slower pairs** on that corpus (worst saving 0; best 18). Full corpus SHA256: `7f80ef3d1e2fe7559ae601dcbc18fd62a524398e5ccf867c74f813b7defdbb6d`. The **public** mini6502 same-input CI screen passed at [GitHub Actions #38722317028](https://github.com/floppyrom/C64-Math-Library/actions/runs/38722317028): identical corpus, cycle vectors and both sizes. This validates the isolated model result at that address, not its suitability for a production resident map.

## Explicit missing gates

- D=0 is an upstream entry/producer behavior: this experiment deliberately excludes it.
- High-word quotient and high-word 16÷16 cost are not included in these tail-only cycles. There is **no claimed full public-call saving**, and 7.5 cycles does not meet the suggested 5% ordinary-call triage target.
- The fragment does not yet prove normal five-profile/ZP/REU relocation, carry at final public RTS, input/flag/stack ABI, self-modification safety, native x64sc, mixed-call interleaving, p95/worst public-call response, or actual integration into the resident.
- It uses no private OptiSearch source or generated private donor. The private optimizer remains separate.

**Decision:** keep as a draft research screen, do not update production `PERFORMANCE.md`, do not publish it as a usable standalone divider or merge into resident until the above gates pass. Issue #144 B remains open. The more important goal remains a substantial unrestricted full-width main-producer architecture win.

## Independent actual x64sc 3.13.2 hardware-model checkpoint

A genuine VICE **x64sc (6510)** headless test has now executed **56 baseline + 56 shared-take = 112 native calls** in two separate BASIC-autostart test PRGs. Each test sets a deterministic full-width 32-bit numerator, nonzero 16-bit divisor and oracle-derived high-word residual in private scratch $30–$35; both 6510 fragments return via RTS. Each call checks the expected **low 16 quotient bits**, complete **16-bit remainder**, and **SP=$FF**, with a per-program completion marker. Real VICE remote monitor reported `$0332–$0334 = 00 38 5A` for each program (**zero mismatches; 56 cases completed**). Independent native corpus SHA-256: `ca42a919490b85dbdbb2fa813744832e26313a510e935f09e507782228635d9c`.

Native program SHA-256 hashes: baseline `93205b250f231aae73d1b90184f7e8220af4eccf31fcf98196af491cc2ef4f9e`, shared `4dbbda3dd196fdfdb8b8ff9b5cf06a51b74168e611c7dc5919e3dfbcb8f75e16`. The source, machine images, private-environment reproduction script and output evidence are preserved in an independent handoff, **not installed in the library**. No native cycle measurements or true full Q32/D=0/public-ABI proof are claimed.

**CI note:** historical workflows that run for every research PR may fail independently. The new dedicated tail-model action is green; the existing release audit requires resealing new paths in `SHA256SUMS.txt`, and the unrelated V2–V4 SHR16 native opt-in job exhibited a first-run mismatch. Neither failure is evidence of an arithmetic error in this new tail fragment; those checks must be resolved or explicitly quarantined before merging.
