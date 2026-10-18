# Pinned upstream VICE trunk for C64 Math Library

**Revision:** upstream [VICE SVN r46284](https://sourceforge.net/p/vice-emu/code/) (15 October 2026), from the public [VICE-Team SVN mirror](https://github.com/VICE-Team/svn-mirror/tree/d4d62d0b9538238e6a84826e951e76debf5df649/vice). The upstream source gitlink is **d4d62d0b9538238e6a84826e951e76debf5df649**, recorded in `third_party/vice` and `PIN.json`. As of 18 October this was the latest upstream *source* SVN revision we could verify; it is **not** the latest published prebuilt Linux archive, and not a VICE stable release. When a newer upstream revision appears, review it, update the gitlink and pin together, and rerun native qualifications.

We intentionally use a **Git submodule** rather than copying the hundreds-of-megabytes of the upstream SVN mirror or an opaque distribution binary into library history. This keeps VICE provenance and GPL licensing separate, permits exact reproduction, and prevents silently switching emulator versions. SourceForge is authoritative; the VICE-Team mirror maps SVN commits and publishes GitHub builds. **The C64 Math Library itself does not redistribute VICE ROMs or binaries.**

## Linux headless build

```bash
git clone --recurse-submodules https://github.com/floppyrom/C64-Math-Library.git
cd C64-Math-Library
# Debian/Ubuntu:
sudo apt-get update
sudo apt-get install -y git make gcc g++ autoconf automake libtool pkg-config \
    bison flex texinfo dos2unix xa65 gettext
bash tools/vice/build_headless.sh
export VICE_WRAPPER="$PWD/.vice-build/r46284/bin/x64sc"
bash tools/vice/verify_headless.sh "$VICE_WRAPPER"
python3 tools/native_selective_linker.py
```

The build runs VICE's own `autogen.sh` and `configure --enable-headlessui`, and installs the resulting binary/resources under `.vice-build/r46284`. The upstream checkout is intentionally not modified by the library's development work (autotools may generate ignored local build files). Override `VICE_JOBS` or `VICE_PREFIX` as needed. On a fresh checkout without submodules, the script initializes the exact pinned submodule automatically. It refuses a mismatching VICE source SHA. A `-version` smoke check proves the binary starts; use native math tests for behavioral qualification.

## GitHub Actions

The separate [`vice-trunk.yml`](../../.github/workflows/vice-trunk.yml) workflow builds the exact Git-linked upstream source, verifies the running `x64sc`, and runs representative native tests. It stores the built executable as a **workflow artifact**, not in normal Git history. Its executable artifact by itself is not a standalone VICE installation; use the source build for installation of VICE support data.

The existing general math-builder workflow uses a checksum-pinned r46274 *prebuilt* emulator; this remains intentionally unchanged while the new trunk source build is qualified. Do not conflate the two emulator versions in benchmarks or claim native qualification before the workflow is green.

For redistribution, consult VICE's `vice/COPYING` (GPL-2.0-or-later) and the upstream ROM notices. No upstream VICE code has been copied into the library's proprietary or other source namespaces.
