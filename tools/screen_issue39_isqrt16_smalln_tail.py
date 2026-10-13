#!/usr/bin/env python3
"""Bounded, exact source-built ISQRT16 small-N tail Pareto screen.

Compares unchanged PR102 main against a candidate that still resides entirely
within the same 303/304-byte code+seed island. No changes to installed PRGs,
public ABI, the private OptiSearch engine, or production profile defaults.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math,random,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import assemble_sources as asm
import validate_source_build as sourcecheck
from validate_unsigned_division import load as oldload,wr,rd
from screen_issue39_isqrt16_seed_square import samples32

N=0xC010;Z=0xC008
def sample(cpu,entry,n,width,io=0xc000):
    naddr=io+0x10;zaddr=io+0x08
    wr(cpu.mem,naddr,n,width//8)
    original=bytes(cpu.mem[naddr:naddr+width//8])
    wr(cpu.mem,zaddr,0xa4b5c6d7,4)
    cpu.d=0;sp=cpu.sp
    cycles=cpu.call(entry,400000)
    assert rd(cpu.mem,zaddr,2)==math.isqrt(n),(width,hex(n),"root")
    assert bytes(cpu.mem[naddr:naddr+width//8])==original,(width,hex(n),"radicand")
    assert cpu.c==0 and cpu.sp==sp,(width,hex(n),"carry/stack")
    assert rd(cpu.mem,zaddr+2,2)==0xa4b5,(width,hex(n),"high output")
    return cycles

def compare(old,new,oldentry,newentry,values,width,io=0xc000):
    baseline=[];candidate=[]
    for n in values:
        baseline.append(sample(old,oldentry,n,width))
        candidate.append(sample(new,newentry,n,width,io))
    delta=[b-a for a,b in zip(baseline,candidate)]
    return {"cases":len(values),
      "baseline_mean_cycles":sum(baseline)/len(values),
      "candidate_mean_cycles":sum(candidate)/len(values),
      "mean_delta_cycles":sum(delta)/len(values),
      "baseline_max_cycles":max(baseline),
      "candidate_max_cycles":max(candidate),
      "max_regression_cycles":max(delta),
      "max_gain_cycles":-min(delta),
      "faster":sum(x<0 for x in delta),
      "equal":sum(x==0 for x in delta),
      "slower":sum(x>0 for x in delta),
      "candidate_cycle_sha256":hashlib.sha256(json.dumps(candidate).encode()).hexdigest()}
def main():
    P="v2_pareto_fast"
    old,api=oldload(P)
    with tempfile.TemporaryDirectory(prefix="issue39_tinyroot_") as temp:
        folder=Path(temp);cfg=ROOT/"relocatable_source"/P/"math_config_reference.inc"
        man=asm.build(P,cfg,folder/P)
        cpu,newapi,io,_,_=sourcecheck.load(P,folder)
        assert man["public_entries"]["MATH_ISQRT16"].lower()=="$5e2d"
        record={"status":"PASS_CANDIDATE_ONLY_NOT_PROMOTED",
          "profile":P,"source_ownership":"same existing root code island",
          "root16":compare(old,cpu,api["MATH_ISQRT16"],newapi["MATH_ISQRT16"],range(65536),16,io),
          "root32":compare(old,cpu,api["MATH_ISQRT32"],newapi["MATH_ISQRT32"],samples32(2048),32,io),
          "source_sha256":man["output_sha256"],"native_vice_calls":0,
          "no_public_contract_change":True}
    a=record["root16"];b=record["root32"]
    assert a["candidate_max_cycles"]<a["baseline_max_cycles"],("no worst-case gain",a)
    assert b["candidate_max_cycles"]<=b["baseline_max_cycles"]+12,("root32 max regression",b)
    assert a["cases"]==65536
    path=ROOT/"validation/review/ISSUE39_ISQRT16_SMALLN_TAIL_RESEARCH.json"
    path.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("ISQRT16 SMALL-N EXACT 65536:",a,"\\nISQRT32 composition:",b,flush=True)
    print("ROOT16 SMALL-N PARETO RESEARCH ONLY PASS",flush=True)
if __name__=="__main__":main()
