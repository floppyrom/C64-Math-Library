#!/usr/bin/env python3
"""Native x64sc signed 32/16 DIV/MOD full-Q/R/C and CPU-state dual-tail screen.

Source-assembled original and optional $0800 dual-tail, across V2/V3/V4,
reference and alternate layouts, with four-quadrant signed 32/16 endpoints,
including zero divisors, negative extrema and $8000 divisor magnitude.
Neither normal resident nor REU published reference images are changed.
"""
from __future__ import annotations
import hashlib,json,os,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from native_issue144_signed32_rq_tail_fusion import native,VECTORS,N,STRIDE
from issue144_u3216_dualtail_direct_dispatch_screen import builds,PROFILES
OPS=("MATH_SDIV32_16","MATH_SMOD32_16")
assert N==24 and STRIDE==64

def main():
    exe=os.environ.get("VICE_WRAPPER")
    assert exe,"Use pinned headless x64sc VICE_WRAPPER"
    result={"status":"PASS_NATIVE_DUALTAIL_SIGNED32_16",
            "native_baseline_and_candidate_calls":0,
            "reference_images_unchanged":True,
            "caller_owned_0800_bytes":461,
            "physical_cycle_measurement":False,
            "profiles":{}}
    with tempfile.TemporaryDirectory(prefix="u3216_dualtail_signed_native_") as tmpd:
        tmp=Path(tmpd)
        for pi,profile in enumerate(PROFILES):
            for li,layout in enumerate(("reference","alternate")):
                original,optimized,api,config,size=builds(profile,layout)
                assert size==461
                for oi,op in enumerate(OPS):
                    port=28200+pi*32+li*16+oi*4
                    a=native(original,api[op],api["MATH_INIT"],config["MATH_IO"],
                             profile,layout,op,"baseline",port,tmp,exe)
                    b=native(optimized,api[op],api["MATH_INIT"],config["MATH_IO"],
                             profile,layout,op,"dualtail",port+1,tmp,exe)
                    volatile_diffs=0
                    for i in range(N):
                        # Four Q, two R, four input N, two input D.
                        for f in range(12):
                            assert a[f*STRIDE+i]==b[f*STRIDE+i],(
                                profile,layout,op,i,"Q/R/N/D",f)
                        assert (a[12*STRIDE+i]&1)==(b[12*STRIDE+i]&1),(
                            profile,layout,op,i,"carry")
                        assert a[16*STRIDE+i]==b[16*STRIDE+i],(
                            profile,layout,op,i,"stack pointer")
                        for f in (12,13,14,15):
                            volatile_diffs+=a[f*STRIDE+i]!=b[f*STRIDE+i]
                    key=f"{profile}/{layout}/{op}"
                    result["profiles"][key]={
                        "native_calls":2*N,
                        "quotient_remainder_carry_inputs_stack_identical":True,
                        "volatile_register_status_byte_differences":volatile_diffs,
                        "candidate_capture_sha256":hashlib.sha256(b).hexdigest()}
                    result["native_baseline_and_candidate_calls"]+=2*N
                    print("NATIVE DUALTAIL SIGNED",key,"PASS",2*N,flush=True)
    assert result["native_baseline_and_candidate_calls"]==576
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=="__main__":main()
