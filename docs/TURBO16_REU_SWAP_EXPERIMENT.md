# Turbo16 REU SWAP: executable BEGIN/CALL/END experiment

**Experimental CPU-model implementation; not a selectable operation-first REU backend.** This moves past source geometry: a new relocatable NMOS-6510 controller executes BEGIN, guarded CALL and END using REU command **$92 SWAP**, following the historical Turbo16/32 executable-zero-page ownership architecture.

## One DMA swap saves the caller's entire zero page

The first SWAP exchanges the 122-byte executable zero-page region with the designated REU bank. The REU now holds the original caller ZP, and the ZP contains executable Turbo16 kernel bytes. The second SWAP in END restores all original caller-ZP bytes exactly and returns the kernel to REU. The kernel's self-modifying immediate operand bytes can change during CALL, so its REU-resident bytes after END are expected to retain those updated SMC operands, not match the pristine payload.

A dedicated state byte rejects nested BEGIN and CALL/END outside active mode. The controller preserves the caller's interrupt-disable flag across each swap. The entire overlay remains exclusively owned while the mode is active. An IRQ or ordinary math call must not use those ZP addresses until END.

## Current test

~~~sh
python3 tools/reu_turbo16_swap_experiment.py --out build/reu-swap-test
python3 -m unittest discover -s tools -p 'test_reu_turbo16_swap_experiment.py' -v
~~~

The source-assembled controller, overlay and binder run through a CPU-model REU SWAP implementation. Tests exercise two batches, exact 16x16 unsigned products and public input/Carry/stack contracts, nested-state rejection, complete original ZP restoration, persisted SMC operands in REU, two memory maps and REU bank placement checks.

**Table limitation:** four 512-byte quarter-square lookup planes for the CPU-model proof are extracted from the *checksum-locked* V3 historical PRG as test-only data. Generating those tables directly for an independent selective binary remains outstanding.

**Hardware limitation:** the CPU-model DMA engine does not certify bus cycles, missing/undersized hardware, VIC contention or native x64sc VICE behavior. There is no source-qualified stock-builder REU variant, REU image installation, or production end-to-end hardware certificate.

The default user installer remains stock-C64 operation-first. For existing REU functionality, the historical V3/V4 compatibility exports are unchanged. Further milestones are tracked in [Issue #376](https://github.com/floppyrom/C64-Math-Library/issues/376).
