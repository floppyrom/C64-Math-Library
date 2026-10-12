#!/usr/bin/env python3
"""Source and current-main 1,705-pair corpus proof for 0-ZP UMOD32 specialist."""
from pathlib import Path
import hashlib,json,sys
from verify import render,MAPS
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler,CPU
from benchmark_unsigned_common_corpus import corpus
NAME="mod_u32_aligned_carry.asm"
SEGMENTS=((0x0600,250,"427f9e9cff0dad83e288f8a723804e1554f62678931f1e810f75e8cb13e56e3a"),(0x2000,225,"820bb0fa526120b72dcdd5ff7259903c0a6bbc7f3f6d1e9949787410346fa27f"))
SOURCE_CASE_SHA="fb175cc99fe3bafeaf7b508ef435579d5bc2d9b8bb56dd9ebcee34ef110a085b"
def check():
 origin=dict(MAPS[0],KERNEL_CODE=0x0600,KERNEL_AUX=0x2000,KERNEL_ADAPTER=0x3000,INPUT_NUM=0x0300,INPUT_DIV=0x0320,OUTPUT_QUOT=0x0540,OUTPUT_REM=0x0560,TEMP_RAM=0x0580)
 original,labels,_=Assembler().assemble(render(NAME,origin))
 assert len(original)==496
 for start,length,sha in SEGMENTS:
  assert hashlib.sha256(bytes(original[i] for i in range(start,start+length))).hexdigest()==sha
 assert bytes(original[i] for i in range(0x3000,0x3015)).hex()=="200006ad20030d21030d22030d2303f00218603860"
 seed,pairs=corpus("MATH_UMOD32_32",32,32,0,1024)
 assert len(pairs)==1705
 assert hashlib.sha256(json.dumps(pairs,separators=(",",":")).encode()).hexdigest()==SOURCE_CASE_SHA
 for m,expected_all,expected_random in [(MAPS[0],476.93782991202346,190.8671875),(MAPS[1],477.1161290322581,191.1181640625)]:
  image,labels,_=Assembler().assemble(render(NAME,m))
  assert len(image)==496
  cpu=CPU(bytearray(65536));cpu.d=0
  for a,b in image.items():cpu.mem[a]=b
  by_kind={};all_cycles=[]
  for idx,(n,d,kind) in enumerate(pairs):
   mem=cpu.mem
   mem[m["INPUT_NUM"]:m["INPUT_NUM"]+4]=n.to_bytes(4,"little")
   mem[m["INPUT_DIV"]:m["INPUT_DIV"]+4]=d.to_bytes(4,"little")
   mem[m["OUTPUT_QUOT"]:m["OUTPUT_QUOT"]+4]=b"\x55"*4
   mem[m["OUTPUT_REM"]:m["OUTPUT_REM"]+4]=b"\x66"*4
   sp=cpu.sp;cpu.c=idx&1
   cycles=cpu.call(labels["FAST_UMOD32_ALIGNED_PUBLIC"],2000000)
   assert int.from_bytes(mem[m["OUTPUT_REM"]:m["OUTPUT_REM"]+4],"little")==(n%d if d else 0)
   assert mem[m["OUTPUT_QUOT"]:m["OUTPUT_QUOT"]+4]==b"\x55"*4
   assert cpu.c==int(d==0) and cpu.sp==sp
   assert mem[m["INPUT_NUM"]:m["INPUT_NUM"]+4]==n.to_bytes(4,"little")
   assert mem[m["INPUT_DIV"]:m["INPUT_DIV"]+4]==d.to_bytes(4,"little")
   by_kind.setdefault(kind,[]).append(cycles);all_cycles.append(cycles)
  full=sum(all_cycles)/len(all_cycles);random_mean=sum(by_kind["random"])/len(by_kind["random"])
  assert abs(full-expected_all)<1e-9,(m["name"],full,expected_all)
  assert abs(random_mean-expected_random)<1e-9,(m["name"],random_mean,expected_random)
  print(NAME,m["name"],"PASS 1705, full",round(full,6),"random",round(random_mean,6),flush=True)
 print("UMOD32 0-ZP ALIGNED SOURCE/CORPUS PASS 3410 calls")
if __name__=="__main__":check()
