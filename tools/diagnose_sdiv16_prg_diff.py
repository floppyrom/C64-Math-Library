#!/usr/bin/env python3
from pathlib import Path
import shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
from assemble_sources import build
from mini6502 import CPU
P="v2_pareto_fast"
def load(path):
 b=path.read_bytes();a=b[0]|b[1]<<8
 return a,b[2:]
tmp=Path(tempfile.mkdtemp(prefix="diag-diff-"))
try:
 build(P,ROOT/"relocatable_source"/P/"math_config_reference.inc",tmp)
 ba,bb=load(ROOT/P/"resident"/f"math_{P}_game_math.prg")
 ca,cb=load(tmp/f"math_{P}_source_built.prg")
 assert ba==ca and len(bb)==len(cb),(ba,ca,len(bb),len(cb))
 dif=[ba+i for i,(x,y) in enumerate(zip(bb,cb)) if x!=y]
 print("changed_bytes",len(dif))
 runs=[]
 if dif:
  st=pr=dif[0]
  for a in dif[1:]:
   if a==pr+1:pr=a
   else:runs.append((st,pr));st=pr=a
  runs.append((st,pr))
 for st,en in runs:
  off=st-ba
  print(f"RANGE 0x{st:04x}-0x{en:04x} bytes={en-st+1}")
  print(" base",bb[off:off+min(24,en-st+1)].hex())
  print(" cand",cb[off:off+min(24,en-st+1)].hex())
 # Compare initialized machine state too; hidden init-time coupling would show
 # up as extra changes outside the raw signed prefix.
 bm=bytearray(65536);cm=bytearray(65536)
 bm[ba:ba+len(bb)]=bb;cm[ca:ca+len(cb)]=cb
 bcpu=CPU(bm);ccpu=CPU(cm);bcpu.d=0;ccpu.d=0
 bcpu.call(0x3280,2_000_000);ccpu.call(0x3280,2_000_000)
 ids=[a for a in range(65536) if bcpu.mem[a]!=ccpu.mem[a]]
 print("init_changed_bytes",len(ids))
 ir=[]
 if ids:
  st=pr=ids[0]
  for a in ids[1:]:
   if a==pr+1:pr=a
   else:ir.append((st,pr));st=pr=a
  ir.append((st,pr))
 for st,en in ir:
  print(f"INIT_RANGE 0x{st:04x}-0x{en:04x} bytes={en-st+1}")
finally:shutil.rmtree(tmp,ignore_errors=True)
