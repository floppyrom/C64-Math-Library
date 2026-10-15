#!/usr/bin/env python3
"""Seal native-qualified unrestricted signed SHR16 exclusive research, no default promotion."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from issue144_signed_full_exclusive import PROFILES,sha
from stage_issue39_v1_3216_ool_release import reseal
MODEL="validation/review/ISSUE144_SIGNED_SHR16_FULL_EXCLUSIVE_MODEL.json"
ASM="validation/review/ISSUE144_SIGNED_SHR16_FULL_EXCLUSIVE_INSTALLER.json"
VICE="validation/review/ISSUE144_SIGNED_SHR16_FULL_EXCLUSIVE_NATIVE_VICE.json"
DOC="docs/ISSUE144_SIGNED_FULL_DOMAIN_EXCLUSIVE_2026-10-15.md"
TAG="2026-10-15 ISSUE144 SIGNED SHR16 FULL DOMAIN EXCLUSIVE PRODUCER"
def data(p):return json.loads((R/p).read_text())
def file_sha(p):return sha((R/p).read_bytes())
def main():
 model,installer,native=map(data,(MODEL,ASM,VICE))
 assert model["status"]=="PASS_ALL_SIGNED_DOMAIN_EXCLUSIVE_ONLY"
 assert installer["status"]=="PASS_ASSEMBLED_BEGIN_END_AND_FULL_SIGNED_RESTORATION"
 assert native["status"]=="PASS_NATIVE_ALL_SIGNED_DOMAIN_EXCLUSIVE_ONLY"
 assert model["pairs_per_profile"]==2409
 assert native["baseline_and_candidate_calls"]==144
 assert set(model["profiles"])==set(installer["profiles"])==set(native["profiles"])==set(PROFILES)
 status=data("RELEASE_STATUS.json")
 resident_before=dict(status["reference_prg_sha256"])
 reu_before=dict(status.get("reference_reu_sha256",{}))
 for p in PROFILES:
  row=model["profiles"][p]
  cycle=row["paired_savings"]
  assert row["status"]=="PASS_ALL_SIGNED_OUTPUT_CARRY_INPUTS_STACK"
  assert cycle["mean_cycles"]==cycle["min_cycles"]==cycle["max_cycles"]==53
  assembly=installer["profiles"][p]
  assert (assembly["begin_cycles"],assembly["end_cycles"])==(218,224)
  assert assembly["patched_bytes"]==49 and assembly["code_bytes"]==334
  assert native["profiles"][p]["status"]=="PASS_NATIVE_SIX_OUTPUT_BYTES_CARRY_INPUTS_SP"
  assert row["source_sha256"]==file_sha("optional/issue144_signed_shr16_exclusive/"+p+".asm")
  assert file_sha(p+"/resident/math_"+p+"_game_math.prg")==resident_before[p]
 baseline=model["profiles"][PROFILES[0]]["baseline"]["mean_cycles"]
 optimized=model["profiles"][PROFILES[0]]["candidate"]["mean_cycles"]
 lines=[
  "# Issue144: unrestricted signed 32×32 SHR16 output-slice EXCLUSIVE overlay",
  "",
  "**Source-only opt-in batch accelerator; NOT a safe default MATH_SMUL32 replacement.**",
  "",
  "For all sign quadrants and arbitrary 32-bit signed operands, the",
  "ordinary public MATH_SMUL32_SHR16 address $5E15 is preserved.",
  "The 6510 source-backed overlay redirects final full-product stores",
  "within each of four distinct signed producer paths directly into",
  "$C008..$C00D and changes the SHR16 adapter JSR into a JMP so",
  "the normal six-byte output copy is skipped.",
  "Exactly **53 CPU-model cycles saved per call**, independent of operands.",
  "",
  "| Profile | Baseline cycles | Opt-in cycles | Saved |",
  "|---|---:|---:|---:|"]
 for p in PROFILES:
  v=model["profiles"][p]
  lines.append("| "+p+" | %.3f | %.3f | %.3f |"%
   (v["baseline"]["mean_cycles"],v["candidate"]["mean_cycles"],v["paired_savings"]["mean_cycles"]))
 lines += [
  "",
  "**7,227 matched signed 32-bit operand pairs across V2/V3/V4**",
  "pass exact six-byte output, input preservation, carry=0, and stack.",
  "Native x64sc: 144 baseline/opt-in executions pass output and flags;",
  "VICE proves correctness, **not CPU cycle timing**.",
  "",
  "Three separately assembled 334-byte BEGIN/END installers,",
  "original-source-derived, examples placed in caller-owned $0900..$0A4D.",
  "Each exact original resident configuration requires its own source",
  "file; they are not interchangeable. 49 existing executable bytes",
  "are patched and restored exactly. CPU model runs both actual",
  "assembled entrypoints and checks original SMUL32 and SHR16 after END.",
  "BEGIN costs **218** CPU-model cycles; END costs **224**.",
  "Counting caller JSR overhead (6 cycles each), a batch of",
  "**9 or more calls** amortizes the 454-cycle setup+teardown cost.",
  "",
  "CRITICAL: the shared ordinary signed full producer is NOT valid",
  "while this overlay is active. You MUST NOT call MATH_SMUL32,",
  "the READY alias, any other shared signed consumer, or invoke",
  "signed math from IRQ/NMI during BEGIN, the batch, or END.",
  "Avoid concurrent/multitasking reentry; patch transitions are NOT atomic.",
  "This candidate is distinct from the earlier independently resident",
  "signed nonnegative-input clone: the present one accepts ALL signs",
  "but trades away mixed-call composability until disabled.",
  "",
  "Verify exact original resident SHA, original code bytes,",
  "all application live memory occupancy, RAM bank mapping,",
  "MATH_INIT, and that $0900..$0A4D is free before loading.",
  "Do not combine with the optional unsigned $0900 overlay.",
  "BEGIN/END clobber A and processor flags; they do not add ZP.",
  "",
  "Source: optional/issue144_signed_shr16_exclusive/v2_pareto_fast.asm",
  "Source: optional/issue144_signed_shr16_exclusive/v3_reu_512k.asm",
  "Source: optional/issue144_signed_shr16_exclusive/v4_reu_16m.asm",
  "Generator/model: tools/issue144_signed_full_exclusive.py",
  "Native VICE: tools/native_issue144_signed_full_exclusive.py",
  "CPU proof: "+MODEL,"Installer proof: "+ASM,"Native proof: "+VICE,
  "",
  "Default resident PRGs/REUs, normal API, zero page, public",
  "PERFORMANCE leaderboard and main library binary are unchanged.",
  "No private OptiSearch generator/source is published."
 ]
 path=R/DOC;path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text("\n".join(lines)+"\n")
 (R/"optional/issue144_signed_shr16_exclusive/README.md").write_text(
   "# All-sign SHR16 exclusive signed producer\n\nSee ../../"+DOC+
   ". Do NOT mix normal SMUL32 while BEGIN has been applied. "+
   "Call END before returning to ordinary signed math. Each profile's "+
   "assembly is exactly source-coupled to that binary image.\n")
 status["issue144_all_sign_signed32_shr16_exclusive_2026_10_15"]={
  "status":"PASS_CPU_NATIVE_ASM_SOURCE_EXCLUSIVE_ONLY_NO_DEFAULT_PROMOTION",
  "profile_names":list(PROFILES),"full_signed_operand_domain":True,
  "per_call_saved_cycles":53,"setup_begin_cycles":218,"setup_end_cycles":224,
  "source_installer_bytes":334,"patch_resident_bytes":49,
  "mixed_smultiplication_calls_during_enabled_period_valid":False,
  "model_paired_cases":7227,"native_before_after_calls":144,
  "extra_normal_ZP":0,"native_cycles_measured":False,
  "ordinary_resident_prgs_or_reu_changed":False,
  "documentation":DOC,"cpu_proof":MODEL,
  "installer_proof":ASM,"native_proof":VICE}
 (R/"RELEASE_STATUS.json").write_text(json.dumps(status,indent=2)+"\n")
 note=(TAG+"\n- Source-only unrestricted all-sign SMUL32_SHR16 exclusive overlay V2/V3/V4: "+
       "53 CPU-model cycles faster per public call across 7,227 paired calls, "+
       "144 native x64sc original/candidate calls PASS. Reversible 334-byte "+
       "BEGIN/END, changes 49 in-memory code bytes, 218/224 cycle setup/teardown. "+
       "Shared SMUL32 cannot be called while overlay enabled, no regular "+
       "profile/ABI/ZP or PERFORMANCE promotion. "+DOC+"\n\n")
 for fn in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  p=R/fn
  if TAG not in p.read_text():p.write_text(note+p.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
 assert all(file_sha(p+"/resident/math_"+p+"_game_math.prg")==sha for p,sha in resident_before.items())
 assert dict(data("RELEASE_STATUS.json").get("reference_reu_sha256",{}))==reu_before
 print("ISSUE144 SIGNED FULL-DOMAIN EXCLUSIVE SOURCE/CPU/NATIVE/CHANGELOGS/SHA SEALED")
if __name__=="__main__":main()
