#!/usr/bin/env python3
"""Release-staging for separate-RAM, sequential, 62-cycle-faster SHR16 record.

C64ML's published regular public resident binaries and REU payloads are never
modified. Source depends on the existing resident's shared lookup tables and
MATH_INIT and shares normal scratch with ordinary 32-bit routines.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
from mini6502 import Assembler
from issue144_shr16_independent_clone import assemble,patched_assembly,PROFILES,CLONE,ENTRY_CLONE,LAST,ORIGINAL

CPU="validation/review/ISSUE144_SHR16_STANDALONE_CLONE_CPU_MODEL.json"
VICE="validation/review/ISSUE144_SHR16_INDEPENDENT_CLONE_NATIVE_VICE.json"
ASM="optional/issue144_v234_umul32_shr16_independent/standalone_clone.asm"
README="optional/issue144_v234_umul32_shr16_independent/README.md"
DOC="docs/ISSUE144_UMUL32_SHR16_SEQUENTIAL_CLONE_2026-10-15.md"
STAMP="2026-10-15 ISSUE144 INDEPENDENT SHR16 MULTIPLY CLONE PARETO POINT"
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 cpu=read(CPU);native=read(VICE);sp=R/"RELEASE_STATUS.json";status=read("RELEASE_STATUS.json")
 assert cpu["status"]=="PASS_RESEARCH_SEQUENTIAL_CLONE_CPU_MODEL"
 assert native["status"]=="PASS_NATIVE_VICE_INDEPENDENT_SHR16_CLONE"
 assert cpu["cases_per_profile"]==2409
 assert native["native_pairs_total"]==144
 assert set(cpu["profiles"])==set(native["results"])==set(PROFILES)
 old,clone,labels,source,changed=assemble()
 assert labels["MATH_UMUL32_SHR16_CLONE"]==ENTRY_CLONE
 assert min(clone)==CLONE and max(clone)==CLONE+(LAST-ORIGINAL)
 dest=R/ASM
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_text(source)
 fresh,labels2,_=Assembler().assemble(dest.read_text())
 assert fresh==clone and labels2["MATH_UMUL32_SHR16_CLONE"]==ENTRY_CLONE
 assert sha(ASM)==cpu["source_sha256"]==native["source_sha256"]
 for p in PROFILES:
  q=cpu["profiles"][p]
  assert q["status"]=="PASS_SEQUENTIAL_COMPOSABLE_MODEL"
  assert q["pairs"]==2409
  assert q["savings"]["min_cycles"]==q["savings"]["max_cycles"]==62
  assert q["native_vice_candidate_qualified"] is False
  assert q["ordinary_UMUL32_and_SMUL32_interleaved"]
  assert native["results"][p]["status"]=="PASS_NATIVE_INDEPENDENT_SHR16_PUBLIC_RESULT"
  assert native["results"][p]["baseline_calls"]==native["results"][p]["clone_calls"]==24
  installed=p+"/resident/math_"+p+"_game_math.prg"
  assert sha(installed)==status["reference_prg_sha256"][p]==q["source_installed_sha256"]
  assert q["clone_origin"]==hex(CLONE) and q["clone_entry"]==hex(ENTRY_CLONE)
  assert q["clone_bytes_generated"]==len(clone)
 original_end=CLONE+(LAST-ORIGINAL)
 assert original_end==0x0E49
 assert ENTRY_CLONE==0x0E03
 doc=[
  "# Issue #144 — independent sequential SHR16 multiplier clone",
  "",
  "**Validated opt-in Pareto source, NOT an installed public replacement.**",
  "",
  "Instead of temporarily modifying the standard library's shared",
  "unsigned 32-bit multiplier (PRs #145–#146), this variant clones",
  "its two executable islands to a separate RAM region, relocates",
  "internal absolute code/self-modifying references, and directly",
  "stores the shifted 48-bit product. The original MATH_UMUL32",
  "executable remains untouched by the clone itself. The zero-page",
  "scratch and original immutable quarter-square lookup tables",
  "remain shared, so the calls must be sequential/non-reentrant.",
  "",
  "## Shipped public versus independent clone on the same 2,409 pairs",
  "",
  "| Profile | Ordinary SHR16 | Cloned SHR16 | Savings | Matched pairs | Native original/clone |",
  "|---|---:|---:|---:|---:|---:|"]
 for p in PROFILES:
  q=cpu["profiles"][p]
  doc.append("| "+p+" | "+
             f"{q['baseline']['mean_cycles']:.3f} | "+
             f"{q['independent_clone']['mean_cycles']:.3f} | "+
             f"{q['savings']['mean_cycles']:.0f} | 2,409 | 48 |")
 doc += [
  "",
  "All 7,227 model paired cases pass complete 48-bit shifted output,",
  "carry, input/stack invariants. Mixed ordinary MATH_UMUL32 and",
  "MATH_SMUL32 calls were executed before and after each clone call;",
  "the clone did not overwrite the stock executable core. Native",
  "x64sc executes 144 baseline/clone cases across all three profiles.",
  "**62 CPU-model cycles are saved per call on every input tested.**",
  "Native emulator timing is NOT measured; only correctness is native.",
  "",
  "## Exact resource and linking contract",
  "",
  f"- Clone executable RAM: $0D05–$0E49 ({original_end-CLONE+1} address bytes),",
  "  with the public-style alternate entry at $0E03; avoid overlap with",
  "  application code, screen, loader and interrupt hooks.",
  f"- Emitted instruction bytes: {len(clone)}; gaps between islands can",
  "  exist and must remain reserved for the assembled code span.",
  "- Requires the current V2, V3 or V4 C64ML resident, its ordinary",
  "  immutable quarter-square tables ($7000 region), initialized",
  "  pointer state and MATH_INIT, plus existing shared scratch ZP.",
  "- Ordinary full UMUL32 and signed SMUL32 remain callable between",
  "  invocations, unlike the 53-cycle exclusive patch. Do not execute",
  "  either normal and cloned routines simultaneously or from IRQ/NMI:",
  "  shared scratch and code self-modification make this non-reentrant.",
  "- Same result I/O ABI: unsigned 32x32 operands at $C000/$C004,",
  "  six output bytes at $C008–$C00D, C=0, preserved operands/stack.",
  "- This is an opt-in fixed-address specialist source for a future",
  "  builder, NOT an automatic regular MATH_UMUL32_SHR16 replacement.",
  "  The hard-coded clone location is one tested location, not proof",
  "  that any other location or arbitrary user layout is safe.",
  "",
  "Current production PRGs, REU images, normal ZP budgets and API",
  "addresses are unchanged. No private OptiSearch source is present.",
  "",
  "Source: "+ASM,
  "Model/test generator: tools/issue144_shr16_independent_clone.py",
  "Native x64sc: tools/native_issue144_shr16_independent_clone.py",
  "Model evidence: "+CPU,
  "Native evidence: "+VICE
 ]
 (R/DOC).write_text("\n".join(doc)+"\n")
 (R/README).write_text(
  "# Independent SHR16 unsigned 32-bit clone (V2/V3/V4)\n\n"
  "Opt-in source with fixed RAM placement $0D05–$0E49 and entry"
  " $0E03. Assemble standalone_clone.asm into free application RAM"
  " and call MATH_INIT on the SHA-pinned V2/V3/V4 library resident"
  " before use. Pass operands as for normal MATH_UMUL32_SHR16;"
  " use JSR $0E03. This uses the shared normal ZP scratch and"
  " resident lookup tables—sequential calls only, NO reentrancy,"
  " IRQ/NMI concurrent users, or arbitrary relocation without"
  " new verification. Ordinary UMUL32 and SMUL32 are safe between"
  " calls on the tested profiles. Source and proof: ../../"+DOC+".\n")
 status["issue144_sequential_independent_shr16_clone_2026_10_15"]={
  "status":"PASS_NATIVE_CPU_MODEL_OPTIN_NO_DEFAULT_PROMOTION",
  "supported_profiles":list(PROFILES),"model_paired_calls":7227,
  "saved_cpu_model_cycles_per_call":62,
  "native_old_candidate_public_calls":144,
  "executable_reserved_range":"$0D05-$0E49",
  "clone_entry":"$0E03","emitted_executable_bytes":len(clone),
  "normal_signed_unsigned_interleaving_verified":True,
  "shares_existing_zp_and_lookup_tables":True,
  "reentrant_or_interrupt_safe":False,
  "native_cycles_measured":False,"native_reu_bus_timing_measured":False,
  "public_production_prgs_changed":False,
  "default_public_abi_changed":False,"private_optisearch_published":False,
  "source":ASM,"documentation":DOC,"model_proof":CPU,"native_proof":VICE}
 sp.write_text(json.dumps(status,indent=2)+"\n")
 note=(STAMP+"\n- Opt-in original-source-derived unsigned 32x32"
       " SHR16 separate-RAM producer saves exactly 62 CPU-model"
       " cycles on 7,227 common pairs V2/V3/V4, with 144 native"
       " x64sc baseline/clone correctness calls passing. Interleaves"
       " ordinary UMUL32 and SMUL32, unlike prior exclusive overlay."
       " Uses separate $0D05–$0E49 RAM and shared ZP/tables;"
       " NOT reentrant, no shipped code/REU, normal ABI change,"
       " no private OptiSearch redistribution. "+DOC+"\n\n")
 for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  p=R/name
  if STAMP not in p.read_text():p.write_text(note+p.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
 print("ISSUE144 INDEPENDENT SEQUENTIAL CLONE SOURCE AND PACKAGE AUDIT PASS")
if __name__=="__main__":main()
