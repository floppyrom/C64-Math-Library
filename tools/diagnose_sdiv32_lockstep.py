#!/usr/bin/env python3
from pathlib import Path
import re,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build
P="v2_pareto_fast";SENT=0xff00

class TraceCPU(CPU):
    def __post_init__(self):
        super().__post_init__();self.reads=[];self.writes=[]
    def rd(self,a):
        v=super().rd(a);self.reads.append((a&0xffff,v));return v
    def wr(self,a,v):
        self.writes.append((a&0xffff,v&255));return super().wr(a,v)
def parse(path):
 out={}
 for l in path.read_text().splitlines():
  m=re.match(r"\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)",l)
  if m:out[m.group(1)]=int(m.group(2),16)
 return out
def load(path,inc):
 b=path.read_bytes();a=b[0]|b[1]<<8;mem=bytearray(65536);mem[a:a+len(b)-2]=b[2:]
 c=TraceCPU(mem);c.d=0;api=parse(inc);c.call(api["MATH_INIT"],2_000_000);c.reads=[];c.writes=[];return c,api
def prep(c,entry):
 for a in range(0xc010,0xc018):c.mem[a]=0
 ret=(SENT-1)&0xffff;c.push(ret>>8);c.push(ret&255);c.pc=entry;c.reads=[];c.writes=[]
def state(c):
 return (c.pc,c.a,c.x,c.y,c.sp,c.c,c.z,c.n,c.v,c.d)
def main():
 tmp=Path(tempfile.mkdtemp(prefix="lock-sdiv32-"))
 try:
  build(P,ROOT/"relocatable_source"/P/"math_config_reference.inc",tmp)
  b,ba=load(ROOT/P/"resident"/f"math_{P}_game_math.prg",ROOT/P/"resident"/"math_api.inc")
  c,ca=load(tmp/f"math_{P}_source_built.prg",tmp/"math_api.inc")
  assert ba["MATH_SDIV32_32"]==ca["MATH_SDIV32_32"]
  prep(b,ba["MATH_SDIV32_32"]);prep(c,ca["MATH_SDIV32_32"])
  print("ENTRY",hex(b.pc),flush=True)
  for i in range(200000):
   if state(b)!=state(c):
    print("PRE_DIVERGENCE",i,state(b),state(c));return
   pc=b.pc
   b.reads=[];b.writes=[];c.reads=[];c.writes=[]
   bo=b.step();co=c.step()
   if state(b)!=state(c) or bo!=co or b.writes!=c.writes:
    print("DIVERGENCE_STEP",i,"pc",hex(pc),"opcode",hex(bo),hex(co),flush=True)
    print("BASE_STATE",state(b),"CAND_STATE",state(c),flush=True)
    print("BASE_READS",[(hex(a),hex(v)) for a,v in b.reads],flush=True)
    print("CAND_READS",[(hex(a),hex(v)) for a,v in c.reads],flush=True)
    print("BASE_WRITES",[(hex(a),hex(v)) for a,v in b.writes],flush=True)
    print("CAND_WRITES",[(hex(a),hex(v)) for a,v in c.writes],flush=True)
    addrs=sorted(set(a for a,_ in b.reads+c.reads))
    diff=[(a,b.mem[a],c.mem[a]) for a in addrs if b.mem[a]!=c.mem[a]]
    print("READ_VALUE_DIFFS",[(hex(a),hex(x),hex(y)) for a,x,y in diff],flush=True)
    return
   if b.pc==SENT or c.pc==SENT:
    print("RETURN",i,state(b),state(c));return
  print("NO_DIVERGENCE_WITHIN_LIMIT")
 finally:shutil.rmtree(tmp,ignore_errors=True)
if __name__=="__main__":main()
