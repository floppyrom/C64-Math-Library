#!/usr/bin/env python3
from pathlib import Path
import shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
from assemble_sources import build
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
finally:shutil.rmtree(tmp,ignore_errors=True)
