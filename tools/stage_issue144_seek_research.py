#!/usr/bin/env python3
"""Issue144 D source-backed SEEK16 relocation research, NOT performance promotion."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
from issue144_seek16_k1_relocate import assemble
P="v2_pareto_fast"
MODEL="validation/review/ISSUE144_SEEK16_K1_RELOCATED_RESEARCH.json"
NATIVE="validation/review/ISSUE144_SEEK16_K1_RELOCATED_NATIVE_VICE.json"
ASM="optional/issue144_seek16_k1_relocated/research_source.asm"
DOC="docs/ISSUE144_SEEK16_INIT_RELOCATED_K1_RESEARCH_2026-10-15.md"
STAMP="2026-10-15 ISSUE144 SEEK16 INIT RELOCATION UNPROMOTED"
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 model=read(MODEL);vice=read(NATIVE)
 assert model["status"]=="PASS_SOURCE_MODEL_RELOCATED_RESEARCH_NOT_PROMOTED"
 assert vice["status"]=="PASS_NATIVE_VICE_RELOCATED_SEEK16_V2_K1"
 assert model["same_input_pairs"]==300
 assert model["candidate_relocated_bytes"]==291
 assert model["foreign_resident_byte_19F0_unmodified"]
 assert model["existing_1A00_table_unmodified"]
 assert vice["outputs_carry_x_stack_bitwise_equal"]
 assert vice["native_original_step_calls"]>=64
 assert model["source_sha256"]==vice["source_sha256"]==sha(ASM)
 orig=read("RELEASE_STATUS.json")
 baselines={p:orig["reference_prg_sha256"][p] for p in
  ("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")}
 for p,v in baselines.items():
  assert sha(p+"/resident/math_"+p+"_game_math.prg")==v
 lines=[
  "# Issue144 D — V2 SEEK16_INIT speed-one relocated research",
  "",
  "**RESEARCH ONLY: NOT PROMOTED TO DEFAULT V2, REU OR OTHER PROFILES.**",
  "",
  "An earlier in-place speed-one candidate (rejected PR #142) overwrote",
  "the occupied foreign byte at $19F0 and active table at $1A00.",
  "This source-backed test instead copies the entire INIT executable",
  "island to separately available caller RAM $0D00-$0E22, while",
  "retaining resident SEEK16 helper islands/zero-page and public object",
  "state. A disposable copy of the public JMP $5E48 points at the",
  "new island; the installed resident PRG is unchanged.",
  "",
  "291-byte candidate versus 270-byte original mirror (+21 bytes),",
  "300 identical operand/vector INIT tests with all 248 state bytes,",
  "caller X, carry and SP checked, followed by STEP and state comparison.",
  "Overall mean gain **"+f"{model['mean_saving']:.3f}"+" CPU-model cycles**;",
  "the speed-one workload gains about 16.7 cycles but some operands",
  "regress up to 18 cycles. Other speeds can regress, thus this does",
  "not qualify for the 5% general-call default-promotion heuristic.",
  "",
  "Native VICE uses four diverse V2 scenarios, 64 baseline STEP",
  "calls and 64 optimized STEP calls, all output/flags/stack",
  "identical. Native cycle timing is NOT measured.",
  "",
  "The exported source is an exact public standalone executable",
  "mirror relocated with independently applied fastpath, not an",
  "independent reusable SEEK engine. The example $0D00-$0E22",
  "RAM must be proven free in the actual application layout.",
  "No code or data may be placed over $19F0/$1A00.",
  "",
  "Source: "+ASM,
  "Generator and model tests: tools/issue144_seek16_k1_relocate.py",
  "Native x64sc: tools/native_issue144_seek16_k1_relocate.py",
  "CPU proof: "+MODEL,
  "Native proof: "+NATIVE,
  "No private OptiSearch code; all normal V1-V5 PRGs, REUs and public",
  "PERFORMANCE leaderboard remain unchanged."
 ]
 (R/DOC).write_text("\n".join(lines)+"\n")
 (R/"optional/issue144_seek16_k1_relocated/README.md").write_text(
  "# Unpromoted V2 SEEK16 INIT research\n\nSee ../../"+DOC+".\n")
 orig["issue144_seek16_relocated_k1_research_2026_10_15"]={
   "status":"PASS_CPU_NATIVE_RESEARCH_ONLY_NOT_PROMOTED",
   "profile":P,"model_pairs":300,"native_steps_old":vice["native_original_step_calls"],
   "native_steps_new":vice["native_candidate_step_calls"],
   "source":ASM,"documentation":DOC,
   "foreign_19f0_and_1a00_unchanged":True,
   "default_prgs_changed":False,"native_cycles_measured":False,
   "overall_mean_saving":model["mean_saving"]}
 (R/"RELEASE_STATUS.json").write_text(json.dumps(orig,indent=2)+"\n")
 note=STAMP+"\n- Unpromoted V2 SEEK16_INIT speed-one source relocation research: 291 bytes in caller RAM, $19F0 and $1A00 preserved, 300 paired model INIT+STEP states and 128 native STEP executions matched; overall gain only ~4.2 CPU cycles, some slower calls. No resident integration. "+DOC+"\n\n"
 for n in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=R/n
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
 assert all(sha(p+"/resident/math_"+p+"_game_math.prg")==v for p,v in baselines.items())
 print("ISSUE144 SEEK16 RELOCATED NATIVE RESEARCH DOCUMENTED, SHA SEALED")
if __name__=="__main__":main()
