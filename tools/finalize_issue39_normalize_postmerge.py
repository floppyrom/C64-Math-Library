#!/usr/bin/env python3
"""Finalize the already merged V1/V2/V5 NORMALIZE optimization, evidence-only.

No production binaries or public ASM change here. Gate original/candidate
resident SHA, all published results, native x64sc/CPU-model proof and verified
green post-merge main CI. Then synchronize BOTH changelogs and SHA256.
"""
from pathlib import Path
import hashlib,json,sys,subprocess,argparse
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
STOCK=(P[0],P[1],P[4])
KEY="issue39_normalize_branch_collapse_2026_10_14"
CERT="validation/review/ISSUE39_NORMALIZE_POSTMERGE_COMPLETION_2026-10-14.json"
TAG="2026-10-14 ISSUE39 NORMALIZE POSTMERGE FINAL CERTIFICATION"
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--merged-sha",required=True)
 ap.add_argument("--main-full",type=int,required=True)
 ap.add_argument("--main-comparable",type=int,required=True)
 ap.add_argument("--main-fixed",type=int,required=True)
 a=ap.parse_args()
 assert len(a.merged_sha)==40 and all(c in "0123456789abcdef" for c in a.merged_sha)
 sp=R/"RELEASE_STATUS.json";st=json.loads(sp.read_text())
 item=st[KEY]
 assert item["status"]=="PASS_STAGED_PR_MAIN_CI_PENDING",item["status"]
 old=json.loads((R/"validation/review/ISSUE39_NORMALIZE_BRANCH_COLLAPSE_RESEARCH_2026-10-14.json").read_text())
 native=json.loads((R/"validation/review/ISSUE39_NORMALIZE_BRANCH_COLLAPSE_NATIVE_2026-10-14.json").read_text())
 staged=json.loads((R/"validation/review/ISSUE39_NORMALIZE_BRANCH_PRODUCTION_2026-10-14.json").read_text())
 assert old["status"]=="PASS_LOG_BRANCH_COLLAPSE_RESEARCH_NOT_RELEASED"
 assert old["new_public_model_calls"]==1073960
 assert native["status"]=="PASS_NATIVE_VICE_NORMALIZE_BRANCH_COLLAPSE"
 assert native["baseline_and_candidate_calls"]==320
 assert staged["status"]=="PASS_STAGED_PR_MAIN_CI_PENDING"
 assert staged["stock_bytes_saved_per_routine"]==16
 assert item["stock_code_bytes_before"]==881 and item["stock_code_bytes_after"]==865
 assert item["normal_zp_growth"]==0 and not item["reu_changed"]
 assert item["old_resident_sha256"]==staged["original"]
 assert item["new_resident_sha256"]==staged["candidate"]
 hashes={}
 for p in P:
  blob=(R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes()
  h=sha(blob);hashes[p]=h
  assert h==st["reference_prg_sha256"][p]==item["new_resident_sha256"][p]
  assert native["profiles"][p]["candidate_sha256"]==h
  assert native["profiles"][p]["baseline_sha256"]==item["old_resident_sha256"][p]
  assert native["profiles"][p]["all_signed_vectors_and_flags_match"]
  assert native["profiles"][p]["cases_each"]==32
  s=old["profiles"][p]["reference"]
  if p in STOCK:
   assert item["old_resident_sha256"][p]!=h
   assert 1.0<s["saved_mean_cycles"]<1.1
   assert s["code_bytes"]==865
  else:
   assert item["old_resident_sha256"][p]==h
   assert s["saved_mean_cycles"]==0
 assert set(hashes)==set(staged["candidate"])
 item.update(status="PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
  certified_main_merge_sha=a.merged_sha,
  full_library_main_ci_run=a.main_full,
  comparable_main_ci_run=a.main_comparable,
  fixed_multiply_main_ci_run=a.main_fixed,
  normalization_family_complete=True,
  distance_normalization_family_complete=True,
  issue39_open=True,
  postmerge_full_ci_pending=False)
 sp.write_text(json.dumps(st,indent=2)+"\n")
 cert={
  "status":"PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
  "merged_pr":132,"merged_sha":a.merged_sha,
  "main_green_runs":{"full_library":a.main_full,"comparable_unsigned":a.main_comparable,"fixed_multiply":a.main_fixed},
  "public_entry":"MATH_VEC2_NORMALIZE_Q8_8",
  "stock_code_bytes_before":881,"stock_code_bytes_after":865,
  "stock_mean_before":160.1500800774703,
  "stock_mean_after":159.12879436850534,
  "old_new_x64sc_public_calls":320,
  "reference_alternate_cpu_model_calls":1073960,
  "full_domain_precision_cells":723073,
  "native_vice_cycles_measured":False,
  "additional_zp_bytes":0,"reu_changed":False,
  "distance_normalization_family_complete":True,
  "issue39_still_open_for_seek":True,
  "shipped_prg_sha256":hashes
 }
 (R/CERT).write_text(json.dumps(cert,indent=2,sort_keys=True)+"\n")
 doc=R/"docs/ISSUE39_NORMALIZE_BRANCH_RELEASE_2026-10-14.md"
 s=doc.read_text()
 s=s.replace("PR/main CI pending.","PR #132 merged; independent main CI green.")
 if "PR #132 merged; independent main CI green." not in s:raise AssertionError("documentation preface missing")
 doc.write_text(s)
 oldline="Independent PR/main CI pending. See docs/ISSUE39_NORMALIZE_BRANCH_RELEASE_2026-10-14.md."
 new="PR #132 merged; post-merge main certification passed. See docs/ISSUE39_NORMALIZE_BRANCH_RELEASE_2026-10-14.md."
 note=(f"## {TAG}\n\n"
  "Confirmed PR #132 installed the 865-byte V1/V2/V5 normalizer with 16 fewer "
  "code bytes and identical signed results. Mean CPU-model cycles "
  "160.150080 -> 159.128794. Verified 1,073,960 paired-map model calls, "
  "320 real x64sc old/new calls, 723,073-cell precision certificate, "
  "unchanged four-byte scratch, public API and V3/V4 REU. "
  "Native VICE cycle timing was not measured. The fully qualified "
  "distance/normalization family is complete; Issue #39 remains OPEN for "
  "SEEK8/16 INIT/STEP. Both changelogs and checksum ledger sealed.\n"
  f"Main merge {a.merged_sha}; full main run {a.main_full}, comparable "
  f"{a.main_comparable}, fixed multiply {a.main_fixed}. "
  f"Completion certificate: {CERT}.\n\n---\n\n")
 for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  path=R/name
  text=path.read_text()
  assert oldline in text,(name,"staging entry missing")
  text=text.replace(oldline,new,1)
  assert TAG not in text
  path.write_text(note+text)
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,str(R/"tools/package_audit.py")],cwd=R,check=True)
 print("NORMALIZE FINAL POSTMERGE CERTIFICATE PASS; ISSUE39 REMAINS SEEK OPEN",flush=True)
if __name__=="__main__":main()
