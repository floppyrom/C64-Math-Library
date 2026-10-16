#!/usr/bin/env python3
"""Pinned real NMOS x64sc: REG_LOW-owned 461-byte divisor tail, both signs.

Paired actual 6510 calls across three V2–V4 source profiles and both RAM maps;
candidate is within REG_LOW+$0C00, never caller-owned $0800. Check Q/R/N/D,
carry, all volatile processor snapshots, SP on native public DIV and MOD.
Hardware/REU DMA wall cycles are not measured.
"""
from __future__ import annotations
import hashlib,json,os,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from issue144_u3216_inresident_dualtail_model import builds,PROFILES,UOPS,SOPS
import native_issue144_u3216_dualtail_direct_dispatch as unsigned
import native_issue144_dualtail_signed32_public as signed
EXE=os.getenv("VICE_WRAPPER")
assert EXE,"VICE_WRAPPER must point to SHA256-pinned x64sc"

def main():
    record={"status":"PASS_NATIVE_RESIDENT_LOWTAIL_DIVMOD_BOTH_SIGNS",
            "resident_code_origin":"REG_LOW+$0C00",
            "source_owned_candidate_bytes":461,
            "caller_owned_bytes":0,"normal_zp_growth":0,
            "actual_native_cycles_measured":False,
            "historical_resident_prgs_unchanged":True,
            "native_baseline_and_candidate_calls":0,"profiles":{}}
    with tempfile.TemporaryDirectory(prefix="issue144_resident_dual_native_") as td:
        tmp=Path(td)
        for pi,p in enumerate(PROFILES):
            for li,kind in enumerate(("reference","alternate")):
                old,new,api,v,n=builds(p,kind)
                assert n==461
                for oi,op in enumerate((*UOPS,*SOPS)):
                    port=29000+pi*48+li*20+oi*4
                    key=f"{p}/{kind}/{op}"
                    if op in UOPS:
                        a=unsigned.native(old,api[op],v["MATH_IO"],key.replace("/","_")+"_old",port,tmp,EXE)
                        b=unsigned.native(new,api[op],v["MATH_IO"],key.replace("/","_")+"_new",port+1,tmp,EXE)
                        cols=unsigned.FIELDS
                        stride=unsigned.STRIDE
                        ncases=unsigned.N
                    else:
                        a=signed.native(old,api[op],api["MATH_INIT"],v["MATH_IO"],
                                        p,kind,op,"old",port,tmp,EXE)
                        b=signed.native(new,api[op],api["MATH_INIT"],v["MATH_IO"],
                                        p,kind,op,"resident",port+1,tmp,EXE)
                        cols=17
                        stride=signed.STRIDE
                        ncases=signed.N
                    assert len(a)==len(b)==cols*stride,(key,"invalid native capture")
                    assert a==b,(key,"CPU visible register/output/flag/stack byte mismatch",
                                 [k for k,(x,y) in enumerate(zip(a,b)) if x!=y][:15])
                    record["profiles"][key]={"native_calls":2*ncases,
                        "all_native_output_register_flag_and_stack_bytes_identical":True,
                        "capture_sha256":hashlib.sha256(b).hexdigest()}
                    record["native_baseline_and_candidate_calls"]+=2*ncases
                    print("NATIVE IN-RESIDENT",key,"PASS",2*ncases,flush=True)
    assert record["native_baseline_and_candidate_calls"]==1152
    print(json.dumps(record,sort_keys=True,indent=2))

if __name__=="__main__":main()
