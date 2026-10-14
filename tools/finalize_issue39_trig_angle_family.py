#!/usr/bin/env python3
"""Finalize trig/angle four-routine Issue39 family against verified main green.

This is a publication-only step. Published resident PRGs, REU images, table
selection, ZP/stack allocation, stable ABI and OptiSearch source stay unchanged.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_SIN8","MATH_COS8","MATH_SINCOS8","MATH_ATAN2_8")
DOC="docs/ISSUE39_TRIG_ANGLE_FAMILY_REVIEW_2026-10-14.md"
SOURCE="validation/review/ISSUE39_TRIG_ANGLE_FAMILY_SOURCE_AUDIT_2026-10-14.json"
NATIVE="validation/review/ISSUE39_TRIG_ANGLE_NATIVE_2026-10-14.json"
CERT="validation/review/ISSUE39_TRIG_ANGLE_FAMILY_COMPLETION_2026-10-14.json"
STAMP="2026-10-14 ISSUE39 TRIG ANGLE FAMILY FINAL CERTIFICATION"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--main-sha",required=True)
    ap.add_argument("--full-ci",type=int,required=True)
    ap.add_argument("--comparable-ci",type=int,required=True)
    ap.add_argument("--native-ci",type=int,required=True)
    a=ap.parse_args()
    assert len(a.main_sha)==40 and all(x in "0123456789abcdef" for x in a.main_sha)
    status_path=R/"RELEASE_STATUS.json"
    st=json.loads(status_path.read_text())
    row=st["issue39_trig_angle_family_2026_10_14"]
    assert row["status"] in ("PASS_NATIVE_VICE_PR_MAIN_CI_PENDING",
                             "PASS_COMPLETED_POSTMERGE_MAIN_GREEN")
    assert row["native_vice_calls"]==480
    originals={p:sha(R/p/"resident"/("math_"+p+"_game_math.prg")) for p in P}
    assert originals==st["reference_prg_sha256"]==row["baseline_prg_sha256"]
    model=json.loads((R/SOURCE).read_text())
    native=json.loads((R/NATIVE).read_text())
    atan=json.loads((R/"validation/ATAN2_DISPATCH_VALIDATION.json").read_text())
    assert model["status"]=="PASS_PUBLIC_TRIG_ANGLE_EXHAUSTIVE"
    assert model["new_public_trig_calls"]==7680
    assert atan["status"]=="PASS" and atan["machine_calls"]==655360
    assert model["already_qualified_public_atan2_calls"]==655360
    assert native["status"]=="PASS_NATIVE_VICE_TRIG_PUBLIC" and native["public_calls"]==480
    assert not native["native_cycle_timing_measured"]
    assert model["source_maps"]==["reference","alternate"]
    for p in P:
        maps=model["profiles"][p]
        for kind in ("reference","alternate"):
            v=maps[kind]
            for op in OPS[:3]:
                assert v[op]["cases"]==256 and v[op]["carry_clear"] and v[op]["inputs_preserved"] and v[op]["stack_stable"]
            assert v["paired_combined_vs_two_separate"]["output_identity_all_256_phases"]
        for op in OPS[:3]:
            assert maps["reference"][op]["output_sha256"]==maps["alternate"][op]["output_sha256"]
            assert maps["reference"][op]["cycle_vector_sha256"]==maps["alternate"][op]["cycle_vector_sha256"]
        pair=maps["reference"]["paired_combined_vs_two_separate"]
        assert pair["mean_saving_public_entry_cycles"]==(13 if p==P[0] else 15)
        assert maps["reference"]["MATH_SINCOS8"]["mean_cycles"]==(39 if p==P[0] else 31)
        for op in OPS:
            val=native["profiles"][p][op]
            assert val["cases"]==24 and val["matched_model_public_results"] and val["carry_clear"]
            assert atan["results"][p]["reference"]["cases"]==65536
    row.update(status="PASS_COMPLETED_POSTMERGE_MAIN_GREEN",family_complete=True,
         certified_main_sha=a.main_sha,postmerge_full_library_ci_run=a.full_ci,
         postmerge_comparable_ci_run=a.comparable_ci,premerge_native_vice_run=a.native_ci,
         issue39_remains_open=True)
    st["issue39_trig_angle_family_2026_10_14"]=row
    status_path.write_text(json.dumps(st,indent=2)+"\n")
    proof={"status":"PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
        "family_complete":True,"issue39_complete":False,"routines":list(OPS),
        "model_new_sincos_sin_cos_calls":7680,"previous_exhaustive_atan2_calls":655360,
        "native_vice_trig_public_calls":480,"native_cycle_timing_measured":False,
        "profiles":list(P),"both_source_maps":True,
        "v1_sincos_mean_cycles":39,"other_sincos_mean_cycles":31,
        "v1_sincos_saving_vs_separate":13,"other_sincos_saving_vs_separate":15,
        "production_resident_modified":False,"normal_zp_growth":0,
        "private_optisearch_source_published":False,
        "published_resident_sha256":originals,
        "source_evidence":SOURCE,"native_evidence":NATIVE,
        "main_sha":a.main_sha,"main_full_library_run":a.full_ci,
        "main_comparable_unsigned_run":a.comparable_ci,
        "premerge_native_vice_run":a.native_ci,
        "other_open_families":["Distance / normalization","Seek movement"]}
    path=R/CERT;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n")
    doc=R/DOC
    text=("**Final certification (14 October 2026):** SIN8, COS8, "
       "SINCOS8 and ATAN2_8 all passed exhaustive public CPU-model "
       "checks, 480 native VICE calls and post-merge main qualification. "
       "No public ABI/resource-compatible new speed gain was demonstrated; "
       "the existing V1 memory-saving and V2-V5 speed-first "
       "implementations are retained. Issue #39 stays open.\n\n")
    d=doc.read_text()
    if text not in d:doc.write_text(d.replace("## Identical-input public-entry results",text+"## Identical-input public-entry results") if "## Identical-input public-entry results" in d else text+d)
    log=(f"## {STAMP}\n\n"
      f"**Complete:** SIN8/COS8/SINCOS8 plus ATAN2_8, all five profiles, "
      f"both source relocations. 7,680 CPU-model SIN/COS/SINCOS public calls; "
      f"655,360 exhaustive signed ATAN2 public calls; 480 real x64sc "
      f"native calls (including V3/V4 REU image). V1 SINCOS 39 model cycles "
      f"vs combined two-call saving 13; V2–V5 SINCOS 31 and saving 15. "
      f"All combined outputs equal separate calls. No production PRG, ABI, "
      f"ZP, table or reserved stack change, no private OptiSearch source. "
      f"Native cycles were **not** measured.\n\n"
      f"Certified main `{a.main_sha}`; full library [#{a.full_ci}](https://github.com/floppyrom/C64-Math-Library/actions/runs/{a.full_ci}), "
      f"comparable [#{a.comparable_ci}](https://github.com/floppyrom/C64-Math-Library/actions/runs/{a.comparable_ci}), "
      f"native [#{a.native_ci}](https://github.com/floppyrom/C64-Math-Library/actions/runs/{a.native_ci}). "
      f"See `{CERT}`. Issue #39 OPEN for distance and seek.\n\n---\n\n")
    for filename in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        f=R/filename
        if STAMP not in f.read_text():f.write_text(log+f.read_text())
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(R/"tools/package_audit.py")],cwd=R,check=True)
    print("ISSUE39 TRIG ANGLE FOUR-ROUTINE FAMILY COMPLETE; ISSUE39 OPEN",flush=True)
if __name__=="__main__":main()
