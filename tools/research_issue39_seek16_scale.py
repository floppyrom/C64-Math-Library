#!/usr/bin/env python3
"""Issue39 SEEK16 Euclidean high-byte scaling loop research (unreleased).

Compare shipped/reference-source candidate on the SAME fixed corpus, same
positions, flags, preserved public IO and slot, ALL initialized movement
state and first 8 STEP frames. Native VICE and production release separate.
"""
from pathlib import Path
import hashlib,json,random,sys,subprocess
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import CPU
from benchmark_seek_profiles import api
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
REU={
 "v3_reu_512k":R/"v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
 "v4_reu_16m":R/"v4_reu_16m/reu/c64_math_v4_16m_game_math.reu"}
SPEEDS=(0x0001,0x0080,0x0100,0x0180,0x0200,0x0500,0x1000,0x7E00)
EDGE=((0,0,319,199),(319,199,0,0),(0,199,319,0),
 (50,80,50,80),(0,0,0,199),(100,100,100,101),
 (127,127,0,0),(0,20,32767,20),(32767,20,0,20),
 (100,20,32000,110),(32000,110,100,20),
 (319,1,319,199),(319,199,319,1),(42,31,43,31),
 (31,42,30,43),(0,0,319,0),(0,0,0,1),(300,190,0,0))
def corpus():
 r=random.Random(0x53EE16)
 return list(EDGE)+[(r.randrange(320),r.randrange(200),r.randrange(320),r.randrange(200))
  for _ in range(64)]
def sha(b):return hashlib.sha256(b).hexdigest()
def prg(p,mode):
 if mode=="before":return (R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes()
 d=(R/("build_hybrid" if p=="v5_hybrid_lowzp" else "build_source")/"reference"/p)
 m=json.loads((d/"source_build_manifest.json").read_text())
 return (d/m["output_prg"]).read_bytes()
def machine(p,data):
 mem=bytearray(65536);offset=data[0]|data[1]<<8
 mem[offset:offset+len(data)-2]=data[2:]
 reu=bytearray(REU[p].read_bytes()) if p in REU else None
 c=CPU(mem,reu=reu);c.d=0
 names=api(p);c.call(names["MATH_INIT"],2000000)
 return c,names
def do_init(c,a,slot,m,speed):
 x0,y0,x1,y1=m
 base=a["MATH_SEEK16_POS_XL"];io=a["MATH_X"]
 c.mem[base+slot]=x0&255;c.mem[base+8+slot]=x0>>8
 c.mem[base+16+slot]=y0
 c.mem[io]=x1&255;c.mem[io+1]=x1>>8;c.mem[io+4]=y1
 c.mem[io+0x10]=speed&255;c.mem[io+0x11]=speed>>8
 before=bytes(c.mem[io:io+0x12]);c.x=slot;c.d=0
 cycles=c.call(a["MATH_SEEK16_INIT"],2000000)
 assert bytes(c.mem[io:io+0x12])==before
 assert c.x==slot and c.sp==0xfd
 return cycles,c.c,bytes(c.mem[base:base+248])
def run():
 for kind in ("reference","alternate"):
  subprocess.run([sys.executable,str(R/"tools/generate_seek_sources.py"),"--check"],check=True,cwd=R)
  subprocess.run([sys.executable,str(R/"tools/assemble_sources.py"),"--profile","all","--config-kind",kind],check=True,cwd=R)
  subprocess.run([sys.executable,str(R/"tools/build_hybrid.py"),"--config-kind",kind],check=True,cwd=R)
 # Both source map pass independently, reference compared to shipped resident.
 st=json.loads((R/"RELEASE_STATUS.json").read_text())
 results={"status":"PASS_SEEK16_SCALE_LOOP_RESEARCH_NOT_RELEASED",
  "native_vice_cycles_measured":False,"production_binaries_modified":False,
  "profiles":{},"input_vectors":len(corpus()),"speed_variants":len(SPEEDS)*2}
 for p in P:
  old=prg(p,"before");new=prg(p,"after")
  assert sha(old)==st["reference_prg_sha256"][p]
  assert len(old)==len(new) and old[:2]==new[:2]
  assert sha(old)!=sha(new),(p,"source candidate was not incorporated")
  c,a=machine(p,old);d,b=machine(p,new)
  assert a["MATH_SEEK16_INIT"]==b["MATH_SEEK16_INIT"]
  summary={"old_prg_sha256":sha(old),"candidate_prg_sha256":sha(new),
   "init_calls_each":0,"step_calls_each":0,"euclid_hi_cases":0,
   "euclid_hi_mean_saved":None,"max_gain":-1e9,"min_gain":1e9,
   "non_euclid_cycle_mismatches":0,"state_and_carry_mismatches":0}
  gains=[]
  for index,m in enumerate(corpus()):
   for speed in SPEEDS:
    for flag in (0,0x8000):
     sp=speed|flag;slot=index&7
     aa=do_init(c,a,slot,m,sp)
     bb=do_init(d,b,slot,m,sp)
     assert aa[1:]==bb[1:],(p,m,sp,"INIT state/carry drift")
     gain=aa[0]-bb[0]
     if not flag:assert gain==0,(p,m,sp,gain)
     if flag:
      assert gain>=0,(p,m,sp,gain)
      if abs(m[2]-m[0])>=256:
       assert gain>=4,(p,m,sp,gain)
       gains.append(gain)
     summary["init_calls_each"]+=1
     summary["min_gain"]=min(summary["min_gain"],gain)
     summary["max_gain"]=max(summary["max_gain"],gain)
     for step in range(8):
      c.x=d.x=slot
      cy0=c.call(a["MATH_SEEK16_STEP"],2000000)
      cy1=d.call(b["MATH_SEEK16_STEP"],2000000)
      assert cy0==cy1,(p,m,sp,step,"STEP slowed/changed")
      assert c.c==d.c and c.x==d.x and c.sp==d.sp==0xfd
      base=a["MATH_SEEK16_POS_XL"]
      assert bytes(c.mem[base:base+248])==bytes(d.mem[base:base+248]),(p,m,sp,step)
      summary["step_calls_each"]+=1
  assert gains,("no high-byte Euclidean corpus",p)
  summary["euclid_hi_cases"]=len(gains)
  summary["euclid_hi_mean_saved"]=sum(gains)/len(gains)
  results["profiles"][p]=summary
  print("SEEK16 SCALE",p,summary["init_calls_each"],"init calls; Euclidean high-byte mean saving",
   summary["euclid_hi_mean_saved"],flush=True)
 out=R/"validation/review/ISSUE39_SEEK16_SCALE_RESEARCH_2026-10-14.json"
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
 print("SEEK16 SCALE LOOP 5-PROFILE PUBLIC STATE/STEP RESEARCH PASS",flush=True)
if __name__=="__main__":run()
