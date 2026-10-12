#!/usr/bin/env python3
"""Verify relocated standalone NMOS math kernels at 3 disjoint RAM maps."""
from pathlib import Path
import collections,hashlib,random,re,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler,CPU
HERE=Path(__file__).resolve().parent
CASES=(("div_u16_biased.asm",16,False,323,"FAST_UDIV16_BIASED"),("mod_u16_biased_carry.asm",16,True,262,"FAST_UMOD16_PUBLIC"),("div_u32_zptail.asm",32,False,544,"FAST_UDIV32_PUBLIC"))
MAPS=(
{"name":"aligned_8000","KERNEL_CODE":0x8000,"KERNEL_ADAPTER":0x8400,"KERNEL_AUX":0x9000,"INPUT_NUM":0xc010,"INPUT_DIV":0xc014,"OUTPUT_QUOT":0xc018,"OUTPUT_REM":0xc01c,"TEMP_ZP":0x50},
{"name":"unaligned_7123","KERNEL_CODE":0x7123,"KERNEL_ADAPTER":0x7607,"KERNEL_AUX":0x9507,"INPUT_NUM":0xc040,"INPUT_DIV":0xc044,"OUTPUT_QUOT":0xc048,"OUTPUT_REM":0xc04c,"TEMP_ZP":0x60},
{"name":"unaligned_830f","KERNEL_CODE":0x830f,"KERNEL_ADAPTER":0x8800,"KERNEL_AUX":0x9900,"INPUT_NUM":0xc080,"INPUT_DIV":0xc084,"OUTPUT_QUOT":0xc088,"OUTPUT_REM":0xc08c,"TEMP_ZP":0x70})
def render(name,mp):
 s=(HERE/name).read_text()
 for k,v in mp.items():
  if k=="name":continue
  s=re.sub(r"(?m)^"+k+r"\s*=\s*\$[0-9A-Fa-f]+$",k+" = $"+format(v,"04X"),s)
 names=re.findall(r"(?m)^([A-Za-z_][A-Za-z0-9_]*):\s*$",s)
 assert len(names)==len(set(names)),(name,"duplicate labels",collections.Counter(names))
 return s
def pairs(bits,name):
 M=(1<<bits)-1;half=1<<(bits-1)
 edges=list(dict.fromkeys(x&M for x in (0,1,2,3,4,7,15,16,31,63,127,128,255,256,511,1023,half-2,half-1,half,half+1,M-2,M-1,M)))
 rng=random.Random(0x39C0+bits+len(name))
 return [(n,d) for n in edges for d in edges]+[(rng.getrandbits(bits),rng.getrandbits(bits)) for _ in range(512)]+[(rng.getrandbits(bits),0) for _ in range(32)]
def main():
 total=0
 for name,bits,mod_only,expected_length,label in CASES:
  for mp in MAPS:
   source=render(name,mp);image,labels,_=Assembler().assemble(source)
   assert len(image)==expected_length,(name,len(image))
   original=bytes(image[a] for a in sorted(image));cpu=CPU(bytearray(65536));cpu.d=0
   for a,b in image.items():cpu.mem[a]=b
   entry=labels[label];size=bits//8;cycles=[]
   for idx,(n,d) in enumerate(pairs(bits,name)):
    mem=cpu.mem
    mem[mp["INPUT_NUM"]:mp["INPUT_NUM"]+size]=n.to_bytes(size,"little")
    mem[mp["INPUT_DIV"]:mp["INPUT_DIV"]+size]=d.to_bytes(size,"little")
    mem[mp["OUTPUT_QUOT"]:mp["OUTPUT_QUOT"]+size]=b"\x55"*size
    mem[mp["OUTPUT_REM"]:mp["OUTPUT_REM"]+size]=b"\x66"*size
    sp=cpu.sp;cpu.c=idx&1
    cycles.append(cpu.call(entry,2000000))
    q=int.from_bytes(mem[mp["OUTPUT_QUOT"]:mp["OUTPUT_QUOT"]+size],"little")
    r=int.from_bytes(mem[mp["OUTPUT_REM"]:mp["OUTPUT_REM"]+size],"little")
    assert (r,cpu.c)==((n%d if d else 0),int(d==0)),(name,mp["name"],n,d,"R/C",r,cpu.c)
    assert q==(int.from_bytes(b"\x55"*size,"little") if mod_only else (n//d if d else 0)),(name,mp["name"],n,d,"Q",q)
    assert mem[mp["INPUT_NUM"]:mp["INPUT_NUM"]+size]==n.to_bytes(size,"little")
    assert mem[mp["INPUT_DIV"]:mp["INPUT_DIV"]+size]==d.to_bytes(size,"little")
    assert cpu.sp==sp
   assert bytes(cpu.mem[a] for a in sorted(image))==original,(name,"code overwritten")
   total+=len(cycles)
   print(name,mp["name"],"PASS",len(cycles),"avg",round(sum(cycles)/len(cycles),3),flush=True)
 assert total==9657
 print("RELOCATABLE STANDALONE PASS",total)
if __name__=="__main__":main()
