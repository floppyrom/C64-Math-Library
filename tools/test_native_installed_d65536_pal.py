#!/usr/bin/env python3
"""Exact installed PRG provenance and PAL three-plan evidence fail-closed tests."""
from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

import mixed_seven_d65536_frame as source
import native_installed_d65536_pal as native


class InstalledD65536PALTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=source.complete_report()

    def test_stock_both_and_signed_only_have_source_identical_installed_prgs(self):
        proofs={}
        with tempfile.TemporaryDirectory(prefix="installed_d65536_") as td:
            for label in native.CHOICES:
                with self.subTest(plan=label):
                    binary,entries,proof=native.build_one(
                        label,self.report,Path(td)/label)
                    self.assertEqual(set(entries),set(source.OPS))
                    self.assertEqual(proof["zero_page_bytes"],31)
                    self.assertEqual(len(proof["linked_prg_sha256"]),64)
                    self.assertEqual(binary[:2],native.CODE.to_bytes(2,"little"))
                    self.assertLess(native.CODE+len(binary)-2,native.cia.HARNESS)
                    proofs[label]=proof
        stock=proofs["fast31-stock-v2"]
        signed=proofs["fast31-uv2-s65536"]
        both=proofs["fast31-u65536-s65536"]
        self.assertEqual(stock["linked_ram_bytes"],signed["linked_ram_bytes"])
        self.assertEqual(both["linked_ram_bytes"]-stock["linked_ram_bytes"],256)
        self.assertNotEqual(stock["linked_prg_sha256"],signed["linked_prg_sha256"])

    @staticmethod
    def sample(label,frame,display,clock):
        return {
            "plan":label,"frame":frame,"display_enabled":display,
            "measured_cia_phi2_slots":clock,
            "qualified_prg_sha256":label,
            "captured_outputs_sha256":"e"*64 if frame==8 else "f"*64,
            "source_frame_inputs_sha256":"a"*64 if frame==8 else "b"*64,
            "source_linked_calls":24 if frame==8 else 3,
        }

    def test_per_frame_wall_slots_and_nominal_deadline_misses(self):
        names=native.CHOICES[:2]
        frames=(0,8)
        rows=[]
        for plan in names:
            for frame in frames:
                off=16174 if plan==names[0] else 16190
                off=(19500 if plan==names[0] else 17000) if frame==8 else off
                on=19883 if frame==8 and plan==names[0] else (
                   17618 if frame==8 else off+300)
                rows += [self.sample(plan,frame,False,off),
                         self.sample(plan,frame,True,on)]
        report=native.summarize(rows,names,frames)
        self.assertEqual(report[names[0]]["nominal_deadline_overruns"],1)
        self.assertEqual(report[names[0]]["peak_frame_index"],8)
        self.assertEqual(report[names[0]]["worst_nominal_headroom_slots"],-227)
        self.assertEqual(report[names[1]]["nominal_deadline_overruns"],0)
        self.assertEqual(report[names[1]]["peak_visible_slots"],17618)

    def test_reject_missing_duplicate_forged_output_or_wrong_prg(self):
        names=native.CHOICES[:2]
        frames=(0,)
        rows=[
            self.sample(name,0,display,16100+100*int(display))
            for name in names for display in (False,True)
        ]
        self.assertEqual(len(native.summarize(rows,names,frames)),2)
        with self.assertRaises(ValueError):
            native.summarize(rows[:3],names,frames)
        with self.assertRaises(ValueError):
            native.summarize(rows+[rows[0]],names,frames)
        forged=copy.deepcopy(rows)
        forged[1]["captured_outputs_sha256"]="0"*64
        with self.assertRaises(AssertionError):
            native.summarize(forged,names,frames)
        forged=copy.deepcopy(rows)
        forged[3]["captured_outputs_sha256"]="0"*64
        forged[2]["captured_outputs_sha256"]="0"*64
        with self.assertRaises(AssertionError):
            native.summarize(forged,names,frames)
        forged=copy.deepcopy(rows)
        forged[1]["qualified_prg_sha256"]="0"*64
        with self.assertRaises(AssertionError):
            native.summarize(forged,names,frames)
        forged=copy.deepcopy(rows)
        forged[1]["measured_cia_phi2_slots"]=1
        with self.assertRaises(AssertionError):
            native.summarize(forged,names,frames)

    def test_refuse_subset_when_real_native_qualification_requested(self):
        with self.assertRaises(ValueError):
            native.run(__file__,frames=(8,))
        with self.assertRaises(ValueError):
            native.run(__file__,labels=native.CHOICES[:1])


if __name__=="__main__":
    unittest.main()
