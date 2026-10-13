#!/usr/bin/env python3
"""Research-only public UMUL24 V1/V5 fast24 private-core tail-call A/B.

Same-input public profile old versus source-built new on reference/alternate
maps, with signed producer interleaves. No released resident or metadata change.
"""
from pathlib import Path
import hashlib,json,collections,sys,tempfile,random
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
import assemble_sources as asm,build_hybrid
import validate_source_build as src
from validate_unsigned_division import load as original
from validate_umul24_directout import corpus
P=("v1_balanced","v5_hybrid_lowzp")
def sha(b):return hashlib.sha256(b).hexdigest()
def wr(m,a,n):
 for j in range(3):m[a+j]=(n>>(8*j))&255
def rd(m,a):return sum(m[a+j]<<(8*j) for j in range(6))
def signed(n):return n-(1<<24) if n&(1<<23) else n
def sample(cpu,api,io,a,b,name):
 wr(cpu.mem,io,a);wr(cpu.mem,io+4,b)
 inp=bytes(cpu.mem[io:io+3]+cpu.mem[io+4:io+7])
 sp=cpu.sp;cpu.d=0
 cyc=cpu.call(api[name],10000)
 got=rd(cpu.mem,io+8)
 p=(signed(a)*signed(b) if name=="MATH_SMUL24" else a*b)&((1<<48)-1)
 assert got==p and cpu.c==0 and cpu.sp==sp,(name,hex(a),hex(b),hex(got),hex(p),cpu.c)
 assert bytes(cpu.mem[io:io+3]+cpu.mem[io+4:io+7])==inp,("input mutate",name)
 return cyc,got
def main():
 vectors=corpus()
 assert len(vectors)==10324
 rnd=random.Random(0x161924)
 alt=[vectors[k] for k in rnd.sample(range(len(vectors)),1024)]
 st=json.loads((R/"RELEASE_STATUS.json").read_text())
 result={"status":"PASS_RESEARCH_ONLY","no_release_change":True,"profiles":{},"paired_calls":0}
 with tempfile.TemporaryDirectory(prefix="issue39_umul24_v1_") as d:
  for profile in P:
   base,api=original(profile)
   orig=(R/profile/"resident"/f"math_{profile}_game_math.prg").read_bytes()
   assert sha(orig)==st["reference_prg_sha256"][profile]
   report={}
   for mode in ("reference","alternate"):
    folder=Path(d)/mode/profile
    conf=R/"relocatable_source"/profile/("math_config_"+mode+".inc")
    manifest=(asm.build(profile,conf,folder) if profile==P[0] else build_hybrid.build(conf,folder))
    newer,pub,io,man,_=src.load(profile,Path(d)/mode)
    cand=(folder/manifest["output_prg"]).read_bytes()
    if mode=="reference":
     assert len(cand)==len(orig)
     ld=int.from_bytes(cand[:2],"little")
     diff=[ld+i for i,(a,b) in enumerate(zip(orig[2:],cand[2:])) if a!=b]
     assert diff and all(0x2700<=v<0x3000 for v in diff),(profile,"unexpected modified region",list(map(hex,diff[:22])))
    pairs=vectors if mode=="reference" else alt
    hist=collections.Counter()
    for a,b in pairs:
     before,prod=sample(base,api,0xc000,a,b,"MATH_UMUL24")
     after,got=sample(newer,pub,io,a,b,"MATH_UMUL24")
     assert prod==got
     hist[after-before]+=1
    assert min(hist)<0 and max(hist)<=0,(profile,mode,hist)
    for a,b in pairs[:320]:
     before,res=sample(base,api,0xc000,a,b,"MATH_SMUL24")
     after,got=sample(newer,pub,io,a,b,"MATH_SMUL24")
     assert res==got and before==after,("signed executable changed",profile,mode,a,b,before,after)
     # Mix old and new entries in same public session
     sample(newer,pub,io,a,b,"MATH_UMUL24")
    result["paired_calls"]+=2*len(pairs)
    report[mode]={"cases":len(pairs),"mean_delta":sum(k*v for k,v in hist.items())/len(pairs),
                  "cycle_deltas":dict(sorted(hist.items())),
                  "candidate_prg_sha256":sha(cand)}
    print("UMUL24 FAST24",profile,mode,"SAVING",report[mode]["mean_delta"],
          "DIST",report[mode]["cycle_deltas"],flush=True)
   result["profiles"][profile]=report
 dst=R/"validation/review/ISSUE39_V1V5_UMUL24_TAILCALL_RESEARCH.json"
 dst.parent.mkdir(parents=True,exist_ok=True)
 dst.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
 print("V1/V5 PRIVATE FAST24 PRODUCER TAIL-CALL SOURCE SCREEN PASS",result["paired_calls"],flush=True)
if __name__=="__main__":main()
