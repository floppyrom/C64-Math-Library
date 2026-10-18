#!/usr/bin/env bash
# Fail closed: an existing path or successfully downloaded archive is not enough.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
BIN="${1:-${VICE_WRAPPER:-$ROOT/.vice-build/r46284/bin/x64sc}}"
if [[ ! -x "$BIN" ]]; then
    echo "Missing or non-executable VICE x64sc: $BIN" >&2
    exit 1
fi
echo "VICE binary: $BIN"
VERSION="$(timeout 20s "$BIN" -version 2>&1)" || {
    echo "VICE -version failed or timed out." >&2
    exit 1
}
printf '%s\n' "$VERSION"
if ! printf '%s\n' "$VERSION" | grep -Ei -q 'VICE|x64sc|3\.10'; then
    echo "Unrecognized VICE version output" >&2
    exit 1
fi
# Verify the upstream checkout is the promised source, if present.
if [[ -d "$ROOT/third_party/vice/.git" || -f "$ROOT/third_party/vice/.git" ]]; then
    ACTUAL="$(git -C "$ROOT/third_party/vice" rev-parse HEAD)"
    [[ "$ACTUAL" == "d4d62d0b9538238e6a84826e951e76debf5df649" ]] || {
        echo "Source submodule drifted away from r46284: $ACTUAL" >&2
        exit 1
    }
fi
echo "PASS: headless VICE can execute -version; native PRG tests are separate."
