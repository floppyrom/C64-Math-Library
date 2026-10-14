#!/usr/bin/env python3
"""Native x64sc DIST8 shipped-vs-source candidate equivalence.

Tests real installed reference-map C64 machine code for all five profiles,
including V3/V4 with real REU images. CPU model is the independent value
oracle. NOT a native cycle timer or a full release seal.
"""
import hashlib,json,os,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from native_issue39_trig_angle import native,original_prg,original_reu
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k",
          "v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_DIST8_FAST","MATH_DIST8_ACCURATE")
def sha(data):return hashlib.sha256(data).hexdigest()
def candidate(p):
    d=(R/"build_hybrid/reference" if p=="v5_hybrid_lowzp" else R/"build_source/reference")/p
    man=json.loads((d/"source_build_manifest.json").read_text())
    return (d/man["output_prg"]).read_bytes()
def main():
    exe=os.getenv("VICE_WRAPPER","x64sc")
    status=json.loads((R/"RELEASE_STATUS.json").read_text())
    out={"status":"PASS_NATIVE_DIST8_OLD_NEW_SOURCE_MATCH",
         "native_cycle_timing_measured":False,
         "source_build_not_published":True,"public_calls":0,
         "private_optisearch_source_published":False,"profiles":{}}
    with tempfile.TemporaryDirectory(prefix="issue39_dist8_native_") as folder:
        tmp=Path(folder)
        for pi,p in enumerate(PROFILES):
            original=original_prg(p);optimized=candidate(p);reu=original_reu(p)
            assert sha(original)==status["reference_prg_sha256"][p]
            if reu: assert sha(reu.read_bytes())==status["reference_reu_sha256"][p]
            out["profiles"][p]={}
            for oi,op in enumerate(OPS):
                before=native(p,op,original,reu,9300+pi*16+oi*2,tmp,exe)
                after=native(p,op,optimized,reu,9301+pi*16+oi*2,tmp,exe)
                assert before["native_output_sha256"]==after["native_output_sha256"],(p,op,"native outputs differ")
                assert before["same_hardware_stack_pointer"]==after["same_hardware_stack_pointer"],(p,op,"native stack differs")
                out["profiles"][p][op]={
                   "baseline_native_output_sha256":before["native_output_sha256"],
                   "optimized_native_output_sha256":after["native_output_sha256"],
                   "native_calls_each_image":before["cases"],
                   "output_flags_and_stack_equal":True,
                   "new_prg_sha256":sha(optimized)}
                out["public_calls"]+=before["cases"]+after["cases"]
                print("DIST8 NATIVE VICE",p,op,"baseline/candidate PASS",flush=True)
    assert out["public_calls"]==480
    dest=R/"validation/review/ISSUE39_DIST8_SOURCE_NATIVE_2026-10-14.json"
    dest.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("DIST8 NATIVE 480 BASELINE/CANDIDATE PUBLIC CALLS PASS",flush=True)
if __name__=="__main__":main()
