#!/usr/bin/env python3
"""Issue144 B: rigorous 56-entry source-build gate for resident dual-tail opt-in.

Temporarily edit common V2-V4 division include *only in this test checkout*,
build real relocatable source PRGs and V3/V4 REUs, check all 56 API entries on
reference and alternate maps, and guard all CPU writes into REG_LOW+$0C00
461-byte code island. Restore the source include on every exit path.

Never mutate committed reference PRGs, REUs, PERFORMANCE, or default sources.
"""
from __future__ import annotations
import hashlib,json,sys,tempfile
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from issue144_u3216_inresident_dualtail_model import builds,PROFILES,OFFSET,NBYTES
from issue144_u3216_dualtail_direct_dispatch_screen import (
    ENTRY_OLD,ENTRY_NEW,STUB_BEFORE,STUB_AFTER,low_divisor_tail)
from assemble_sources import build as build_source,parse_config
from validate_source_build import validate
from mini6502 import CPU
FILE=R/"relocatable_source/division/udiv32_16_split_direct.inc"

def variant(src):
    assert src.count(ENTRY_OLD)==src.count(STUB_BEFORE)==1,"canonical source drift"
    text=src.replace(ENTRY_OLD,ENTRY_NEW).replace(STUB_BEFORE,STUB_AFTER)
    extra=low_divisor_tail().replace("* = $0800","* = REG_LOW+$0C00",1)
    assert extra.startswith("* = REG_LOW+$0C00")
    return text+"\n; Issue144 B opt-in source-owned 461-byte 32/16 low-D tail.\n"+extra

def main():
    base=FILE.read_text()
    snap=hashlib.sha256(base.encode()).hexdigest()
    result={"status":"PASS_INRESIDENT_56_ENTRY_SOURCE_BUILDS",
            "source_restore_verified":False,
            "normal_ZP_growth":0,"caller_RAM_bytes":0,
            "temporary_source_patch_only":True,
            "normal_secondary_tail_bytes":NBYTES,
            "reference_prgs_and_reus_untouched":True,"rows":[]}
    try:
        FILE.write_text(variant(base))
        with tempfile.TemporaryDirectory(prefix="issue144_u3216_resident_fullabi_") as tmp:
            output=Path(tmp)
            for layout in ("reference","alternate"):
                for p in PROFILES:
                    cfg=R/"relocatable_source"/p/("math_config_"+layout+".inc")
                    values=parse_config(cfg)
                    buildpath=output/layout/p
                    man=build_source(p,cfg,buildpath)
                    start=values["REG_LOW"]+OFFSET
                    end=start+NBYTES
                    assert man["status"]=="BUILT_FROM_SOURCE",(p,layout,man["status"])
                    old_write=CPU.wr
                    writes=[]
                    def guarded_write(cpu,addr,value):
                        if start<=(addr&0xFFFF)<end:
                            writes.append((hex(addr),hex(value)))
                            raise AssertionError(("resident executable overwritten by API",p,layout,writes[:16]))
                        return old_write(cpu,addr,value)
                    CPU.wr=guarded_write
                    try:
                        validated=validate(p,output/layout)
                    finally:
                        CPU.wr=old_write
                    assert validated["public_entries_executed"]==56,(p,layout)
                    assert validated["machine_calls"]>15000,(p,layout,validated["machine_calls"])
                    result["rows"].append({
                        "profile":p,"layout":layout,
                        "all_56_public_apis_pass":True,
                        "public_cpu_calls":validated["machine_calls"],
                        "resident_code_runtime_writes":len(writes),
                        "output_prg":man["output_prg"],
                        "output_sha256":man["output_sha256"],
                        "resident_tail":f"${start:04X}-${end-1:04X}",
                        "referential_and_reentrancy_proof_complete":False})
                    print("IN-RESIDENT ALL API",p,layout,"PASS",
                          validated["machine_calls"],"calls",flush=True)
    finally:
        FILE.write_text(base)
    assert hashlib.sha256(FILE.read_bytes()).hexdigest()==snap,"patch not restored"
    result["source_restore_verified"]=True
    print(json.dumps(result,sort_keys=True,indent=2))
if __name__=="__main__":main()
