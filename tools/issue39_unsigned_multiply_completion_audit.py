#!/usr/bin/env python3
"""Issue39 unsigned multiply family: release-evidence and same-input gate.

Read-only with respect to tracked files. Never imports or publishes OptiSearch.
The --exercise flag rebuilds relocation maps and reruns public CPU-model
qualifications. Hardware native checks are separately pinned release evidence.
"""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k",
          "v4_reu_16m","v5_hybrid_lowzp")
P5=(PROFILES[0],PROFILES[4]); P234=PROFILES[1:4]
def read(p):return json.loads((ROOT/p).read_text())
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def equal(x,y,name):
    if x!=y:raise AssertionError((name,x,y))
def near(x,y,name):
    if abs(x-y)>0.00000001:raise AssertionError((name,x,y))
def run(tool,*args):
    subprocess.run([sys.executable,str(ROOT/"tools"/(tool+".py")),*args],
                   check=True,cwd=ROOT)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--exercise",action="store_true")
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    release=read("RELEASE_STATUS.json")
    actual={p:sha(p+"/resident/math_"+p+"_game_math.prg") for p in PROFILES}
    equal(actual,release["reference_prg_sha256"],"release checksum identity")
    # Exhaustive 8-bit public implementation evidence, not 16-bit sampling.
    u8=read("validation/review/ISSUE39_V1V5_UMUL8_DIRECTOUT_PRODUCTION_2026-10-13.json")
    equal(u8["status"],"MERGED_MAIN_ALL_POSTMERGE_CI_PASS","V1/V5 UMUL8")
    equal(u8["exhaustive_pairs_per_profile"],65536,"UMUL8 exhaustive")
    equal(u8["paired_savings_each"],6,"UMUL8 saving per input")
    equal(u8["extra_normal_zp"],0,"UMUL8 ZP")
    equal(u8["resident_size_growth"],0,"UMUL8 resident growth")
    # V2 public adapter has its own public source-generation and native proof.
    u8v2=read("validation/review/ISSUE39_V2_UMUL8_DIRECT_OUTPUT_RELEASE.json")
    equal(u8v2["exhaustive"]["cases"],65536,"V2 UMUL8 exhaustive")
    near(u8v2["exhaustive"]["mean_cycles"],72.494140625,"V2 UMUL8 mean")
    # Matched corpus and two relocation maps; do not compare unrelated
    # published V1/V2 means sourced from different distributions.
    u16=read("validation/multiply_refresh/UMUL16_DIRECTOUT_VALIDATION.json")
    u24=read("validation/multiply_refresh/UMUL24_DIRECTOUT_VALIDATION.json")
    for profile in PROFILES:
        x=u16["results"][profile]
        y=u24["results"][profile]
        equal(x["reference"],x["alternate"],("UMUL16 relocation",profile))
        equal(y["reference"],y["alternate"],("UMUL24 relocation",profile))
        equal(x["reference"]["cases"],10169,("UMUL16 corpus",profile))
        equal(y["reference"]["cases"],10324,("UMUL24 corpus",profile))
        near(x["reference"]["mean_cycles"],273.98003736847284 if profile in P5 else 216.9800373684728,
             ("UMUL16 mean",profile))
        near(y["reference"]["mean_cycles"],465.0423285548237 if profile in P5 else 417.78322355676096,
             ("UMUL24 mean",profile))
    # Repaired V1/V5 carry-flow: one cycle EVERY matched call.
    u24prod=read("validation/review/ISSUE39_V1V5_UMUL24_RARECARRY_RELEASE_2026-10-14.json")
    equal(u24prod["cycle_deltas"],{"-1":10324},"V1/V5 UMUL24 paired delta")
    equal(u24prod["zero_page_growth"],0,"UMUL24 zero-page growth")
    equal(u24prod["resident_growth"],0,"UMUL24 resident growth")
    for p in PROFILES:
        equal(u24prod["new_sha256"][p],actual[p],("UMUL24 installed",p))
    u24native=read("validation/review/ISSUE39_V1V5_UMUL24_RARECARRY_NATIVE_2026-10-14.json")
    equal(u24native["native_calls"],384,"UMUL24 native x64sc")
    equal(u24native["native_cycle_timing_measured"],False,"native timing provenance")
    # READY is a distinct, stateful ABI. Invalidating pointer prebinds can
    # never be justified by the 22-cycle paired clean-state observation.
    ready=read("validation/review/ISSUE39_UMUL32_READY_PAIRED_AUDIT.json")
    equal(ready["input_pairs"],2409,"UMUL32 shared corpus")
    equal(ready["full_corpus"],True,"UMUL32 corpus completeness")
    for row in ready["profiles"]:
        p=row["profile"];equal(row["paired_cases"],2409,p)
        near(row["ordinary_mean_cycles"],712.2353673723537 if p in P5 else 690.2353673723537,p)
        near(row["ready_mean_cycles"],690.2353673723537,p)
        near(row["mean_ready_saving_cycles"],22 if p in P5 else 0,p)
        equal(row["product_carry_and_input_preservation"],"PASS",p)
    lifetime=read("validation/review/ISSUE39_UMUL32_READY_POINTER_LIFETIME.json")
    for p in P5:
        row=lifetime["result_by_profile"][p]
        equal(row["normal_public_valid_calls"],1456,p)
        equal(row["unqualified_ready_invalid_calls"],312,p)
        equal(row["affected_pointer_high_bytes"],["0x09","0x0b","0x0d"],p)
    # Retained PRIVATE OptiSearch claims are evidence, not a license to
    # transplant executable ZP/stack code into the public 56-entry ABI.
    os=read("validation/review/ISSUE39_UMUL16_UMUL24_OPTISEARCH_RESOURCE_AUDIT.json")
    equal(os["private_source_published"],False,"private source policy")
    equal(os["umul16"]["private_candidate_correct"],10169,"private UMUL16 correctness")
    equal(os["umul16"]["private_candidate_executable_zp"],95,"private UMUL16 ZP")
    equal(os["umul16"]["private_candidate_executable_stack_page"],81,"private UMUL16 stack")
    equal(os["umul16"]["private_candidate_public_abi_qualified"],False,"private ABI")
    equal(os["umul24"]["public_record_zp"],24,"public UMUL24 record ZP")
    equal(os["umul24"]["private_retained_zp"],27,"private UMUL24 ZP")
    equal(os["umul24"]["paired_comparison_qualified"],False,"UMUL24 model comparability")
    status=release["issue39_umul24_v1v5_rare_carry_clc_2026_10_14"]
    equal(status["gain_cycles_every_case"],1,"production gain metadata")
    equal(status["native_vice_calls"],384,"native production evidence")
    if a.exercise:
        for kind in ("reference","alternate"):
            run("assemble_sources","--profile","all","--config-kind",kind)
            run("build_hybrid","--config-kind",kind)
        run("validate_umul16_directout")
        run("validate_umul24_directout")
        run("issue39_umul32_ready_same_input","--output",str(Path(tempfile.gettempdir())/"issue39_unsigned_multiply_ready.json"))
        run("issue39_umul32_ready_lifetime_audit","--output",str(Path(tempfile.gettempdir())/"issue39_unsigned_multiply_lifetime.json"))
        # Build output is strictly transient; leave a clean package.
        subprocess.run(["make","clean"],cwd=ROOT,check=True)
        run("package_audit")
    report={"status":"PASS_PUBLIC_PROFILE_AUDIT" if not a.exercise else "PASS_EXERCISED_PUBLIC_PROFILE_AUDIT",
            "profiles":list(PROFILES),"family":["UMUL8","UMUL16","UMUL24","UMUL32","UMUL32_READY"],
            "normal_public_api_unchanged":True,"private_optisearch_source_included":False,
            "umul8_exhaustive_pairs_per_v1v5":65536,"umul16_pairs_per_profile_map":10169,
            "umul24_pairs_per_profile_map":10324,"umul32_ready_pairs_per_profile":2409,
            "ready_lifetime_normal_calls_per_v1v5":1456,
            "ready_lifetime_unsafe_ready_calls_per_v1v5":312,
            "native_umul24_public_calls":384,
            "native_cycle_timing_measured":False,
            "rejected_transplants":["UMUL16 private near-page executable ZP/stack and register ABI",
                                    "UMUL24 private carry record without matched public gain",
                                    "UMUL32 READY unconditional pointer-fix removal"],
            "production_prgs_sha256":actual,
            "remaining_separate_campaign":"REU Turbo16/Turbo32/QS16 multiplier modes"}
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 UNSIGNED MULTIPLY FAMILY AUDIT",report["status"],flush=True)
if __name__=="__main__":main()
