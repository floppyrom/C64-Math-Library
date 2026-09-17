#!/usr/bin/env bash
set -euo pipefail

# Package an already built Quake64 tree into the normal KERNAL-load D64.
# The caller should first run build_quake64_experiment.sh so generated assets,
# relocation data and the second-pass game.prg are current.

if [[ $# -lt 1 ]]; then
  echo "usage: $0 /path/to/Quake64 [output-dir]" >&2
  exit 2
fi

QROOT="$(cd "$1" && pwd)"
OUT="${2:-$QROOT/disk-artifacts}"
ACME_BIN="${ACME:-acme}"
C1541_BIN="${C1541:-c1541}"
mkdir -p "$OUT"

cd "$QROOT"
command -v "$ACME_BIN" >/dev/null
command -v "$C1541_BIN" >/dev/null

# Boot/splash controller are assembled after the generated splash data exists.
pushd src >/dev/null
"$ACME_BIN" boot.asm
"$ACME_BIN" splashc.asm
popd >/dev/null
mv -f src/boot.prg boot.prg
mv -f src/splashc.prg splashc.prg

# Required normal-disk inputs. mkdisk.py additionally adds generated maps and
# enemies when present.
for f in boot.prg splashc.prg splash.prg menu.prg tab.prg fnt.prg scr.prg sqt.prg game.prg; do
  test -s "$f" || { echo "missing disk input: $f" >&2; exit 1; }
done

python tools/mkdisk.py --out "$OUT/quake64-prepared-compact.d64" --c1541 "$(command -v "$C1541_BIN")"

"$C1541_BIN" -attach "$OUT/quake64-prepared-compact.d64" -list \
  | tee "$OUT/directory.txt"

sha256sum "$OUT/quake64-prepared-compact.d64" | tee "$OUT/SHA256SUM.txt"
stat -c 'd64 bytes: %s' "$OUT/quake64-prepared-compact.d64" | tee "$OUT/disk-size.txt"

echo "QUAKE64_COMPACT_D64_PASS"
