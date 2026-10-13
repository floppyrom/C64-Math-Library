#!/usr/bin/env python3
"""Stage V2-V4 UMUL24 no-carry CLC removal; never merge without native VICE/PR/main CI."""
from pathlib import Path
import hashlib,csv,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
FAST=P[1:4]
DOC="docs/ISSUE39_UMUL24_NO_CARRY_RTS_2026-10-13.md"
PROOF="validation/review/ISSUE39_UMUL24_NO_CARRY_RTS_RELEASE_2026-10-13.json"
STAMP="2026-10-13 ISSUE39 UMUL24 NONCARRY CLEAR-FLAG REMOVAL PRODUCTION"
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def prg(p):return R/p/"resident"/("math_"+p+"_game_math.prg")
def py(tool,*args):
 cmd=[sys.executable,str(R/"tools"/(tool+".py")),*map(str,args)]
 print("RUN",*cmd,flush=True);subprocess.run(cmd,check=True,cwd=R)
def source(p,mode):
 parent=(R/"build_hybrid" if p==P[-1] else R/"build_source")/mode/p
 m=json.loads((parent/"source_build_manifest.json").read_text())
 return parent/m["output_prg"],m
def maps():
 for mode in ("reference","alternate"):
  py("assemble_sources","--profile","all","--config-kind",mode)
  py("build_hybrid","--config-kind",mode)
def csvupdate(p,row):
 path=R/p/"PUBLIC_PERFORMANCE.csv"
 with path.open(newline="") as f: data=list(csv.DictReader(f))
 hit=[v for v in data if v["operation"] in ("math_umul24","umul24")]
 assert len(hit)==1,(p,hit)
 if p=="v2_pareto_fast":
  hit[0].update(avg_cycles=format(row["mean_cycles"],".6f"),
                min_cycles=str(row["min_cycles"]),max_cycles=str(row["max_cycles"]),
                cases=str(row["cases"]),
                evidence="2026-10-13 source-built 24-bit fast public return")
 elif p=="v3_reu_512k":
  hit[0].update(v2_pareto_fast_cycles=format(row["mean_cycles"],".6f"),
                v3_reu_default_cycles=format(row["mean_cycles"],".6f"),
                v3_evidence="2026-10-13 source-built UMUL24 fast return")
 elif p=="v4_reu_16m":
  hit[0].update(v3_reu_512k_cycles=format(row["mean_cycles"],".6f"),
                v4_reu_16m_cycles=format(row["mean_cycles"],".6f"),
                v4_evidence="2026-10-13 source-built UMUL24 fast return")
 else: raise AssertionError(("unexpected UMUL24 profile",p))
 with path.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator="\n")
  w.writeheader();w.writerows(data)
def main():
 statuspath=R/"RELEASE_STATUS.json";status=json.loads(statuspath.read_text())
 old={p:sha(prg(p)) for p in P};assert old==status["reference_prg_sha256"]
 size={p:prg(p).stat().st_size for p in P}
 maps()
 new={p:sha(source(p,"reference")[0]) for p in P}
 assert all(new[p]!=old[p] for p in FAST)
 assert new[P[0]]==old[P[0]] and new[P[-1]]==old[P[-1]]
 assert all(source(p,"reference")[0].stat().st_size==size[p] for p in P)
 for p in FAST:shutil.copyfile(source(p,"reference")[0],prg(p))
 py("generate_sources");maps()
 assert all(sha(prg(p))==sha(source(p,"reference")[0]) for p in P), "source regen drift"
 alternate={p:source(p,"alternate")[1]["output_sha256"] for p in P}
 py("validate_umul24_directout")
 validation=json.loads((R/"validation/multiply_refresh/UMUL24_DIRECTOUT_VALIDATION.json").read_text())
 expected=validation["results"][FAST[0]]["reference"]
 assert expected["cases"]==10324 and expected["mean_cycles"]<419.292135
 assert 1.50<419.29213483146066-expected["mean_cycles"]<1.52
 for p in FAST:
  assert validation["results"][p]["reference"]==expected
  assert validation["results"][p]["alternate"]==expected
  csvupdate(p,expected)
 performance=R/"PERFORMANCE.md";lines=performance.read_text().splitlines()
 hits=[i for i,l in enumerate(lines) if l.startswith("| "+chr(96)+"MATH_UMUL24"+chr(96)+" |")]
 assert len(hits)==1
 cells=lines[hits[0]].split("|")
 for i,p in enumerate(P):
  if p in FAST:cells[i+3]=" "+format(expected["mean_cycles"],".6f")+" "
 lines[hits[0]]="|".join(cells);performance.write_text("\n".join(lines)+"\n")
 # Full native-model public regression and standalone publication.
 for tool in ("validate_signed_multiply","benchmark_unsigned_common_corpus",
              "benchmark_unsigned_3216_workloads","audit_issue39_unsigned_small_workloads",
              "publish_standalone_sources","generate_consolidated_routine_table",
              "generate_public_indexes","validate_public_catalog",
              "validate_standalone_sources","verify_deterministic_rebuild",
              "validate_unsigned_division","validate_signed_division"):
  py(tool)
 report={
  "status":"PASS_SOURCE_STAGED_NATIVE_PENDING","old_sha256":old,"new_sha256":new,
  "alternate_sha256":alternate,"modified_profiles":list(FAST),
  "previous_mean_cycles":419.29213483146066,"new_mean_cycles":expected["mean_cycles"],
  "mean_saving_cycles":419.29213483146066-expected["mean_cycles"],
  "cases_per_fast_profile":10324,"no_slowdown_tested":True,
  "preserved_public_abi":True,"zero_page_growth":0,"resident_growth":0,
  "V1_V5_unchanged":True,"native_vice_calls":0,"issue39_complete":False}
 target=R/PROOF;target.parent.mkdir(parents=True,exist_ok=True)
 target.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 d=R/DOC
 d.write_text("# Issue39 — V2-V4 UMUL24 no-carry CLC removal\n\n"
  "Staged 13 October 2026. NOT RELEASED until native VICE/PR/main CI.\n\n"
  "The BCS fallthrough already proves carry clear; STA/STX preserve carry"
  " so replacing redundant CLC/RTS by RTS/NOP saves two CPU cycles. Rare final"
  " carry continues through the old branch. The signed producer is unchanged.\n\n"
  "In the paired 10,324-case public corpus, 7,789 calls save two cycles"
  " and 2,535 are unchanged, with no regressions. Official mean "
  +format(report["previous_mean_cycles"],".6f")+" -> "
  +format(expected["mean_cycles"],".6f")+" cycles.\n\n"
  "No new ZP or table data, no new resident bytes, stable public API,"
  " V1/V5 unchanged; reference/alternate and hybrid source validated."
  " No private OptiSearch code is published. Issue #39 remains open.\n")
 note=(STAMP+"\n"
  "- V2/V3/V4 UMUL24 no-carry CLC/RTS to RTS/NOP: 7,789/10,324 calls -2"
  " cycles and 2,535 unchanged; mean "+format(expected["mean_cycles"],".6f")
  + " cycles; 0 extra resident/ZP bytes. V1/V5 unchanged.\n"
  "- Signed/mixed regression, standalone source, alternate maps and"
  " package checked. Native VICE/PR/main pending. "+DOC+"\n\n")
 for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=R/name
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 status["reference_prg_sha256"]=new;status["alternate_prg_sha256"]=alternate
 status["issue39_umul24_no_carry_rts_2026_10_13"]={
  "status":"PASS_STAGED_NATIVE_VICE_PENDING","proof":PROOF,"doc":DOC,
  "baseline":old,"candidate":new,"new_mean_cycles":expected["mean_cycles"],
  "zero_page_growth":0,"resident_growth":0,"issue39_complete":False}
 for key,doc,keysha in (
   ("issue39_common_input_unsigned_divmod","validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json","benchmark_sha256"),
   ("issue39_unsigned_3216_multiworkload_2026_10_11","validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json","report_sha256"),
   ("issue39_unsigned_small_width_workloads_2026_10_11","validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json","data_sha256")):
  if isinstance(status.get(key),dict) and (R/doc).exists():
   status[key][keysha]=sha(R/doc)
 statuspath.write_text(json.dumps(status,indent=2)+"\n")
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal();py("package_audit")
 print("ISSUE39 UMUL24 CLC REDUCTION STAGED ALL GATES EXCEPT NATIVE PR MAIN",flush=True)
if __name__=="__main__":main()
