#!/usr/bin/env python3
"""Issue39 DIST8 generated-source transplant audit: research, not a release.

Pair old published resident images with current generated reference/alternate
source builds. Confirm public data/flags, exact output and scratch semantics,
relocatable patches, same-input CPU-model timing and resource class.
"""
from pathlib import Path
import argparse, hashlib, json, random, sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import CPU
from validate_smul24_directout import load, parse_inc
from assemble_sources import parse_config
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k",
          "v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_DIST8_FAST","MATH_DIST8_ACCURATE")
PATCH={"v1_balanced":(0x09ED,14,9,True),
       "v2_pareto_fast":(0x0906,10,8,False),
       "v3_reu_512k":(0x0911,10,8,False),
       "v4_reu_16m":(0x07D0,10,8,False),
       "v5_hybrid_lowzp":(0x09ED,14,9,True)}
def baseline(profile):
    b=(R/profile/"resident"/("math_"+profile+"_game_math.prg")).read_bytes()
    addr=int.from_bytes(b[:2],"little")
    mem=bytearray(65536)
    mem[addr:addr+len(b)-2]=b[2:]
    reu_name={"v3_reu_512k":"c64_math_v3_512k_game_math.reu",
              "v4_reu_16m":"c64_math_v4_16m_game_math.reu"}.get(profile)
    reu=(R/profile/"reu"/reu_name).read_bytes() if reu_name else None
    c=CPU(mem,reu=bytearray(reu) if reu else None)
    api=parse_inc(R/profile/"resident"/"math_api.inc")
    c.d=0;c.call(api["MATH_INIT"],2_000_000)
    return c,api,hashlib.sha256(b).hexdigest()
def corpus():
    e=(-128,-127,-126,-65,-64,-33,-32,-17,-16,-8,-7,-3,-2,-1,0,1,2,3,7,8,16,17,32,33,63,64,65,126,127)
    out=list(dict.fromkeys(((a&255,b&255) for a in e for b in e)))
    r=random.Random(0xD1578)
    out.extend((r.randrange(256),r.randrange(256)) for _ in range(5120))
    return out
def call(c,api,op,x,y,where,abs_scratch):
    I=api["MATH_X"];J=api["MATH_Y"];Z=api["MATH_Z"]
    c.mem[I]=x;c.mem[J]=y
    c.mem[Z]=0xA5;c.mem[Z+1]=0x5A
    c.c=(x^y)&1;c.d=0
    cy=c.call(api[op],2_000_000)
    assert c.mem[I]==x and c.mem[J]==y,(where,op,x,y,"input")
    assert c.mem[Z+1]==0x5A and c.c==0 and c.sp==0xfd,(where,op,x,y,"flags/stack")
    return cy,c.mem[Z]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    cases=corpus()
    status=json.loads((R/"RELEASE_STATUS.json").read_text())
    out={"status":"PASS_SOURCE_DUAL_RELOCATION_DIST8_RESEARCH",
         "candidate_production_integrated":False,
         "native_vice_cycles_measured":False,"private_optisearch_source_published":False,
         "public_entry_count_per_routine_per_map":len(cases),
         "profiles":{}}
    for p in PROFILES:
        old,old_api,digest=baseline(p)
        assert digest==status["reference_prg_sha256"][p],(p,"baseline changed")
        offsets,length,saving,abspath=PATCH[p]
        out["profiles"][p]={}
        for kind in ("reference","alternate"):
            new,api=load(p,kind)
            basep="v1_balanced" if p=="v5_hybrid_lowzp" else p
            cfg=parse_config(R/"relocatable_source"/basep/("math_config_"+kind+".inc"))
            site=cfg["REG_GAME"]+offsets
            mem=new.mem
            assert mem[site]==0xAA,(p,kind,"TAX missing",hex(site))
            assert mem[site+1]==(0xAD if abspath else 0xA5),(p,kind,"LDA kind")
            assert mem[site+length]==0x60,(p,kind,"original BCC destination RTS")
            assert mem[site-2]==0x90,(p,kind,"BCC at swap start")
            output_hash=hashlib.sha256()
            per_op={}
            for op in OPS:
                total=old_total=swapped=0;diff_min=10000;diff_max=-1
                for x,y in cases:
                    base_cy,base_out=call(old,old_api,op,x,y,p+"/resident",abspath)
                    got_cy,got_out=call(new,api,op,x,y,p+"/"+kind,abspath)
                    assert base_out==got_out,(p,kind,op,x,y,base_out,got_out)
                    delta=base_cy-got_cy
                    expect=saving*int(abs(y-256 if y>=128 else y)>=abs(x-256 if x>=128 else x))
                    assert delta==expect,(p,kind,op,x,y,delta,expect)
                    old_total+=base_cy;total+=got_cy;swapped+=bool(expect)
                    diff_min=min(diff_min,delta);diff_max=max(diff_max,delta)
                    output_hash.update(bytes((got_out,)))
                per_op[op]={"cases":len(cases),"matched_shipped_resident_outputs":True,
                     "mean_old_cpu_cycles":old_total/len(cases),
                     "mean_candidate_cpu_cycles":total/len(cases),
                     "mean_saved_cpu_cycles":(old_total-total)/len(cases),
                     "swap_path_cases":swapped,"min_saving":diff_min,"max_saving":diff_max}
            out["profiles"][p][kind]={"patch_address":f"${site:04X}","routines":per_op,
                "combined_output_sha256":output_hash.hexdigest()}
            print(p,kind,"PASS",len(cases)*len(OPS),flush=True)
        assert out["profiles"][p]["reference"]["combined_output_sha256"]==out["profiles"][p]["alternate"]["combined_output_sha256"],(p,"relocation mismatch")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 DIST8 SOURCE TRANSPLANT REFERENCE/ALTERNATE PASS",flush=True)
if __name__=="__main__":main()
