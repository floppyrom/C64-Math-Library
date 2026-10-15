#!/usr/bin/env python3
"""Issue144 D: V2 source-backed relocatable SEEK16_INIT k0=1 optimization audit.

Only the original INIT executable island is copied from an auditable public
mirror to separately reserved application RAM; foreign byte at $19F0 and the
initialized $1A00 table are never overwritten. The old shared helper/ZP
are retained. Not a standalone, general-profile or default integration.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,re,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from benchmark_seek_profiles import load,corpus
P="v2_pareto_fast";SOURCE=ROOT/P/"standalone/seek_u16_u8_init.asm"
NEW=0x0D00;PUBLIC=0x5E48
def assemble(mode):
 s=SOURCE.read_text()
 i=s.index("; ---- executable island $18E2 ----")
 j=s.index("; ---- executable island $3D23 ----")
 segment=s[i:j]
 original={x.upper() for x in re.findall(r"(?m)^\s*(L[0-9A-Fa-f]{4}):",segment)}
 assert "L1981" in original
 segment=re.sub(r"(?<!\w)L([0-9A-Fa-f]{4})\b",
   lambda m:m.group(0) if m.group(0).upper() in original else "$"+m.group(1),segment)
 segment=segment.replace("* = $18E2","* = $0D00")
 needle="    ldy $9158,x                        ; @1989 BC 58 91\n    beq L1994                          ; @198C F0 06\n"
 assert needle in segment
 if mode=="k1":
  fast="""    ldy $9158,x
    beq L1994
    cpy #$01
    bne L198E
    lda $61
    bne k1fast
    lda $62
    cmp $60
    bcs L198E
k1fast:
    lda $62
    sta $63
    jmp L1994
"""
  segment=segment.replace(needle,fast)
 blob,labels,_=Assembler().assemble("!cpu 6510\n"+segment)
 assert min(blob)==NEW and max(blob)<0x1000
 return blob,labels,"!cpu 6510\n"+segment

def transfer(cpu,code):
 for addr,b in code.items():
  assert cpu.mem[addr]==0,(hex(addr),cpu.mem[addr])
  cpu.mem[addr]=b
 assert cpu.mem[PUBLIC]==0x4c
 cpu.mem[PUBLIC+1:PUBLIC+3]=NEW.to_bytes(2,"little")

def main():
 stock,_,_=assemble("baseline");faster,labels,source=assemble("k1")
 assert len(stock)==270 and len(faster)==291 and max(faster)<=0x0E22
 a,api=load(P);b,_=load(P)
 assert api["MATH_SEEK16_POS_XL"]==0x90e8
 transfer(b,faster)
 original19f0=bytes(a.mem[0x19F0:0x19F1]);original1a00=bytes(a.mem[0x1A00:0x1B00])
 assert bytes(b.mem[0x19F0:0x19F1])==original19f0
 assert bytes(b.mem[0x1A00:0x1B00])==original1a00
 rng=random.Random(0x1445E16)
 tests=[]
 for move in corpus(320)[:50]:
  for speed in (0x0100,0x0180,0x0200,0,0x0300,0x8100):
   tests.append((move,speed))
 old=[];new=[];byclass={};bad=[]
 for i,(move,speed) in enumerate(tests):
  x0,y0,x1,y1=move;slot=i&7
  for cpu in (a,b):
   cpu.mem[api["MATH_SEEK16_POS_XL"]+slot]=x0&255
   cpu.mem[api["MATH_SEEK16_POS_XH"]+slot]=x0>>8
   cpu.mem[api["MATH_SEEK16_POS_Y"]+slot]=y0
   cpu.mem[api["MATH_X"]]=x1&255;cpu.mem[api["MATH_X"]+1]=x1>>8
   cpu.mem[api["MATH_Y"]]=y1
   cpu.mem[api["MATH_N"]]=speed&255;cpu.mem[api["MATH_N"]+1]=speed>>8
   cpu.x=slot
  ca=a.call(PUBLIC,4000000);cb=b.call(PUBLIC,4000000)
  old.append(ca);new.append(cb)
  if (bytes(a.mem[0x90e8:0x90e8+248])!=bytes(b.mem[0x90e8:0x90e8+248])
      or a.c!=b.c or a.x!=b.x or a.sp!=b.sp):
   bad.append((i,"INIT"))
  byclass.setdefault(hex(speed),[]).append(ca-cb)
  a.x=b.x=slot
  a.call(api["MATH_SEEK16_STEP"],4000000)
  b.call(api["MATH_SEEK16_STEP"],4000000)
  if bytes(a.mem[0x90e8:0x90e8+248])!=bytes(b.mem[0x90e8:0x90e8+248]) or a.c!=b.c:
   bad.append((i,"STEP"))
 assert not bad,bad[:3]
 gains=[x-y for x,y in zip(old,new)]
 report={"status":"PASS_SOURCE_MODEL_RELOCATED_RESEARCH_NOT_PROMOTED",
  "profile":P,"same_input_pairs":len(tests),
  "original_island_code_bytes":len(stock),"candidate_relocated_bytes":len(faster),
  "separate_reserved_code_range":"$0D00-$0E22",
  "foreign_resident_byte_19F0_unmodified":True,
  "existing_1A00_table_unmodified":True,
  "original_library_api_and_reu_untouched":True,
  "full_248_byte_state_input_carry_X_SP_and_step_equal":True,
  "mean_saving":sum(gains)/len(gains),
  "worst_regression":-min(gains),
  "by_speed":{k:{"mean_saved":sum(v)/len(v),"min_saved":min(v),"max_saved":max(v)} for k,v in byclass.items()},
  "source_sha256":hashlib.sha256(source.encode()).hexdigest(),
  "requires_original_resident_helpers_ZP":True,
  "native_cycles_measured":False}
 p=ROOT/"validation/review/ISSUE144_SEEK16_K1_RELOCATED_RESEARCH.json"
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(report,indent=2)+"\n")
 dest=ROOT/"optional/issue144_seek16_k1_relocated/research_source.asm"
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(source)
 print("ISSUE144 SEEK16 RELOCATED RESEARCH PASS",len(tests),report["mean_saving"],flush=True)
if __name__=="__main__":
 main()
