#!/usr/bin/env python3
"""Issue144: V1 normal-resident highword seed feasibility; V5 not yet proven."""
from pathlib import Path
import json,math,random,statistics,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler,CPU
from assemble_sources import preprocess,parse_config
from validate_unsigned_division import wr,rd
P="v1_balanced"; HELPERS=(0x0A90,0x0A98,0x0AA0,0x0AA8,0x0AB0,0x0AB8,0x0AC0,0x0AC8,0x0AD0)
def source(helper):
 s=(ROOT/"optional/issue144_isqrt32_highword_direct"/(P+".asm")).read_text()
 assert s.startswith("!cpu 6510\n* = $0C00\n")
 s=s.replace("!cpu 6510\n","").replace("* = $0C00","* = REG_GAME+$0A40")
 s=s.replace("* = $0C90","* = REG_GAME+$"+format(helper,"04X"))
 for old,new in [
 ("$C008","MATH_IO+$08"),("$C009","MATH_IO+$09"),("$C010","MATH_IO+$10"),
 ("$C011","MATH_IO+$11"),("$C012","MATH_IO+$12"),("$C013","MATH_IO+$13"),
 ("$9800","REG_TABLE+$3800"),("$9900","REG_TABLE+$3900"),
 ("$C901","REG_GAME+$0801"),("$CA24","REG_GAME+$0924"),
 ("$C041","V1_SCRATCH+$01"),("$C042","V1_SCRATCH+$02"),
 ("$C043","V1_SCRATCH+$03"),("$C044","V1_SCRATCH+$04"),
 ("$C045","V1_SCRATCH+$05")]:
  s=s.replace(old,new)
 return s
def probe(layout,helper):
 cfg=ROOT/"relocatable_source"/P/("math_config_"+layout+".inc")
 values=parse_config(cfg)
 main=preprocess(ROOT/"relocatable_source"/P/"math_relocatable.asm",cfg)
 before,_,_=Assembler().assemble(main)
 module=source(helper)
 candidate,_,_=Assembler().assemble(cfg.read_text()+"\n"+module)
 start=values["REG_GAME"]+0x0A40;aux=values["REG_GAME"]+helper
 hbytes=[a for a in candidate if a>=aux]
 mainbytes=[a for a in candidate if a<aux]
 overlap=[hex(a) for a in hbytes if before.get(a,0)!=0]
 illegal=[hex(a) for a in mainbytes if not start<=a<aux]
 record={"layout":layout,"helper":hex(helper),"main_bytes":len(mainbytes),
         "helper_bytes":len(hbytes),"occupied_helper_bytes":overlap[:10],
         "illegal_main_bytes":illegal[:10]}
 if overlap or illegal:return record,None
 after,labels,cons=Assembler().assemble(main+"\n"+module)
 changes=[a for a in set(before)|set(after) if before.get(a,0)!=after.get(a,0)]
 assert changes and all(start<=a<values["REG_GAME"]+0x0AE0 for a in changes),(layout,helper,changes[:10])
 assert labels["LCB40"]==start and labels["LC8DB"]==aux
 api=values["REG_GAME_API"]+0x30
 assert before[api]==after[api]==0x4C and (before[api+1],before[api+2])==(after[api+1],after[api+2])
 def machine(code):
  ram=bytearray(65536)
  for a,v in code.items():ram[a]=v
  cpu=CPU(ram);cpu.d=0;cpu.call(cons["MATH_INIT"],2000000);return cpu
 record["changed_bytes"]=len(changes)
 return record,(machine(before),machine(after),api,values["MATH_IO"])
def model(before,after,api,io):
 r=random.Random(0x144151)
 values=[0,1,2,3,4,7,15,16,255,256,257,65535,65536,65537,0x7fffffff,0x80000000,0xffffffff]
 values +=[r.getrandbits(32) for _ in range(640)]
 saved=[]
 for i,n in enumerate(values):
  for c in (before,after):wr(c.mem,io+0x10,n,4);c.x=(i*7)&255;c.y=(i*13)&255
  sp0,sp1=before.sp,after.sp
  a=before.call(api,500000);b=after.call(api,500000)
  assert rd(before.mem,io+8,2)==rd(after.mem,io+8,2)==math.isqrt(n)
  assert before.c==after.c==0
  assert rd(before.mem,io+0x10,4)==rd(after.mem,io+0x10,4)==n
  assert (before.x,before.y)==(after.x,after.y)
  assert (before.sp,after.sp)==(sp0,sp1)
  saved.append(a-b)
 return {"cases":len(saved),"mean_saved":statistics.mean(saved),"min_saved":min(saved),"max_saved":max(saved),"slower":sum(x<0 for x in saved)}
def main():
 results=[];winner=None
 for loc in HELPERS:
  one,cpu1=probe("reference",loc)
  two,cpu2=probe("alternate",loc)
  assert bool(cpu1)==bool(cpu2),(loc,"relocation inconsistent")
  row={"offset":hex(loc),"reference":one,"alternate":two}
  if cpu1:
   row["model_reference"]=model(*cpu1)
   row["model_alternate"]=model(*cpu2)
   row["result"]="FEASIBLE"
   winner=row;results.append(row);break
  row["result"]="COLLISION";results.append(row)
 print(json.dumps({"status":"PASS_SCREEN" if winner else "REJECTED_NO_FREE_RESIDENT_SPACE",
                   "candidate":winner,"attempts":results,"v5_not_yet_verified":True,
                   "no_reference_source_prg_or_reu_changes":True},indent=2,sort_keys=True))
if __name__=="__main__":main()
