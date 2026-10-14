#!/usr/bin/env python3
"""Source-backed SEEK family closeout staging; never changes resident binaries."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal

EVID="validation/review/ISSUE39_SEEK_FAMILY_FINAL_AUDIT_2026-10-14.json"
DOC="docs/ISSUE39_SEEK_FAMILY_COMPLETION_2026-10-14.md"
STAMP="2026-10-14 ISSUE39 SEEK8/16 COMPLETE FAMILY AUDIT"
P=("v1_balanced","v2_pareto_fast","v3_reu_512k",
   "v4_reu_16m","v5_hybrid_lowzp")
API=("MATH_SEEK8_INIT","MATH_SEEK8_STEP","MATH_SEEK8_STEP_INT","MATH_SEEK8_STEP1",
     "MATH_SEEK16_INIT","MATH_SEEK16_STEP","MATH_SEEK16_STEP_INT","MATH_SEEK16_STEP1")
def sha(path):return hashlib.sha256((R/path).read_bytes()).hexdigest()
def main():
    evidence=json.loads((R/EVID).read_text())
    assert evidence["status"]=="PASS_FAMILY_AUDIT_WITH_NO_NEW_PRODUCTION_CANDIDATE"
    assert evidence["binary_unchanged"] and evidence["abi_unchanged"]
    bench=json.loads((R/"validation/movement/SEEK_PROFILE_BENCHMARK.json").read_text())
    assert bench["status"]=="PASS"
    statepath=R/"RELEASE_STATUS.json"
    status=json.loads(statepath.read_text())
    assert status["reference_prg_sha256"]==bench["prg_sha256"]
    assert status["issue39_seek_native_all_modes_2026_10_14"]["native_public_step_calls"]==640
    assert status["issue39_seek16_euclid_scale_2026_10_14"]["issue136_v1v5_division_seek_collision_repaired"]
    for p in P:
        assert set(bench["profiles"][p])==set(API)
        assert sha(p+"/resident/math_"+p+"_game_math.prg")==bench["prg_sha256"][p]
        assert all(bench["profiles"][p][entry]["cases"]>0 for entry in API)
        assert all(not evidence["resource_screening"][p]["source_maps"][k]["fits_existing_island"]
                   for k in ("reference","alternate"))
    doc=[
      "# Issue #39: completed SEEK8/16 public-family audit",
      "",
      "**Audit PASS, without an additional qualified production optimization.**",
      "This is not a claim that no faster algorithm exists.",
      "",
      "The existing source-integrated SEEK16_INIT Euclidean scaling optimization",
      "(PR #135) remains published. The V1/V5 UDIV32/16 and SEEK-state overlap",
      "(Issue #136) remains repaired. No new binary, API, REU or ZP changes",
      "were made in this final family audit.",
      "",
      "## Official public-entry 408-move CPU-model mean cycles",
      "",
      "| Profile | SEEK8 INIT | STEP | STEP_INT | STEP1 | SEEK16 INIT | STEP | STEP_INT | STEP1 |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in P:
        values=[f"{bench['profiles'][p][x]['mean_cycles']:.3f}" for x in API]
        doc.append("| "+p+" | "+" | ".join(values)+" |")
    doc += [
      "",
      "These are CPU-model cycles; native VICE cycle timing was not measured.",
      "",
      "## Explicit resource screen: SEEK16 integer-speed-one shortcut",
      "",
      "| Profile | Stock INIT bytes | Verified available island bytes | Candidate bytes | Fits |",
      "|---|---:|---:|---:|---|",
    ]
    for p in P:
        x=evidence["resource_screening"][p]
        trial=x["source_maps"]["reference"]
        doc.append(f"| {p} | {x['current_bytes']} | {x['single_island_capacity_bytes']} | "
                   f"{trial['candidate_bytes']} | no |")
    doc += [
      "",
      "The proposed shortcut is larger than every safely occupied code",
      "island. Importantly, the V2 SEEK16_INIT ends at $19EF but $19F0",
      "already contains an unrelated resident byte and the initialized",
      "table at $1A00 must not be overwritten. The separate trial in",
      "PR #142 correctly failed public validation when extended to $1A04.",
      "That candidate is rejected; neither performance gain nor native",
      "correctness has been claimed for it. A relocation-based specialist",
      "would require a separate, independently qualified architectural",
      "study rather than silently changing stable resources.",
      "",
      "## Exact public-family tests",
      "",
      "- Five profiles, both source relocations, eight live SEEK objects:",
      "  480 INIT calls and 246,480 public STEPs covering 86,960 reference",
      "  movement frames with full unrelated-slot isolation (PR #139).",
      "- Native x64sc with real V3/V4 REU images: 40 INIT and 640 STEP",
      "  public calls, including fractional, integer, Euclidean and",
      "  post-arrival paths (PR #140). No native cycle timing measured.",
      "- Mixed safety: 18,280 UDIV/UMOD public calls and 13,580 SEEK",
      "  calls with full 408-byte movement-state preservation; placement PASS.",
      "",
      "OptiSearch P40 raw-delta kernels have distinct speed/state contracts",
      "and cannot be ranked as drop-in replacements for the public Q8.8",
      "SEEK family. Its private source is not part of this release.",
      "",
      "Existing per-frame STEP/STEP_INT/STEP1 paths remain because no",
      "additional publicly compatible winner was validated under the",
      "fixed resource budgets. This ends the Issue #39 SEEK audit, subject",
      "to a successful post-merge main CI closeout.",
      "",
      "Evidence: "+EVID,
      "Official benchmark: validation/movement/SEEK_PROFILE_BENCHMARK.json",
      "Native proof: validation/review/ISSUE39_SEEK_ALL_MODES_NATIVE_VICE_2026-10-14.json",
      "All-slot proof: validation/review/ISSUE39_SEEK_ALL_SLOTS_RESEARCH_2026-10-14.json",
    ]
    (R/DOC).write_text("\n".join(doc)+"\n")
    status["issue39_seek_family_completion_2026_10_14"]={
      "status":"PASS_FAMILY_AUDIT_MAIN_POSTMERGE_PENDING",
      "all_eight_public_ops_audited":True,
      "native_init_calls":40,"native_step_calls":640,
      "all_slot_init_calls":480,"all_slot_step_calls":246480,
      "k1_fastpath_rejected_due_occupied_resident_bytes":True,
      "new_public_speed_winner_promoted":False,
      "existing_seek16_init_optimization_remains_published":True,
      "profile_prgs_unchanged":True,"abi_and_reu_unchanged":True,
      "native_cycle_timing_measured":False,
      "private_optisearch_published":False,
      "certificate":EVID,"documentation":DOC,
      "main_ci_postmerge_certified":False,
      "issue39_closeout_pending":True}
    statepath.write_text(json.dumps(status,indent=2)+"\n")
    note=(STAMP+"\n- Final audited all eight SEEK8/16 public APIs."
          " 480 INIT / 246,480 STEP CPU-model calls across all slots/maps,"
          " 40 INIT / 640 STEP native x64sc calls with V3/V4 REU."
          " V2 k0=1 shortcut rejected: foreign resident bytes at"
          " $19F0 and table $1A00, not an available code island."
          " No new qualified speed winner; shipped binaries, REU,"
          " public ABI and ZP remain unchanged. Prior SEEK16_INIT"
          " optimization remains in release. Main CI required for"
          " Issue #39 closeout. "+DOC+"\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        f=R/name
        if STAMP not in f.read_text():f.write_text(note+f.read_text())
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
    print("ISSUE39 SEEK FAMILY AUDIT SEALED, MAIN CI PENDING",flush=True)
if __name__=="__main__":main()
