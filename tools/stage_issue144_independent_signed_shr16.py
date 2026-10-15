#!/usr/bin/env python3
"""Gate source-only independent signed SHR16 mixed-call Pareto point, five profiles."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from issue144_independent_signed_shr16 import make_source,sha
from validate_unsigned_division import PROFILES
from stage_issue39_v1_3216_ool_release import reseal

MODEL="validation/review/ISSUE144_SIGNED_SHR16_INDEPENDENT_MODEL.json"
VICE="validation/review/ISSUE144_SIGNED_SHR16_INDEPENDENT_NATIVE_VICE.json"
DOC="docs/ISSUE144_SIGNED_SHR16_INDEPENDENT_MIXED_2026-10-15.md"
STAMP="2026-10-15 ISSUE144 SIGNED SHR16 INDEPENDENT MIXED-CALL PRODUCER"
SRC="optional/issue144_signed_shr16_independent"
def read(path):return json.loads((R/path).read_text())
def digest(path):return sha((R/path).read_bytes())
def main():
 model=read(MODEL);native=read(VICE);state=read("RELEASE_STATUS.json")
 assert model["status"]=="PASS_ALL_FIVE_PUBLIC_SEQUENTIAL_MIXED_SIGNED_SHR16"
 assert native["status"]=="PASS_NATIVE_FIVE_PROFILE_INDEPENDENT_SIGNED_SHR16_MIXED"
 assert model["pairs_per_profile"]==2409
 assert native["original_and_candidate_calls"]==240
 assert set(model["profiles"])==set(native["profiles"])==set(PROFILES)
 resident=dict(state["reference_prg_sha256"])
 reu=dict(state.get("reference_reu_sha256",{}))
 rows={}
 for p in PROFILES:
  q=model["profiles"][p];r=native["profiles"][p]
  assert q["cases"]==2409
  assert q["status"]=="PASS_PUBLIC_ABI_MIXED_SIGNED_UNSIGNED_NORMAL_CALLS"
  assert q["paired_savings"]["min_cycles"]>0
  assert q["code_bytes"] in (1371,1405)
  assert q["ordinary_32bit_core_unchanged"] and q["source_fully_relocated"]
  assert r["status"]=="PASS_REAL_X64SC_SEQUENTIAL_MIXED_S32_U32"
  assert r["signed_output_inputs_carry_equal"]
  assert (r["baseline"]["native_vectors"],r["independent"]["native_vectors"])==(24,24)
  source,code,entry,layout,donor_sha=make_source(p)
  path=SRC+"/"+p+".asm"
  assert (R/path).read_text()==source
  assert q["source_sha256"]==r["source_sha256"]==digest(path)
  assert q["donor_public_source_sha256"]==donor_sha
  assert q["clone_entry"]==hex(entry)
  assert q["code_range"]==[hex(min(code)),hex(max(code))]
  assert q["baseline"]["mean_cycles"]>q["independent"]["mean_cycles"]
  rows[p]={"ordinary_signed_baseline":q["baseline"]["mean_cycles"],
           "independent_signed_shr16":q["independent"]["mean_cycles"],
           "paired_saving":q["paired_savings"]["mean_cycles"],
           "minimum_saving":q["paired_savings"]["min_cycles"],
           "p95_baseline":q["baseline"]["p95_cycles"],
           "p95_independent":q["independent"]["p95_cycles"],
           "executable_bytes":len(code),
           "entry":hex(entry),"code_end":hex(max(code))}
  assert digest(p+"/resident/math_"+p+"_game_math.prg")==resident[p]
 doc=[
  "# Issue144 A — independent signed32 SHR16 direct producer; mixed-call safe",
  "",
  "**Individually accessible opt-in implementation for ALL signed 32-bit inputs.**",
  "Unlike the exclusive overlay, this source makes a separate copy of the",
  "original published full signed producer rather than modifying it.",
  "The nine (V2/V3/V4) or ten (V1/V5) executable source islands and",
  "their absolute self-modifying operand-byte references are relocated",
  "into caller-owned RAM. The producer writes only the exact six output",
  "bytes from product bits 16–63 without an intermediate eight-byte",
  "full product + six-byte copy.",
  "",
  "The original SMUL32 and UMUL32 residents remain executable;",
  "sequential calls to both normal producers were interleaved in all",
  "CPU-model and native VICE comparisons. Ordinary SHR16 public JMP",
  "address remains $5E15; an optional *in-memory* two-byte target patch",
  "at $5E16/$5E17 directs calls to the independent entry.",
  "This opt-in does not alter binary files on disk.",
  "",
  "## Paired same-input public-call CPU-model cycles",
  "",
  "| Profile | Original | Independent | Saved | Smallest gain | Code bytes |",
  "|---|---:|---:|---:|---:|---:|"]
 for p in PROFILES:
  a=rows[p]
  doc.append("| %s | %.3f | %.3f | %.3f | %s | %d |"%
             (p,a["ordinary_signed_baseline"],a["independent_signed_shr16"],
              a["paired_saving"],a["minimum_saving"],a["executable_bytes"]))
 doc += [
  "",
  "**12,045 paired 32-bit signed corpus calls** across five profiles",
  "(2,409 same operand pairs/profile). Every candidate call is faster;",
  "all six output bytes, inputs, carry=0 and stack match, and normal",
  "SMUL32/UMUL32 calls succeed when interleaved.",
  "Independent native x64sc correctness: 240 baseline/candidate calls",
  "across V1–V5, with ordinary signed and unsigned full multiplication",
  "interleaved *before every* SHR16 invocation. Native cycles NOT measured.",
  "Unlike an earlier exclusive overlay, **no BEGIN/END batch overhead**.",
  "",
  "## Resource and caller integration contract",
  "",
  "Source assemblies are individually usable per profile; assembly",
  "placement is an *example*, not permanently reserved library RAM.",
  "Current emitted code uses $0800..$0DC0 (1405 bytes for V1/V5,",
  "1371 for V2/V3/V4) with gaps between relocated islands.",
  "**On a normal C64 $0801 is BASIC program RAM**; verify caller",
  "ownership and no loader/screen/stack/IRQ/data conflicts, or rebuild",
  "and requalify with a different placement before adoption.",
  "Requires original MATH_INIT, shared installed lookup tables",
  "and the ordinary mathematical scratch ZP. **NOT interrupt/NMI",
  "reentrant:** simultaneous math calls can corrupt shared zero page.",
  "Disable or synchronize other callers while modifying the signed",
  "SHR16 public JMP operands; the two-byte target update is not atomic.",
  "Normal full signed and unsigned producers remain usable between",
  "completed independent SHR16 calls, unlike in the exclusive overlay.",
  "No regular resident PRG, REU payload, public symbol location, normal",
  "ZP budget, or ordinary performance leaderboard is changed.",
  "",
  "Assembler sources: "+SRC+"/<profile>.asm",
  "Independent generator and common-input CPU model:",
  "  tools/issue144_independent_signed_shr16.py",
  "Independent real native VICE mixed-call harness:",
  "  tools/native_issue144_independent_signed_shr16.py",
  "CPU proof: "+MODEL,
  "VICE proof: "+VICE,
  "No private OptiSearch source, donor archive or proprietary method is published."
 ]
 (R/DOC).write_text("\n".join(doc)+"\n")
 (R/SRC/"README.md").write_text(
  "# Signed 32x32 SHR16 independent mixed-call-safe source\n\n"+
  "See ../../"+DOC+
  ". Loader must reserve caller RAM for the emitted islands, "+
  "initialise the resident library, and optionally repoint only "+
  "the public $5E15 JMP target after protecting against concurrent calls. "+
  "Original SMUL32/UMUL32 routines coexist for sequential mixed calls; "+
  "shared ZP prevents IRQ/NMI reentrancy.\n")
 state["issue144_all_sign_shr16_independent_mixed_2026_10_15"]={
  "status":"PASS_MODEL_NATIVE_OPTIONAL_SOURCE_SEQUENTIAL_MIXED",
  "profiles":list(PROFILES),
  "model_pairs":12045,"native_old_new_calls":240,
  "ordinary_public_full_producers_unchanged":True,
  "shared_normal_zero_page":True,"IRQ_reentrant":False,
  "extra_code_bytes_by_profile":{p:rows[p]["executable_bytes"] for p in PROFILES},
  "mean_cycle_comparison":rows,"documentation":DOC,
  "source_directory":SRC,"CPU_proof":MODEL,"VICE_proof":VICE,
  "stock_PRGs_and_REUs_unchanged":True,
  "native_CPU_cycles_measured":False}
 (R/"RELEASE_STATUS.json").write_text(json.dumps(state,indent=2)+"\n")
 note=(STAMP+"\n- Source-only all-sign SMUL32_SHR16 independent producer: "+
   "1,371–1,405 bytes additional caller-owned code RAM, 12,045 paired "+
   "CPU-model calls across V1–V5 saving 53.69–56.00 mean cycles; "+
   "240 native x64sc old/new calls with normal SMUL32 and UMUL32 "+
   "interleaved. Original full producers untouched (sequential mixed-call "+
   "safe, not IRQ/NMI reentrant). No default PRG, REU, ABI, ZP or ordinary "+
   "PERFORMANCE leaderboard changes. "+DOC+"\n\n")
 for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=R/name
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
 assert all(digest(p+"/resident/math_"+p+"_game_math.prg")==resident[p] for p in PROFILES)
 assert dict(read("RELEASE_STATUS.json").get("reference_reu_sha256",{}))==reu
 print("ISSUE144 SIGNED INDEPENDENT CPU/NATIVE/CHANGES/RELEASE SEALED")
if __name__=="__main__":main()
