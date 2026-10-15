#!/usr/bin/env python3
"""Research only: optional complete UDIV32/16 public ABI, unrestricted N,D.

Branch once: for $0100 <= D < $8000, use certified V2-V4 16/16 highword
producer followed by no-overflow unrolled lowword tail; for all other
denominators, including D=0 and all 8-bit D, JMP the original public UDIV32/16. Code is assembled in
caller-owned $0800 RAM; shipped residents and REUs are untouched.
"""
import hashlib, json, random, statistics, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from validate_udiv32_16_integrated import load_resident,one
from issue144_u3216_nooverflow_lowd_tail_screen import low_d_source

PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
OPS=("MATH_UDIV32_16","MATH_UMOD32_16")
ENTRY=0x0800
NAMES={
 "U3216_N0":0x10,"U3216_N1":0x11,"U3216_D0":0x12,"U3216_D1":0x13,
 "U3216_Q2":0x14,"U3216_Q3":0x15,"U3216_R0":0x16,"U3216_R1":0x17,
 "U3216_LN0":0x18,"U3216_LN1":0x19,
}
def body():
 s=low_d_source().splitlines()
 assert s[1:3]==["clc","lda $35"] and s[-3:]==["rol $33","sta $35","jmp $07FF"]
 s=s[3:-2]
 for i,line in enumerate(s):
  for old,new in (("$34","U3216_LN1"),("$33","U3216_LN0"),
                  ("$32","U3216_R0"),("$31","U3216_D1"),("$30","U3216_D0")):
   line=line.replace(old,new)
  s[i]=line
 return "\n".join(s)+"\n"

def assemble():
 const="\n".join(k+" = $"+format(v,"02X") for k,v in NAMES.items())
 header="""* = $0800
OPT_U3216_LOW:
    lda $c015
    beq FALLBACK
    bpl COPY_INPUT
FALLBACK:
    jmp $31b0
COPY_INPUT:
    lda $c010
    sta U3216_LN0
    lda $c011
    sta U3216_LN1
    lda $c012
    sta U3216_N0
    lda $c013
    sta U3216_N1
    lda $c014
    sta U3216_D0
    lda $c015
    sta U3216_D1
    jsr $420c
    lda U3216_R1
"""
 epilogue="""    sta $c01d
    lda U3216_LN0
    sta $c018
    lda U3216_LN1
    sta $c019
    lda U3216_Q2
    sta $c01a
    lda U3216_Q3
    sta $c01b
    lda U3216_R0
    sta $c01c
    clc
    rts
"""
 code,labels,_=Assembler().assemble(const+"\n"+header+body()+epilogue)
 assert min(code)==ENTRY and max(code)<0x0b00
 return code

def vectors():
 r=random.Random(0x144F003216)
 ds=[0,1,2,3,127,255,256,257,0x4000,0x7ffe,0x7fff,
     0x8000,0x8001,0xfffe,0xffff]
 ns=[0,1,255,256,65535,65536,0x12345678,0x7fffffff,
     0x80000000,0xfffffffe,0xffffffff]
 v=[(n,d) for d in ds for n in ns]
 v += [(r.getrandbits(32),r.getrandbits(16)) for _ in range(1536)]
 v += [(r.getrandbits(32),r.randint(1,0x7fff)) for _ in range(1536)]
 v += [(r.getrandbits(32),r.randint(0x8000,0xffff)) for _ in range(512)]
 v += [(r.getrandbits(32),r.randrange(1,256)) for _ in range(512)]
 return v

def stats(xs):
 s=sorted(xs)
 return dict(n=len(xs),mean=statistics.mean(xs),median=statistics.median(xs),
             p5=s[int(.05*(len(s)-1))],p95=s[int(.95*(len(s)-1))],
             minimum=s[0],maximum=s[-1])

def main():
 code=assemble()
 standalone=ROOT/"optional/issue144_u3216_nooverflow_lowdiv/optin_v2_v3_v4_reference.asm"
 if standalone.exists():
  compiled,labels,_=Assembler().assemble(standalone.read_text())
  assert compiled==code,("published standalone assembler byte mismatch",len(compiled),len(code))
  assert labels["OPT_U3216_LOW"]==ENTRY
 pairs=vectors()
 digest=hashlib.sha256(b"".join(n.to_bytes(4,"little")+d.to_bytes(2,"little")
                              for n,d in pairs)).hexdigest()
 out={"status":"PASS_OPTIN_PUBLIC_U3216_ALL_D16_MODEL",
      "cases":len(pairs),"corpus_sha256":digest,"code_bytes":len(code),
      "caller_ram_start":hex(ENTRY),"caller_ram_end":hex(max(code)),
      "normal_zp_extra":0,"resident_binaries_unchanged":True,
      "native_vice_not_yet_qualified":True,"profiles":{}}
 for p in PROFILES:
  original,api=load_resident(p)
  changed,_=load_resident(p)
  for addr,b in code.items(): changed.mem[addr]=b
  out["profiles"][p]={}
  for op in OPS:
   savings=[]; low=[];eligible=[];high=[];D8=[];zero=[];uniform=[]
   for i,(n,d) in enumerate(pairs):
    before,ok1,a,want=one(original,api[op],n,d)
    after,ok2,b,want2=one(changed,ENTRY,n,d)
    assert ok1 and ok2 and a==b==want==want2,(p,op,i,hex(n),hex(d),a,b,want)
    z=before-after
    savings.append(z)
    if 165<=i<1701: uniform.append(z)
    if d==0:zero.append(z)
    elif d<0x8000:
     low.append(z)
     if d<256:D8.append(z)
     else:eligible.append(z)
    else:high.append(z)
   out["profiles"][p][op]={
    "all":stats(savings),"uniform":stats(uniform),"low_D":stats(low),
    "high_D":stats(high),"eligible_D0100_7FFF":stats(eligible),"D8":stats(D8),"zero":stats(zero),
    "slower_calls":sum(z<0 for z in savings)}
  print(p,out["profiles"][p],flush=True)
 print(json.dumps(out,indent=2))
if __name__=="__main__":main()
