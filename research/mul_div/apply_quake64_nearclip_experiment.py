#!/usr/bin/env python3
"""Apply the prepared-fraction near-clip experiment to an audited Quake64 tree.

Target:
    Kweepa/Quake64 @ 7c84654946a60314568b709e7e7b97467fed69df

The patch is deliberately narrow:
  * include generated prepared_fraction_smc.asm in GAME;
  * PREP once in .near0/.near1 instead of saving/restoring n/d;
  * route only the four near-plane component helpers to qfrac_apply_s16;
  * leave the shared .nlrun helper untouched, because it is also used by
    Cohen-Sutherland side/top/bottom clipping where no prepared fraction exists.

That last point is important: replacing .nlrun globally would be incorrect.

The script uses exact audited source blocks and fails closed if the target tree
has drifted. It is research tooling, not an upstream Quake64 patch release.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

TARGET_COMMIT = "7c84654946a60314568b709e7e7b97467fed69df"


def replace_once(text: str, old: str, new: str, what: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{what}: expected exactly one audited block, found {count}")
    return text.replace(old, new, 1)


def verify_checkout(root: Path) -> None:
    git = root / ".git"
    if not git.exists():
        return
    try:
        head = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return
    if head != TARGET_COMMIT:
        raise RuntimeError(f"Quake64 checkout drift: expected {TARGET_COMMIT}, got {head}")


def patch_quake64_asm(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    old = '!source "loader.asm"\n\n!source "map_bss.asm"'
    new = (
        '!source "loader.asm"\n'
        '!source "prepared_fraction_smc.asm"\n\n'
        '!source "map_bss.asm"'
    )
    text = replace_once(text, old, new, "quake64.asm include insertion")
    path.write_text(text, encoding="utf-8")


def patch_cube_asm(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    near0_old = """.near0
\tjsr .nd01
\tlda nlo
\tpha
\tlda nhi
\tpha
\tlda dlo
\tpha
\tlda dhi
\tpha
\tjsr .nlx0
\tpla
\tsta dhi
\tpla
\tsta dlo
\tpla
\tsta nhi
\tpla
\tsta nlo
\tjsr .nly0
\tlda #<ZCLIP
\tsta e0z
\tlda #>ZCLIP
\tsta e0zh
\trts
"""
    near0_new = """.near0
\tjsr .nd01
\tjsr qfrac_prep
\tjsr .nlx0
\tjsr .nly0
\tlda #<ZCLIP
\tsta e0z
\tlda #>ZCLIP
\tsta e0zh
\trts
"""
    text = replace_once(text, near0_old, near0_new, "cube.asm .near0")

    near1_old = """.near1
\tjsr .nd10
\tlda nlo
\tpha
\tlda nhi
\tpha
\tlda dlo
\tpha
\tlda dhi
\tpha
\tjsr .nlx1
\tpla
\tsta dhi
\tpla
\tsta dlo
\tpla
\tsta nhi
\tpla
\tsta nlo
\tjsr .nly1
\tlda #<ZCLIP
\tsta e1z
\tlda #>ZCLIP
\tsta e1zh
\trts
"""
    near1_new = """.near1
\tjsr .nd10
\tjsr qfrac_prep
\tjsr .nlx1
\tjsr .nly1
\tlda #<ZCLIP
\tsta e1z
\tlda #>ZCLIP
\tsta e1zh
\trts
"""
    text = replace_once(text, near1_old, near1_new, "cube.asm .near1")

    # Patch only the four dedicated near-plane component helpers. Do not touch
    # .nlrun itself: later Cohen-Sutherland interpolation also calls it.
    helpers = (".nlx0", ".nly0", ".nlx1", ".nly1")
    for label in helpers:
        # Require a real label at column zero. A plain search for ".nlx0\n"
        # also matches the earlier "jsr .nlx0" inside .near0.
        marker = "\n" + label + "\n"
        found = text.count(marker)
        if found != 1:
            raise RuntimeError(f"{label}: expected one audited label, found {found}")
        start = text.index(marker) + 1
        end = text.index("\trts\n", start) + len("\trts\n")
        block = text[start:end]
        if block.count("\tjsr .nlrun\n") != 1:
            raise RuntimeError(f"{label}: audited .nlrun call not found exactly once")
        block = block.replace(
            "\tjsr .nlrun\n",
            "\tjsr qfrac_apply_s16\n\tlda rot0\n",
            1,
        )
        text = text[:start] + block + text[end:]

    # Safety gate: the shared generic helper and its non-near callers must still
    # exist. The experiment is not allowed to silently retarget all .nlrun uses.
    if ".nlrun\n\tjsr scale_nd\n" not in text:
        raise RuntimeError("shared .nlrun was modified; refusing unsafe patch")
    if text.count("jsr qfrac_apply_s16") != 4:
        raise RuntimeError("expected exactly four prepared near-plane APPLY calls")
    if text.count("jsr qfrac_prep") != 2:
        raise RuntimeError("expected exactly two prepared near-plane PREP calls")

    path.write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("quake_root", type=Path)
    ap.add_argument(
        "--prepared-source",
        type=Path,
        required=True,
        help="origin-free prepared_fraction_smc.asm exported by this repository",
    )
    args = ap.parse_args()

    root = args.quake_root.resolve()
    src = root / "src"
    if not (src / "quake64.asm").exists() or not (src / "cube.asm").exists():
        raise SystemExit(f"not a Quake64 source tree: {root}")
    if not args.prepared_source.exists():
        raise SystemExit(f"missing prepared source: {args.prepared_source}")

    verify_checkout(root)
    shutil.copyfile(args.prepared_source, src / "prepared_fraction_smc.asm")
    patch_quake64_asm(src / "quake64.asm")
    patch_cube_asm(src / "cube.asm")

    print(f"patched Quake64 {TARGET_COMMIT}")
    print("shared .nlrun preserved; only near-plane helpers use prepared APPLY")


if __name__ == "__main__":
    main()
