#!/usr/bin/env python3
"""Research-only V2 SEEK16_INIT speed-one fastpath with strict public ABI proof.

Mutates the CI runner's canonical template and builds; does not commit any
candidate code or PRG. A measured speed win does not imply release fitness.
"""
from __future__ import annotations
import hashlib,json,os,random,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"routines/movement"))
import benchmark_seek_profiles as benchmark
import validate_source_build as vsb
from mini6502 import CPU

P="v2_pareto_fast"
OLD="""        ldy S16_KI,x
        beq s16i_r0done
s16i_r0:"""
NEW="""        ldy S16_KI,x
        beq s16i_r0done
        cpy #1
        bne s16i_r0
        lda SK_DMAJH
        bne s16i_k1fast
        lda SK_DMIN
        cmp SK_DMAJL
        bcs s16i_r0
s16i_k1fast:
        lda SK_DMIN
        sta SK_REML
        jmp s16i_r0done
s16i_r0:"""

def sha(b):return hashlib.sha256(b).hexdigest()
def run(tool,*args):
 subprocess.run([sys.executable,str(ROOT/"tools"/tool),*args],cwd=ROOT,check=True)
def patch_source():
 path=ROOT/"tools/seek_kernel.py"
 source=path.read_text()
 insertion="SEEK16_V2_K1_FAST = SEEK16_INIT.replace("+repr(OLD)+","+repr(NEW)+")\n"
 anchor="BLOCKS = {\n"
 assert source.count(anchor)==1 and source.count(OLD)==1
 source=source.replace(anchor,insertion+"\n"+anchor,1)
 old_line="        lines.append(BLOCKS[block].rstrip('\\n'))"
 new_line="""        selected = (SEEK16_V2_K1_FAST if
                    profile == 'v2_pareto_fast' and block == 'seek16_init'
                    else BLOCKS[block])
        lines.append(selected.rstrip('\\n'))"""
 assert source.count(old_line)==1
 source=source.replace(old_line,new_line,1)
 path.write_text(source)
def resident():
 return ROOT/P/"resident"/("math_"+P+"_game_math.prg")
def built(kind):
 root=ROOT/"build_source"/kind/P
 m=json.loads((root/"source_build_manifest.json").read_text())
 return (root/m["output_prg"]).read_bytes(),root,m
def emulator(prg):
 load=prg[0]|prg[1]<<8
 mem=bytearray(65536)
 mem[load:load+len(prg)-2]=prg[2:]
 c=CPU(mem);c.d=0
 A=benchmark.api(P)
 c.call(A["MATH_INIT"],2000000)
 return c,A
def put(c,pos,value,n):
 for i in range(n):c.mem[pos+i]=(value>>(8*i))&255
def common_init_pairs(original,candidate,source_symbols,additional=180):
 r=random.Random(0x39B002)
 moves=list(benchmark.corpus(320))
 moves +=[(0,0,319,199),(0,0,32767,0),(65000,100,64999,100),
          (50000,100,50199,100),(60000,255,59900,0),
          (65535,120,65530,120),(255,1,256,2),(100,80,100,80),
          (20,0,20,200),(0,199,0,0),(50,10,55,15),(127,12,128,11)]
 for _ in range(additional):
  x=r.randrange(65536)
  dx=r.randint(-320,320)
  moves.append((x,r.randrange(200),(x+dx)&65535,r.randrange(200)))
 speeds=tuple(benchmark.SPEEDS)+tuple(x|0x8000 for x in benchmark.SPEEDS)+tuple(benchmark.INT_SPEEDS)+(0x0100,0x0200)
 a,api=emulator(original);b,_=emulator(candidate)
 S=source_symbols
 base=S["MATH_SEEK16_POS_XL"]
 io=api["MATH_X"]
 count=0
 improvements={"k1":[],"other":[]}
 for index,move in enumerate(moves):
  x0,y0,x1,y1=move
  # Public SEEK16 documented domain requires |dx|<=32767.
  if abs(x1-x0)>32767:continue
  for speed in speeds:
   slot=index&7
   for c in (a,b):
    put(c,S["MATH_SEEK16_POS_XL"]+slot,x0&255,1)
    put(c,S["MATH_SEEK16_POS_XH"]+slot,x0>>8,1)
    put(c,S["MATH_SEEK16_POS_Y"]+slot,y0,1)
    put(c,io,x1,2);put(c,io+4,y1,1);put(c,io+0x10,speed,2)
    c.x=slot;c.c=index&1
   snap=bytes(a.mem[io:io+0x12])
   old_cycles=a.call(api["MATH_SEEK16_INIT"],200000)
   new_cycles=b.call(api["MATH_SEEK16_INIT"],200000)
   assert a.x==b.x==slot and a.c==b.c and a.sp==b.sp,(
       index,move,speed,"public result/stack")
   assert bytes(a.mem[base:base+248])==bytes(b.mem[base:base+248]),(
       index,move,speed,"complete eight-slot state differs")
   assert bytes(a.mem[io:io+0x12])==bytes(b.mem[io:io+0x12])==snap,(
       index,move,speed,"input overwritten")
   import seek_kernel as K
   ki_offset=dict(K.S16_FIELDS)["KI"]
   group="k1" if a.mem[base+ki_offset+slot]==1 else "other"
   improvements[group].append(old_cycles-new_cycles)
   count+=1
 assert count>5500
 return {"pairs":count,"class_means":{
         k:{"cases":len(v),"mean_cycles_saved":sum(v)/len(v),
            "minimum_cycles_saved":min(v),"maximum_cycles_saved":max(v)}
         for k,v in improvements.items()},
         "mean_cycles_saved":sum(map(sum,improvements.values()))/count}

def main():
 baseline_path=resident()
 original=baseline_path.read_bytes()
 original_sha=sha(original)
 baseline_status=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
 assert original_sha==baseline_status["reference_prg_sha256"][P]
 base=benchmark.run(P)
 recorded=json.loads((ROOT/"validation/movement/SEEK_PROFILE_BENCHMARK.json").read_text())["profiles"][P]
 assert all(base[k]["mean_cycles"]==recorded[k]["mean_cycles"] for k in recorded)
 patch_source()
 run("generate_seek_sources.py")
 run("generate_seek_sources.py","--check")
 run("generate_sources.py")
 for kind in ("reference","alternate"):
  run("assemble_sources.py","--profile","all","--config-kind",kind)
  run("build_hybrid.py","--config-kind",kind)
 # The v2 source maps may move as regions, but must remain valid.
 for kind in ("reference","alternate"):
  run("validate_source_build.py","all","--build",str(ROOT/"build_source"/kind),
      "--out","validation/source_relocation/"+kind)
 run("validate_seek_placement.py")
 # Extended all-slot and mixed-DIV/MOD proof are source-candidate tests.
 run("validate_issue39_seek_all_slots.py")
 run("validate_issue136_seek_divmod_mixed.py")
 new,folder,m=built("reference")
 alternate,alternate_root,_=built("alternate")
 assert len(new)==len(original) and new!=original
 assert sha(new)==m["output_sha256"]
 S=vsb.seek_symbols(folder)
 paired=common_init_pairs(original,new,S)
 try:
  baseline_path.write_bytes(new)
  measured=benchmark.run(P)
 finally:baseline_path.write_bytes(original)
 assert sha(baseline_path.read_bytes())==original_sha
 results={}
 for op in recorded:
  old=recorded[op];newr=measured[op]
  results[op]={"baseline_mean_cpu_cycles":old["mean_cycles"],
               "candidate_mean_cpu_cycles":newr["mean_cycles"],
               "saved_mean_cpu_cycles":old["mean_cycles"]-newr["mean_cycles"],
               "cases":newr["cases"]}
  if op!="MATH_SEEK16_INIT":
   assert old==newr,("other public STEP/INIT changed",op)
 assert results["MATH_SEEK16_INIT"]["saved_mean_cpu_cycles"]>0,(
     "candidate is not faster on official corpus",results["MATH_SEEK16_INIT"])
 output={
  "status":"PASS_RESEARCH_ONLY_FASTER_V2_SEEK16_K1",
  "profile":P,"source_island_start":"$18E2",
  "source_island_capacity_bytes":542,
  "candidate_source_bytes":291,
  "candidate_growth_bytes":21,
  "public_abi_pins_preserved":True,
  "source_reference_sha256":sha(new),
  "source_alternate_sha256":sha(alternate),
  "baseline_resident_sha256":original_sha,
  "official_public_benchmark":results,
  "expanded_paired_init":paired,
  "all_eight_slots_all_steppers":"PASS",
  "mixed_divmod_and_memory_placement":"PASS",
  "native_vice_candidate_qualified":False,
  "main_release_certified":False,
  "production_code_committed":False,
  "other_profiles_unchanged":True,
  "private_optisearch_published":False
 }
 out=ROOT/"validation/review/ISSUE39_V2_SEEK16_K1_RESEARCH_2026-10-14.json"
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
 print("V2 K1 RESEARCH BENCHMARK PASS",results["MATH_SEEK16_INIT"],flush=True)
 print("V2 K1 PAIRED INIT",paired,flush=True)

if __name__=="__main__":
 main()
