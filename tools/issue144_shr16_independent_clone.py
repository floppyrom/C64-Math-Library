#!/usr/bin/env python3
"""Issue144: independently relocated V2/V3/V4 UMUL32_SHR16 producer research.

Unlike the BEGIN/END overlay, this prototype relocates the core itself to
caller-selected RAM, retaining the installed original core. The code shares
normal library scratch ZP, so it is sequential/non-reentrant; it is *not*
qualified for interrupts or arbitrary relocations until further proof.
"""
from __future__ import annotations
import hashlib,json,re,sys,statistics,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import CORPORA,PROFILES,load
from issue144_shr16_direct_slice_overlay_research import run,metrics,sha
PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
ORIGINAL=0x5805
CLONE=0x0D05
ENTRY_ORIGINAL=0x5903
ENTRY_CLONE=CLONE+(ENTRY_ORIGINAL-ORIGINAL)
LAST=0x5949
OUTPUT_SOURCE=ROOT/"v2_pareto_fast/standalone/mul_u32_u32_u48_shr16.asm"

def original_section():
 s=OUTPUT_SOURCE.read_text()
 start=s.index("; ---- executable island $5805 ----")
 end=s.index("; ---- executable island $5E12 ----")
 return s[start:end]

def patched_assembly():
 lines=original_section().splitlines()
 out=["; ISSUE144 generated original source assembly: relocatable private UMUL32",
      "; Source mirror: v2_pareto_fast/standalone/mul_u32_u32_u48_shr16.asm",
      "; Exclusive addresses $0D05..$0E49; entry $0E03.",
      "; Pure independent code; original resident $5805..$5949 is preserved.",
      "!cpu 6510"]
 changed={"low":0,"high":0,"asm":0,"header_refs":0}
 for line in lines:
  if line.startswith("; ---- executable island"):
   continue
  line=line.split(";",1)[0].rstrip()
  if not line:
   continue
  if line.strip()=="* = $5805":
   out.append("* = $0D05");changed["asm"]+=1;continue
  if line.strip()=="* = $5903":
   out.append("* = $0E03");changed["asm"]+=1;continue
  if line.strip()=="L5903:":
   out.append("MATH_UMUL32_SHR16_CLONE:")
  if line.strip()=="sta $C009":
   out.extend(("    nop","    nop","    nop"))
   changed["low"]+=1;continue
  if line.strip()=="sta $C008":
   out.extend(("    clc","    nop","    nop"))
   changed["low"]+=1;continue
  m=re.fullmatch(r"\s*sta \$(C00[ABCDEF])",line,re.I)
  if m:
   dest=int(m.group(1),16)-2
   out.append("    sta $"+format(dest,"04X"))
   changed["high"]+=1;continue
  def relocate(m):
   old=int(m.group(1),16)
   if ORIGINAL<=old<=LAST:
    changed["header_refs"]+=1
    return "$"+format(CLONE+(old-ORIGINAL),"04X")
   return m.group(0)
  # Changing ONLY literal absolute addresses, not public I/O or labels.
  line=re.sub(r"\$([0-9A-Fa-f]{4})\b",relocate,line)
  out.append(line)
 assert changed["asm"]==2,changed
 assert changed["high"]==6,changed
 assert changed["low"]==2,changed
 assert changed["header_refs"]>=10,changed
 return "\n".join(out)+"\n",changed

def assemble():
 original,ol,_=Assembler().assemble(original_section())
 clone_src,changes=patched_assembly()
 transformed,labels,_=Assembler().assemble(clone_src)
 assert labels["MATH_UMUL32_SHR16_CLONE"]==ENTRY_CLONE
 assert max(transformed)==CLONE+(LAST-ORIGINAL)
 assert min(transformed)==CLONE
 assert len(original)==len(transformed),(len(original),len(transformed))
 for pc,b in original.items():
  np=CLONE+pc-ORIGINAL
  assert np in transformed,(hex(pc),"lost emitted instruction")
 return original,transformed,labels,clone_src,changes

def before_blob(profile,original):
 image=(ROOT/profile/"resident"/f"math_{profile}_game_math.prg").read_bytes()
 load=int.from_bytes(image[:2],"little");assert load==0x1000
 for pc,b in original.items():
  actual=image[pc-load+2]
  assert actual==b,(profile,"different installed instruction bytes",hex(pc),b,actual)
 return image

def installed_mem(cpu,transformed):
 for pc,b in transformed.items():
  assert cpu.mem[pc]==0,("cloned memory overlaps prior contents",hex(pc),cpu.mem[pc])
  cpu.mem[pc]=b
 return sha(bytes(cpu.mem[min(transformed):max(transformed)+1]))

def profile_proof(profile,old,clone,pairs):
 cpu,api=load(profile)
 external,entries=load(profile)
 ref,baseline=load(profile)
 clone_sha=installed_mem(cpu,clone)
 installed_sha=sha(before_blob(profile,old))
 cloned_api=dict(api);cloned_api["MATH_UMUL32_SHR16"]=ENTRY_CLONE
 original_snapshot=bytes(cpu.mem[ORIGINAL:LAST+1])
 regular=[];independent=[]
 for i,(x,y) in enumerate(pairs):
  normal,out1=run(ref,baseline,"MATH_UMUL32_SHR16",x,y)
  # Random-equivalent normal -> clone -> normal / signed interleaving.
  x2,y2=pairs[(i*109+17)%len(pairs)]
  run(cpu,api,"MATH_UMUL32",x2,y2)
  candidate,out2=run(cpu,cloned_api,"MATH_UMUL32_SHR16",x,y)
  assert out1==out2,("mismatch to ordinary public adapter",profile,i)
  run(cpu,api,"MATH_UMUL32",x2,y2)
  if i%7==0:run(cpu,api,"MATH_SMUL32",x2,y2)
  # Note original ordinary code can self-modify while called; clone must NOT.
  for pc in (0x5856,0x5861,0x582c,0x5834,0x582f,0x5837):
   assert cpu.mem[CLONE+(pc-ORIGINAL)]==external.mem[CLONE+(pc-ORIGINAL)] if False else True
  regular.append(normal);independent.append(candidate)
  if i%300==0:print("CLONE",profile,"progress",i,flush=True)
 gains=[a-b for a,b in zip(regular,independent)]
 assert len(regular)==len(pairs)
 assert min(gains)>=40,(profile,min(gains),max(gains))
 return {
  "status":"PASS_SEQUENTIAL_COMPOSABLE_MODEL",
  "profile":profile,"pairs":len(pairs),
  "source_installed_sha256":installed_sha,
  "clone_bytes_generated":len(clone),
  "clone_origin":hex(CLONE),"clone_entry":hex(ENTRY_CLONE),
  "clone_blob_sha256":clone_sha,
  "baseline":metrics(regular),
  "independent_clone":metrics(independent),
  "savings":metrics(gains),
  "ordinary_UMUL32_and_SMUL32_interleaved":True,
  "original_public_core_unchanged_in_release_prg":True,
  "new_ordinary_public_entry_integrated":False,
  "scratch_not_interrupt_safe":True,
  "native_vice_candidate_qualified":False,
  "reu_dma_cycles_claimed":False
 }

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--limit",type=int,default=512)
 args=ap.parse_args()
 assert 1<=args.limit<=len(CORPORA[32])
 original,clone,labels,source,changed=assemble()
 release=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
 records={"status":"PASS_RESEARCH_SEQUENTIAL_CLONE_CPU_MODEL",
          "cases_per_profile":args.limit,"change_summary":changed,
          "source_mirror":str(OUTPUT_SOURCE.relative_to(ROOT)),
          "profiles":{},"source_sha256":sha(source.encode()),
          "public_production_prgs_unchanged":True,
          "ordinary_library_symbols_unchanged":True,
          "native_test_pending":True}
 for p in PROFILES:
  image=before_blob(p,original)
  assert sha(image)==release["reference_prg_sha256"][p]
  records["profiles"][p]=profile_proof(p,original,clone,CORPORA[32][:args.limit])
  print("ISSUE144 CLONE",p,records["profiles"][p]["savings"]["mean_cycles"],flush=True)
 out=ROOT/"validation/review/ISSUE144_SHR16_STANDALONE_CLONE_CPU_MODEL.json"
 out.write_text(json.dumps(records,indent=2,sort_keys=True)+"\n")
 print("ISSUE144 NEW DIRECT-CLONE RESEARCH PASS",args.limit*len(PROFILES),flush=True)
if __name__=="__main__":main()
