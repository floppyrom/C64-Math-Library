#!/usr/bin/env python3
"""Issue144 unrestricted signed 32x32 SHR16 exclusive direct-slice source/CPU proof.

Executable instruction sites come only from the public shipped signed full
multiply standalone source mirrors. No private optimizer code. This overlay
modifies the shared signed full producer; SMUL32 is INVALID until END.
"""
from __future__ import annotations
import argparse,hashlib,json,re,statistics,sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from benchmark_multiply_refresh import CORPORA,load
from issue144_shr16_direct_slice_overlay_research import run
from mini6502 import Assembler
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
DIRECTORY="optional/issue144_signed_shr16_exclusive"
def sha(b):return hashlib.sha256(b).hexdigest()
def metrics(a):
 s=sorted(a)
 return {"mean_cycles":sum(a)/len(a),"median_cycles":statistics.median(a),
  "p95_cycles":s[int(.95*(len(s)-1))],"min_cycles":s[0],"max_cycles":s[-1],
  "cycle_vector_sha256":sha(b"".join(int(x).to_bytes(4,"little",signed=True) for x in a))}
def patch_map(profile):
 src=(ROOT/profile/"standalone/mul_s32_s32_s64.asm").read_text()
 lines=re.findall(r"(?m)^\s*sta \$C00([89A-F])\s+; @([0-9A-F]{4}) 8D (?:[0-9A-F]{2}) C0",src)
 assert len(lines)==32,(profile,len(lines))
 p={}
 for digit,location in lines:
  pos=int(location,16)
  if digit in ("8","9"):p[pos]=bytes((0xEA,0xEA,0xEA))
  else:p[pos+1]=bytes((int(digit,16)-2,))
 p[0xC575 if profile in ("v1_balanced","v5_hybrid_lowzp") else 0xC50C]=bytes((0x4C,))
 return p
def generate(profile):
 cpu,_=load(profile)
 changes=patch_map(profile)
 adapter=0xC575 if profile in ("v1_balanced","v5_hybrid_lowzp") else 0xC50C
 assert bytes(cpu.mem[adapter:adapter+3])==b"\x20\x40\x3C"
 assert bytes(cpu.mem[0x5E15:0x5E18])==bytes((0x4C,adapter&255,adapter>>8))
 before,after={},{}
 for addr,data in changes.items():
  original=bytes(cpu.mem[addr:addr+len(data)])
  if len(data)==3:assert original[0]==0x8D
  elif addr in (0xC50C,0xC575):assert original==b"\x20"
  else:assert cpu.mem[addr-1]==0x8D and cpu.mem[addr+1]==0xC0
  for i,v in enumerate(original):before[addr+i]=v
  for i,v in enumerate(data):after[addr+i]=v
 assert set(before)==set(after) and len(before)==49
 source=[
  "; C64ML Issue144 signed SHR16 direct-slice EXCLUSIVE overlay: "+profile,
  "; Exact stock resident required; 49 shared producer bytes modified.",
  "; BEGIN/END must not be interrupted by code calling signed math.",
  "; NO ordinary SMUL32, READY or overlapping IRQ/NMI math while enabled.",
  "; Requires MATH_INIT; no additional normal zero page or data tables.",
  "; User must verify example $0900 installer RAM actually available.",
  "; Overlay conflicts with any other optional $0900 batch installer.",
  "; Normal SHR16 public address $5E15 unchanged, all signed inputs valid.",
  "!cpu 6510","* = $0900","","SMUL32_SHR16_EXCLUSIVE_BEGIN:"]
 def emit(mapping):
  groups=defaultdict(list)
  for pos,v in mapping.items():groups[v].append(pos)
  for v,places in sorted(groups.items()):
   source.append("    lda #$%02X"%v)
   for pc in sorted(places):source.append("    sta $%04X"%pc)
  source.append("    rts")
 emit(after)
 source+=["","SMUL32_SHR16_EXCLUSIVE_END:"]
 emit(before);source.append("")
 asm="\n".join(source)
 code,labels,_=Assembler().assemble(asm)
 assert len(code)==334 and min(code)==0x900 and max(code)<0xB00
 assert set(code).isdisjoint(set(before))
 return asm,code,labels,before,after
def store(filename,value):
 dest=ROOT/filename;dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(value)
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--limit",type=int,default=2409)
 args=ap.parse_args()
 assert 1<=args.limit<=len(CORPORA[32])
 pairs=CORPORA[32][:args.limit]
 model={"status":"PASS_ALL_SIGNED_DOMAIN_EXCLUSIVE_ONLY",
  "profiles":{},"pairs_per_profile":len(pairs),
  "normal_resident_images_unchanged":True,"no_private_optisearch":True,
  "mixed_SMUL32_calls_while_enabled_safe":False}
 assembler={"status":"PASS_ASSEMBLED_BEGIN_END_AND_FULL_SIGNED_RESTORATION",
  "profiles":{},"normal_resident_images_unchanged":True}
 inventory={}
 for p in PROFILES:
  src,program,labels,old,new=generate(p)
  store(DIRECTORY+"/"+p+".asm",src)
  inventory[p]={"source_sha256":sha(src.encode()),"installer_code_bytes":len(program),
    "changed_resident_bytes":len(old),"entry_begin":hex(labels["SMUL32_SHR16_EXCLUSIVE_BEGIN"]),
    "entry_end":hex(labels["SMUL32_SHR16_EXCLUSIVE_END"])}
  stock,api=load(p);candidate,api2=load(p);assert api==api2
  for addr,v in program.items():
   assert candidate.mem[addr]==0,(p,hex(addr),"installer RAM not free")
   candidate.mem[addr]=v
  assert all(candidate.mem[addr]==v for addr,v in old.items())
  sp=candidate.sp
  begin=candidate.call(labels["SMUL32_SHR16_EXCLUSIVE_BEGIN"],200000)
  assert candidate.sp==sp and all(candidate.mem[addr]==v for addr,v in new.items())
  old_cycles=[];new_cycles=[]
  for x,y in pairs:
   ca,oa=run(stock,api,"MATH_SMUL32_SHR16",x,y)
   cb,ob=run(candidate,api,"MATH_SMUL32_SHR16",x,y)
   assert oa==ob,(p,x,y)
   old_cycles.append(ca);new_cycles.append(cb)
  end=candidate.call(labels["SMUL32_SHR16_EXCLUSIVE_END"],200000)
  assert candidate.sp==sp and all(candidate.mem[addr]==v for addr,v in old.items())
  for x,y in pairs[:min(len(pairs),120)]:
   run(candidate,api,"MATH_SMUL32",x,y)
   run(candidate,api,"MATH_SMUL32_SHR16",x,y)
  savings=[a-b for a,b in zip(old_cycles,new_cycles)]
  assert min(savings)==max(savings)==53
  assert (begin,end)==(218,224),(p,begin,end)
  model["profiles"][p]={"status":"PASS_ALL_SIGNED_OUTPUT_CARRY_INPUTS_STACK",
    "baseline":metrics(old_cycles),"candidate":metrics(new_cycles),
    "paired_savings":metrics(savings),"source_sha256":sha(src.encode())}
  assembler["profiles"][p]={"status":"PASS_6510_BEGIN_END_RESTORED_SMUL32",
    "begin_cycles":begin,"end_cycles":end,"public_signed_full_after_restore":True,
    "code_bytes":len(program),"patched_bytes":len(old),
    "native_cycle_timing_measured":False}
  print("SIGNED SHR16 EXCLUSIVE",p,"saved",53,"setup",begin+end,"PASS",flush=True)
 store(DIRECTORY+"/overlay_inventory.json",json.dumps(inventory,indent=2,sort_keys=True)+"\n")
 store("validation/review/ISSUE144_SIGNED_SHR16_FULL_EXCLUSIVE_MODEL.json",json.dumps(model,indent=2,sort_keys=True)+"\n")
 store("validation/review/ISSUE144_SIGNED_SHR16_FULL_EXCLUSIVE_INSTALLER.json",json.dumps(assembler,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 SIGNED EXCLUSIVE MODEL PASS",len(pairs)*len(PROFILES))
if __name__=="__main__":main()
