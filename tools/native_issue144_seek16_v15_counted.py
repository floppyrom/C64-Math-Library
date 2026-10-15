#!/usr/bin/env python3
"""Real x64sc source-built V1/V5 SEEK16 counted-loop native parity.

The baseline is the original public V1 SEEK assembly, independently
reassembled in a disposable source-built image. No release PRG changes.
CPU-model equality is independently checked against every native output.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from assemble_sources import build,parse_config
from build_hybrid import build as hybrid_build
from issue144_seek16_v15_counted_source_proof import synth_old
from generate_seek_sources import LAYOUTS,SCRATCH
import seek_kernel as K
from native_issue39_seek16_scale import native,check_model,sha,COUNT

PROFILES=("v1_balanced","v5_hybrid_lowzp")

def paired(profile,tmp):
    cfg=ROOT/"relocatable_source"/profile/"math_config_reference.inc"
    dest=tmp/profile
    manifest=build(profile,cfg,dest) if profile==PROFILES[0] else hybrid_build(cfg,dest)
    fresh=(dest/manifest["output_prg"]).read_bytes()
    start=int.from_bytes(fresh[:2],"little")
    raw=bytearray(fresh)
    vals=parse_config(ROOT/"relocatable_source/v1_balanced/math_config_reference.inc")
    constants="".join(f"{k} = ${v:04X}\n" for k,v in vals.items())
    candidate_source=K.library("v1_balanced",LAYOUTS["v1_balanced"],*SCRATCH["v1_balanced"])
    candidate_mem,_,_=Assembler().assemble(constants+candidate_source)
    archived_mem,_,_=synth_old("reference")
    assert archived_mem.keys() != candidate_mem.keys()
    assert all(raw[2+addr-start]==val for addr,val in candidate_mem.items()),("candidate source mismatch",profile)
    changed=0
    for a in set(candidate_mem)|set(archived_mem):
        idx=2+a-start
        assert 2<=idx<len(raw),(profile,hex(a))
        previous=archived_mem.get(a,0)
        changed += raw[idx]!=previous
        raw[idx]=previous
    assert 0<changed<400,(profile,changed)
    return bytes(raw),fresh,changed

def main():
    exe=os.getenv("VICE_WRAPPER")
    assert exe,"Set VICE_WRAPPER to installed x64sc"
    report={"status":"PASS_NATIVE_VICE_V1V5_COUNTED_SEEK16",
            "native_emulator_cycles_measured":False,"profiles":{}}
    with tempfile.TemporaryDirectory(prefix="seek16_v15_counted_native_") as d:
        tmp=Path(d)
        for i,p in enumerate(PROFILES):
            old,new,nbytes=paired(p,tmp)
            lhs=native(p,old,None,24900+4*i,tmp,exe)
            rhs=native(p,new,None,24901+4*i,tmp,exe)
            assert lhs==rhs,(p,"native init output differs",sha(lhs),sha(rhs))
            assert check_model(p,old,None,lhs)
            assert check_model(p,new,None,rhs)
            report["profiles"][p]={"status":"PASS_VICE_AND_6510_MODEL",
                 "paired_init":COUNT,"changed_SEEK_source_bytes":nbytes,
                 "old_source_sha256":sha(old),"new_source_sha256":sha(new),
                 "native_output_sha256":sha(rhs)}
            print(p,"real x64sc",COUNT,"paired source-built INIT calls PASS",flush=True)
    print(json.dumps(report,indent=2))
if __name__=="__main__":
    main()
