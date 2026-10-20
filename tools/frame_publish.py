#!/usr/bin/env python3
"""Rollback-safe publication of a validated operation-first C64 frame image.

The five related outputs must all be staged and checked before publication.
If a filesystem replace fails, restore every original file and remove newly
created entries. This is *rollback protection*, not atomic visibility of a
multi-file set for concurrent readers; consumers should read the manifest last.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

NAMES = ("math_selective.prg", "math_api.inc", "frame_qualified_config.json",
         "frame_qualified_evidence.json", "selective_manifest.json")


class PublicationError(OSError):
    pass


def publish(stage: Path, destination: Path) -> None:
    stage, destination = Path(stage), Path(destination)
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        raise PublicationError("Unsafe frame output directory")
    if stage == destination or not stage.is_dir():
        raise PublicationError("Missing independent staging directory")
    for name in NAMES:
        source = stage / name
        target = destination / name
        if not source.is_file() or source.is_symlink():
            raise PublicationError("Missing or unsafe staged file: " + name)
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise PublicationError("Refuse to replace nonregular output: " + name)
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".math_frame_backup_", dir=destination.parent) as tmp:
        backup = Path(tmp)
        for name in NAMES:
            target = destination / name
            if target.exists():
                shutil.copy2(target, backup / name)
        touched: list[str] = []
        try:
            # Keep the manifest as the *last* completion marker.
            for name in NAMES:
                os.replace(stage / name, destination / name)
                touched.append(name)
        except OSError as error:
            restore_failures: list[str] = []
            for name in reversed(touched):
                target = destination / name
                original = backup / name
                try:
                    if original.exists():
                        os.replace(original, target)
                    else:
                        target.unlink(missing_ok=True)
                except OSError as rollback_error:
                    restore_failures.append(name + ": " + str(rollback_error))
            if restore_failures:
                # Avoid silently losing original files if restore itself fails.
                rescue = destination.parent / (".math_frame_rescue_" + backup.name)
                os.replace(backup, rescue)
                raise PublicationError(
                    "Rollback failed; originals retained in " + str(rescue) +
                    ": " + "; ".join(restore_failures)) from error
            raise PublicationError("Frame output publication failed; prior files restored") from error
