#!/usr/bin/env python3
"""Seal native-qualified signed SHR16 domain specialist (never modify resident PRGs)."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
from issue144_shr16_independent_clone import PROFILES,sha
from issue144_signed_shr16_hybrid_research import SOURCE

SCREEN="validation/review/ISSUE144_SIGNED_SHR16_HYBRID_RESEARCH.json"
VICE="validation/review/ISSUE144_SIGNED_SHR16_HYBRID_NATIVE_VICE.json"
NONNEG="validation/review/ISSUE144_SIGNED_NONNEGATIVE_SHR16_OPTIN_MODEL.json"
NONNEG_VICE="validation/review/ISSUE144_SIGNED_NONNEGATIVE_SHR16_NATIVE_VICE.json"
INSTALL="validation/review/ISSUE144_SIGNED_NONNEGATIVE_INSTALLER_MODEL.json"
PATCH="optional/issue144_signed_shr16_hybrid/nonnegative_enable_disable.asm"
DOC="docs/ISSUE144_SIGNED_SHR16_SPECIALISTS_2026-10-15.md"
STAMP="2026-10-15 ISSUE144 SIGNED SHR16 NONNEGATIVE SPECIALIST AND QUADRANT RESEARCH"
def data(p):return json.loads((R/p).read_text())
def digest(p):return sha((R/p).read_bytes())

def main():
 a,b,c,d,e=map(data,(SCREEN,VICE,NONNEG,NONNEG_VICE,INSTALL))
 assert a["status"]=="PASS_RESEARCH_MODEL_ONLY_NO_PROMOTION"
 assert b["status"]=="PASS_NATIVE_SIGNED_SHR16_OPTIONAL_SOURCE_CORRECTNESS"
 assert c["status"]=="PASS_NONNEGATIVE_SIGNED_SHR16_RESEARCH_MODEL"
 assert d["status"]=="PASS_NATIVE_NONNEGATIVE_SIGNED_SHR16_OPTIN"
 assert e["status"]=="PASS_SIGNED_NONNEGATIVE_INSTALL_RESTORE_MODEL"
 assert (b["native_calls_total"],d["native_calls"],c["input_pairs"])==(216,144,715)
 assert a["source_sha256"]==digest(SOURCE)
 assert e["assembly_sha256"]==digest(PATCH)
 assert set(a["profiles"])==set(b["results"])==set(c["profiles"])==set(d["profiles"])==set(e["profiles"])==set(PROFILES)
 state=data("RELEASE_STATUS.json")
 old={p:state["reference_prg_sha256"][p] for p in PROFILES}
 def binaries_unchanged():
  return all(digest(p+"/resident/math_"+p+"_game_math.prg")==old[p] for p in PROFILES)
 assert binaries_unchanged()
 rows={}
 for p in PROFILES:
  x=a["profiles"][p];y=c["profiles"][p]
  assert x["pairs"]==2409 and y["cases"]==715
  assert y["min_savings_positive"] and y["paired_savings"]["minimum"]>0
  assert y["paired_savings"]["mean_cycles"]/y["baseline"]["mean_cycles"]>0.05
  assert e["profiles"][p]["status"]=="PASS"
  assert d["profiles"][p]["status"]=="PASS_NATIVE_PRECONDITIONED_PUBLIC_ENTRY"
  rows[p]={
   "stock_all_signed":x["stock"]["mean_cycles"],
   "hybrid_all_signed":x["variants"]["negative_pair_fallback"]["timing"]["mean_cycles"],
   "hybrid_mean_saving":x["variants"]["negative_pair_fallback"]["savings_stock_minus_candidate"]["mean_cycles"],
   "hybrid_worst_regression":-x["variants"]["negative_pair_fallback"]["savings_stock_minus_candidate"]["minimum"],
   "stock_nonnegative":y["baseline"]["mean_cycles"],
   "optin_nonnegative":y["optin"]["mean_cycles"],
   "nonnegative_mean_saving":y["paired_savings"]["mean_cycles"],
   "nonnegative_min_saving":y["paired_savings"]["minimum"]}
 lines=[
  "# Issue 144: signed 32×32 SHR16 specialist screen",
  "",
  "**Nonnegative-domain opt-in only; no change to the normal signed library.**",
  "",
  "When BOTH signed 32-bit operands have their sign bit clear, the signed",
  "product equals the unsigned product exactly. After MATH_INIT and loading",
  "the previously published unsigned independent clone at $0D05–$0E49,",
  "source-assemble the signed enable/disable at $0C00 (or free RAM).",
  "It temporarily redirects only the two JMP target bytes of the original",
  "signed public entry $5E15, from $C50C to the clone at $0E03.",
  "Both inputs MUST be nonnegative during the entire enabled period.",
  "",
  "## Qualified nonnegative domain — matched public entry cycles",
  "",
  "| Profile | Signed baseline | Specialist | Saving | % | Pairs |",
  "|---|---:|---:|---:|---:|---:|"]
 for p in PROFILES:
  v=rows[p]
  lines.append(f"| {p} | {v['stock_nonnegative']:.3f} | {v['optin_nonnegative']:.3f} | {v['nonnegative_mean_saving']:.3f} | {100*v['nonnegative_mean_saving']/v['stock_nonnegative']:.2f}% | 715 |")
 lines += [
  "",
  "715 paired nonnegative 32-bit operand pairs per profile, 2,145 exact",
  "model cases; 144 native x64sc baseline/candidate calls; 3-profile",
  "source-assembled enable/disable with restored original public JMP,",
  "input/output, carry and stack checks. Native cycles NOT measured.",
  "The standard signed and unsigned full multiplication routines remain",
  "available BETWEEN calls; code and ZP are shared and NONREENTRANT.",
  "",
  "## General signed inputs — screened but not promoted",
  "",
  "The exact sign-correction and the quadrant hybrid variants both pass",
  "7,227 model cases and 216 baseline/candidate native x64sc calls;",
  "however general correction has large worst-case regressions. The",
  "hybrid speeds the mixed-sign corpus by only ~2.12% and also regresses",
  "on negative-negative inputs. Neither replaces the default signed API.",
  "",
  "| Profile | Stock signed mean | Hybrid mean | Saving | Worst regression |",
  "|---|---:|---:|---:|---:|"]
 for p in PROFILES:
  v=rows[p]
  lines.append(f"| {p} | {v['stock_all_signed']:.3f} | {v['hybrid_all_signed']:.3f} | {v['hybrid_mean_saving']:.3f} | +{v['hybrid_worst_regression']} |")
 lines += [
  "",
  "Resource contract: V2/V3/V4 only; original quarter-square tables and",
  "MATH_INIT; reserve $0D05–$0E49 for unsigned producer and $0C00",
  "installer source, or relocate only after fresh proof. Shared regular ZP;",
  "not safe to run concurrently from IRQ/NMI. JMP update not atomic:",
  "disable interrupts/other callers while enabling or disabling.",
  "Conditional nonnegative specialist does NOT need general signed",
  "research code at $0E50–$0F18. Existing resident PRGs, REUs, public",
  "entry address, normal ZP and regular PERFORMANCE rankings unchanged.",
  "",
  "Source installer: "+PATCH,
  "Research general signed source (not default): "+SOURCE,
  "Proof model/native general: "+SCREEN+" ; "+VICE,
  "Proof model/native nonnegative: "+NONNEG+" ; "+NONNEG_VICE,
  "Installer proof: "+INSTALL,
  "Private OptiSearch source is not included."
 ]
 (R/DOC).write_text("\n".join(lines)+"\n")
 (R/"optional/issue144_signed_shr16_hybrid/README.md").write_text(
    "# Signed SHR16 opt-ins and research\n\nSee ../../"+DOC+".\n\n"
    "nonnegative_enable_disable.asm is opt-in ONLY for signed inputs >= 0; "
    "research_signed_shr16.asm holds two general-domain screened variants "
    "that are NOT promoted. Use the previously released V2-V4 unsigned "
    "clone, shared tables, original public entry $5E15, nonreentrant calls.\n")
 state["issue144_signed_shr16_nonnegative_optin_2026_10_15"]={
  "status":"PASS_NATIVE_MODEL_PRECONDITIONED_OPTIN_NOT_DEFAULT",
  "supported_profiles":list(PROFILES),"precondition":"both signed 32-bit operands nonnegative",
  "total_cpu_model_nonnegative_pairs":2145,"total_native_nonnegative_old_new_calls":144,
  "general_signed_hybrid_unpromoted":True,
  "general_signed_cpu_model_calls":7227,"general_signed_native_calls":216,
  "public_entry_address":"$5E15","clone_entry":"$0E03",
  "extra_code_ram":True,"shared_existing_zero_page":True,
  "nonreentrant":True,"default_resident_binary_changed":False,
  "native_cycles_measured":False,"metrics":rows,"doc":DOC,
  "cpu_proof":NONNEG,"native_proof":NONNEG_VICE,"installer_proof":INSTALL}
 (R/"RELEASE_STATUS.json").write_text(json.dumps(state,indent=2)+"\n")
 note=(STAMP+"\n- Domain-qualified optional signed 32x32 SHR16 public-entry alias for nonnegative input pairs: 58.372 CPU-model cycles saved on 715 paired cases/profile V2-V4, 144 native x64sc baseline/alias calls PASS, reversible source-assembled signed JMP enable/disable. General all-sign hybrid screened: 16.438 mean saved but negative-quadrant regressions, NOT promoted. Stock PRGs, REU, ABI, normal ZP and regular leaderboard unchanged. "+DOC+"\n\n")
 for filename in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=R/filename
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
 assert binaries_unchanged()
 print("ISSUE144 SIGNED OPTIN SOURCE, BOTH CHANGELOGS AND SHA SEALED")
if __name__=="__main__":main()
