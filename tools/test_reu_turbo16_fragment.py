#!/usr/bin/env python3
"""Turbo16 independent assembled-source geometry/relocation qualifications."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import reu_turbo16_fragment as core

class ModularTurbo16SourceTests(unittest.TestCase):
    def test_exact_executable_zp_and_call_binder_across_two_memmaps(self):
        a,blocks=core.assemble()
        self.assertEqual(a["exclusive_zp_bytes"],122)
        self.assertEqual(a["exclusive_zp_start"],"$3E")
        self.assertEqual(a["call_entry"],"$3840")
        self.assertFalse(a["reu_dma_begin_end_implemented"])
        self.assertFalse(a["source_code_link_qualified"])
        self.assertEqual(len(blocks["turbo16_zp_overlay.bin"]),122)
        for name,blob in blocks.items():
            self.assertEqual(a["segment_sha256"][name],hashlib.sha256(blob).hexdigest())
        b,other=core.assemble(zp=0x20,io=0xc040,table=0x5000,api=0x4000)
        self.assertEqual(b["exclusive_zp_start"],"$20")
        self.assertEqual(b["call_entry"],"$4840")
        self.assertNotEqual(a["segment_sha256"]["turbo16_call_binder.bin"],
                            b["segment_sha256"]["turbo16_call_binder.bin"])
        self.assertNotEqual(blocks["turbo16_zp_overlay.bin"],other["turbo16_zp_overlay.bin"])
        self.assertEqual(a["reference_sources_sha256"],b["reference_sources_sha256"])

    def test_reject_unqualified_memory_placement(self):
        examples=(({"zp":1},"zero page"),
                  ({"zp":0x86},"zero page"),
                  ({"io":0xd000},"C64 RAM/I/O"),
                  ({"table":0x5001},"page aligned"),
                  ({"table":0xc000},"C64 RAM/I/O"),
                  ({"api":0xc800},"C64 RAM/I/O"))
        for kwargs,message in examples:
            with self.subTest(kwargs=kwargs),self.assertRaisesRegex(core.FragmentError,message):
                core.assemble(**kwargs)

    def test_source_tamper_fails_closed(self):
        with patch.object(core,"locked_source",side_effect=core.FragmentError("SHA-qualified source drift")):
            with self.assertRaisesRegex(core.FragmentError,"SHA-qualified"):
                core.assemble()

    def test_nonoverwriting_cli_and_report_byte_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)/"modular"
            cmd=[sys.executable,str(core.ROOT/"tools"/"reu_turbo16_fragment.py"),
                 "--out",str(out)]
            first=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(first.returncode,0,first.stderr)
            report=json.loads((out/"fragment_manifest.json").read_text())
            self.assertEqual(report["status"],"ASSEMBLED_SOURCE_FRAGMENTS_NO_NATIVE_REU_BACKEND")
            for name,hashval in report["segment_sha256"].items():
                self.assertEqual(hashlib.sha256((out/name).read_bytes()).hexdigest(),hashval)
            second=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(second.returncode,0)
            self.assertIn("refusing to overwrite",second.stderr)

if __name__=="__main__":
    unittest.main()
