#!/usr/bin/env python3
"""Issue39 signed multiply full-public-ABI screening with identical-input READY.

Correctness before timing. No edits to production, and no private OptiSearch
source imported or distributed. The output is a reproducible CPU-model report.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, random, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from validate_signed_multiply import load_profile,edge_values,signed,wr,rd,PROFILES
from benchmark_multiply_refresh import CORPORA
IO=0xc000
OP=(("MATH_SMUL8",8),("MATH_SMUL16",16),
    ("MATH_SMUL24",24),("MATH_SMUL32",32))
def sha(data):return hashlib.sha256(data).hexdigest()
def corpus(bits):
    if bits==8:return CORPORA[8]
    e=edge_values(bits)
    seed=0x39_5153_00+bits
    rng=random.Random(seed)
    count={16:4096,24:2048,32:2048}[bits]
    return [(x,y) for x in e for y in e]+[
        (rng.getrandbits(bits),rng.getrandbits(bits)) for _ in range(count)]
def execute(cpu,api,name,bits,x,y):
    n=bits//8
    wr(cpu.mem,IO,x,n);wr(cpu.mem,IO+4,y,n)
    before=(bytes(cpu.mem[IO:IO+n]),bytes(cpu.mem[IO+4:IO+4+n]))
    cpu.d=0
    cycles=cpu.call(api[name],2_000_000)
    product=(signed(x,bits)*signed(y,bits))&((1<<(bits*2))-1)
    output=rd(cpu.mem,IO+8,n*2)
    assert (output,cpu.c,bytes(cpu.mem[IO:IO+n]),
            bytes(cpu.mem[IO+4:IO+4+n]))==(product,0,*before),(
            name,hex(x),hex(y),hex(output),hex(product),cpu.c)
    assert cpu.sp==0xfd,(name,"SP",cpu.sp)
    return cycles
def run_profile(profile,all_corpora):
    cpu,api=load_profile(profile)
    sizes={};results={}
    for name,bits in OP:
        pairs=all_corpora[bits];sumcycles=0;lo=10**9;hi=0;hashes=hashlib.sha256()
        for x,y in pairs:
            c=execute(cpu,api,name,bits,x,y)
            sumcycles+=c;lo=min(lo,c);hi=max(hi,c);hashes.update(c.to_bytes(2,"little"))
        results[name]={"pairs":len(pairs),"mean_cycles":sumcycles/len(pairs),
                        "minimum":lo,"maximum":hi,"cycle_vector_sha256":hashes.hexdigest(),
                        "arithmetic_carry_input_stack":"PASS"}
        print(profile,name,"PASS",len(pairs),"mean",results[name]["mean_cycles"],flush=True)
    pairs=all_corpora[32];times=[0,0];hist={};hashes=[hashlib.sha256(),hashlib.sha256()]
    for x,y in pairs:
        ordinary=execute(cpu,api,"MATH_SMUL32",32,x,y)
        ready=execute(cpu,api,"MATH_SMUL32_READY",32,x,y)
        for i,t in enumerate((ordinary,ready)):
            times[i]+=t;hashes[i].update(t.to_bytes(2,"little"))
        d=ordinary-ready
        hist[str(d)]=hist.get(str(d),0)+1
    results["MATH_SMUL32_READY"]={
         "pairs":len(pairs),"ordinary_mean_cycles":times[0]/len(pairs),
         "ready_mean_cycles":times[1]/len(pairs),
         "mean_ready_saving_cycles":(times[0]-times[1])/len(pairs),
         "delta_histogram":hist,"ordinary_vector_sha256":hashes[0].hexdigest(),
         "ready_vector_sha256":hashes[1].hexdigest(),
         "identical_operand_and_initialized_pointer_corpus":True,
         "arithmetic_carry_input_stack":"PASS"}
    print(profile,"SMUL32 READY SAME-INPUT PASS",results["MATH_SMUL32_READY"]["mean_ready_saving_cycles"],flush=True)
    return results
def mixed_lowzp(profile):
    """Check dirty-pointer witnesses without treating unprepared READY as an ABI promise."""
    ops=[("MATH_UMUL24",24),("MATH_SMUL16",16),("MATH_SMUL24",24),
         ("MATH_UMUL16",16),("MATH_SMUL8",8),("MATH_UDIV16",16)]
    pairs=corpus(32)[:20]
    rng=random.Random(0x3932)
    cases=0;normal_valid=0;unqualified_ready_wrong=0;witnesses=[]
    for op,bits in ops:
        for state in range(3):
            cpu,api=load_profile(profile)
            # An ordinary entry always establishes the READY pointer state.
            execute(cpu,api,"MATH_SMUL32",32,0x12345678,0x9abcdef0)
            x=rng.getrandbits(bits);y=rng.getrandbits(bits)
            wr(cpu.mem,IO,x,bits//8);wr(cpu.mem,IO+4,y,bits//8)
            cpu.call(api[op],2_000_000)
            for u,v in pairs:
                ca=copy.deepcopy(cpu);cb=copy.deepcopy(cpu)
                execute(ca,api,"MATH_SMUL32",32,u,v)
                normal_valid+=1
                try:execute(cb,api,"MATH_SMUL32_READY",32,u,v)
                except (AssertionError,RuntimeError) as e:
                    unqualified_ready_wrong+=1
                    if len(witnesses)<18:witnesses.append({
                        "preceding_op":op,"state":state,"x":hex(u),"y":hex(v),
                        "error_type":type(e).__name__})
                cases+=1
    return {"states":len(ops)*3,"paired_calls":cases,
            "ordinary_valid":normal_valid,
            "unqualified_ready_wrong":unqualified_ready_wrong,
            "witnesses":witnesses,
            "ready_state_is_a_precondition_not_a_normal_api_substitute":True}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    status=json.loads((R/"RELEASE_STATUS.json").read_text())
    prgs={p:sha((R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes())
          for p in PROFILES}
    assert prgs==status["reference_prg_sha256"]
    previous=json.loads((R/"validation/review/SIGNED_MULTIPLY_VALIDATION.json").read_text())
    assert previous["status"]=="PASS" and previous["summary"]["machine_calls"]==264999
    all_corpora={bits:corpus(bits) for _,bits in OP}
    rows={p:run_profile(p,all_corpora) for p in PROFILES}
    identical={}
    for bits in (8,16,24,32):
        name="MATH_SMUL"+str(bits)
        # A repeated relocation must not be misdiagnosed as a performance win.
        identical[name]={p:rows[p][name]["cycle_vector_sha256"] for p in PROFILES}
        if bits==8:assert len(set(identical[name].values()))==1
        if bits==24:assert rows["v1_balanced"][name]["cycle_vector_sha256"]==rows["v5_hybrid_lowzp"][name]["cycle_vector_sha256"]
    ready={p:rows[p]["MATH_SMUL32_READY"] for p in PROFILES}
    lowzp={p:mixed_lowzp(p) for p in ("v1_balanced","v5_hybrid_lowzp")}
    report={"status":"PASS_PUBLIC_ABI_MODEL","date":"2026-10-14",
        "scope":"signed multiply 8,16,24,32 and signed 32 READY",
        "profiles":list(PROFILES),"same_input_per_profile":rows,
        "same_input_corpus_sizes":{str(k):len(v) for k,v in all_corpora.items()},
        "s8_exhaustive_all_five_profiles":True,
        "reference_prg_sha256":prgs,
        "previous_264999_signed_calls":"PASS",
        "ready_same_input_confirmed":{p:ready[p]["pairs"] for p in PROFILES},
        "ready_mixed_lifetime_lowzp":lowzp,
        "cycle_provenance":"CPU-model public entry through RTS, excludes caller JSR/input stores",
        "resident_modified":False,"normal_ZP_modified":False,
        "private_optisearch_code_published":False}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 SIGNED MULTIPLY FAMILY PUBLIC ABI PASS",sum(len(v) for v in all_corpora.values())*5+len(all_corpora[32])*5,flush=True)
if __name__=="__main__":main()
