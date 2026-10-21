# Experimental PAL native REU test without debugger CPU PC injection

**Diagnostic research only. Not a replacement for the bounded PAL gate in PR #385.**

VICE's traditional remote monitor entry flow manually installs a program
counter and an execution breakpoint before running a source-built PAL
REU/IRQ harness. That method passed some cold 16 MiB REU tests but
intermittently failed others, despite normal-speed emulation. The
full eight-case certificate remains blocked until an independently
reproducible native launch method is established.

This branch adds a comparison using a genuine tokenized C64 BASIC line
`10 SYS 3072` at $0801. The exact same Turbo16 REU and independently
source-linked stock images are loaded in the PRG, while the self-contained
test harness is assembled at $0C00. Pinned VICE
`-autostart <file.prg>` performs the BASIC RUN/SYS entry rather than any
monitor `r pc=...` or `g <address>` command. The remote monitor is used
only to wait for a completion breakpoint and read native result memory.
The SID-writing raster IRQ and all source data remain unchanged.

```sh
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
python3 tools/native_reu_pal_irq_dma.py \
  --launch-mode basic-autostart \
  --only-case reu_16384_display0_irq1 \
  --out build/autostart-diagnostic.json
```

The [first pinned VICE run](https://github.com/floppyrom/C64-Math-Library/actions/runs/39660398732)
passed isolated first-process 16 MiB bank-200 IRQ and 512 KiB bank-4 IRQ,
both measuring 6,491 native PAL clock slots and exactly one IRQ, with
correct arithmetic and restored 122-byte caller ZP.

The extended qualification runs **three separate cold GitHub Actions
machines**, each with the 16 MiB high-bank IRQ test as the very first
emulator process, the 512 KiB IRQ control and the entire eight-case
BASIC-autostart hardware/display/IRQ matrix. Source-image identity,
math products, Carry, caller ZP, and real CIA timings must all pass.
No diagnostic warmup runs beforehand.

The full research matrix has a deliberately distinct status:
`PASS_EXPERIMENTAL_BASIC_AUTOSTART_8_CASES_NOT_RELEASE_QUALIFIED`.
Production/native PAL certification remains exclusively bound to the
unchanged non-warp monitor launch gate from PR #385 until new criteria
are reviewed. Even 3/3 passing cold machines would demonstrate
repeatability of this alternative *emulated* launch, not prove the
real-hardware IRQ/REU corner case fully resolved. No IRQ handler may use the
122-byte executable Turbo16 overlay while the REU batch is active.
Real SID playback, continuous 50 Hz and actual hardware remain unqualified.

Relevant VICE issue: https://sourceforge.net/p/vice-emu/bugs/2024/
