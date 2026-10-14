#!/usr/bin/env python3
"""Seal the passing research-only Issue39 8-object SEEK family audit."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
EVID="validation/review/ISSUE39_SEEK_ALL_SLOTS_RESEARCH_2026-10-14.json"
DOC="docs/ISSUE39_SEEK_ALL_SLOTS_RESEARCH_2026-10-14.md"
STAMP="2026-10-14 ISSUE39 SEEK8/16 EIGHT-OBJECT INTERLEAVING RESEARCH"
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
K=("reference","alternate")
MODES=("SEEK8_STEP","SEEK8_INT","SEEK8_ONE","SEEK16_STEP","SEEK16_INT","SEEK16_ONE")

def main():
 d=json.loads((R/EVID).read_text())
 assert d["status"]=="PASS_SEEK_ALL_EIGHT_SLOTS"
 assert d["totals"]=={"init_calls":480,"step_calls":246480,"model_frames":86960},d["totals"]
 release=json.loads((R/"RELEASE_STATUS.json").read_text())
 assert release["issue39_seek16_euclid_scale_2026_10_14"]["issue136_v1v5_division_seek_collision_repaired"]
 for p in P:
  for k in K:
   row=d["profiles"][p][k]
   assert row["status"]=="PASS" and set(row["scenarios"])==set(MODES)
   assert len(row["public_api_addresses"])==8
   for obj in row["scenarios"].values():
    assert obj["init_calls"]==8 and obj["eight_simultaneous_slots"]
    assert obj["post_arrival_calls_per_slot"]==2
   root=R/("build_hybrid" if p==P[-1] else "build_source")/k/p
   man=json.loads((root/"source_build_manifest.json").read_text())
   b=(root/man["output_prg"]).read_bytes()
   assert hashlib.sha256(b).hexdigest()==row["source_prg_sha256"]
 lines=[
  "# SEEK8/16 all-slots public ABI research — Issue #39",
  "",
  "**Status: research PASS.** No production code/PRG/REU changes or new",
  "performance winner is asserted. The overall SEEK campaign remains open.",
  "",
  "V1–V5 were source-built in both relocations. Eight objects were initialized",
  "concurrently for each width and mode; every frame matched the independent",
  "Bresenham reference path, carry, X and stack pointer. State/planes for",
  "the other seven slots were checked byte-for-byte after every call,",
  "including two post-arrival calls per slot.",
  "",
  "| Check | Total |","|---|---:|",
  "| INIT public calls | 480 |",
  "| STEP, STEP_INT and STEP1 public calls | 246,480 |",
  "| Independent movement frames | 86,960 |",
  "",
  "Additionally, the permanent Issue #136 mixed DIV/MOD coexistence test",
  "passed 18,280 DIV/MOD calls and 13,580 SEEK steps, while the full",
  "SEEK memory-placement tracer passed on both relocations.",
  "",
  "## Same-case CPU-model performance (not native hardware timing)",
  "",
  "| Profile | Map | Mode | INIT average cycles | STEP average cycles | STEP calls |",
  "|---|---|---|---:|---:|---:|",
 ]
 for p in P:
  for k in K:
   for mode in MODES:
    x=d["profiles"][p][k]["scenarios"][mode]
    lines.append(f"| {p} | {k} | {mode} | {x['init_mean_cpu_cycles']:.3f} | "
                 f"{x['step_mean_cpu_cycles']:.3f} | {x['step_calls']:,} |")
 lines += [
  "",
  "## Optimization disposition",
  "",
  "The current hot steppers use no scratch or additional ZP. Any replacement",
  "must retain per-frame carry, all stored movement planes, all eight slots",
  "and the exact public ABI. The existing SEEK16 Euclidean init branch",
  "improvement was source-published in PR #135. OptiSearch P40 raw-delta",
  "Bresenham and clock-precise kernels use different state/speed contracts,",
  "so their standalone sizes are not comparable to the full SEEK8/16 ABI.",
  "Private OptiSearch code is not included. An axis-aligned init shortcut",
  "remains a research hypothesis, not a measured public speed win.",
  "",
  "The native all-stepper qualification, final optimizer audit and",
  "postmerge main CI closeout remain pending. This research result",
  "does not claim native emulator cycle measurements.",
  "",
  "Source: tools/validate_issue39_seek_all_slots.py",
  "Evidence: "+EVID,
  "CI: https://github.com/floppyrom/C64-Math-Library/actions/runs/38625412203"
 ]
 (R/DOC).write_text("\n".join(lines)+"\n")
 note=(STAMP+"\n- Five profiles, reference/alternate, eight concurrent slots"
       " and all INIT/STEP/STEP_INT/STEP1 modes qualified: 480 INITs,"
       " 246,480 STEP calls, 86,960 model frames, slot isolation and"
       " post-arrival safety. Mixed DIV/MOD and memory-island gates passed."
       " No changes to public API, resident PRGs, REU or speed tables."
       " Native all-stepper proof and full SEEK optimization still open."
       " "+DOC+"\n\n")
 for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=R/name
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
 print("ISSUE39 EIGHT-SLOT RESEARCH SEALED; PRODUCTION BINARIES UNCHANGED",flush=True)
if __name__=="__main__":
 main()
