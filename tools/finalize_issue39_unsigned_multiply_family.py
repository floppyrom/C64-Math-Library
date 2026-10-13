#!/usr/bin/env python3
"""Finalize Issue39 basic unsigned multiply family after main release checks.

Use ONLY after verifying the specified post-merge main SHA and runs on GitHub.
OptiSearch source must remain private. Further REU Turbo/QS work is separate.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
DOC=R/"docs/ISSUE39_UNSIGNED_MULTIPLY_FAMILY_REVIEW_2026-10-14.md"
STAMP="2026-10-14 ISSUE39 UNSIGNED MULTIPLY FAMILY COMPLETE"
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--main-sha",required=True)
    ap.add_argument("--full-ci",required=True,type=int)
    ap.add_argument("--comparable-ci",required=True,type=int)
    ap.add_argument("--family-ci",required=True,type=int)
    a=ap.parse_args()
    assert len(a.main_sha)==40 and all(c in "0123456789abcdef" for c in a.main_sha)
    stfile=R/"RELEASE_STATUS.json"
    status=json.loads(stfile.read_text())
    residents={p:hashfile(R/p/"resident"/("math_"+p+"_game_math.prg")) for p in PROFILES}
    assert residents==status["reference_prg_sha256"]
    row=status["issue39_umul24_v1v5_rare_carry_clc_2026_10_14"]
    assert row["status"] in ("PASS_NATIVE_VICE_PR_CI_PENDING","PASS_POSTMERGE_MAIN_GREEN")
    assert row["native_vice_calls"]==384 and row["gain_cycles_every_case"]==1
    proof=json.loads((R/"validation/review/ISSUE39_V1V5_UMUL24_RARECARRY_RELEASE_2026-10-14.json").read_text())
    assert proof["mean_saving"]==1 and proof["tested_calls_per_profile"]==10324
    private=json.loads((R/"validation/review/ISSUE39_UMUL16_UMUL24_OPTISEARCH_RESOURCE_AUDIT.json").read_text())
    assert private["private_source_published"] is False
    row.update(status="PASS_POSTMERGE_MAIN_GREEN",merge_sha=a.main_sha,
       postmerge_full_ci_run=a.full_ci,postmerge_comparable_ci_run=a.comparable_ci)
    status["issue39_unsigned_multiply_family_2026_10_14"]={
      "status":"PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
      "completed":True,"issue39_remains_open":True,
      "routines":["MATH_UMUL8","MATH_UMUL16","MATH_UMUL24","MATH_UMUL32","MATH_UMUL32_READY"],
      "source_and_optisearch_review":"docs/ISSUE39_UNSIGNED_MULTIPLY_FAMILY_REVIEW_2026-10-14.md",
      "private_optisearch_source_published":False,
      "normal_umul32_pointer_repair_preserved":True,
      "umult32_ready_wrong_after_dirty_state_per_lowzp_profile":312,
      "native_umul24_calls":384,
      "native_cycle_timing_measured":False,
      "postmerge_main_sha":a.main_sha,
      "qualification_checks":{"postmerge_full_library":a.full_ci,
                              "postmerge_comparable_unsigned":a.comparable_ci,
                              "premerge_family_audit":a.family_ci},
      "reference_prg_sha256":residents,
      "separate_campaign":"REU Turbo16/Turbo32/QS16 multiply and remaining Issue39 families"}
    stfile.write_text(json.dumps(status,indent=2)+"\n")
    certificate={
       "status":"PASS_POSTMERGE_MAIN_GREEN",
       "issue39_complete":False,
       "unsigned_multiply_family_complete":True,
       "routines":status["issue39_unsigned_multiply_family_2026_10_14"]["routines"],
       "compiled_profile_sha256":residents,
       "UMUL8_exhaustive_pairs_per_lowzp_profile":65536,
       "UMUL16_pairs_per_profile_per_map":10169,
       "UMUL24_pairs_per_profile_per_map":10324,
       "UMUL32_ready_shared_pairs_per_profile":2409,
       "UMUL32_normal_lowzp_pointer_repair_preserved":True,
       "UMUL32_unqualified_ready_wrong_per_lowzp_profile":312,
       "UMUL24_rarecarry_uniform_saving_cycles":1,
       "native_VICE_calls":384,
       "native_cycle_timing_measured":False,
       "private_optisearch_source_published":False,
       "main_sha":a.main_sha,
       "main_full_library_run":a.full_ci,
       "main_comparable_unsigned_run":a.comparable_ci,
       "premerge_family_run":a.family_ci,
       "separate_reu_multiply_step_pending":True
    }
    target=R/"validation/review/ISSUE39_UNSIGNED_MULTIPLY_FAMILY_COMPLETION_2026-10-14.json"
    target.write_text(json.dumps(certificate,indent=2,sort_keys=True)+"\n")
    doc=DOC.read_text()
    statement=("**Completion certification (14 October 2026):** The basic unsigned "
       "multiply implementation family is complete. The merged V1/V5 rare-carry "
       "change, independent full-source five-profile family gate, checksummed "
       "package and post-merge main library/performance checks passed. "
       "Issue #39 stays open for remaining families.\n\n")
    if statement not in doc:
       doc=doc.replace("## Compatible source/ABI decisions",statement+"## Compatible source/ABI decisions")
       DOC.write_text(doc)
    note=(STAMP+"\n- UMUL8/16/24/32 and stateful READY: five-profile ABI, "
       "reference/alternate source-build and deterministic mixed-call review completed. "
       "UMUL8 exhaustive 65,536; UMUL16 10,169; UMUL24 10,324; UMUL32/READY "
       "2,409 matched inputs/profile.\n- V1/V5 UMUL24 uniform -1 CPU-model cycle "
       "(466.042329 to 465.042329), 384 native x64sc old/new calls; no extra "
       "resident/ZP bytes. Normal UMUL32 pointer repair retained; private "
       "OptiSearch candidates not promoted without ABI/resource proof.\n"
       +"- Postmerge main "+a.main_sha+" full CI "+str(a.full_ci)
       +", comparable "+str(a.comparable_ci)+"; family gate "+str(a.family_ci)
       +". Other Issue39 families and REU Turbo/QS remain OPEN.\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
       p=R/name
       if STAMP not in p.read_text():p.write_text(note+p.read_text())
    readme=R/"README.md"
    if readme.exists():
       content=readme.read_text()
       dest="docs/ISSUE39_UNSIGNED_MULTIPLY_FAMILY_REVIEW_2026-10-14.md"
       if dest not in content:
          readme.write_text(content+"\nThe standard unsigned multiply family "
             "(UMUL8/16/24/32 and stateful READY) is [qualified and complete]("
             +dest+"). REU Turbo/QS multiply modes are separate.\n")
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
       reseal()
       subprocess.run([sys.executable,str(R/"tools/package_audit.py")],
                      cwd=R,check=True)
    subprocess.run([sys.executable,str(R/"tools/issue39_unsigned_multiply_completion_audit.py")],
                   cwd=R,check=True)
    print("ISSUE39 UNSIGNED MULTIPLY FAMILY PUBLICATION SEALED; ISSUE39 OPEN")
if __name__=="__main__":main()
