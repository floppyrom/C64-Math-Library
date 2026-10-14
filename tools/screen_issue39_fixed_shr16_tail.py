#!/usr/bin/env python3
"""Issue #39 fixed multiply SHR16: no-growth return-tail source A/B research.

Tests BOTH signed/unsigned 32x32>>16 public calls in all five profiles and
both source relocation maps. No production binaries or source are published by
this read-only research run. Preserve independent 16-bit SHR8 qualifications.
"""
from pathlib import Path
import hashlib,json,random,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from validate_smul24_directout import load as load_candidate
from benchmark_multiply_refresh import load as load_original,CORPORA
import assemble_sources as asm
import build_hybrid
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
SOURCE=P[:-1]
OPS=(("MATH_UMUL32","MATH_UMUL32_SHR16",False),
     ("MATH_SMUL32","MATH_SMUL32_SHR16",True))
TYPES=("reference","alternate")
OLD="    clc\n    rts\n"
NEW="    rts\n    nop\n"
def sha(data):return hashlib.sha256(data).hexdigest()
def patch(src):
    chunks=[];diffs={}
    for parent in ("    jsr REG_API+$00B0\n","    jsr REG_API+$0C40\n"):
        assert src.count(parent)==1,(parent,src.count(parent))
        i=src.index(parent);j=src.index("    rts\n",i)+len("    rts\n")
        chunk=src[i:j]
        assert chunk.endswith(OLD) and chunk.count("    lda MATH_IO+") == 6 and chunk.count("    sta MATH_IO+")==6,chunk
        chunks.append((chunk,chunk[:-len(OLD)]+NEW))
    updated=src
    for old,new in chunks:
        assert old!=new and updated.count(old)==1
        updated=updated.replace(old,new)
    return updated
def build():
    for kind in TYPES:
        subprocess.run([sys.executable,str(ROOT/"tools/assemble_sources.py"),"--profile","all","--config-kind",kind],cwd=ROOT,check=True)
        subprocess.run([sys.executable,str(ROOT/"tools/build_hybrid.py"),"--config-kind",kind],cwd=ROOT,check=True)
def prg(p,kind):
    d=ROOT/("build_hybrid" if p==P[-1] else "build_source")/kind/p
    m=json.loads((d/"source_build_manifest.json").read_text())
    return (d/m["output_prg"]).read_bytes()
def setup_image(blob,profile,kind,is_candidate):
    from validate_smul24_directout import parse_inc
    mem=bytearray(65536)
    load=int.from_bytes(blob[:2],"little")
    mem[load:load+len(blob)-2]=blob[2:]
    if is_candidate:
        d=ROOT/("build_hybrid" if profile==P[-1] else "build_source")/kind/profile
        m=json.loads((d/"source_build_manifest.json").read_text())
        api=parse_inc(d/"math_api.inc")
        reu=bytearray((d/m["reu_image"]["file"]).read_bytes()) if m.get("reu_image") else None
    else:
        api=parse_inc(ROOT/profile/"resident"/"math_api.inc")
        reu=None
        if profile=="v3_reu_512k":
            reu=bytearray((ROOT/"v3_reu_512k/reu/c64_math_v3_512k_game_math.reu").read_bytes())
        if profile=="v4_reu_16m":
            reu=bytearray((ROOT/"v4_reu_16m/reu/c64_math_v4_16m_game_math.reu").read_bytes())
    cpu=CPU(mem,reu=reu);cpu.d=0;cpu.call(api["MATH_INIT"],2_000_000)
    return cpu,api
def run_call(cpu,api,op,x,y,signed):
    X,Y,Z=api["MATH_X"],api["MATH_Y"],api["MATH_Z"]
    for i in range(4):
        cpu.mem[X+i]=(x>>(8*i))&255
        cpu.mem[Y+i]=(y>>(8*i))&255
    for i in range(6):cpu.mem[Z+i]=0xa7
    bx=bytes(cpu.mem[X:X+4]);by=bytes(cpu.mem[Y:Y+4])
    cpu.c=x&1
    cyc=cpu.call(api[op],2_000_000)
    signed32=lambda t:(t-(1<<32)) if t&(1<<31) else t
    a,b=(signed32(x),signed32(y)) if signed else (x,y)
    exp=((a*b)>>16)&((1<<48)-1)
    result=int.from_bytes(cpu.mem[Z:Z+6],"little")
    assert (result==exp and cpu.c==0 and cpu.sp==0xfd and
            bytes(cpu.mem[X:X+4])==bx and bytes(cpu.mem[Y:Y+4])==by),(
            op,hex(x),hex(y),hex(result),hex(exp),cpu.c)
    return cyc,result

def paired(profile,kind,original,candidate,cases):
    before,api=setup_image(original,profile,'reference',False)
    after,apic=setup_image(candidate,profile,kind,True)
    assert set(api)==set(apic)
    entries={}
    for _,op,signed in OPS:
        old_total=new_total=0;delta={};vector=hashlib.sha256()
        for x,y in cases:
            o,product=run_call(before,api,op,x,y,signed)
            n,other=run_call(after,apic,op,x,y,signed)
            assert product==other
            d=n-o;delta[str(d)]=delta.get(str(d),0)+1
            old_total+=o;new_total+=n
            vector.update(o.to_bytes(2,"little")+n.to_bytes(2,"little"))
        assert delta=={"-2":len(cases)},(profile,kind,op,delta)
        entries[op]={"cases":len(cases),"old_mean_cycles":old_total/len(cases),
             "new_mean_cycles":new_total/len(cases),"delta_histogram":delta,
             "public_abi":"PASS","cycle_vector_sha256":vector.hexdigest()}
    return entries
def main():
    sources={p:ROOT/"relocatable_source"/p/"math_relocatable.asm" for p in SOURCE}
    oldtext={p:path.read_text() for p,path in sources.items()}
    old={p:(ROOT/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes() for p in P}
    status=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    assert {p:sha(old[p]) for p in P}==status["reference_prg_sha256"]
    corpus=CORPORA["shift32"]
    assert len(corpus)==4361
    rep={"status":"PASS_RESEARCH_NOT_RELEASED","source_files_modified":False,
         "production_binaries_modified":False,"native_cycle_timing_measured":False,
         "source_maps":list(TYPES),"profile_results":{},"resident_reference_sha256":status["reference_prg_sha256"],
         "paired_cases_per_profile_per_entry_per_map":len(corpus),
         "optimizer":"replace redundant CLC RTS tail with RTS NOP; preserve binary span and carry C=0"}
    try:
        for p,path in sources.items():path.write_text(patch(oldtext[p]))
        build()
        for p in P:
            rep["profile_results"][p]={}
            for kind in TYPES:
                candidate=prg(p,kind)
                if kind=="reference":
                    assert len(old[p])==len(candidate),(p,"span changed")
                    offsets=[i for i,(a,b) in enumerate(zip(old[p],candidate)) if a!=b]
                    assert len(offsets)==4,(p,offsets)
                    image_load=int.from_bytes(old[p][:2],"little")
                    changed=[hex(image_load+i-2) for i in offsets]
                    assert all(0xc000<=int(z,16)<0xd000 for z in changed),(p,changed)
                    rep["profile_results"][p]["changed_absolute_addresses"]=changed
                    rep["profile_results"][p]["candidate_sha256"]=sha(candidate)
                rep["profile_results"][p][kind]=paired(p,kind,old[p],candidate,corpus)
                print("SHR16 PAIRED SOURCE",p,kind,"PASS",len(corpus),"each op -2",flush=True)
        # Invariant 16-bit fixed output: already qualified per-call register return.
        prior=json.loads((ROOT/"validation/multiply_refresh/MUL16_SHR8_REGISTER_VALIDATION.json").read_text())
        assert prior["status"]=="PASS"
        for p in P:
            row=prior["results"][p]["reference"]
            assert row["cases"]==10196
            assert abs(row["umul16_shr8"]["mean_cycles"]-row["umul16"]["mean_cycles"]-(31 if p in (P[0],P[-1]) else 27))<1e-8
            assert abs(row["smul16_shr8"]["mean_cycles"]-row["smul16"]["mean_cycles"]-31)<1e-8
        report=ROOT/"validation/review/ISSUE39_FIXED_SHR16_RETURN_TAIL_RESEARCH_2026-10-14.json"
        report.write_text(json.dumps(rep,indent=2,sort_keys=True)+"\n")
    finally:
        for p,path in sources.items():path.write_text(oldtext[p])
    assert all(sources[p].read_text()==oldtext[p] for p in SOURCE)
    assert all((ROOT/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes()==old[p] for p in P)
    print("SHR16 A/B RESEARCH VERIFIED; NO PRODUCTION BINARY CHANGED",flush=True)
if __name__=="__main__":main()
