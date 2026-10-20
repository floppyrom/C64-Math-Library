#!/usr/bin/env python3
"""Unit tests for model-only attribution and qualified native burst metadata."""
from __future__ import annotations

import hashlib
import json
import unittest

import mixed_seven_frame_parity as seven
from frame8_source_hotspots import (
    PROFILE_LABELS, PAL_FRAME, rank_attribution, native_sweep_attribution,
)
from native_pal_vic_cia_probe import expected_byte
from native_pal_vic_cia_sweep import summarize as summarize_native


def model(profile, shift=0, frame=8):
    calls = []
    for i, operation in enumerate(seven.OPS):
        calls.append({
            "frame": frame, "ordinal": i, "operation": operation,
            "input_id": str(i)*64, "source_variant": profile,
            "math_and_jsr_cycles": (1000 + 20*i + shift),
        })
    return {
        "source": profile, "label": PROFILE_LABELS[profile],
        "source_prg_sha256": ("a" if profile=="compact" else "b")*64,
        "frame": frame, "calls": calls,
    }


def synthetic_native(compact, fast):
    rows = []
    for profile, source in (("compact",compact),("fast31",fast)):
        for frame in range(seven.FRAMES):
            original = [r for r in seven.scenario() if r[0] == frame]
            ident = hashlib.sha256(json.dumps(
                [r[-1] for r in original],separators=(",", ":")).encode()).hexdigest()
            digest = hashlib.sha256(bytes(
                byte for r in original for byte in expected_byte(r[2],r[3],r[4],r[5])
            )).hexdigest()
            for display in (False, True):
                rows.append({
                    "frame": frame,
                    "display_enabled": display,
                    "name": f"{profile}_f{frame:02d}_screen{int(display)}",
                    "measured_cia_phi2_slots": 12000+(int(display)*200)+frame,
                    "qualified_prg_sha256":source["source_prg_sha256"],
                    "selected_choice":source["label"],
                    "source_frame_inputs_sha256":ident,
                    "captured_outputs_sha256":digest,
                    "source_linked_calls":len(original),
                    "nominal_pal_frame_slots":PAL_FRAME,
                    "limited_probe_not_application_frame_qualification":True,
                })
    return {
        "schema":"independent-native-pal-vic-cia-frame-sweep-v1",
        "real_application_frame_certified":False,
        "consecutive_50hz_frames_measured":False,
        "irq_sid_reu_dma_measured":False,
        "profiles":["compact","fast31"],
        "frames":list(range(seven.FRAMES)),
        "runs":rows,
        "summaries":[summarize_native(
            [r for r in rows if r["name"].startswith(profile+"_f")],
            frames=tuple(range(seven.FRAMES)),profile=profile)
            for profile in ("compact","fast31")],
    }


class SourceHotspotsTests(unittest.TestCase):
    def test_source_model_ranking_and_pairing(self):
        compact, fast = model("compact",shift=500), model("fast31")
        result=rank_attribution(compact,fast)
        self.assertEqual(result["public_calls"],7)
        self.assertEqual(result["model_math_and_jsr_cycles_saved"],3500)
        self.assertEqual(result["per_operation_ranked_by_fast31_model_cycles"][0]
                         ["operation"],seven.OPS[-1])
        self.assertEqual(result["per_call_ranked_by_fast31_model_cycles"][0]
                         ["ordinal"],6)
        self.assertFalse(result["native_per_call_timing_measured"])
        fast["calls"][0]["input_id"]="tampered"
        with self.assertRaises(ValueError):
            rank_attribution(compact,fast)

    def test_real_benchmark_provenance_and_exact_native_inputs(self):
        compact,fast=model("compact"),model("fast31")
        report=synthetic_native(compact,fast)
        valid=native_sweep_attribution(report,compact,fast,frame=8)
        self.assertEqual(valid["native_whole_burst_for_selected_frame"]
                         ["fast31"]["whole_burst_cia_display_on_slots"],12208)
        self.assertFalse(valid["real_application_frame_certified"])
        report["runs"][1]["qualified_prg_sha256"]="0"*64
        with self.assertRaises(ValueError):
            native_sweep_attribution(report,compact,fast,frame=8)

    def test_reject_forged_call_result_and_missing_native_sample(self):
        compact,fast=model("compact"),model("fast31")
        report=synthetic_native(compact,fast)
        report["runs"][8]["captured_outputs_sha256"]="f"*64
        with self.assertRaises(ValueError):
            native_sweep_attribution(report,compact,fast,frame=8)
        report=synthetic_native(compact,fast)
        report["runs"].pop()
        with self.assertRaises(ValueError):
            native_sweep_attribution(report,compact,fast,frame=8)
        report=synthetic_native(compact,fast)
        report["summaries"][0]["peak_display_on_native_slots"]=1
        with self.assertRaises(ValueError):
            native_sweep_attribution(report,compact,fast,frame=8)


if __name__=="__main__":
    unittest.main()
