#!/usr/bin/env python3
"""Frame PRG publication protects prior artifacts if one replace fails."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from frame_publish import NAMES, PublicationError, publish


def staged(folder, label):
    folder.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        (folder / name).write_bytes((label + "/" + name).encode("ascii"))


class FramePublicationTests(unittest.TestCase):
    def test_complete_set_and_unrelated_files_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output, source = root / "output", root / "stage"
            staged(source, "new")
            staged(output, "old")
            (output / "userdata.bin").write_bytes(b"DO NOT TOUCH")
            publish(source, output)
            for name in NAMES:
                self.assertEqual((output / name).read_bytes(), ("new/" + name).encode("ascii"))
            self.assertEqual((output / "userdata.bin").read_bytes(), b"DO NOT TOUCH")
            self.assertFalse(any(root.glob(".math_frame_backup_*")))

    def test_rollback_restores_all_old_outputs_after_third_replacement_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output, source = root / "output", root / "stage"
            staged(source, "new")
            staged(output, "old")
            (output / "userdata.bin").write_bytes(b"preserve")
            original_replace = os.replace
            counter = [0]

            def fail_on_third(src, dest):
                if Path(src).parent == source:
                    counter[0] += 1
                    if counter[0] == 3:
                        raise OSError("injected third-artifact I/O failure")
                return original_replace(src, dest)

            with mock.patch("frame_publish.os.replace", side_effect=fail_on_third):
                with self.assertRaisesRegex(PublicationError, "prior files restored"):
                    publish(source, output)
            self.assertEqual(counter[0], 3)
            for name in NAMES:
                self.assertEqual((output / name).read_bytes(), ("old/" + name).encode("ascii"))
            self.assertEqual((output / "userdata.bin").read_bytes(), b"preserve")
            self.assertFalse(any(root.glob(".math_frame_backup_*")))

    def test_failed_new_install_has_no_partial_binary(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output, source = root / "output", root / "stage"
            staged(source, "new")
            original_replace = os.replace
            counter = [0]

            def fail_second(src, dest):
                if Path(src).parent == source:
                    counter[0] += 1
                    if counter[0] == 2:
                        raise OSError("simulated disk error")
                return original_replace(src, dest)

            with mock.patch("frame_publish.os.replace", side_effect=fail_second):
                with self.assertRaises(PublicationError):
                    publish(source, output)
            self.assertEqual(counter[0], 2)
            self.assertFalse(any((output / p).exists() for p in NAMES))

    def test_rejects_missing_staged_file_before_any_destination_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output, source = root / "output", root / "stage"
            staged(output, "old")
            staged(source, "new")
            (source / NAMES[2]).unlink()
            with self.assertRaisesRegex(PublicationError, "Missing or unsafe staged"):
                publish(source, output)
            for name in NAMES:
                self.assertEqual((output / name).read_bytes(), ("old/" + name).encode("ascii"))

    def test_rejects_existing_symlink_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            output, source = root / "output", root / "stage"
            staged(output, "old")
            staged(source, "new")
            target = root / "external.data"
            target.write_bytes(b"untouched")
            (output / NAMES[0]).unlink()
            (output / NAMES[0]).symlink_to(target)
            with self.assertRaisesRegex(PublicationError, "nonregular"):
                publish(source, output)
            self.assertEqual(target.read_bytes(), b"untouched")
            self.assertTrue((output / NAMES[0]).is_symlink())


if __name__ == "__main__":
    unittest.main()
