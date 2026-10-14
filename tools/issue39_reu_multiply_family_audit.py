#!/usr/bin/env python3
"""Issue #39: matched-corpus REU multiply family audit.

Compare normal UMUL16/32 against Turbo16/32 on EXACTLY the same operands,
including BEGIN/END and second-batch restore. V4 QS16 is also tested against
normal UMUL16. No source/code change and no private OptiSearch publication.

The CPU model includes deterministic REU DMA costs; it is NOT raster-accurate
native VICE timing. API call figures include RTS, not caller JSR/input setup.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from validate_turbo_relocation import cases,parse_inc,put,get,load_prg
from benchmark_multiply_refresh import load as load_published
P=("v3_reu_512k","v4_reu_16m")
KINDS=("published","reference","alternate")
MODE16="MATH_REU_UMUL16"
MODE32="MATH_REU_UMUL32"
QS="MATH_REU_QS16"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def take(profile,kind):
    if kind=="published":
        cpu,_=load_published(profile)
        api=parse_inc(ROOT/profile/'resident/math_api.inc')
        return cpu,api,None
    base=ROOT/"build_source"/kind/profile
    inc=parse_inc(base/"math_api.inc")
    mem=load_prg(base/f"math_{profile}_source_built.prg")
    reu=bytearray((base/f"c64_math_{profile}_source_built.reu").read_bytes())
    cpu=CPU(mem,reu=reu)
    cpu.d=0
    cpu.call(inc["MATH_INIT"],2_000_000)
    return cpu,inc,base
def run(cpu,api,name,bits,pairs):
    xaddr,yaddr,zaddr=api["MATH_X"],api["MATH_Y"],api["MATH_Z"]
    count=bits//8
    cy=[];witnesses=[]
    for x,y in pairs:
        put(cpu.mem,xaddr,x,count);put(cpu.mem,yaddr,y,count)
        beforeX=bytes(cpu.mem[xaddr:xaddr+count])
        beforeY=bytes(cpu.mem[yaddr:yaddr+count])
        cpu.c=(x^y)&1
        ticks=cpu.call(api[name],2_000_000)
        actual=get(cpu.mem,zaddr,2*count)
        expected=x*y
        assert actual==expected and cpu.c==0 and cpu.sp==0xfd,(name,hex(x),hex(y),hex(actual),hex(expected),cpu.c,cpu.sp)
        assert bytes(cpu.mem[xaddr:xaddr+count])==beforeX and bytes(cpu.mem[yaddr:yaddr+count])==beforeY,(name,"operands",x,y)
        cy.append(ticks)
    digest=hashlib.sha256(",".join(map(str,cy)).encode()).hexdigest()
    return {"cases":len(cy),"mean_cycles":sum(cy)/len(cy),"min_cycles":min(cy),
            "max_cycles":max(cy),"cycle_vector_sha256":digest,
            "arithmetic_carry_stack_inputs":"PASS"}
def lifecycle(cpu,api,prefix,bits,pairs,base,zplen):
    before=bytes((i*73+bits+17)&255 for i in range(zplen))
    cpu.mem[base:base+zplen]=before
    begin=cpu.call(api[prefix+"_BEGIN"],2_000_000)
    installed=bytes(cpu.mem[base:base+zplen])
    assert installed!=before,(prefix,"BEGIN failed to install")
    results=run(cpu,api,prefix,bits,pairs)
    end=cpu.call(api[prefix+"_END"],2_000_000)
    assert bytes(cpu.mem[base:base+zplen])==before,(prefix,"END did not restore caller ZP")
    # A new batch must use the REU-saved self-modified overlay again.
    begin2=cpu.call(api[prefix+"_BEGIN"],2_000_000)
    special=[(0xA55A,0x5AA5)] if bits==16 else [(0xA55A1234,0x5AA5FEDC)]
    second=run(cpu,api,prefix,bits,special)
    end2=cpu.call(api[prefix+"_END"],2_000_000)
    assert bytes(cpu.mem[base:base+zplen])==before,(prefix,"second batch ZP not restored")
    assert (begin,end)==(begin2,end2)
    return {**results,"begin_cycles":begin,"end_cycles":end,
        "second_begin_cycles":begin2,"second_end_cycles":end2,
        "second_batch_calls":second["cases"],
        "installed_overlay_sha256":hashlib.sha256(installed).hexdigest(),
        "zp_bytes_owned":zplen,
        "saved_ZP_exactly_restored":True,"second_batch_valid":True}
def break_even(normal,turbo):
    gain=normal["mean_cycles"]-turbo["mean_cycles"]
    overhead=turbo["begin_cycles"]+turbo["end_cycles"]
    if gain<=0:return {"beneficial":False,"normal_minus_mode_per_call_cycles":gain,
        "lifecycle_cycles":overhead,"crossover_calls":None}
    return {"beneficial":True,"normal_minus_mode_per_call_cycles":gain,
        "lifecycle_cycles":overhead,"crossover_calls":int(overhead//gain)+1}
def qs16(cpu,api,pairs):
    begin=cpu.call(api[QS+"_BEGIN"],2_000_000)
    q=run(cpu,api,QS,16,pairs)
    end=cpu.call(api[QS+"_END"],2_000_000)
    # After QS16_END one-byte REU services must work again.
    test=run(cpu,api,"MATH_UMUL8",8,[(0,0),(1,255),(255,255)])
    assert test["cases"]==3
    return {**q,"begin_cycles":begin,"end_cycles":end,"reu_mode_restored":True}
def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--all-maps",action="store_true")
    pa.add_argument("--output",type=Path)
    args=pa.parse_args()
    status=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    existing=json.loads((ROOT/"validation/turbo_relocation/TURBO_RELOCATION_VALIDATION.json").read_text())
    boundary=json.loads((ROOT/"validation/turbo_relocation/TURBO_BOUNDARY_SWEEP.json").read_text())
    assert existing["status"]==boundary["status"]=="PASS"
    assert existing["total_turbo_api_calls"]==17196 and boundary["total_product_calls"]==3556
    for p in P:
        assert sha(ROOT/p/"resident"/f"math_{p}_game_math.prg")==status["reference_prg_sha256"][p]
        assert sha(ROOT/p/"reu"/("c64_math_v3_512k_game_math.reu" if p==P[0] else "c64_math_v4_16m_game_math.reu"))==status["reference_reu_sha256"][p]
    kinds=KINDS if args.all_maps else KINDS[:1]
    if args.all_maps:
        for k in ("reference","alternate"):
            subprocess.run([sys.executable,str(ROOT/"tools/assemble_sources.py"),"--profile","all","--config-kind",k],cwd=ROOT,check=True)
    report={"status":"PASS_PUBLIC_REU_MULTIPLY_MODES","profiles":{},
      "source_kinds":list(kinds),"reproducible_turbo_relocation_prior_calls":17196,
      "reproducible_turbo_boundary_prior_calls":3556,
      "mean_cycle_basis":"CPU model including deterministic REU DMA, public entry through RTS, caller JSR/input preparation excluded",
      "native_raster_timing_measured":False,"no_code_or_resource_change":True,
      "private_optisearch_source_published":False}
    for p in P:
        report["profiles"][p]={}
        for k in kinds:
            cpu,api,buildpath=take(p,k)
            v={}
            for bits,prefix,old,zplen in ((16,MODE16,"MATH_UMUL16",122),
                                           (32,MODE32,"MATH_UMUL32",135)):
                pairs=cases(bits)
                normal=run(cpu,api,old,bits,pairs)
                base=api[f"TURBO{bits}_ZP_BASE"]
                turbo=lifecycle(cpu,api,prefix,bits,pairs,base,zplen)
                v[f"turbo{bits}"]={"normal":normal,"mode":turbo,
                                   "batch_vs_normal":break_even(normal,turbo)}
                if k in ("reference","alternate"):
                    previous=existing["profiles"][p][k][f"turbo{bits}"]
                    assert previous["cycle_vector_sha256"]==turbo["cycle_vector_sha256"],(p,k,bits,"cycle provenance drift")
                    assert previous["begin_cycles"]==turbo["begin_cycles"] and previous["end_cycles"]==turbo["end_cycles"]
                print("REU",p,k,prefix,"PASS",len(pairs),"normal",round(normal["mean_cycles"],5),"mode",round(turbo["mean_cycles"],5),flush=True)
            if p==P[1]:
                qs=qs16(cpu,api,cases(16))
                v["v4_qs16"]={"normal":v["turbo16"]["normal"],"mode":qs,
                    "batch_vs_normal":break_even(v["turbo16"]["normal"],qs)}
                print("REU",p,k,"QS16 PASS",qs["cases"],"mean",round(qs["mean_cycles"],5),flush=True)
            report["profiles"][p][k]=v
    # Equivalence of identical-input Turbo mode vectors across REU profiles.
    for k in kinds:
        for name in ("turbo16","turbo32"):
            a=report["profiles"][P[0]][k][name]["mode"]
            b=report["profiles"][P[1]][k][name]["mode"]
            assert a["cycle_vector_sha256"]==b["cycle_vector_sha256"] and a["begin_cycles"]==b["begin_cycles"] and a["end_cycles"]==b["end_cycles"],(k,name)
    if args.all_maps:
        for p in P:
            for name in ("turbo16","turbo32"):
                a=report["profiles"][p]["reference"][name]["mode"]
                b=report["profiles"][p]["alternate"][name]["mode"]
                assert a["cycle_vector_sha256"]==b["cycle_vector_sha256"]
                assert a["begin_cycles"]==b["begin_cycles"] and a["end_cycles"]==b["end_cycles"]
        # Source map artifacts, not current installed source, are temporary.
        subprocess.run(["make","clean"],cwd=ROOT,check=True)
    report["total_public_product_calls"]=sum(
        sum(q["mode"]["cases"]+q["normal"]["cases"] for key,q in r.items() if key.startswith("turbo"))
        + (r["v4_qs16"]["mode"]["cases"] if "v4_qs16" in r else 0)
        for profiles in report["profiles"].values() for r in profiles.values())
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 REU MULTIPLY MODES PUBLIC QUALIFICATION PASS",report["total_public_product_calls"],flush=True)
if __name__=="__main__":main()
