#!/usr/bin/env bash
# Build the exact, source-pinned VICE SVN r46284 headless x64sc for C64 tests.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
MIRROR="$ROOT/third_party/vice"
SOURCE="$MIRROR/vice"
EXPECTED="d4d62d0b9538238e6a84826e951e76debf5df649"
PREFIX="$ROOT/.vice-build/r46284"
if [[ -n "${VICE_PREFIX:-}" ]]; then PREFIX="$VICE_PREFIX"; fi

if [[ ! -f "$SOURCE/configure.ac" ]]; then
    echo "VICE git submodule missing; fetching its pinned source..." >&2
    git -C "$ROOT" submodule update --init third_party/vice
fi
if [[ ! -f "$SOURCE/configure.ac" ]]; then
    echo "ERROR: unable to find VICE source in $SOURCE" >&2
    exit 1
fi
ACTUAL="$(git -C "$MIRROR" rev-parse HEAD)"
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
    echo "ERROR: VICE is $ACTUAL but r46284 requires $EXPECTED" >&2
    echo "Run: git submodule update --init --force third_party/vice" >&2
    exit 1
fi
mkdir -p "$PREFIX"
PREFIX="$(cd "$PREFIX" && pwd -P)"
echo "Building pinned VICE r46284 / $EXPECTED"
echo "Installing into $PREFIX"
cd "$SOURCE"
./autogen.sh
./configure --enable-headlessui --disable-pdf-docs     --without-pulse --without-alsa --without-oss     --without-libcurl --without-libusb     --prefix="$PREFIX"
make -j "${VICE_JOBS:-2}"
make install
"$ROOT/tools/vice/verify_headless.sh" "$PREFIX/bin/x64sc"
echo "READY: export VICE_WRAPPER=$PREFIX/bin/x64sc"
