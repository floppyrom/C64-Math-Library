#!/usr/bin/env python3
"""Stage signed Q8.8 normalization branch-collapse, with strict source parity."""
from pathlib import Path
import hashlib,json,csv,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
STOCK=(P[0],P[1],P[4])
KEY="issue39_normalize_branch_collapse_2026_10_14"
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(p.read_bytes())
def run(name,*args):subprocess.run([sys.executable,str(R/"tools"/name),*args],cwd=R,check=True)
def installed(p):return R/p/"resident"/("math_"+p+"_game_math.prg")
def generated(p,kind):
 d=R/("build_hybrid" if p==P[4] else "build_source")/kind/p
 return d/json.loads((d/"source_build_manifest.json").read_text())["output_prg"]
def rebuild():
 run("generate_sources.py")
 for kind in ("reference","alternate"):
  run("assemble_sources.py","--profile","all","--config-kind",kind)
  run("build_hybrid.py","--config-kind",kind)
def refresh_csv(path,p,perf):
 with path.open(newline="") as f:rows=list(csv.DictReader(f))
 fields=list(rows[0]);hits=0
 for row in rows:
  if row["routine"] not in ("VEC2_NORMALIZE_Q8_8","MATH_VEC2_NORMALIZE_Q8_8"):continue
  if "profile" in fields and row["profile"]!=p:continue
  row["mean_cycles"]=str(perf["mean"])
  row["min_cycles"]=str(perf["min"])
  row["max_cycles"]=str(perf["max"])
  hits+=1
 assert hits==1,(str(path),p,hits)
 with path.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(rows)
def corpus_recheck():
 common=R/"validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json"
 before=json.loads(common.read_text());run("benchmark_unsigned_common_corpus.py")
 after=json.loads(common.read_text())
 assert before["routines"]==after["routines"] and after["total_calls"]==136335
 workload=R/"validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json"
 old=json.loads(workload.read_text());run("benchmark_unsigned_3216_workloads.py")
 new=json.loads(workload.read_text())
 assert old["workloads"]==new["workloads"] and new["total_calls"]==30720
 return common,workload
def main():
 sp=R/"RELEASE_STATUS.json";st=json.loads(sp.read_text())
 assert KEY not in st
 research=json.loads((R/"validation/review/ISSUE39_NORMALIZE_BRANCH_COLLAPSE_RESEARCH_2026-10-14.json").read_text())
 vice=json.loads((R/"validation/review/ISSUE39_NORMALIZE_BRANCH_COLLAPSE_NATIVE_2026-10-14.json").read_text())
 assert research["status"]=="PASS_LOG_BRANCH_COLLAPSE_RESEARCH_NOT_RELEASED"
 assert research["new_public_model_calls"]==1073960
 assert vice["status"]=="PASS_NATIVE_VICE_NORMALIZE_BRANCH_COLLAPSE"
 assert vice["baseline_and_candidate_calls"]==320
 old_reu=st["reference_reu_sha256"].copy()
 rebuild()
 old={};new={};restore={}
 for p in P:
  original=installed(p).read_bytes();candidate=generated(p,"reference").read_bytes()
  assert digest(original)==st["reference_prg_sha256"][p]==vice["profiles"][p]["baseline_sha256"]
  assert digest(candidate)==vice["profiles"][p]["candidate_sha256"]
  assert len(original)==len(candidate) and original[:2]==candidate[:2]
  old[p]=digest(original);new[p]=digest(candidate)
  changes=[[i,a] for i,(a,b) in enumerate(zip(original,candidate)) if a!=b]
  if p in STOCK:
   start=int.from_bytes(original[:2],"little")
   assert 0<len(changes)<1000
   assert all(0x1500<=start+i-2<0x1900 for i,_ in changes),(p,changes[:8])
   restore[p]={"old_sha256":old[p],"candidate_sha256":new[p],
    "file_len":len(original),"original_bytes_at_changed_offsets":changes}
  else:assert original==candidate,p
  print("SOURCE NORMALIZE CHANGED",p,len(changes),flush=True)
 saved=R/"validation/review/ISSUE39_NORMALIZE_PREVIOUS_PRG_BYTES_2026-10-14.json"
 saved.write_text(json.dumps({"profiles":restore,"old_prgs":old,"new_prgs":new},indent=2)+"\n")
 for p in STOCK:shutil.copyfile(generated(p,"reference"),installed(p))
 for p in STOCK:
  b=bytearray(installed(p).read_bytes())
  for i,val in restore[p]["original_bytes_at_changed_offsets"]:b[i]=val
  assert digest(b)==old[p]
 rebuild()
 assert all(sha(generated(p,"reference"))==new[p] for p in P)
 alternate={p:sha(generated(p,"alternate")) for p in P}
 for cmd,args in (("generate_normalize_tables.py",("--check",)),
    ("validate_normalize_native_sources.py",()),
    ("benchmark_normalize_profile_parity.py",()),
    ("validate_normalize_optimized.py",()),
    ("certify_normalize_exact_ratio.py",())):run(cmd,*args)
 parity=json.loads((R/"validation/normalize/NORMALIZE_PROFILE_PARITY_107396.json").read_text())
 assert parity["status"]=="PASS" and parity["corpus_vectors"]==107396
 means={}
 for row in parity["profiles"]:
  p=row["profile"];reference=row["reference"];alt=row["alternate"]
  assert reference["prg_sha256"]==new[p] and alt["prg_sha256"]==alternate[p]
  assert reference["output_sha256"]==alt["output_sha256"]
  assert row["cycle_vector_mismatches"]==row["output_vector_mismatches"]==0
  assert abs(reference["mean_cycles"]-research["profiles"][p]["reference"]["candidate_mean_cycles"])<1e-9
  means[p]={"mean":reference["mean_cycles"],"min":reference["min_cycles"],"max":reference["max_cycles"]}
  if p in STOCK:
   if (R/p/"PUBLIC_PERFORMANCE_GAME_MATH.csv").exists():
    refresh_csv(R/p/"PUBLIC_PERFORMANCE_GAME_MATH.csv",p,means[p])
   if p!=P[4]:
    refresh_csv(R/"docs/PERFORMANCE_GAME_MATH_FINAL.csv",p,means[p])
 perf=R/"PERFORMANCE.md";s=perf.read_text()
 row=next(x for x in s.splitlines() if "MATH_VEC2_NORMALIZE_Q8_8" in x and x.startswith("|"))
 pieces=row.split("|")
 for i,p in enumerate(P):pieces[i+3]=f" {means[p]['mean']:.6f} "
 perf.write_text(s.replace(row,"|".join(pieces)))
 run("publish_standalone_sources.py")
 run("generate_consolidated_routine_table.py")
 common,workload=corpus_recheck()
 run("generate_public_indexes.py")
 assert all(sha(installed(p))==new[p] for p in P)
 for p in (P[2],P[3]):
  f=R/p/"reu"/("c64_math_v3_512k_game_math.reu" if p==P[2] else "c64_math_v4_16m_game_math.reu")
  assert sha(f)==old_reu[p]
 st["reference_prg_sha256"]=new;st["alternate_prg_sha256"]=alternate
 if isinstance(st.get("hybrid_v5"),dict):
  st["hybrid_v5"]["reference_prg_sha256"]=new[P[4]]
  st["hybrid_v5"]["alternate_prg_sha256"]=alternate[P[4]]
 st["issue39_common_input_unsigned_divmod"]["benchmark_sha256"]=sha(common)
 st["issue39_unsigned_3216_multiworkload_2026_10_11"]["report_sha256"]=sha(workload)
 st["vec2_normalize_q8_8"]["mean_cycles"]={p:means[p]["mean"] for p in P}
 st["vec2_normalize_q8_8"]["native_sources"]["stock_code_bytes"]=865
 st[KEY]={"status":"PASS_STAGED_PR_MAIN_CI_PENDING","public_api":"MATH_VEC2_NORMALIZE_Q8_8",
    "stock_profiles":list(STOCK),"unchanged_reu_profiles":list(P[2:4]),
    "old_resident_sha256":old,"new_resident_sha256":new,
    "reversible_parent_bytes":str(saved.relative_to(R)),"model_calls":1073960,
    "native_x64sc_old_new_calls":320,"stock_code_bytes_before":881,
    "stock_code_bytes_after":865,"normal_zp_growth":0,"reu_changed":False,
    "normalization_family_complete":False,"issue39_open":True}
 sp.write_text(json.dumps(st,indent=2)+"\n")
 report={"status":"PASS_STAGED_PR_MAIN_CI_PENDING","original":old,"candidate":new,
   "alternate":alternate,"stock_bytes_saved_per_routine":16,"means":means,
   "native_x64sc_calls":320,"cpu_model_calls":1073960,
   "reu_unchanged":True,"normal_zp_growth":0}
 path=R/"validation/review/ISSUE39_NORMALIZE_BRANCH_PRODUCTION_2026-10-14.json"
 path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 doc=R/"docs/ISSUE39_NORMALIZE_BRANCH_RELEASE_2026-10-14.md"
 doc.write_text("# Issue39 normalize logarithmic branch collapse\n\n"
   "V1, V2 and V5: eight two-branch lookup decisions replaced with one BEQ each. "
   "Code 881 to 865 bytes. CPU-model mean 160.150080 to 159.128794 cycles; "
   "same exact signed output bytes on 1,073,960 reference/alternate input calls, "
   "320 real native VICE old/new public calls. Existing certified 723073-cell "
   "signed precision envelope, public ABI, 4 ZP scratch and REU unchanged. "
   "Native VICE cycle timing not measured. PR/main CI pending.\n")
 entry=("## 2026-10-14 ISSUE39 NORMALIZE STOCK LOG BRANCH PRODUCTION\n\n"
  "Optimized V1/V2/V5 VEC2_NORMALIZE_Q8_8: redundant BNE/BEQ branch collapse, "
  "16 fewer code bytes, mean CPU-model 160.150080 -> 159.128794 cycles. "
  "1,073,960 public model calls; 320 old/new x64sc calls. Exact signed outputs "
  "and full-domain angular/component accuracy preserved; no extra ZP or REU. "
  "Rebuilt standalone sources, performance tables, verified reversible old "
  "PRG bytes and checksums. Independent PR/main CI pending. "
  "See docs/ISSUE39_NORMALIZE_BRANCH_RELEASE_2026-10-14.md.\n\n---\n\n")
 for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  path=R/name
  if "ISSUE39 NORMALIZE STOCK LOG BRANCH PRODUCTION" not in path.read_text():
   path.write_text(entry+path.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal();run("package_audit.py")
 print("STOCK NORMALIZE SOURCE PRODUCTION STAGED; FULL CI NOT YET CERTIFIED",flush=True)
if __name__=="__main__":main()
