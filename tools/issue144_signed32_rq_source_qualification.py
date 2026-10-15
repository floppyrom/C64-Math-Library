#!/usr/bin/env python3
"""Issue144 B: prove canonical signed 32/16 R-first tail across four source-built profiles.

Only source-built binaries under TemporaryDirectory; published PRGs/REUs
remain historical. Public interface, normal map, and 56-entry mixed math ABI.
"""
from __future__ import annotations
import json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from assemble_sources import build as build_source
from build_hybrid import build as build_hybrid
from validate_source_build import validate
from issue144_signed32_rq_tail_fusion_screen import PROFILES,pair

def main():
    result={"status":"PASS_SIGNED32_RQ_CANONICAL_SOURCE","rows":[],
            "normal_zp_added":0,"caller_ram_added":0,"published_images_modified":False}
    with tempfile.TemporaryDirectory(prefix="issue144_b_signed32_source_") as dirname:
        top=Path(dirname)
        for layout in ("reference","alternate"):
            out=top/layout
            for p in (*PROFILES,"v5_hybrid_lowzp"):
                cfg=ROOT/"relocatable_source"/p/("math_config_"+layout+".inc")
                if p=="v5_hybrid_lowzp":
                    man=build_hybrid(cfg,out/p)
                    assert man["normal_zp_bytes"]==31
                else:
                    man=build_source(p,cfg,out/p)
                    a,b,api,values=pair(p,layout)
                    assert api["D32F_R_THEN_Q"]>=values["REG_TABLE"]+0x3200
                check=validate(p,out)
                assert check["public_entries_executed"]==56,(p,layout,check)
                result["rows"].append({
                  "profile":p,"layout":layout,
                  "all_56_public_entries_pass":True,
                  "source_model_machine_calls":check["machine_calls"],
                  "signed_native_vice_external_gate":True,
                  "built_from_current_canonical_source":True})
                print("SIGNED32 RQ SOURCE",p,layout,"PASS",
                      check["machine_calls"],flush=True)
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=="__main__":main()
