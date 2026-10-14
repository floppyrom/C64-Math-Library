#!/usr/bin/env python3
"""Certify Issue39 four public fixed multiply outputs after green main release.

Guard against any resident, ABI, ready-pointer, performance or proof drift.
The 16-bit register-return adapters remain unchanged. This script records the
post-merge result only, and never changes compiled arithmetic source.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_UMUL16_SHR8","MATH_SMUL16_SHR8","MATH_UMUL32_SHR16","MATH_SMUL32_SHR16")
STAMP="2026-10-14 ISSUE39 FIXED MULTIPLY OUTPUTS FINAL PUBLICATION"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--main-sha",required=True)
    ap.add_argument("--full-ci",type=int,required=True)
    ap.add_argument("--comparable-ci",type=int,required=True)
    ap.add_argument("--turbo-ci",type=int,required=True)
    ap.add_argument("--native-ci",type=int,required=True)
    a=ap.parse_args()
    assert len(a.main_sha)==40 and all(c in "0123456789abcdef" for c in a.main_sha)
    path=R/"RELEASE_STATUS.json"
    st=json.loads(path.read_text())
    row=st["issue39_fixed_shr16_clc_2026_10_14"]
    assert row["status"] in ("PASS_NATIVE_VICE_PR_MAIN_CI_PENDING","PASS_COMPLETED_POSTMERGE_MAIN_GREEN")
    actual={p:sha(R/p/"resident"/("math_"+p+"_game_math.prg")) for p in P}
    assert actual==st["reference_prg_sha256"]==row["new_sha256"]
    proof=json.loads((R/row["proof"]).read_text())
    native=json.loads((R/row["native_evidence"]).read_text())
    reg16=json.loads((R/"validation/multiply_refresh/MUL16_SHR8_REGISTER_VALIDATION.json").read_text())
    assert proof["mean_gain_each_call_cycles"]==2
    assert proof["source_same_operand"]["pairs_per_profile_per_op_per_map"]==4361
    assert native["status"]=="PASS_NATIVE_VICE_INSTALLED_FIXED_SHR16"
    assert native["original_and_candidate_public_calls"]==480
    assert reg16["status"]=="PASS"
    assert all(reg16["results"][p]["reference"]["cases"]==10196 for p in P)
    assert row["resident_growth"]==row["normal_ZP_growth"]==row["abi_growth"]==0
    row.update(status="PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
        complete=True,postmerge_main_sha=a.main_sha,postmerge_full_ci_run=a.full_ci,
        postmerge_comparable_ci_run=a.comparable_ci,postmerge_turbo_ci_run=a.turbo_ci,
        premerge_native_ci_run=a.native_ci)
    st["issue39_fixed_shr16_clc_2026_10_14"]=row
    st["issue39_fixed_multiply_family_2026_10_14"]={
       "status":"PASS_COMPLETED_POSTMERGE_MAIN_GREEN","family_complete":True,
       "issue39_remains_open":True,"routines":list(OPS),
       "two_32bit_entries_gain_cycles_each_input":2,
       "signed_unsigned_32bit_matched_pairs_per_profile_per_map":4361,
       "all_5_profiles_and_both_source_maps":True,
       "signed_unsigned_16bit_register_return_pairs_per_profile_per_map":10196,
       "native_original_and_optimized_calls":480,
       "native_cycle_timing_measured":False,
       "normal_zp_growth":0,"resident_span_growth":0,"reserved_stack_growth":0,
       "public_abi_changed":False,"private_optisearch_source_published":False,
       "compiled_profile_sha256":actual,
       "postmerge_main_sha":a.main_sha,
       "full_library_main_run":a.full_ci,"comparable_unsigned_main_run":a.comparable_ci,
       "turbo32_main_run":a.turbo_ci,"native_old_new_run":a.native_ci,
       "source_proof":row["proof"],"native_proof":row["native_evidence"],
       "separate_remaining_steps":"REU Turbo/QS, trig, distance, seek"}
    path.write_text(json.dumps(st,indent=2)+"\n")
    cert={
       "status":"PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
       "issue39_complete":False,"fixed_multiply_family_complete":True,
       "operations":list(OPS),"baseline_profiles":actual,
       "source_paired_calls_per_32bit_entry_per_profile_per_map":4361,
       "model_saving_per_32bit_call_cycles":2,
       "native_old_new_calls":480,"native_cycle_timing_measured":False,
       "16bit_register_return_adapters_unchanged":True,
       "resource_and_public_abi_growth":0,
       "main_sha":a.main_sha,
       "checks":{"main_full":a.full_ci,"main_comparable":a.comparable_ci,
                 "main_turbo32":a.turbo_ci,"native":a.native_ci},
       "separate_remaining_steps":"REU Turbo/QS, trig, distance, seek",
       "private_optisearch_source_published":False}
    certfile=R/"validation/review/ISSUE39_FIXED_MULTIPLY_FAMILY_COMPLETION_2026-10-14.json"
    certfile.write_text(json.dumps(cert,indent=2,sort_keys=True)+"\n")
    doc=R/row["document"]
    note=("**Final certification (14 October 2026):** The four standard fixed "
      "multiply outputs are complete after native signed/unsigned public "
      "equivalence and independent full-library, comparable and Turbo32 "
      "checks on post-merge main. Both 32-bit SHR16 tails improve two "
      "CPU-model cycles per call; both 16-bit SHR8 register-return adapters "
      "remain qualified and unchanged. Issue #39 remains open.\n\n")
    old=doc.read_text()
    if note not in old:doc.write_text(note+old)
    detail=(STAMP+"\n- UMUL16_SHR8 and SMUL16_SHR8 unchanged, existing "
       "10,196-case all-profile reference/alternate register-return qualification. "
       "UMUL32_SHR16 and SMUL32_SHR16 source-integrated -2 CPU-model cycles on "
       "all 4,361 matched calls/entry/profile/map, no code span/ZP/stack growth. "
       "480 native original/new installed public calls identical; native "
       "cycle timing NOT measured.\n- Postmerge main "+a.main_sha+
       ": full "+str(a.full_ci)+", comparable "+str(a.comparable_ci)+
       ", Turbo32 "+str(a.turbo_ci)+
       ". REU Turbo/QS and other Issue39 families remain OPEN.\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        file=R/name
        if STAMP not in file.read_text():file.write_text(detail+file.read_text())
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(R/"tools/package_audit.py")],cwd=R,check=True)
    print("FIXED MULTIPLY FAMILY COMPLETE; ISSUE39 OPEN")
if __name__=="__main__":main()
