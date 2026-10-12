#!/usr/bin/env python3
"""Reassemble the zero-ZP aligned UDIV32 donor and verify frozen public operands."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,sys
from verify import MAPS,render
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler,CPU
from benchmark_unsigned_common_corpus import corpus

NAME="div_u32_aligned_nozp.asm"
CASE_SHA="3d0cb9fef736fbf7967246f397c18deaa199d33f9ef6a095fcde9c504a0aeaee"
SEGMENTS=((0x600,325,"4ca3c3ecd21a64f650db19568560a5e64dae2136e05c9b3ed93ffde3342e5847"),
          (0x2000,251,"3c867e9d1f97c5c9f11de2cbefd90444e3d0bff2ed787e92d4f3fbecc2d82d93"))
MEANS=((408.0117259069256,196.8896484375),
       (408.22425796995236,197.14990234375),
       (408.0117259069256,196.8896484375))

def run():
 original_map=dict(MAPS[0],KERNEL_CODE=0x600,KERNEL_AUX=0x2000,
                   INPUT_NUM=0x300,INPUT_DIV=0x320,OUTPUT_QUOT=0x540,
                   OUTPUT_REM=0x560,TEMP_RAM=0x580)
 original,_,_=Assembler().assemble(render(NAME,original_map))
 assert len(original)==576
 for start,length,checksum in SEGMENTS:
  actual=hashlib.sha256(bytes(original[x] for x in range(start,start+length))).hexdigest()
  assert actual==checksum,(start,actual,checksum)
 _,pairs=corpus("MATH_UDIV32_32",32,32,0,2048)
 assert len(pairs)==2729
 assert hashlib.sha256(json.dumps(pairs,separators=(",",":")).encode()).hexdigest()==CASE_SHA
 for cfg,(want_full,want_random) in zip(MAPS,MEANS):
  image,labels,_=Assembler().assemble(render(NAME,cfg))
  assert len(image)==576
  cpu=CPU(bytearray(65536));cpu.d=0
  for addr,byte in image.items():cpu.mem[addr]=byte
  frozen=bytes(cpu.mem[k] for k in sorted(image))
  by_kind=defaultdict(list)
  for i,(n,d,kind) in enumerate(pairs):
   mem=cpu.mem
   mem[cfg["INPUT_NUM"]:cfg["INPUT_NUM"]+4]=n.to_bytes(4,"little")
   mem[cfg["INPUT_DIV"]:cfg["INPUT_DIV"]+4]=d.to_bytes(4,"little")
   mem[cfg["OUTPUT_QUOT"]:cfg["OUTPUT_QUOT"]+4]=b"\x55"*4
   mem[cfg["OUTPUT_REM"]:cfg["OUTPUT_REM"]+4]=b"\x66"*4
   cpu.c=i&1;sp=cpu.sp
   cycles=cpu.call(labels["FAST_UDIV32_PUBLIC"],2_000_000)
   q=int.from_bytes(mem[cfg["OUTPUT_QUOT"]:cfg["OUTPUT_QUOT"]+4],"little")
   r=int.from_bytes(mem[cfg["OUTPUT_REM"]:cfg["OUTPUT_REM"]+4],"little")
   expected=(n//d if d else 0,n%d if d else 0,int(d==0))
   assert (q,r,cpu.c)==expected,(cfg["name"],hex(n),hex(d),(q,r,cpu.c),expected)
   assert mem[cfg["INPUT_NUM"]:cfg["INPUT_NUM"]+4]==n.to_bytes(4,"little")
   assert mem[cfg["INPUT_DIV"]:cfg["INPUT_DIV"]+4]==d.to_bytes(4,"little")
   assert cpu.sp==sp
   by_kind[kind].append(cycles)
  assert bytes(cpu.mem[k] for k in sorted(image))==frozen
  average=sum(sum(v) for v in by_kind.values())/len(pairs)
  random_avg=sum(by_kind["random"])/len(by_kind["random"])
  assert abs(average-want_full)<1e-9,(cfg["name"],average,want_full)
  assert abs(random_avg-want_random)<1e-9,(cfg["name"],random_avg,want_random)
  print(NAME,cfg["name"],"PASS",len(pairs),
        f"overall={average:.6f}",f"random={random_avg:.6f}",flush=True)
 print("ZERO-ZP UDIV32 ALIGNED PASS: 8187 source-executed calls")
if __name__=="__main__":run()
