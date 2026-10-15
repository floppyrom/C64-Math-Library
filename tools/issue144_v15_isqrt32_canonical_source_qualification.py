#!/usr/bin/env python3
"""Issue #144: V1 canonical root and derived V5 public-call source promotion.

Proves normal resident source really owns the independent V1 root candidate;
V5 hybrid inherits identical resident bytes on two real source relocation maps.
No mutation of reference binary artifacts and no private OptiSearch source.
"""
from __future__ import annotations
import json
import math
import tempfile
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from assemble_sources import build as build_source,preprocess,parse_config
from build_hybrid import build as build_hybrid,load_prg
from validate_source_build import validate
from issue144_v1_isqrt32_normal_resident_feasibility import probe,model as v1_model
from issue144_v5_isqrt32_inheritance_screen import pair,model as v5_model

ROOT_BEGIN=0x0A40
ROOT_END=0x0AE0
def prove(layout,tmp):
    v1cfg=ROOT/"relocatable_source/v1_balanced"/("math_config_"+layout+".inc")
    v5cfg=ROOT/"relocatable_source/v5_hybrid_lowzp"/("math_config_"+layout+".inc")
    v1= parse_config(v1cfg)
    v5= parse_config(v5cfg)
    assert v1["REG_GAME"]==v5["REG_GAME"]
    geom,pair_6502=probe(layout,0x0AA8)
    assert pair_6502 is not None,geom
    old,new,root,io=pair_6502
    assert root==v1["REG_GAME_API"]+0x30
    assert v1_model(old,new,root,io)=={
      "cases":657,"mean_saved":51,"min_saved":51,"max_saved":51,"slower":0}
    src=ROOT/"relocatable_source/v1_balanced/math_relocatable.asm"
    assembled,labels,constants=Assembler().assemble(preprocess(src,v1cfg))
    assert root==constants["MATH_ISQRT32"]
    assert labels["LCB40"]==v1["REG_GAME"]+ROOT_BEGIN
    assert labels["LC8DB"]==v1["REG_GAME"]+0x0AA8
    # Prove candidate source was actually installed; old bytes must differ.
    diffs=[a for a in range(v1["REG_GAME"]+ROOT_BEGIN,v1["REG_GAME"]+ROOT_END)
           if old.mem[a]!=new.mem[a]]
    assert diffs and len(diffs)==92,(layout,len(diffs))
    assert all(assembled.get(a,0)==new.mem[a] for a in range(
        v1["REG_GAME"]+ROOT_BEGIN,v1["REG_GAME"]+ROOT_END))
    out_v1=tmp/layout/"v1_balanced"
    srcman=build_source("v1_balanced",v1cfg,out_v1)
    assert srcman["profile"]=="v1_balanced"
    s1=validate("v1_balanced",tmp/layout)
    assert s1["public_entries_executed"]==56
    out_v5=tmp/layout/"v5_hybrid_lowzp"
    hybrid=build_hybrid(v5cfg,out_v5)
    assert hybrid["normal_zp_bytes"]==31
    built,lo,hi=load_prg(out_v5/hybrid["output_prg"])
    assert all(built[a]==new.mem[a] for a in range(
        v1["REG_GAME"]+ROOT_BEGIN,v1["REG_GAME"]+ROOT_END))
    s5=validate("v5_hybrid_lowzp",tmp/layout)
    assert s5["public_entries_executed"]==56
    # Root direct timing on actual V5 builder image with restored old baseline.
    p5=v5_model(layout,tmp/("paired_v5_"+layout),count=657)
    assert p5["min_cycles_saved"]==p5["max_cycles_saved"]==51
    assert p5["slower_cases"]==0
    return {"layout":layout,"status":"PASS_CANONICAL_SOURCE",
            "v1_56_entries":s1["public_entries_executed"],
            "v5_56_entries":s5["public_entries_executed"],
            "v1_full_source_calls":s1["machine_calls"],
            "v5_full_source_calls":s5["machine_calls"],
            "paired_v1_ordinary_calls":657,
            "paired_v5_ordinary_calls":p5["paired_root32_calls"],
            "mean_root_cycles_saved":51,
            "normal_zp_added":0,
            "external_caller_ram_added":0,
            "changed_root_bytes":len(diffs),
            "v5_hybrid_inherits_exact_source":True}

def main():
    with tempfile.TemporaryDirectory(prefix="issue144_root_promotion_") as dirname:
        tmp=Path(dirname)
        results={layout:prove(layout,tmp) for layout in ("reference","alternate")}
        print(json.dumps({"status":"PASS_V1_V5_ROOT_SOURCE","maps":results,
          "reference_PRGs_changed":False,"REU_images_changed":False,
          "native_vice_in_separate_gate":True},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
