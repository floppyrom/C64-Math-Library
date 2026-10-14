#!/usr/bin/env python3
"""Finalize signed and unsigned 32-bit fixed SHR16 native VICE qualification.

This only marks the native old/new proof; production code was source-staged
and A/B CPU-proven independently. Postmerge main checks remain mandatory.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
STAMP="2026-10-14 ISSUE39 FIXED SHR16 TWO-CYCLE NATIVE VICE CONFIRMATION"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    stp=R/"RELEASE_STATUS.json"
    s=json.loads(stp.read_text())
    r=s["issue39_fixed_shr16_clc_2026_10_14"]
    assert r["status"] in ("PASS_STAGED_NATIVE_CI_PENDING","PASS_NATIVE_VICE_PR_MAIN_CI_PENDING")
    proof=json.loads((R/r["proof"]).read_text())
    native=json.loads((R/"validation/review/ISSUE39_FIXED_SHR16_NATIVE_2026-10-14.json").read_text())
    assert proof["status"]=="PASS_SOURCE_PRODUCTION_NATIVE_PENDING"
    assert proof["mean_gain_each_call_cycles"]==2
    assert proof["source_same_operand"]["pairs_per_profile_per_op_per_map"]==4361
    assert native["status"]=="PASS_NATIVE_VICE_INSTALLED_FIXED_SHR16"
    assert native["original_and_candidate_public_calls"]==480
    assert native["native_cycle_timing_measured"] is False
    assert native["source_main_baseline_sha"]=="bfc43c2f6643a893304799683f73396e0eba3096"
    for p in ("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp"):
        assert sha(R/p/"resident"/("math_"+p+"_game_math.prg"))==r["new_sha256"][p]
        assert native["results"][p]["changed_bytes"]==4
        for n in ("MATH_UMUL32_SHR16","MATH_SMUL32_SHR16"):
            v=native["results"][p]["entries"][n]
            assert v["before_calls"]==v["after_calls"]==24
            assert v["bytewise_identical_native_records"]
    r.update(status="PASS_NATIVE_VICE_PR_MAIN_CI_PENDING",
             native_VICE_calls=480,
             native_evidence="validation/review/ISSUE39_FIXED_SHR16_NATIVE_2026-10-14.json",
             native_cycle_timing_measured=False,
             public_NZV_flags_unchanged=True)
    s["issue39_fixed_shr16_clc_2026_10_14"]=r
    stp.write_text(json.dumps(s,indent=2)+"\n")
    doc=R/r["document"]
    old=doc.read_text()
    old=old.replace("**This is staged until actual native VICE and independent CI pass.**",
         "**Native x64sc old/new output equivalence PASSED (480 calls), independent PR and main CI remain mandatory.**")
    doc.write_text(old+"\nInstalled x64sc passed all 480 original/optimized "
      "signed and unsigned calls across the five profiles, including "
      "every public result byte, carry, X/Y preservation, flags and "
      "stack preservation. Native timing was not measured.\n")
    text=(STAMP+"\n- Installed x64sc old/new signed/unsigned "
          "UMUL32_SHR16/SMUL32_SHR16: 480 public calls across five "
          "profiles, complete bytewise identical output/flags/stack "
          "snapshots. The 2-cycle saving is from paired CPU model, not "
          "VICE timing. No new code memory or ZP. Independent PR/main "
          "CI pending.\n\n")
    for f in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        p=R/f
        if STAMP not in p.read_text():p.write_text(text+p.read_text())
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(R/"tools/package_audit.py")],cwd=R,check=True)
    print("ISSUE39 FIXED SHR16 NATIVE CERTIFIED; PR AND MAIN CI PENDING")
if __name__=="__main__":main()
