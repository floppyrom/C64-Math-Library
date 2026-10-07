#!/usr/bin/env python3
from pathlib import Path
import re, shutil, sys, tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from assemble_sources import build
P="v2_pareto_fast";N=0xc010;D=0xc014

def api(path):
 out={}
 for l in path.read_text().splitlines():
  m=re.match(r"\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)",l)
  if m:out[m.group(1)]=int(m.group(2),16)
 return out
def load(tmp):
 b=(tmp/f"math_{P}_source_built.prg").read_bytes();a=b[0]|b[1]<<8
 mem=bytearray(65536);mem[a:a+len(b)-2]=b[2:]
 c=CPU(mem);c.d=0;ap=api(tmp/"math_api.inc");c.call(ap["MATH_INIT"],2_000_000);return c,ap
def wr(mem,a,v,n):
 for i in range(n):mem[a+i]=(v>>(8*i))&255
def call(c,ap,name,n,d,nb,db):
 wr(c.mem,N,n,(nb+7)//8);wr(c.mem,D,d,(db+7)//8)
 try:
  cy=c.call(ap[name],4_000_000);print("OK",name,hex(n),hex(d),"cy",cy,"pc",hex(c.pc),"sp",hex(c.sp),flush=True);return True
 except RuntimeError:
  print("FAIL",name,hex(n),hex(d),"pc",hex(c.pc),"sp",hex(c.sp),flush=True);return False
def trial(tmp,label,pre):
 c,ap=load(tmp);print("TRIAL",label,flush=True)
 for x in pre:
  if not call(c,ap,*x):return
 call(c,ap,"MATH_SDIV32_32",0,0,32,32)
def main():
 tmp=Path(tempfile.mkdtemp(prefix="diag-state-"))
 try:
  build(P,ROOT/"relocatable_source"/P/"math_config_reference.inc",tmp)
  trial(tmp,"fresh",[])
  tests=[
   ("after_sdiv8",[("MATH_SDIV8",7,3,8,8)]),
   ("after_sdiv16_pp_q1",[("MATH_SDIV16",7,4,16,16)]),
   ("after_sdiv16_pp_q0",[("MATH_SDIV16",3,7,16,16)]),
   ("after_sdiv16_pp_qge2",[("MATH_SDIV16",100,7,16,16)]),
   ("after_sdiv24",[("MATH_SDIV24",100,7,24,24)]),
   ("after_sdiv32_16",[("MATH_SDIV32_16",100,7,32,16)]),
   ("full_prefix",[("MATH_SDIV8",7,3,8,8),("MATH_SDIV16",7,4,16,16),("MATH_SDIV24",100,7,24,24),("MATH_SDIV32_16",100,7,32,16)]),
  ]
  for label,pre in tests:trial(tmp,label,pre)
 finally:shutil.rmtree(tmp,ignore_errors=True)
if __name__=="__main__":main()
