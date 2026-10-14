**Final certification (14 October 2026):** The four standard fixed multiply outputs are complete after native signed/unsigned public equivalence and independent full-library, comparable and Turbo32 checks on post-merge main. Both 32-bit SHR16 tails improve two CPU-model cycles per call; both 16-bit SHR8 register-return adapters remain qualified and unchanged. Issue #39 remains open.

# Issue39 fixed multiply output 32-bit return-tail production stage

The full signed and unsigned SMUL32/UMUL32 public calls return with carry clear. In the two 32x32->48 shifted-result adapters, six absolute LDA/STA overlapping result moves preserve carry. The adapter's trailing redundant `CLC; RTS` can therefore be encoded as `RTS; NOP` without changing source address, resident footprint or public flags contract. No additional code or zero-page is needed.

Each of 4,361 identical source A/B inputs for **both routines**, all five profiles and **both relocations** saves **exactly two CPU-model cycles**. Correct 48-bit shifted signed/unsigned results, C=0, caller inputs, and stack checked on every case. No full-width multiply producer was changed. Signed/unsigned 16-bit SHR8 adapter already consumes X/A/Y register returns and remains unchanged.

**Native x64sc old/new output equivalence PASSED (480 calls), independent PR and main CI remain mandatory.** No native cycle measurement is claimed. The private OptiSearch source is excluded. Issue #39 remains open.

Installed x64sc passed all 480 original/optimized signed and unsigned calls across the five profiles, including every public result byte, carry, X/Y preservation, flags and stack preservation. Native timing was not measured.
