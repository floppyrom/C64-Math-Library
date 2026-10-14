#!/usr/bin/env python3
"""Issue144 research-only seal: source-backed exclusive V2 SHR16 batch records.

Never rewrites any resident PRG, REU, standalone public routine, or performance
baseline. The mode is mutually exclusive with ordinary UMUL32.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
from benchmark_multiply_refresh import CORPORA

FILES={
 "paired":"validation/review/ISSUE144_SHR16_DIRECT_SLICE_OVERLAY_RESEARCH.json",
 "batch":"validation/review/ISSUE144_V2_SHR16_BATCH_BREAK_EVEN.json",
 "native_probe":"validation/review/ISSUE144_SHR16_OVERLAY_NATIVE_VICE_RESEARCH.json",
 "native_batch":"validation/review/ISSUE144_V2_SHR16_BEGIN_END_NATIVE_VICE.json",
}
DOC="docs/ISSUE144_V2_SHR16_EXCLUSIVE_BATCH_RESEARCH.md"
README="optional/issue144_v2_umul32_shr16_exclusive/README.md"
SOURCE="optional/issue144_v2_umul32_shr16_exclusive/overlay_begin_end.asm"
STAMP="2026-10-14 ISSUE144 V2 EXCLUSIVE SHR16 DIRECT-SLICE RESEARCH"
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k",
          "v4_reu_16m","v5_hybrid_lowzp")

def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def obj(p):return json.loads((ROOT/p).read_text())

def main():
 evidence={name:obj(path) for name,path in FILES.items()}
 model=evidence["paired"]
 batch=evidence["batch"]
 native=evidence["native_probe"]
 nb=evidence["native_batch"]
 release_path=ROOT/"RELEASE_STATUS.json"
 release=obj("RELEASE_STATUS.json")
 assert model["status"]=="PASS" and model["pairs_per_profile"]==len(CORPORA[32])==2409
 assert set(model["profile_means"])==set(PROFILES)
 assert model["overlay"]["status"]=="PASS_EXCLUSIVE_OVERLAY_ONLY"
 assert model["overlay"]["per_call_savings"]["mean_cycles"]==53
 assert model["overlay"]["per_call_savings"]["min_cycles"]==53
 assert model["overlay"]["per_call_savings"]["max_cycles"]==53
 assert batch["status"]=="PASS_EXCLUSIVE_BATCH_CPU_MODEL"
 assert batch["tested_pairs"]==len(CORPORA[32])
 assert batch["setup_cpu_cycles_excl_caller_jsr"]==76
 assert batch["restore_cpu_cycles_excl_caller_jsr"]==80
 assert batch["first_call_count_with_positive_net_savings_excl_caller_jsrs"]==3
 assert batch["first_call_count_with_positive_net_savings_including_two_caller_jsrs"]==4
 assert batch["source_sha256"]==sha(SOURCE)
 assert native["status"]=="PASS_NATIVE_VICE_EXCLUSIVE_OVERLAY_ONLY"
 assert nb["status"]=="PASS_NATIVE_EXCLUSIVE_BEGIN_CALL_END"
 assert native["native_vice_calls"]==48 and nb["calls"]==48
 assert native["profile"]==nb["profile"]=="v2_pareto_fast"
 assert not nb["native_cycle_timing_measured"]
 assert not nb["default_prg_changed"]
 assert not batch["ordinary_UMUL32_legal_while_active"]
 for p in PROFILES:
  path=p+"/resident/math_"+p+"_game_math.prg"
  assert sha(path)==release["reference_prg_sha256"][p]
 assert native["published_prg_sha256"] if "published_prg_sha256" in native else True
 assert nb["published_prg_sha256"]==release["reference_prg_sha256"]["v2_pareto_fast"]
 v=model["profile_means"]["v2_pareto_fast"]
 ordinary=v["MATH_UMUL32_SHR16"]["mean_cycles"]
 special=ordinary-53
 gain=100*53/ordinary
 table=[
 "# Issue #144 — Exclusive V2 direct-result-slice UMUL32_SHR16 research",
 "",
 "**Research qualification PASS; not a composable standard library routine.**",
 "",
 "The current public shifted-output routine computes a full unsigned 64-bit",
 "product and then performs six output-byte copies. An exclusive source-backed",
 "overlay redirects the six high-result stores into the desired shifted",
 "destination and suppresses the two discarded-result stores. A tail-dispatch",
 "removes the secondary output copy loop. The low-order multiplication",
 "arithmetic still executes and preserves its carries into bit 16.",
 "",
 "## Paired public-call baseline (same 2,409 pairs across every profile)",
 "",
 "| Profile | UMUL32 | UMUL32_SHR16 | SMUL32 | SMUL32_SHR16 |",
 "|---|---:|---:|---:|---:|"]
 for p in PROFILES:
  row=model["profile_means"][p]
  table.append("| "+p+" | "+" | ".join(
       f"{row[name]['mean_cycles']:.3f}"
       for name in ("MATH_UMUL32","MATH_UMUL32_SHR16",
                    "MATH_SMUL32","MATH_SMUL32_SHR16"))+" |")
 table += [
 "",
 "These timings are CPU-model public entry through RTS; caller JSR and",
 "input writes are excluded. This is a *single matched 2,409-pair corpus*.",
 "Different historical performance rows use different samples.",
 "",
 "## V2 exclusive overlay result",
 "",
 f"- Regular public MATH_UMUL32_SHR16: **{ordinary:.3f} CPU-model cycles**.",
 f"- Exclusive direct-slice candidate: **{special:.3f} CPU-model cycles**.",
 f"- Saving: **53 cycles ({gain:.2f}%) for each of 2,409 pairs**.",
 "- BEGIN cost: **76 cycles**; END cost: **80 cycles**",
 "  (entry-through-RTS, excluding each caller JSR).",
 "- Crossover: positive batch saving starting at **3 calls** under the",
 "  entry-only convention, or **4 calls** counting both caller JSRs.",
 "- Native x64sc baseline/temporarily patched proof: 48 calls PASS.",
 "- Native x64sc baseline/source-assembled BEGIN/CALL/END proof:",
 "  48 calls PASS. Native cycle timing **was not** measured.",
 "- V2 ordinary public producer was revalidated after END under",
 "  CPU-model execution. This does not prove IRQ/reentrancy safety.",
 "",
 "## Exact operating restrictions",
 "",
 "This kit targets **only the SHA-pinned V2 profile**. Call MATH_INIT",
 "before BEGIN. Between BEGIN and END, do **not** invoke MATH_UMUL32,",
 "MATH_UMUL32_READY or any other routine transitively relying on its",
 "shared 32-bit unsigned producer. Disable any IRQ/NMI use of that core;",
 "the overlay is non-reentrant. Ensure patched RAM is visible and the",
 "kit's chosen code address does not overlap your program. The example",
 "origin $0900 may be changed before assembly.",
 "",
 "The current source writes 13 executable bytes to a *shared* core.",
 "Patch installation/removal and possible code/data mapping hazards",
 "make it unsuitable for automatic use in a mixed-call public profile.",
 "For an eventual standalone builder, a private-core duplicate or",
 "an explicitly exclusive selected-routine bundle is required.",
 "",
 "The published production PRGs, REU payloads, ABI, ordinary normal ZP",
 "budgets and PERFORMANCE.md are **unchanged**. OptiSearch P40 remains",
 "private; no private code is included here.",
 "",
 "## Reproduction",
 "",
 "- Source: "+SOURCE,
 "- CPU model: tools/issue144_shr16_direct_slice_overlay_research.py",
 "- ASM batch crossover: tools/qualify_issue144_v2_shr16_batch.py",
 "- Native VICE: tools/native_issue144_shr16_overlay.py and",
 "  tools/native_issue144_shr16_batch_source.py",
 "- Proof records: "+", ".join(FILES.values()),
 ]
 (ROOT/DOC).write_text("\n".join(table)+"\n")
 (ROOT/README).write_text(
 "# V2 UMUL32_SHR16 exclusive overlay (research opt-in)\n\n"
 "Requires the SHA-pinned stock V2 resident and a prior MATH_INIT call."
 " Assemble overlay_begin_end.asm at a free RAM origin, then invoke"
 " MUL32_SHR16_BEGIN, make a batch of at least four"
 " MATH_UMUL32_SHR16 calls, and invoke MUL32_SHR16_END."
 " **Do not call normal UMUL32 or any shared-producer consumer"
 " during the active interval, including from IRQ/NMI.**"
 " The BEGIN/END code patches 13 bytes of the installed shared"
 " executable and is non-reentrant. Production profiles remain"
 " unchanged. Read ../../"+DOC+" for actual proof and limits.\n")
 release["issue144_v2_unsigned32_shr16_exclusive_2026_10_14"]={
  "status":"PASS_RESEARCH_ONLY_EXCLUSIVE_NOT_NORMAL_PUBLIC",
  "profile":"v2_pareto_fast","paired_cases":2409,
  "measured_saving_cycles_per_call":53,
  "setup_cpu_cycles_excluding_caller_jsr":76,
  "restore_cpu_cycles_excluding_caller_jsr":80,
  "positive_net_batch_from_calls_including_caller_jsrs":4,
  "native_public_probe_calls":48,
  "native_begin_end_calls":48,
  "native_cycle_timing_measured":False,
  "mixed_calls_safe":False,
  "production_prgs_changed":False,
  "regular_public_abi_promoted":False,
  "source":SOURCE,"documentation":DOC,
  "evidence":FILES}
 release_path.write_text(json.dumps(release,indent=2)+"\n")
 note=(STAMP+"\n- Research-only opt-in V2 unsigned 32x32 SHR16"
       " direct-result-slice overlay measured 53 CPU-model cycles"
       " faster for all 2,409 paired operands; BEGIN/END overhead"
       " 76/80 cycles, four-call full-program crossover. Native VICE"
       " baseline/overlay and assembled BEGIN/CALL/END both passed"
       " 48 calls. Affects shared UMUL32 producer while active;"
       " ordinary public mixed-call ABI NOT qualified, no resident"
       " PRG/REU/default profile changed and no automatic promotion."
       " See "+DOC+"\n\n")
 for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=ROOT/name
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(["make","clean"],cwd=ROOT,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=ROOT,check=True)
 print("ISSUE144 RESEARCH SEALED, NORMAL PUBLIC MULTIPLY UNCHANGED",flush=True)
if __name__=="__main__":main()
