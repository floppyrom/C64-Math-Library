# Issue39 fixed multiply output 32-bit return-tail production stage

The full signed and unsigned SMUL32/UMUL32 public calls return with carry clear. In the two 32x32->48 shifted-result adapters, six absolute LDA/STA overlapping result moves preserve carry. The adapter's trailing redundant `CLC; RTS` can therefore be encoded as `RTS; NOP` without changing source address, resident footprint or public flags contract. No additional code or zero-page is needed.

Each of 4,361 identical source A/B inputs for **both routines**, all five profiles and **both relocations** saves **exactly two CPU-model cycles**. Correct 48-bit shifted signed/unsigned results, C=0, caller inputs, and stack checked on every case. No full-width multiply producer was changed. Signed/unsigned 16-bit SHR8 adapter already consumes X/A/Y register returns and remains unchanged.

**This is staged until actual native VICE and independent CI pass.** No native cycle measurement is claimed. The private OptiSearch source is excluded. Issue #39 remains open.
