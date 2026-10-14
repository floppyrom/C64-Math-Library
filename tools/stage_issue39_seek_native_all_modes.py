#!/usr/bin/env python3
"""Seal successful native VICE all-STEP SEEK research without changing binaries."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
EVID=R/"validation/review/ISSUE39_SEEK_ALL_MODES_NATIVE_VICE_2026-10-14.json"
DOC=R/"docs/ISSUE39_SEEK_NATIVE_ALL_MODES_2026-10-14.md"
STAMP="2026-10-14 ISSUE39 SEEK8/16 ALL-MODE NATIVE VICE CERTIFICATION"
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")

def main():
 data=json.loads(EVID.read_text())
 statuspath=R/"RELEASE_STATUS.json"
 state=json.loads(statuspath.read_text())
 assert data["status"]=="PASS_NATIVE_SEEK8_16_ALL_STEP_MODES" or (
   data["status"]=="PASS_NATIVE_SEEK8_16_ALL_STEP_MODES")
 assert data["native_public_step_calls"]==640
 assert data["native_public_init_calls"]==40
 assert not data["native_cycle_timing_measured"]
 for p in P:
  row=data["profiles"][p]
  assert row["step_calls"]==128 and len(row["public_modes"])==8
  assert row["prg_sha256"]==state["reference_prg_sha256"][p],p
  assert len({s["frames_to_arrive"] for s in row["public_modes"].values()})>1
  f=R/p/"resident"/f"math_{p}_game_math.prg"
  assert hashlib.sha256(f.read_bytes()).hexdigest()==row["prg_sha256"]
 # Research release provenance; does not change public ABI/binaries or
 # certify native cycle timing.
 key="issue39_seek_native_all_modes_2026_10_14"
 state[key]={
   "status":"PASS_NATIVE_RESEARCH_MAIN_CI_PENDING",
   "native_public_init_calls":40,
   "native_public_step_calls":640,
   "all_eight_public_modes":True,
   "all_five_resident_profiles":True,
   "reu_v3_v4_used":True,
   "native_cycle_timing_measured":False,
   "unchanged_production_binaries":True,
   "source":str(EVID.relative_to(R)),
   "doc":str(DOC.relative_to(R)),
   "family_campaign_complete":False,
 }
 statuspath.write_text(json.dumps(state,indent=2)+"\n")
 lines=[
   "# SEEK8/16: native VICE qualification of all stepper modes",
   "",
   "**Result: PASS native research; no native cycle timing measured.**",
   "",
   "The real x64sc 6502 execution harness invokes each of eight public",
   "SEEK modes using shipped V1–V5 PRGs. It tests STEP with major-axis",
   "fraction and Euclidean flag, STEP_INT and STEP1 at 16 frames per test;",
   "all eight INIT routes are invoked. It records the actual frame-by-frame",
   "X and Y positions, carry flag, X register and CPU stack pointer through",
   "the monitor's saved RAM, then checks each against the independent",
   "Bresenham/reference movement model, including post-arrival repeats.",
   "",
   "| Metric | Observed calls |",
   "|---|---:|",
   "| Native public INIT calls | 40 |",
   "| Native public STEP/STEP_INT/STEP1 calls | 640 |",
   "| Profiles | V1, V2, V3, V4, V5 |",
   "| REU simulation | V3 512KiB, V4 16MiB |",
   "",
   "The prior eight-slot CPU-model campaign independently passed 480 INIT",
   "calls, 246,480 STEP calls and 86,960 movement frames across both",
   "source relocations, plus 18,280 mixed DIV/MOD coexistence calls.",
   "",
   "## Per-profile native evidence",
   "",
   "| Profile | Native STEP calls | Dump SHA256 |",
   "|---|---:|---|",
 ]
 for p in P:
  row=data["profiles"][p]
  lines.append(f"| {p} | {row['step_calls']} | {row['native_dump_sha256']} |")
 lines += [
   "",
   "This adds a native correctness check for SEEK8 INIT/STEP/STEP_INT/STEP1",
   "and SEEK16 INIT/STEP/STEP_INT/STEP1 without modifying any public API",
   "address, production PRG, REU image, normal zero page or lookup table.",
   "Its hardware emulator run does **not** provide native cycle counts.",
   "Private OptiSearch code is not published. A final family review and",
   "postmerge main CI check are still required before checking Issue #39.",
   "",
   "Native harness: tools/native_issue39_seek_all_modes.py",
   "Evidence: "+str(EVID.relative_to(R)),
   "Green CI: https://github.com/floppyrom/C64-Math-Library/actions/runs/38626688576",
 ]
 DOC.write_text("\n".join(lines)+"\n")
 note=(STAMP+"\n- Native x64sc executes all eight SEEK8/16 INIT/STEP,"
       " STEP_INT and STEP1 public modes on V1–V5, 40 INIT and 640"
       " STEP calls; checks movement, arrival carry, X, stack and"
       " post-arrival stability against independent model, using"
       " real V3/V4 REU images. No native cycle timing claimed."
       " No production binary/API/REU/ZP changes; main certification"
       " and full SEEK family closeout still pending. "
       +str(DOC.relative_to(R))+"\n\n")
 for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=R/name
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
 print("ISSUE39 NATIVE ALL STEPPERS RESEARCH SEALED; NO BINARIES CHANGED",flush=True)

if __name__=="__main__":
 main()
