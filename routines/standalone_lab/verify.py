#!/usr/bin/env python3
"""Deterministic, independent fixed-map 6502 verification for the standalone lab."""
from pathlib import Path
import sys, random, json, hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler, CPU
HERE=Path(__file__).resolve().parent
RECORDS=[
 ("div_u16_biased.asm","MATH_UDIV16",16,2048,0x0610,152.44301942103334,"0cfe5cf7650dbde591f626dbad83b545ff4fc771420005b5270d29298fbb9078",
  [(0x610,323,"0ad0d856a1aa4578e9a8c1e79c0e08e3538dbf12137a4e0e5fea7ec733911263")]),
 ("mod_u16_biased_carry.asm","MATH_UMOD16",16,1024,0x080f,187.0017595307918,"b60581213496cddefb57554035b6cf1c6b46b8655caac240fe0a6791844e56f1",
  [(0x610,244,"3bf770edb2bb085ed0a7ed4cad146c77aa4d767d5dfdfdb269f926c52beab1d2"),
   (0x800,15,"5b13e9f583efbb860d07eed41e48df485e8baa7400937cce66908b001e6e4bc6"),
   (0x80f,3,"406f44343f5c22b4ce81f1d3a2c4714467eca810826ffe88149da7917f6a7e24")]),
 ("div_u32_zptail.asm","MATH_UDIV32_32",32,2048,0x0600,380.6984243312569,"3d0cb9fef736fbf7967246f397c18deaa199d33f9ef6a095fcde9c504a0aeaee",
  [(0x600,325,"4ca3c3ecd21a64f650db19568560a5e64dae2136e05c9b3ed93ffde3342e5847"),
   (0x2000,219,"015a06123c2ad9634a69f9d51faf3b7f24368d7132c52f8db1a1c285187c9ccd")]),
]
def edge(bits):
 mask=(1<<bits)-1;half=1<<(bits-1)
 return list(dict.fromkeys(x&mask for x in [0,1,2,3,4,7,15,16,31,63,127,128,255,256,511,1023,half-2,half-1,half,half+1,mask-2,mask-1,mask]))
def corpus(api,bits,count):
 rng=random.Random(0xC6390000+sum((i+1)*ord(c) for i,c in enumerate(api)))
 pairs=[(n,d,"edges") for n in edge(bits) for d in edge(bits)]
 pairs.extend((rng.randrange(1<<bits),rng.randrange(1<<bits),"random") for _ in range(count))
 pairs.extend((rng.randrange(1<<bits),0,"zero") for _ in range(128))
 for d in (1,2,3,7,15,255,256,65535):
  for n in ((1<<bits)-1,(1<<(bits-1))-1,((1<<bits)-1)//2):
   pairs.append((n,d,"stress"))
 return pairs
def check(item):
 name,api,bits,random_count,entry,expected_mean,corpus_hash,segments=item
 image,_,_=Assembler().assemble((HERE/name).read_text())
 for start,length,sha in segments:
  data=bytes(image[i] for i in range(start,start+length))
  assert hashlib.sha256(data).hexdigest()==sha,(name,"segment",hex(start))
 cpu=CPU(bytearray(65536));cpu.d=0
 for k,v in image.items():cpu.mem[k]=v
 pairs=corpus(api,bits,random_count)
 assert hashlib.sha256(json.dumps(pairs,separators=(",",":")).encode()).hexdigest()==corpus_hash
 cycles=[];size=bits//8
 for n,d,_ in pairs:
  m=cpu.mem
  m[0x300:0x300+size]=n.to_bytes(size,"little")
  m[0x320:0x320+size]=d.to_bytes(size,"little")
  m[0x540:0x544]=bytes([0x55])*4
  m[0x560:0x564]=bytes([0x66])*4
  sp=cpu.sp
  cycles.append(cpu.call(entry,2_000_000))
  q=int.from_bytes(m[0x540:0x540+size],"little")
  r=int.from_bytes(m[0x560:0x560+size],"little")
  assert (r,cpu.c)==(n%d if d else 0,int(d==0)),(name,hex(n),hex(d),"R,C",r,cpu.c)
  if "UMOD" in api:assert q==0x5555,(name,"Q modified",q)
  else:assert q==(n//d if d else 0),(name,hex(n),hex(d),"Q",q)
  assert m[0x300:0x300+size]==n.to_bytes(size,"little")
  assert m[0x320:0x320+size]==d.to_bytes(size,"little")
  assert cpu.sp==sp
 mean=sum(cycles)/len(cycles)
 assert abs(mean-expected_mean)<1e-9,(name,mean,expected_mean)
 print(f"{name}: PASS {len(cycles)} Q/R/C/N/D/stack calls; {mean:.6f} cycles")
 return len(cycles)
if __name__=="__main__":
 total=sum(check(r) for r in RECORDS)
 assert total==7163
 print("STANDALONE LAB PASS",total,"calls")
