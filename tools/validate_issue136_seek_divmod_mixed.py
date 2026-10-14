#!/usr/bin/env python3
"""Issue #136 permanent public ABI: interleave SEEK8/16 with unsigned DIV/MOD.

CPU-model proof for five profiles on both relocation maps. All movement
positions/carry are checked against the independent Bresenham path model,
every DIV/MOD against Python integer arithmetic, and the entire 408-byte
private SEEK state + the 6502 stack pointer are compared before/after each
arithmetic call. A printed PASS is not native VICE timing/proof.
"""
from __future__ import annotations
import hashlib, json, random, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"routines/movement"))
import validate_source_build as vsb
from seek_model import expected_frames

PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k",
          "v4_reu_16m","v5_hybrid_lowzp")
MAPS=("reference","alternate")
OPERATIONS=("MATH_UDIV32_16","MATH_UMOD32_16",
            "MATH_UDIV32_32","MATH_UMOD32_32")
CORPUS={
 8:((0,0,125,99,0x8200,"step"),
    (125,99,0,0,0x8180,"step"),
    (230,10,40,130,0x0200,"int"),
    (24,35,24,35,0x0100,"one"),
    (1,1,201,71,0x0300,"step"),
    (255,199,45,52,0x8400,"step")),
 16:((0,0,319,199,0x8200,"step"),
     (319,199,0,0,0x8180,"step"),
     (1000,30,1260,190,0x0300,"int"),
     (222,45,222,45,0x0100,"one"),
     (299,198,1,1,0x8400,"step"),
     (0,0,260,180,0x8100,"step")),
}
def put(cpu,where,value,n):
 for i in range(n): cpu.mem[where+i]=(value>>(i*8))&255
def get(cpu,where,n):
 return sum(cpu.mem[where+i] << (i*8) for i in range(n))
def state(cpu,symbols):
 p8=symbols["MATH_SEEK8_POS_X"]
 p16=symbols["MATH_SEEK16_POS_XL"]
 return bytes(cpu.mem[p8:p8+160])+bytes(cpu.mem[p16:p16+248])
def do_arith(cpu,api,io,kind,n,d):
 # Public input and private movement state must survive every arithmetic call.
 width=2 if "16" in kind else 4
 put(cpu,io+0x10,n,4)
 put(cpu,io+0x14,d,width)
 saved=(get(cpu,io+0x10,4),get(cpu,io+0x14,width))
 before=(state(cpu,api),cpu.sp)
 cycles=cpu.call(api[kind],300000)
 assert cycles>0
 remainder=get(cpu,io+0x1c,width)
 if d==0:
  assert cpu.c==1 and remainder==0,(kind,n,d,cpu.c,remainder)
 else:
  assert cpu.c==0 and remainder==n%d,(kind,n,d,cpu.c,remainder)
 if kind.startswith("MATH_UDIV"):
  quotient=get(cpu,io+0x18,4)
  assert quotient==(0 if d==0 else n//d),(kind,n,d,quotient)
 assert saved==(get(cpu,io+0x10,4),get(cpu,io+0x14,width))
 assert before==(state(cpu,api),cpu.sp),(kind,"SEEK state / stack corrupted",n,d)
 return cycles
def test(profile,kind):
 build=ROOT/("build_hybrid" if profile==PROFILES[-1] else "build_source")/kind
 cpu,api,io,manifest,_=vsb.load(profile,build)
 symbols=vsb.seek_symbols(build/profile)
 api.update(symbols)
 rng=random.Random(0x1365EEC)
 div_calls=0;step_calls=0;init_calls=0;cycles_saved=0
 for width in (8,16):
  prefix="MATH_SEEK8_" if width==8 else "MATH_SEEK16_"
  for i,(x0,y0,x1,y1,speed,mode) in enumerate(CORPUS[width]):
   slot=(i*3+width)&7
   if width==8:
    cpu.mem[symbols["MATH_SEEK8_POS_X"]+slot]=x0
    cpu.mem[symbols["MATH_SEEK8_POS_Y"]+slot]=y0
   else:
    cpu.mem[symbols["MATH_SEEK16_POS_XL"]+slot]=x0&255
    cpu.mem[symbols["MATH_SEEK16_POS_XH"]+slot]=x0>>8
    cpu.mem[symbols["MATH_SEEK16_POS_Y"]+slot]=y0
   put(cpu,io,x1,2);put(cpu,io+4,y1,1);put(cpu,io+0x10,speed,2)
   cpu.x=slot
   cpu.call(api[prefix+"INIT"],400000)
   init_calls+=1
   frames=expected_frames(x0,y0,x1,y1,speed,mode)
   assert cpu.c==int(not frames),(profile,kind,width,i,"INIT carry",cpu.c)
   stepper={"step":"STEP","int":"STEP_INT","one":"STEP1"}[mode]
   for t,(want,arrived) in enumerate(frames+[((x1,y1),True)]):
    if t%3==0:
     for j,op in enumerate(OPERATIONS):
      n=rng.getrandbits(32)
      # Stress zero, unit and nontrivial narrow / wide divisors, q0 and q1.
      bits=16 if "16" in op else 32
      d=(0,1,2,255,65535,0xffffffff,rng.getrandbits(bits))[(t+j+i)%7]&((1<<bits)-1)
      do_arith(cpu,api,io,op,n,d);div_calls+=1
    cpu.x=slot
    cpu.call(api[prefix+stepper],70000);step_calls+=1
    if width==8:
     pos=(cpu.mem[symbols["MATH_SEEK8_POS_X"]+slot],
          cpu.mem[symbols["MATH_SEEK8_POS_Y"]+slot])
    else:
     pos=(cpu.mem[symbols["MATH_SEEK16_POS_XL"]+slot]|
         cpu.mem[symbols["MATH_SEEK16_POS_XH"]+slot]<<8,
         cpu.mem[symbols["MATH_SEEK16_POS_Y"]+slot])
    assert (pos,cpu.c,cpu.x)==(want,int(arrived),slot),(
      profile,kind,width,i,t,(pos,cpu.c,cpu.x),(want,int(arrived),slot))
   # A second completed call must remain at destination.
   cpu.x=slot;cpu.call(api[prefix+stepper],70000)
   assert cpu.c==1
 return {"status":"PASS","init_calls":init_calls,
         "step_calls":step_calls,"interleaved_divmod_calls":div_calls,
         "source_prg_sha256":manifest["output_sha256"]}
def main():
 proof={"status":"PASS_MIXED_SEEK_DIVMOD_PUBLIC_SOURCE",
        "native_vice_proof":False,"profiles":{},"totals":{"init_calls":0,
        "step_calls":0,"interleaved_divmod_calls":0}}
 for p in PROFILES:
  proof["profiles"][p]={}
  for k in MAPS:
   row=test(p,k)
   proof["profiles"][p][k]=row
   for key in proof["totals"]:proof["totals"][key]+=row[key]
   print("SEEK/DIVMOD MIXED",p,k,row,flush=True)
 path=ROOT/"validation/review/ISSUE136_SEEK_DIVMOD_MIXED_PROOF.json"
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n")
 print("ISSUE136 MIXED PASS",proof["totals"],flush=True)
if __name__=="__main__":main()
