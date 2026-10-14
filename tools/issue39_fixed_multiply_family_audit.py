#!/usr/bin/env python3
"""Issue #39 fixed multiply output family: stable public ABI and proof gate.

Verifies all four shifted outputs and matched old/new signed/unsigned SHR16
results, with resource growth, native VICE provenance and source relocation
audited separately. No private OptiSearch binary or source imported.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_UMUL16_SHR8","MATH_SMUL16_SHR8","MATH_UMUL32_SHR16","MATH_SMUL32_SHR16")
def read(path):return json.loads((ROOT/path).read_text())
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def check():
    status=read("RELEASE_STATUS.json")
    installed={p:sha(p+"/resident/math_"+p+"_game_math.prg") for p in P}
    assert installed==status["reference_prg_sha256"]
    assert set(OPS)==set(status["issue39_fixed_multiply_family_2026_10_14"]["routines"])
    assert status["issue39_fixed_multiply_family_2026_10_14"]["status"]=="PASS_COMPLETED_POSTMERGE_MAIN_GREEN"
    proof=read("validation/review/ISSUE39_FIXED_SHR16_RETURN_TAIL_PRODUCTION_2026-10-14.json")
    native=read("validation/review/ISSUE39_FIXED_SHR16_NATIVE_2026-10-14.json")
    small=read("validation/multiply_refresh/MUL16_SHR8_REGISTER_VALIDATION.json")
    bench=read("validation/multiply_refresh/MULTIPLY_REFRESH_BENCHMARK.json")
    assert proof["status"]=="PASS_SOURCE_PRODUCTION_NATIVE_PENDING"
    assert proof["after_prg_sha256"]==installed
    assert proof["mean_gain_each_call_cycles"]==2
    assert proof["source_same_operand"]["pairs_per_profile_per_op_per_map"]==4361
    assert proof["resource_growth_ZP"]==proof["resident_span_growth"]==proof["stack_growth"]==0
    assert native["status"]=="PASS_NATIVE_VICE_INSTALLED_FIXED_SHR16"
    assert native["original_and_candidate_public_calls"]==480
    assert native["native_cycle_timing_measured"] is False
    assert small["status"]==bench["status"]=="PASS"
    for p in P:
        assert len(proof["code_delta_four_bytes_per_profile"][p])==4
        for k in ("reference","alternate"):
            q=proof["source_same_operand"]["profiles"][p][k]
            for op in ("MATH_UMUL32_SHR16","MATH_SMUL32_SHR16"):
                row=q[op]
                assert row["cases"]==4361 and row["delta_histogram"]=={"-2":4361}
                assert abs(row["old_mean_cycles"]-row["new_mean_cycles"]-2)<1e-8
                assert row["public_abi"]=="PASS"
        for k in ("reference","alternate"):
            row=small["results"][p][k]
            assert row["cases"]==10196
            udelta=31 if p in (P[0],P[4]) else 27
            assert abs(row["umul16_shr8"]["mean_cycles"]-row["umul16"]["mean_cycles"]-udelta)<1e-8
            assert abs(row["smul16_shr8"]["mean_cycles"]-row["smul16"]["mean_cycles"]-31)<1e-8
        for op in ("MATH_UMUL32_SHR16","MATH_SMUL32_SHR16"):
            row=bench["profiles"][p][op]
            assert row["cases"]==4361 and row["errors"]==0
            certified=proof["source_same_operand"]["profiles"][p]["reference"][op]
            assert abs(row["mean_cycles"]-certified["new_mean_cycles"])<1e-8
            v=native["results"][p]["entries"][op]
            assert v["before_calls"]==v["after_calls"]==24
            assert v["bytewise_identical_native_records"]
    return {"status":"PASS_FIXED_MULTIPLY_FULL_PUBLIC_ABI",
            "profiles":list(P),"operations":list(OPS),
            "signed_unsigned_32_shr16_pairs_per_profile_per_map":4361,
            "signed_unsigned_16_shr8_pairs_per_profile_per_map":10196,
            "paired_32_shr16_saving_cycles_every_input":2,
            "native_VICE_old_new_calls":480,
            "native_cycle_timing_measured":False,
            "public_abi_unchanged":True,"new_ZP_growth":0,
            "resident_growth":0,"private_OptiSearch_source_published":False,
            "resident_sha256":installed}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--exercise",action="store_true")
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    if a.exercise:
        for k in ("reference","alternate"):
            subprocess.run([sys.executable,str(ROOT/"tools/assemble_sources.py"),
                    "--profile","all","--config-kind",k],cwd=ROOT,check=True)
            subprocess.run([sys.executable,str(ROOT/"tools/build_hybrid.py"),
                    "--config-kind",k],cwd=ROOT,check=True)
        subprocess.run([sys.executable,str(ROOT/"tools/validate_mul16_shr8_register.py")],cwd=ROOT,check=True)
        subprocess.run([sys.executable,str(ROOT/"tools/benchmark_multiply_refresh.py")],cwd=ROOT,check=True)
    report=check()
    if a.exercise:
        subprocess.run(["make","clean"],cwd=ROOT,check=True)
        subprocess.run([sys.executable,str(ROOT/"tools/package_audit.py")],cwd=ROOT,check=True)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 FIXED MULTIPLY FAMILY",report["status"])
if __name__=="__main__":main()
