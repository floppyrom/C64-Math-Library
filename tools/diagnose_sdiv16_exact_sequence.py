#!/usr/bin/env python3
from pathlib import Path
import random,re,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build
P="v2_pareto_fast"; N=0xc010; D=0xc014

def mask(bits):return (1<<bits)-1
def edge(bits):
 s=1<<(bits-1);m=mask(bits)
 return list(dict.fromkeys(x&m for x in [0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))
def parse(path):
 out={}
 for l in path.read_text().splitlines():
  m=re.match(r"\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)",l)
  if m:out[m.group(1)]=int(m.group(2),16)
 return out
def load(path,inc):
 b=path.read_bytes();a=b[0]|b[1]<<8;mem=bytearray(65536);mem[a:a+len(b)-2]=b[2:]
 c=CPU(mem);c.d=0;ap=parse(inc);c.call(ap["MATH_INIT"],2_000_000);return c,ap
def wr(mem,a,v,n):
 for i in range(n):mem[a+i]=(v>>(8*i))&255
def cases(name,nb,db,sh,pi=1):
 if name=="MATH_SDIV8": return [(n,d) for n in range(256) for d in range(256)]
 en=edge(nb);ed=edge(db);out=[(n,d) for n in en for d in ed]
 rng=random.Random(0xD1000000+pi*0x10000+nb*0x100+db+sh)
 count=6144 if name=="MATH_SDIV32_32" else 4096
 out += [(rng.randrange(1<<nb),rng.randrange(1<<db)) for _ in range(count)]
 out += [(rng.randrange(1<<nb),0) for _ in range(128)]
 return out
def state(c):return (c.a,c.x,c.y,c.sp,c.c,c.z,c.n,c.v,c.d,c.pc)
def runfamily(b,c,ba,ca,name,nb,db,sh):
 cs=cases(name,nb,db,sh)
 nn=(nb+7)//8;dn=(db+7)//8
 for k,(nr,dr) in enumerate(cs):
  for cpu in (b,c):
   wr(cpu.mem,N,nr,nn);wr(cpu.mem,D,dr,dn)
  b.call(ba[name],4_000_000);c.call(ca[name],4_000_000)
 print("AFTER",name,"states",state(b),state(c),flush=True)
 dif=[a for a in range(65536) if b.mem[a]!=c.mem[a]]
 # Separate the known static candidate code bytes from dynamic state.
 dyn=[a for a in dif if not (0x7a00<=a<=0x7c2a)]
 print("DIFF_COUNTS",name,"all",len(dif),"outside_prefix",len(dyn),flush=True)
 runs=[]
 if dyn:
  st=pr=dyn[0]
  for a in dyn[1:]:
   if a==pr+1:pr=a
   else:runs.append((st,pr));st=pr=a
  runs.append((st,pr))
 for st,en in runs[:40]:
  print("DYN_RANGE",name,hex(st),hex(en),"base",b.mem[st:en+1].hex(),"cand",c.mem[st:en+1].hex(),flush=True)
def main():
 tmp=Path(tempfile.mkdtemp(prefix="diag-seq-"))
 try:
  build(P,ROOT/"relocatable_source"/P/"math_config_reference.inc",tmp)
  b,ba=load(ROOT/P/"resident"/f"math_{P}_game_math.prg",ROOT/P/"resident"/"math_api.inc")
  c,ca=load(tmp/f"math_{P}_source_built.prg",tmp/"math_api.inc")
  pre=[("MATH_SDIV8",8,8,0),("MATH_SDIV16",16,16,0),("MATH_SDIV24",24,24,0),("MATH_SDIV32_16",32,16,0)]
  for spec in pre:runfamily(b,c,ba,ca,*spec)
  # Set first SDIV32_32 edge pair exactly as validator does, but do not call yet.
  for cpu in (b,c):wr(cpu.mem,N,0,4);wr(cpu.mem,D,0,4)
  print("PRE32_STATES",state(b),state(c),flush=True)
  dif=[a for a in range(65536) if b.mem[a]!=c.mem[a] and not (0x7a00<=a<=0x7c2a)]
  print("PRE32_DYNAMIC_DIFFS",len(dif),[(hex(a),hex(b.mem[a]),hex(c.mem[a])) for a in dif[:100]],flush=True)
  for label,cpu,ap in (("BASE",b,ba),("CAND",c,ca)):
   try:
    cy=cpu.call(ap["MATH_SDIV32_32"],4_000_000)
    print(label,"SDIV32_32_RETURN",cy,state(cpu),flush=True)
   except RuntimeError:
    print(label,"SDIV32_32_FAIL",state(cpu),flush=True)
 finally:shutil.rmtree(tmp,ignore_errors=True)
if __name__=="__main__":main()
