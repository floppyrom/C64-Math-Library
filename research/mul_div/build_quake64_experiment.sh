#!/usr/bin/env bash
set -euo pipefail

# Build an audited Quake64 tree far enough to prove:
#   * GAME assembles with ACME;
#   * relocation data can be regenerated;
#   * the second-pass GAME image assembles;
#   * Quake64's own checkheap.py accepts the resulting layout.
#
# The same script can build the untouched audited baseline or the patched
# prepared-fraction experiment. Disk construction/emulator execution remain
# separate gates.

if [[ $# -lt 1 ]]; then
  echo "usage: $0 /path/to/Quake64 [artifact-dir]" >&2
  exit 2
fi

QROOT="$(cd "$1" && pwd)"
OUT="${2:-$QROOT/experiment-artifacts}"
ACME_BIN="${ACME:-acme}"
mkdir -p "$OUT"

cd "$QROOT"

VARIANT=baseline
if [[ -f src/prepared_fraction_smc.asm ]]; then
  VARIANT=prepared-fraction
fi

echo "variant: $VARIANT" | tee "$OUT/build-provenance.txt"
echo "Quake64 commit: $(git rev-parse HEAD)" | tee -a "$OUT/build-provenance.txt"
echo "ACME: $($ACME_BIN --version 2>&1 | head -n 1)" | tee -a "$OUT/build-provenance.txt"
python --version 2>&1 | tee -a "$OUT/build-provenance.txt"

git diff -- src/quake64.asm src/cube.asm > "$OUT/source.diff" || true
if [[ -f src/prepared_fraction_smc.asm ]]; then
  cp -f src/prepared_fraction_smc.asm "$OUT/prepared_fraction_smc.asm"
fi

# Match the source-generation portion of build.bat.
python tools/check_irq_contract.py
python tools/gentables.py
python tools/genscreens.py
python tools/genlinebodies.py
python tools/genrotate.py
python tools/genuifont.py
python tools/genenemymuzzle.py
python tools/gensplat.py
python tools/gensounds.py
python tools/genenemies.py
python tools/genmap.py
python tools/genitems.py
python tools/genweapons.py
python tools/gen_menu_text.py
python tools/gen_menu_cursor_sprites.py
python tools/gen_menu_title.py
python tools/gen_menu_wip_sprite.py
python tools/gen_splash.py

pushd src >/dev/null
"$ACME_BIN" tables.asm
"$ACME_BIN" sqtab.asm
"$ACME_BIN" uifont.asm
"$ACME_BIN" screens.asm
"$ACME_BIN" menu.asm
"$ACME_BIN" --vicelabels ../overlay.lbl overlay.asm
popd >/dev/null

for f in tab sqt fnt scr menu; do
  if [[ -f "src/$f.prg" ]]; then mv -f "src/$f.prg" "$f.prg"; fi
done

# Default KERNAL-load GAME build. First pass creates labels used by mkreloc.py.
pushd src >/dev/null
"$ACME_BIN" -v3 --vicelabels ../game.lbl quake64.asm 2>&1 | tee "$OUT/acme-first-pass.txt"
popd >/dev/null
if [[ -f src/game.prg ]]; then mv -f src/game.prg game.prg; fi

python tools/mkreloc.py 2>&1 | tee "$OUT/mkreloc.txt"

# Second pass consumes regenerated relocation data and is the authoritative
# layout image for the heap comparison.
pushd src >/dev/null
"$ACME_BIN" -v3 --vicelabels ../game.lbl quake64.asm 2>&1 | tee "$OUT/acme-second-pass.txt"
popd >/dev/null
if [[ -f src/game.prg ]]; then mv -f src/game.prg game.prg; fi

python tools/checkheap.py 2>&1 | tee "$OUT/checkheap.txt"

cp -f game.lbl "$OUT/game.lbl"
cp -f game.prg "$OUT/game.prg"

# Pull the key addresses/slack lines into a compact summary without assuming
# exact formatting beyond labels/checkheap's current human-readable output.
{
  echo
  echo "--- selected labels ---"
  grep -Ei '(^|[ .])(end_game|qfrac_prep|qfrac_apply_s16)([ .=]|$)' game.lbl || true
  echo
  echo "--- heap gate ---"
  cat "$OUT/checkheap.txt"
  echo
  echo "game.prg bytes: $(stat -c %s game.prg)"
} | tee -a "$OUT/build-provenance.txt"

echo "QUAKE64_BUILD_PASS variant=$VARIANT"
