# Seven-operation whole-project linked-source busiest-frame experiment

This research tests the **same seven public APIs** in a single linked C64
executable: unsigned/signed 32×32 full64 multiplication, ISQRT16, unsigned
32/32 division and modulo, and signed 32/32 division and modulo.

Earlier three-operation and four-operation measurements cannot simply be
added together to predict a combined project's executable RAM, scratch,
zero page, or busiest frame. A shared-source assembler/linker may reuse
producers and tables, and call placement can change per-frame peaks.

Four complete pinned source combinations are compared, using the same
150 complete public calls in 24 synthetic frames at two relocations:

| Plan | MUL+SQRT source choices | DIV+MOD source choices |
|---|---|---|
| compact-everywhere | compact MUL pair + radix-4 tableless root | unsigned & signed shared 0-ZP |
| fast-mul-compact-div | FAST31 shared multiplication + square-table root | unsigned & signed shared 0-ZP |
| compact-mul-fast-div | compact MUL pair + radix-4 tableless root | unsigned V2 + signed V2 hybrid |
| fast-everywhere | FAST31 shared multiplication + square-table root | unsigned V2 + signed V2 hybrid |

Every configuration uses the operation-first public linker at the actual
memory map. Source and PRG SHA-256, actual RAM and ZP, physical linked source
count, 150 same-input complete Q/R/C/64-bit-result calls, input
preservation, balanced stack and the measured peak/p95/total frame math
cycles are checked. Each call is charged its caller JSR overhead.

Run:

\`\`\`sh
python3 -m unittest discover -s tools -p 'test_mixed_seven_frame_parity.py' -v
python3 tools/mixed_seven_frame_parity.py --out build/seven/frame-report.json
python3 tools/mixed_frame_frontier.py \
  --in-report build/seven/frame-report.json \
  --ram-budget 16000 --zp-budget 64 --out build/seven/frontier.json
\`\`\`

**This is a source-qualified experimental benchmark, not a registered
installer workload yet.** The production \`frame\` objective must not trust
its peak cycles until the exact deterministic seven-API producer is
registered with strict replay and binary checks.

The measurements are *CPU-model arithmetic plus JSR*, not a physically
measured PAL frame including VIC-II bus stealing, IRQ/SID, REU DMA, or
application work. There is no claim of exhaustive optimality among all
56 operations or permission to retire historical V1–V5/REU compatibility.
