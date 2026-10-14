#!/usr/bin/env python3
"""Stage and seal V2/V3/V4 opt-in batch after exact model + VICE proof."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")
MODEL="validation/review/ISSUE144_V234_SHR16_BATCH_CPU_MODEL.json"
NATIVE="validation/review/ISSUE144_V234_SHR16_BATCH_NATIVE_VICE.json"
ASM="optional/issue144_v234_umul32_shr16_exclusive/overlay_begin_end.asm"
README="optional/issue144_v234_umul32_shr16_exclusive/README.md"
DOC="docs/ISSUE144_V234_SHR16_EXCLUSIVE_BATCH_2026-10-15.md"
STAMP="2026-10-15 ISSUE144 V2-V4 EXCLUSIVE MULTIPLY SHR16 RESEARCH"
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 m=read(MODEL);n=read(NATIVE);sp=R/"RELEASE_STATUS.json";s=read("RELEASE_STATUS.json")
 assert m["status"]=="PASS_V234_EXCLUSIVE_RESEARCH"
 assert n["status"]=="PASS_NATIVE_VICE_V234_EXCLUSIVE_BATCH"
 assert m["cases_each"]==2409 and n["total_native_calls"]==144
 assert set(m["profiles"])==set(n["profiles"])==set(P)
 assert m["source_sha256"]==sha(ASM)
 assert not m["public_profile_promotion"] and not n["normal_public_abi_promoted"]
 for p in P:
  row=m["profiles"][p]
  assert row["savings_every_case"]==53
  assert row["paired_savings"]["min_cycles"]==row["paired_savings"]["max_cycles"]==53
  assert row["setup_cycles"]==76 and row["restore_cycles"]==80
  assert row["strict_break_even_calls_with_both_caller_jsrs"]==4
  assert row["ordinary_umul32_revalidated_after_end"]
  assert n["profiles"][p]["status"]=="PASS_NATIVE_EXCLUSIVE_SOURCE_BEGIN_END"
  assert n["profiles"][p]["baseline_calls"]==n["profiles"][p]["candidate_calls"]==24
  assert n["profiles"][p]["source_sha256"]==sha(ASM)
  path=p+"/resident/math_"+p+"_game_math.prg"
  assert sha(path)==s["reference_prg_sha256"][p]==row["released_prg_sha256"]
 doc=[
  "# Issue #144: V2/V3/V4 exclusive SHR16 direct-output batch",
  "",
  "**Research/opt-in source, not the default public library.**",
  "Original V2 experiment: PR #145. Extended V2/V3/V4 exact",
  "installed core verification and native test: PR #146.",
  "",
  "The unsigned multiplier still computes lower-column carries, but",
  "the six final output bytes are written directly to shifted-result",
  "destinations. BEGIN redirects six absolute stores, suppresses two",
  "low-output stores and tail-dispatches the existing producer.",
  "END restores the exact original executable bytes.",
  "",
  "| Profile | Baseline CPU cycles | Exclusive CPU cycles | Saving | Pairs | Native calls |",
  "|---|---:|---:|---:|---:|---:|"
 ]
 for p in P:
  row=m["profiles"][p]
  doc.append("| "+p+" | "+f"{row['baseline']['mean_cycles']:.3f} | "+
             f"{row['candidate']['mean_cycles']:.3f} | 53 | 2,409 | 48 |")
 doc += [
  "",
  "Every tested operand pair in each profile saved exactly 53",
  "CPU-model public-entry cycles. Total: 7,227 matched pairs.",
  "Both original and source-assembled BEGIN/CALL/END results were",
  "verified in native x64sc, 144 calls total. Native instruction",
  "cycles and REU DMA/bus timing were NOT measured.",
  "",
  "BEGIN costs 76 cycles, END costs 80 cycles. Four shifted products",
  "amortize the two setup calls including their caller JSR instructions.",
  "",
  "Critical limitations: source targets only the exact released",
  "V2/V3/V4 binaries. Call MATH_INIT first and place patch code in free",
  "RAM. While BEGIN-END is active, do not call regular UMUL32,",
  "UMUL32_READY, or any other transitively shared producer consumer;",
  "the patch is non-reentrant and unsafe for interrupts using this",
  "producer. V1/V5 have different code and cannot use this source.",
  "There is no mixed-call-safe default API replacement here.",
  "",
  "Production resident PRGs, REU payloads, normal ZP budgets, stable",
  "API addresses, and PERFORMANCE.md are unchanged. No private",
  "OptiSearch material has been published.",
  "",
  "Source: "+ASM,
  "CPU-model evidence: "+MODEL,
  "Native x64sc evidence: "+NATIVE
 ]
 (R/DOC).write_text("\n".join(doc)+"\n")
 (R/README).write_text(
  "# V2/V3/V4 unsigned SHR16 exclusive batch\n\n"
  "This optional assembly source is SHA-pinned to the installed"
  " V2/V3/V4 resident binaries. Assemble overlay_begin_end.asm in"
  " free RAM, call MATH_INIT, then MUL32_SHR16_BEGIN; make at least"
  " four MATH_UMUL32_SHR16 calls; finish with MUL32_SHR16_END."
  " During the active interval normal UMUL32, UMUL32_READY and any"
  " shared-producer clients, including IRQ/NMI callers, MUST NOT run."
  " The patch changes shared executable bytes and is non-reentrant."
  " No default public profile is changed. See ../../"+DOC+".\n")
 s["issue144_v234_umul32_shr16_exclusive_2026_10_15"]={
   "status":"PASS_RESEARCH_ONLY_EXCLUSIVE_NATIVE_MODEL",
   "profiles":list(P),"pairs_per_profile":2409,"paired_calls_total":7227,
   "savings_per_public_call_cycles":53,"begin_cycles":76,"end_cycles":80,
   "minimum_batch_size_including_jsr":4,
   "native_baseline_candidate_calls_total":144,
   "native_cycles_measured":False,"reu_bus_timing_measured":False,
   "normal_umul32_usable_while_patch_active":False,
   "regular_public_api_promoted":False,
   "normal_resident_prgs_modified":False,"normal_reu_images_modified":False,
   "optisearch_private_source_published":False,
   "source":ASM,"documentation":DOC,"model_proof":MODEL,"native_proof":NATIVE}
 sp.write_text(json.dumps(s,indent=2)+"\n")
 note=(STAMP+"\n- Source-backed optional V2/V3/V4 UMUL32_SHR16"
       " exclusive batch saves 53 CPU-model cycles on 7,227 matched"
       " operand pairs; BEGIN/END 76/80 cycles, four-call crossover"
       " including caller JSRs. 144 native x64sc old/new calls pass."
       " Shared UMUL32 core is unsafe for other calls while patched;"
       " no default PRG, REU, ZP or public ABI modification."
       " See "+DOC+"\n\n")
 for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=R/name
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
 print("ISSUE144 V234 RESEARCH SEALED; ORDINARY LIBRARY UNCHANGED",flush=True)
if __name__=="__main__":main()
