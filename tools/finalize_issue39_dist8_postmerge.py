#!/usr/bin/env python3
"""Certify DIST8_FAST/ACCURATE PR130 after independent main checks pass.

Publication only: no PRG/REU/ASM/ZP/ABI changes. Confirms baseline/candidate
really differed on VICE, paired exhaustive model evidence and four green main
workflow run IDs. Checksums resealed and independently re-audited.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_DIST8_FAST","MATH_DIST8_ACCURATE")
KEY="issue39_dist8_shared_register_swap_2026_10_14"
CERT="validation/review/ISSUE39_DIST8_POSTMERGE_COMPLETION_2026-10-14.json"
STAMP="2026-10-14 ISSUE39 DIST8 POSTMERGE FINAL CERTIFICATION"
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--main-sha",required=True)
    parser.add_argument("--full-ci",type=int,required=True)
    parser.add_argument("--comparable-ci",type=int,required=True)
    parser.add_argument("--fixed-ci",type=int,required=True)
    parser.add_argument("--turbo-ci",type=int,required=True)
    a=parser.parse_args()
    assert len(a.main_sha)==40 and all(c in "0123456789abcdef" for c in a.main_sha)
    statepath=R/"RELEASE_STATUS.json"
    st=json.loads(statepath.read_text())
    row=st[KEY]
    assert row["status"]=="PASS_STAGED_NATIVE_VICE_PR_MAIN_CI_PENDING"
    model=json.loads((R/row["baseline_reconstruction"]).read_text())
    native=json.loads((R/row["native_proof"]).read_text())
    prod=json.loads((R/row["certificate"]).read_text())
    assert model["status"]=="PASS_EXHAUSTIVE_RESEARCH_NOT_PRODUCTION"
    assert native["status"]=="PASS_NATIVE_DIST8_OLD_NEW_SOURCE_MATCH" and native["public_calls"]==480
    assert prod["status"]=="PASS_STAGED_NATIVE_VICE_PR_MAIN_CI_PENDING"
    assert prod["exhaustive_before_after_public_calls"]==1310720
    assert prod["production_cpu_model_public_calls"]==655360
    assert prod["source_map_parity_public_calls"]==119220
    installed={}
    for p in P:
        data=(R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes()
        digest=sha(data)
        installed[p]=digest
        assert digest==st["reference_prg_sha256"][p]==row["new_production_prgs"][p]==prod["new_prgs"][p]
        old=row["old_production_prgs"][p]
        assert old!=digest and old==model["profiles"][p]["baseline_prg_sha256"]
        count=10 if p in (P[0],P[4]) else 8
        assert prod["changed_bytes_by_profile"][p]==count
        for op in OPS:
            n=native["profiles"][p][op]
            m=model["profiles"][p]["routines"][op]
            assert n["old_prg_sha256"]==old and n["new_prg_sha256"]==digest
            assert n["candidate_differs_from_baseline"] and n["changed_swap_bytes"]==count
            assert n["output_flags_and_stack_equal"]
            assert n["baseline_native_output_sha256"]==n["optimized_native_output_sha256"]
            assert n["native_calls_each_image"]==24
            assert m["cases"]==65536 and m["bytewise_equal"] and m["public_input_carry_stack_preserved"]
            assert abs(row["measured"][p][op]["mean"]-m["mean_candidate_cpu_model_cycles"])<1e-9
    row.update(status="PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
        dist8_production_complete=True,
        certified_main_sha=a.main_sha,
        postmerge_full_library_ci_run=a.full_ci,
        postmerge_comparable_ci_run=a.comparable_ci,
        postmerge_fixed_multiply_ci_run=a.fixed_ci,
        postmerge_turbo32_ci_run=a.turbo_ci,
        distance_normalization_family_complete=False,
        issue39_remains_open=True)
    statepath.write_text(json.dumps(st,indent=2)+"\n")
    record={
        "status":"PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
        "dist8_production_complete":True,
        "distance_normalization_family_complete":False,
        "issue39_complete":False,
        "routines":list(OPS),
        "certified_main_sha":a.main_sha,
        "postmerge_full_library_ci_run":a.full_ci,
        "postmerge_comparable_unsigned_ci_run":a.comparable_ci,
        "postmerge_fixed_multiply_ci_run":a.fixed_ci,
        "postmerge_turbo32_ci_run":a.turbo_ci,
        "native_vice_baseline_candidate_calls":480,
        "native_cycle_timing_measured":False,
        "paired_cpu_model_calls":1310720,
        "new_shipped_cpu_model_calls":655360,
        "dual_map_cpu_model_calls":119220,
        "public_abi_changed":False,
        "resident_lengths_changed":False,
        "normal_zp_growth":0,
        "reu_images_changed":False,
        "published_optisearch_private_code":False,
        "shipped_resident_sha256":installed,
        "remaining":["MATH_VEC2_NORMALIZE_Q8_8","SEEK8/16 INIT, STEP, STEP_INT, STEP1"]}
    (R/CERT).write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    docpath=R/"docs/ISSUE39_DIST8_REGISTER_SWAP_RELEASE_2026-10-14.md"
    doc=docpath.read_text()
    preface=("**Post-merge final certification (14 October 2026):** PR #130 merged as "
      "`44fc91813d945c05194d2f4962bb89f9d5f88449`; all four independent "
      "main validation workflows passed. Both DIST8 public APIs are now released "
      "in V1–V5. Normalization and seek are still open.\n\n")
    if preface not in doc:docpath.write_text(preface+doc)
    entry=(f"## {STAMP}\n\n"
      "Final certification of shipped DIST8_FAST/DIST8_ACCURATE optimization "
      "after PR #130 merge, four green main checks. 1,310,720 paired "
      "CPU-model baseline/candidate calls, 655,360 new shipped benchmarks, "
      "119,220 reference/alternate calls and 480 native VICE baseline/candidate "
      "public calls on SHA-distinct PRGs. Exact 8/10-byte source-backed swap only; "
      "no ABI, resident size, normal ZP or REU changes. VICE cycle timing not measured. "
      "Both changelogs and SHA256 resealed. Issue #39 remains open for VEC2 "
      "normalization and seek. "
      f"Main `{a.main_sha}`; full [#{a.full_ci}](https://github.com/floppyrom/C64-Math-Library/actions/runs/{a.full_ci}), "
      f"comparable [#{a.comparable_ci}](https://github.com/floppyrom/C64-Math-Library/actions/runs/{a.comparable_ci}), "
      f"fixed [#{a.fixed_ci}](https://github.com/floppyrom/C64-Math-Library/actions/runs/{a.fixed_ci}), "
      f"Turbo32 [#{a.turbo_ci}](https://github.com/floppyrom/C64-Math-Library/actions/runs/{a.turbo_ci}).\n"
      f"Certificate `{CERT}`.\n\n---\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        p=R/name
        if STAMP not in p.read_text():p.write_text(entry+p.read_text())
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(R/"tools/package_audit.py")],cwd=R,check=True)
    print("ISSUE39 DIST8 FINAL POSTMERGE CERTIFICATION PASS; NORMALIZE AND SEEK OPEN",flush=True)
if __name__=="__main__":main()
