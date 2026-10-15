#!/usr/bin/env python3
"""Issue144 V1 direct highword root normal-resident native VICE paired correctness."""
from __future__ import annotations
import json,hashlib,os,tempfile
from pathlib import Path
from issue144_isqrt32_v1_normal_resident_screen import build,PROFILE
from native_issue144_isqrt32_normal_resident import native,E
def main():
    vice=os.environ.get("VICE_WRAPPER")
    assert vice,"requires VICE_WRAPPER=x64sc"
    report={"status":"PASS_V1_NATIVE_RESEARCH","profile":PROFILE,"results":{},
            "native_calls":0,"v5_hybrid_qualified":False,
            "reference_images_changed":False,"physical_cycles_measured":False}
    with tempfile.TemporaryDirectory(prefix="isqrt32_v1_inres_native_") as d:
        tmp=Path(d)
        for i,kind in enumerate(("reference","alternate")):
            old,new,api,io,diff,module_len,source=build(kind)
            a=native(PROFILE,kind,old,24610+i*4,tmp,vice) if False else native(PROFILE,kind,old,api,io,24610+i*4,tmp,vice)
            b=native(PROFILE,kind,new,api,io,24611+i*4,tmp,vice)
            assert a==b,(kind,"native root/status output changed",[(i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y][:8])
            report["results"][kind]={"status":"PASS_NATIVE_EQUIVALENT",
                "calls":len(E)*2,"source_sha256":hashlib.sha256(source.encode()).hexdigest(),
                "capture_sha256":hashlib.sha256(a).hexdigest(),
                "same_capture":True,"modified_normal_resident_bytes":diff}
            report["native_calls"]+=len(E)*2
            print("V1 NORMAL ROOT VICE",kind,"PASS",len(E)*2,"calls",flush=True)
    assert report["native_calls"]==len(E)*4==96
    print(json.dumps(report,indent=2,sort_keys=True))
if __name__=="__main__":main()
