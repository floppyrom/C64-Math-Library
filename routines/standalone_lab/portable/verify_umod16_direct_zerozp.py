#!/usr/bin/env python3
"""Source-backed 0-ZP UMOD16 direct-chain: three relocations, identical-input corpus."""
from pathlib import Path
import sys,re,hashlib,json,random
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[2]/"tools"))
from mini6502 import Assembler,CPU
SRC=(P/"mod_u16_direct_zerozp.asm").read_text()
MAPS=[
 ("aligned_8000",0x8000,0x8400,0x8800,0xc010,209.86803519061584),
 ("unaligned_7123",0x7123,0x752f,0x7955,0x3900,209.9208211143695),
 ("unaligned_830f",0x830f,0x8755,0x8b15,0x3d40,209.86744868035192)]
E=[0,1,2,3,4,7,15,16,31,63,127,128,255,256,511,1023,32766,32767,32768,32769,65533,65534,65535]
def operands():
 name="MATH_UMOD16";rng=random.Random(0xc6390000+sum((i+1)*ord(c) for i,c in enumerate(name)))
 cases=[(n,d,"edges") for n in E for d in E]
 cases.extend((rng.randrange(65536),rng.randrange(65536),"random") for _ in range(1024))
 cases.extend((rng.randrange(65536),0,"zero") for _ in range(128))
 for d in (1,2,3,7,15,255,256,65535):
  for n in (65535,32767,32767):cases.append((n,d,"stress"))
 assert len(cases)==1705
 assert hashlib.sha256(json.dumps(cases,separators=(",",":")).encode()).hexdigest()=="b60581213496cddefb57554035b6cf1c6b46b8655caac240fe0a6791844e56f1"
 return cases
def assemble(mp):
 _,code,table,adapter,buf,_=mp
 mem={"KERNEL_CODE":code,"KERNEL_TABLE":table,"KERNEL_ADAPTER":adapter,"INPUT_NUM":buf,"INPUT_DIV":buf+4,"OUTPUT_QUOT":buf+8,"OUTPUT_REM":buf+12,"TEMP_RAM":buf+16}
 s=SRC
 for k,v in mem.items():
  s,n=re.subn(r"(?m)^"+k+r"\s*=\s*\$[0-9A-Fa-f]+$",k+" = $"+format(v,"04X"),s)
  assert n==1,k
 image,labels,_=Assembler().assemble(s)
 assert len(image)==976
 return image,labels,mem
def main():
 cases=operands()
 for spec in MAPS:
  image,labels,addr=assemble(spec);cpu=CPU(bytearray(65536));cpu.d=0
  for a,b in image.items():cpu.mem[a]=b
  sorted_codes=sorted(image);before=bytes(cpu.mem[a] for a in sorted_codes);cycles=[]
  for i,(n,d,kind) in enumerate(cases):
   for key,v in (("INPUT_NUM",n),("INPUT_DIV",d),("OUTPUT_QUOT",0x5555),("OUTPUT_REM",0x6666)):
    cpu.mem[addr[key]:addr[key]+2]=v.to_bytes(2,"little")
   sp=cpu.sp;cpu.c=i&1
   cycles.append(cpu.call(labels["FAST_UMOD16_DIRECT_PUBLIC"],2_000_000))
   def rd(k):return int.from_bytes(cpu.mem[addr[k]:addr[k]+2],"little")
   assert (rd("OUTPUT_REM"),cpu.c,rd("OUTPUT_QUOT"),rd("INPUT_NUM"),rd("INPUT_DIV"),cpu.sp)==(n%d if d else 0,int(d==0),0x5555,n,d,sp),(spec[0],hex(n),hex(d))
  assert bytes(cpu.mem[a] for a in sorted_codes)==before
  mean=sum(cycles)/len(cycles)
  assert abs(mean-spec[5])<1e-6,(spec[0],mean,spec[5])
  print(spec[0],"PASS",len(cycles),"mean",round(mean,6),flush=True)
 print("0-ZP UMOD16 DIRECT PASS",len(cases)*len(MAPS),"source-executed calls")
if __name__=="__main__":main()
