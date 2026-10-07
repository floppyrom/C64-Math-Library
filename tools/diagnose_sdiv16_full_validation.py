#!/usr/bin/env python3
from pathlib import Path
import random, shutil, sys, tempfile, re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build

PROFILE="v2_pareto_fast"
def mask(bits):return (1<<bits)-1
def edge(bits):
 s=1<<(bits-1);m=mask(bits)
 return list(dict.fromkeys(x&m for x in [0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))
def parse_api(path):
 out={}
 for line in path.read_text().splitlines():
  m=re.match(r"\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)",line)
  if m:out[m.group(1)]=int(m.group(2),16)
 return out
def load(prg,inc):
 b=prg.read_bytes();a=b[0]|b[1]<<8
 mem=bytearray(65536);mem[a:a+len(b)-2]=b[2:]
 c=CPU(mem);c.d=0;api=parse_api(inc);c.call(api["MATH_INIT"],2_000_000)
 return c,api
def wr(mem,a,v,n):
 for i in range(n):mem[a+i]=(v>>(8*i))&255
def main():
 tmp=Path(tempfile.mkdtemp(prefix="diag-sdiv16-"))
 try:
  build(PROFILE,ROOT/"relocatable_source"/PROFILE/"math_config_reference.inc",tmp)
  cpu,api=load(tmp/f"math_{PROFILE}_source_built.prg",tmp/"math_api.inc")
  pi=1
  defs=[
   ("MATH_SDIV8",8,8,8,8,0),("MATH_SDIV16",16,16,16,16,0),
   ("MATH_SDIV24",24,24,24,24,0),("MATH_SDIV32_16",32,16,32,16,0),
   ("MATH_SDIV32_32",32,32,32,32,0),("MATH_SDIV16_SHL8",16,16,24,16,8)]
  for name,nb,db,qb,rb,sh in defs:
   if name=="MATH_SDIV8":
    cases=[(n,d) for n in range(256) for d in range(256)]
   else:
    en=edge(nb);ed=edge(db);cases=[(n,d) for n in en for d in ed]
    rng=random.Random(0xD1000000+pi*0x10000+nb*0x100+db+sh)
    count=6144 if name=="MATH_SDIV32_32" else 4096
    cases += [(rng.randrange(1<<nb),rng.randrange(1<<db)) for _ in range(count)]
    cases += [(rng.randrange(1<<nb),0) for _ in range(128)]
   print("BEGIN",name,"entry",hex(api[name]),"cases",len(cases),flush=True)
   nn=(nb+7)//8;dn=(db+7)//8
   for k,(nr,dr) in enumerate(cases):
    wr(cpu.mem,0xc010,nr,nn);wr(cpu.mem,0xc014,dr,dn)
    try:cpu.call(api[name],4_000_000)
    except RuntimeError as e:
     print("STEP_LIMIT",name,"index",k,"n",hex(nr),"d",hex(dr),"pc",hex(cpu.pc),"sp",hex(cpu.sp),flush=True)
     raise
   print("END",name,flush=True)
 finally:shutil.rmtree(tmp,ignore_errors=True)
if __name__=="__main__":main()
