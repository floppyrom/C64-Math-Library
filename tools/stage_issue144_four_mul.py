#!/usr/bin/env python3
"""Publish source-only Issue144 four multiplication 16bit-domain optimizations.

Every proof is matched same-input and resource-preserving; normal residents,
normal ABI and production PERFORMANCE rows must stay byte-identical.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
from validate_unsigned_division import PROFILES
SRC="optional/issue144_four_mul_narrow16/four_u32_narrow16.asm"
NATIVE="validation/review/ISSUE144_FOUR_MUL_NARROW16_NATIVE_VICE.json"
DOC="docs/ISSUE144_A_FOUR_MUL_NARROW16_SPECIALIST_2026-10-15.md"
OPS=("MATH_UMUL32","MATH_SMUL32","MATH_UMUL32_SHR16","MATH_SMUL32_SHR16")
STAMP="2026-10-15 ISSUE144 FOUR 32BIT MULTIPLY NARROW16 OPTINS"
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 status=read("RELEASE_STATUS.json")
 existing={p:status["reference_prg_sha256"][p] for p in PROFILES}
 old_reu=dict(status.get("reference_reu_sha256",{}))
 native=read(NATIVE)
 assert native["status"]=="PASS_NATIVE_VICE_FOUR_NARROW16_U32_MUL"
 assert native["total_native_calls"]==960
 assert set(native["profiles"])==set(PROFILES)
 assert native["source_sha256"]==sha(SRC)
 rows={}
 for p in PROFILES:
  rec=read("validation/review/ISSUE144_FOUR_MUL_NARROW16_"+p+".json")
  assert rec["status"]=="PASS_FOUR_NARROW16_PUBLIC_ABI_SHAPED_OPTINS"
  assert rec["cases_per_operation"]==1145
  assert rec["source_sha256"]==sha(SRC)
  assert set(rec["entries"])==set(OPS)
  assert set(native["profiles"][p])==set(OPS)
  results={}
  for op in OPS:
   x=rec["entries"][op]
   assert x["paired_savings"]["min_cycles"]>0
   assert x["cases"]==1145
   assert native["profiles"][p][op]["correct_inputs_outputs_carry_stack"]
   assert native["profiles"][p][op]["native_candidate_calls"]==24
   results[op]={"baseline":x["stock"]["mean_cycles"],
      "optin":x["optin"]["mean_cycles"],
      "saved":x["paired_savings"]["mean_cycles"],
      "worst_case_saved":x["paired_savings"]["min_cycles"]}
  rows[p]=results
  assert sha(p+"/resident/math_"+p+"_game_math.prg")==existing[p]
 doc=[
  "# Issue #144 A — four source-only upper-word-zero multiply specialists",
  "",
  "**Explicit operand-domain Pareto alternatives; NOT installed resident replacements.**",
  "",
  "PRECONDITION: BOTH 32-bit input operands $C000–$C003/$C004–$C007",
  "have ZERO upper 16-bit words. Low 16 bits can be any unsigned",
  "value 0..65535, including bit15 set. This is still nonnegative in",
  "signed 32-bit arithmetic; do NOT confuse with signed 16-bit multiply.",
  "",
  "The separately assembled 6510 source at caller-owned $0E60",
  "uses the existing public resident unsigned MATH_UMUL16 entry $3020.",
  "It constructs the full 64-bit product with zero upper 32 bits or",
  "the exact 48-bit product shifted by 16, for four operation names.",
  "No new normal ZP, tables, installed call-site addresses or REU use.",
  "Requires MATH_INIT and resident tables; mutually exclusive use of",
  "shared scratch from interrupts; not reentrant.",
  "",
  "## Paired CPU-model baseline/alternative (1,145 operand pairs per op/profile)",
  "",
  "| Profile | Operation | Stock cycles | Optional cycles | Saved cycles |",
  "|---|---|---:|---:|---:|"]
 for p in PROFILES:
  for op in OPS:
   r=rows[p][op]
   doc.append(f"| {p} | {op} | {r['baseline']:.3f} | {r['optin']:.3f} | {r['saved']:.3f} |")
 doc += [
  "",
  "22,900 model before/after pairs across five public profiles and four",
  "signed/unsigned operation signatures passed output 8 or 6 bytes,",
  "carry=0, input preservation and stack. 960 native x64sc",
  "baseline/optin calls also pass. These are public-ABI-shaped",
  "direct-candidate calls with identical raw operands; the stock",
  "public entries are NOT redirected in the shipped libraries.",
  "Native emulator correctness is qualified, native cycle timing NOT.",
  "",
  "Signed narrow16-domain calls deliberately reuse UNSIGNED UMUL16;",
  "signed 16-bit multiplication gives incorrect results for values",
  "$8000–$FFFF even though the 32-bit signed operand is positive.",
  "Do not run on inputs with any upper 16-bit bit set; doing so",
  "silently yields incorrect arithmetic.",
  "",
  "The address $0E60 is not generally free: caller/builders must",
  "check actual occupied RAM/loader/IRQ maps or reassemble to an",
  "independently tested safe address. Shared scratch requires",
  "strictly sequential calls, and callers cannot have IRQ/NMI math",
  "operations overlap. Current production PRGs, REU payloads,",
  "performance leaderboards and normal public ABI are unchanged.",
  "",
  "Source: "+SRC,
  "CPU-model proof: validation/review/ISSUE144_FOUR_MUL_NARROW16_<profile>.json",
  "Native VICE proof: "+NATIVE,
  "Reproducer: tools/issue144_four_mul_narrow16_model.py",
  "Native reproducer: tools/native_issue144_four_mul_narrow16.py",
  "No private OptiSearch generator source is included."
 ]
 (R/DOC).write_text("\n".join(doc)+"\n")
 (R/"optional/issue144_four_mul_narrow16/README.md").write_text(
  "# Four narrow16-domain 32bit multiplication opt-ins\n\n"
  "Read ../../"+DOC+" before use. Operand upper words must BOTH"
  " equal zero; not general 32-bit routines, no default replacement.\n")
 status["issue144_four_mul_narrow16_optin_2026_10_15"]={
   "status":"PASS_CPU_NATIVE_SOURCE_ONLY_NO_DEFAULT_PROMOTION",
   "precondition":"both U32 operand upper 16-bit words zero",
   "profiles":list(PROFILES),"operations":list(OPS),
   "model_paired_cases_total":22900,
   "native_baseline_candidate_calls":960,
   "native_cycles_measured":False,"no_regular_ZP_growth":True,
   "default_PRGs_changed":False,"default_REUs_changed":False,
   "source":SRC,"documentation":DOC,"native_proof":NATIVE,
   "model_proof_prefix":"validation/review/ISSUE144_FOUR_MUL_NARROW16_",
   "mean_public_call_metrics":rows}
 (R/"RELEASE_STATUS.json").write_text(json.dumps(status,indent=2)+"\n")
 note=STAMP+"\n- Published four source-only opt-in U32 and S32 full/SHR16 multiply variants for the strict both-upper-words-zero operand domain: 22,900 paired CPU model calls, 960 real x64sc calls across all profiles passing. No regular profile/API/ZP/REU/benchmark leaderboard modification. "+DOC+"\n\n"
 for fname in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=R/fname
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for i in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
 assert all(sha(p+"/resident/math_"+p+"_game_math.prg")==existing[p] for p in PROFILES)
 assert dict(read("RELEASE_STATUS.json").get("reference_reu_sha256",{}))==old_reu
 print("ISSUE144 FOUR MUL DOMAIN SPECIALISTS SOURCE, PROOF, DOC, CHANGELOG, SHA SEALED")
if __name__=="__main__":
 main()
