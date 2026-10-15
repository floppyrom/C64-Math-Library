#!/usr/bin/env python3
"""Issue144: independent all-sign 32x32 SHR16 cloned source, V1–V5.

Relocates the nine/ten live signed producer code islands into caller RAM,
including all assembler labels AND SMC absolute operands. Original normal
signed/unsigned 32x32 producers remain untouched. Fixed-point output is
emitted directly from the independent producer, no six-byte copy. Sequential
mixed-call safe, NOT IRQ/NMI reentrant because it shares resident ZP scratch.
"""
from __future__ import annotations
import argparse,hashlib,json,re,statistics,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import CORPORA,load
from issue144_shr16_direct_slice_overlay_research import run
from validate_unsigned_division import PROFILES

SOURCE_DIR="optional/issue144_signed_shr16_independent"
MODEL="validation/review/ISSUE144_SIGNED_SHR16_INDEPENDENT_MODEL.json"
def sha(b):return hashlib.sha256(b).hexdigest()
def metric(values):
 a=list(values);v=sorted(a)
 return {"mean_cycles":sum(a)/len(a),"median_cycles":statistics.median(a),
         "p95_cycles":v[int(.95*(len(v)-1))],"min_cycles":v[0],
         "max_cycles":v[-1],
         "cycle_vector_sha256":sha(b"".join(int(x).to_bytes(4,"little",signed=True) for x in a))}

def make_source(profile):
 donor=(R/profile/"standalone/mul_s32_s32_s64.asm").read_text()
 orig,_,_=Assembler().assemble(donor)
 starts=[int(t,16) for t in re.findall(r"^\* = \$([0-9A-F]{4})",donor,re.M)]
 ends=[max(i for i in orig if i>=s and (n==len(starts)-1 or i<starts[n+1]))
       for n,s in enumerate(starts)]
 next_addr=0x0800
 islands=[]
 for first,last in zip(starts,ends):
  next_addr=(next_addr+15)&~15
  assert next_addr+last-first<0x1000,("insufficient 2KB low RAM",profile)
  islands.append((first,last,next_addr))
  next_addr+=last-first+1
 def move(addr):
  for first,last,new in islands:
   if first<=addr<=last+1:return new+addr-first
  return addr
 lines=[];discarded=shifted=0
 for line in donor.splitlines():
  org=re.match(r"^\* = \$([0-9A-F]{4})",line)
  if org:
   lines.append("* = $%04X"%move(int(org.group(1),16)));continue
  if "; @" in line:
   ins=line.split(";")[0]
   # Every absolute store/operand referring to an included executable island
   # must move with it. Branches and symbolic JMPs auto-reassemble from labels.
   ins=re.sub(r"(?<!#)\$([0-9A-Fa-f]{4})",
     lambda x:"$%04X"%move(int(x.group(1),16)),ins)
   if re.search(r"\bsta \$C00[89]\b",ins):
    ins=re.sub(r"sta \$C00[89]","nop\n    nop\n    nop",ins)
    discarded+=1
   else:
    before=ins
    ins=re.sub(r"\bsta \$C00([A-F])\b",
      lambda x:"sta $C00%X"%(int(x.group(1),16)-2),ins)
    if ins!=before:shifted+=1
   lines.append(ins.rstrip())
  else:lines.append(line)
 assert (discarded,shifted)==(8,24),(profile,discarded,shifted)
 source="\n".join(lines)+"\n"
 code,_,_=Assembler().assemble(source)
 assert len(code)==len(orig)
 assert all(move(pc) in code for pc in orig)
 assert min(code)>=0x0800 and max(code)<0x0E00
 entry=move(0x3C40)
 assert entry in code
 return source,code,entry,islands,sha(donor.encode())

def check(profile,pairs,write):
 src,code,entry,islands,donor_sha=make_source(profile)
 baseline,api=load(profile)
 optimized,newapi=load(profile)
 assert api==newapi and optimized.mem[0x5E15]==0x4C
 saved=bytes(optimized.mem[0x5E15:0x5E18])
 before=bytes(optimized.mem[0x3C40:0x3C70])
 for pc,val in code.items():
  assert optimized.mem[pc]==0,(profile,hex(pc),"caller-owned RAM occupied")
  optimized.mem[pc]=val
 optimized.mem[0x5E16:0x5E18]=entry.to_bytes(2,"little")
 old=[];new=[]
 for i,(x,y) in enumerate(pairs):
  a,ab=run(baseline,api,"MATH_SMUL32_SHR16",x,y)
  b,bb=run(optimized,api,"MATH_SMUL32_SHR16",x,y)
  assert ab==bb,(profile,i,hex(x),hex(y))
  old.append(a);new.append(b)
  # Interleave both normal public 32-bit producers on the same machines.
  if i%17==0 or i%23==0:
   u,v=pairs[(i*109+13)%len(pairs)]
   for cpu in (baseline,optimized):
    if i%17==0:run(cpu,api,"MATH_SMUL32",u,v)
    if i%23==0:run(cpu,api,"MATH_UMUL32",u,v)
   assert bytes(optimized.mem[0x3C40:0x3C70])==before
 optimized.mem[0x5E15:0x5E18]=saved
 for x,y in pairs[:min(100,len(pairs))]:
  run(optimized,api,"MATH_SMUL32_SHR16",x,y)
  run(optimized,api,"MATH_SMUL32",x,y)
 gains=[a-b for a,b in zip(old,new)]
 assert min(gains)>0
 if write:
  path=R/SOURCE_DIR/(profile+".asm")
  path.parent.mkdir(parents=True,exist_ok=True)
  path.write_text(src)
 result={"status":"PASS_PUBLIC_ABI_MIXED_SIGNED_UNSIGNED_NORMAL_CALLS",
         "cases":len(pairs),"baseline":metric(old),"independent":metric(new),
         "paired_savings":metric(gains),"code_bytes":len(code),
         "code_range":[hex(min(code)),hex(max(code))],
         "clone_entry":hex(entry),"source_sha256":sha(src.encode()),
         "donor_public_source_sha256":donor_sha,
         "relocated_islands":[[hex(x) for x in row] for row in islands],
         "ordinary_32bit_core_unchanged":True,
         "shared_normal_ZP_nonreentrant":True,"source_fully_relocated":True}
 print("INDEPENDENT MIXED SIGNED",profile,len(pairs),round(result["paired_savings"]["mean_cycles"],3),"PASS",flush=True)
 return result

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--limit",type=int,default=2409)
 ap.add_argument("--profile",choices=list(PROFILES)+["all"],default="all")
 ap.add_argument("--write",action="store_true")
 args=ap.parse_args()
 assert 1<=args.limit<=len(CORPORA[32])
 pairs=CORPORA[32][:args.limit]
 data={"status":"PASS_ALL_FIVE_PUBLIC_SEQUENTIAL_MIXED_SIGNED_SHR16",
       "profiles":{},"pairs_per_profile":len(pairs),
       "corpus_sha256":sha(b"".join(x.to_bytes(4,"little")+y.to_bytes(4,"little") for x,y in pairs)),
       "stock_PRGs_REU_unchanged":True,"normal_ZP_growth":0,
       "IRQ_NMI_reentrant":False,"native_VICE_cycles_measured":False}
 for profile in PROFILES if args.profile=="all" else (args.profile,):
  data["profiles"][profile]=check(profile,pairs,args.write)
 if args.write:
  out=R/MODEL
  out.parent.mkdir(parents=True,exist_ok=True)
  out.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 INDEPENDENT SIGNED SHR16 MODEL PASS",len(pairs)*len(data["profiles"]))
if __name__=="__main__":main()
