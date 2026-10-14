#!/usr/bin/env python3
"""Issue 39: same-input SEEK16 Euclidean-init scaler candidate screen.

Research only; shipped PRGs, ABI and REU assets are not replaced. Benchmarks
ALL frame trajectories against Bresenham oracle using the existing public
profile corpus. Requires exact unchanged SEEK8 and STEP behavior.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_SEEK8_INIT","MATH_SEEK8_STEP","MATH_SEEK8_STEP_INT","MATH_SEEK8_STEP1",
     "MATH_SEEK16_INIT","MATH_SEEK16_STEP","MATH_SEEK16_STEP_INT","MATH_SEEK16_STEP1")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def py(script,*args):
    subprocess.run([sys.executable,str(ROOT/"tools"/script),*args],cwd=ROOT,check=True)
def main():
    oldp=ROOT/"validation/movement/SEEK_PROFILE_BENCHMARK.json"
    old=json.loads(oldp.read_text())
    release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    assert old["status"]=="PASS"
    original={}
    for p in PROFILES:
        path=ROOT/p/"resident"/("math_"+p+"_game_math.prg")
        original[p]=sha(path)
        assert original[p]==release["reference_prg_sha256"][p]
    py("generate_seek_sources.py")
    # Placement guard currently fails on the unchanged released main
    # (confirmed in independent main-checkout workflow #38590897224).
    # Keep this as research ONLY until the separate state/layout issue is fixed.
    for kind in ("reference","alternate"):
        py("generate_sources.py")
        py("assemble_sources.py","--profile","all","--config-kind",kind)
        py("build_hybrid.py","--config-kind",kind)
    py("generate_seek_sources.py","--check")
    py("test_mini6502_illegal.py")
    py("benchmark_seek_profiles.py")
    new=json.loads(oldp.read_text())
    assert new["status"]=="PASS"
    assert old["corpus"]==new["corpus"] and old["basis"]==new["basis"]
    assert old["prg_sha256"]==new["prg_sha256"]==original
    report={"status":"PASS_SEEK16_EUCLID_SCALE_LOOP_RESEARCH_ONLY",
        "public_abi_or_published_prgs_changed":False,
        "normal_zp_growth":0,"reu_images_changed":False,
        "init_scaler_source_change":"replace JMP/reentry BEQ with direct BNE back edge",
        "corpus":old["corpus"],
        "already_proven":"every frame checked against unchanged Bresenham reference by benchmark_seek_profiles.py",
        "native_vice_proof_pending":True,
        "placement_certification_blocked_by_released_main_regression":True,
        "baseline_placement_workflow_run":38590897224,"profiles":{}}
    total_gain=0
    for p in PROFILES:
        oldrows=old["profiles"][p]; newrows=new["profiles"][p];rr={}
        assert set(oldrows)==set(newrows)==set(OPS)
        for opname in OPS:
            before=oldrows[opname];after=newrows[opname]
            assert before["cases"]==after["cases"],(p,opname,"different benchmark corpus")
            if opname=="MATH_SEEK16_INIT":
                details={}
                for speedkind in ("major_axis_speed","euclidean_speed","integer_speed","one_pixel"):
                    x,y=before[speedkind],after[speedkind]
                    assert x["cases"]==y["cases"]
                    gain=x["mean_cycles"]-y["mean_cycles"]
                    if speedkind=="euclidean_speed":
                        assert gain>0,(p,speedkind,"no euclidean INIT benefit",gain)
                        assert y["max_cycles"]<=x["max_cycles"]
                        total_gain+=gain
                    else:assert abs(gain)<1e-10,(p,speedkind,gain)
                    details[speedkind]={"before":x["mean_cycles"],"candidate":y["mean_cycles"],"saved":gain,"calls":y["cases"]}
                rr[opname]={"before":before["mean_cycles"],"candidate":after["mean_cycles"],
                    "saved":before["mean_cycles"]-after["mean_cycles"],"by_speed_mode":details}
            else:
                assert before==after,(p,opname,"unrelated step or seek8 change",before,after)
                rr[opname]={"before":before["mean_cycles"],"candidate":after["mean_cycles"],"saved":0}
        report["profiles"][p]=rr
        assert sha(ROOT/p/"resident"/("math_"+p+"_game_math.prg"))==original[p],p
        print("SEEK16 SCALE",p,"euclidean mean saved",
              rr["MATH_SEEK16_INIT"]["by_speed_mode"]["euclidean_speed"]["saved"],flush=True)
    assert total_gain>0
    target=ROOT/"validation/review/ISSUE39_SEEK16_INIT_SCALE_LOOP_RESEARCH_2026-10-14.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 SEEK16 INIT SCALER RESEARCH PASS, SHIPPED PRGS UNMODIFIED",flush=True)
if __name__=="__main__":main()
