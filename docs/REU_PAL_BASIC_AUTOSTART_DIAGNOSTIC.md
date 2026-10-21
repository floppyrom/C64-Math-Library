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

A passing isolated run is only a **diagnostic**. It must be repeated on
independent cold runners and across 512 KiB / 16 MiB, display-on/off
and IRQ-on/off configurations before it is considered a possible
replacement for the production test gate. No IRQ handler may use the
122-byte executable Turbo16 overlay while the REU batch is active.
Real SID playback, continuous 50 Hz and actual hardware remain unqualified.

Relevant VICE issue: https://sourceforge.net/p/vice-emu/bugs/2024/
