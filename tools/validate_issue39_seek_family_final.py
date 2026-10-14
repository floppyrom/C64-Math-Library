#!/usr/bin/env python3
"""Issue39: source-realistic final SEEK8/16 family resource and ABI audit.

Assess one plausible SEEK16 integer-speed-one INIT fast path without changing
production bytes. Results are resource-screening only, not a speed claim.
Reads all public benchmark/native/all-slot certificates and emits a signed
research disposition for five profiles and two relocation maps.
"""
from __future__ import annotations
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import seek_kernel as K
import generate_seek_sources as G
from mini6502 import Assembler

PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k",
          "v4_reu_16m","v5_hybrid_lowzp")
MAPS=("reference","alternate")
ROUTINES=("MATH_SEEK8_INIT","MATH_SEEK8_STEP","MATH_SEEK8_STEP_INT","MATH_SEEK8_STEP1",
          "MATH_SEEK16_INIT","MATH_SEEK16_STEP","MATH_SEEK16_STEP_INT","MATH_SEEK16_STEP1")
OLD="""        ldy S16_KI,x
        beq s16i_r0done
s16i_r0:"""
NEW="""        ldy S16_KI,x
        beq s16i_r0done
        cpy #1
        bne s16i_r0
        lda SK_DMAJH
        bne s16i_k1fast
        lda SK_DMIN
        cmp SK_DMAJL
        bcs s16i_r0
s16i_k1fast:
        lda SK_DMIN
        sta SK_REML
        jmp s16i_r0done
s16i_r0:"""

def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()

def body():
 assert K.S8_BYTES==160 and K.S16_BYTES==248
 assert K.SCRATCH_BYTES>0
 orig=K.BLOCKS["seek16_init"]
 assert orig.count(OLD)==1
 assert not any(label in orig for label in ("s16i_k1fast:",))
 result={}
 try:
  # The proposed specialized branch handles k0=1, including exactly
  # diagonal moves (dmin==dmaj) by falling back to the old helper.
  for profile in PROFILES:
   base="v1_balanced" if profile==PROFILES[-1] else profile
   layout=G.LAYOUTS[base]
   cfgs={}
   for kind in MAPS:
    cfg=(ROOT/"relocatable_source"/base/("math_config_"+kind+".inc")).read_text()
    cfgs[kind]=cfg
   readme=(ROOT/profile/"resident/movement/native/README.md").read_text()
   match=re.search(r"^\| seek16_init \|[^|]+\| \$([0-9A-Fa-f]{4})-\$([0-9A-Fa-f]{4}) \| (\d+) \|$",readme,re.M)
   assert match,(profile,"readme drift")
   historical_length=int(match.group(3))
   available_bytes=312 if base=="v1_balanced" else (
       542 if base=="v2_pareto_fast" else 273)
   row={"current_bytes":historical_length,
        "single_island_capacity_bytes":available_bytes,
        "same_island_headroom_bytes":available_bytes-historical_length,
        "profile_resource_class":base,"source_maps":{}}
   for kind in MAPS:
    cfg=cfgs[kind]
    baseline_mem,baseline_labels,_=Assembler().assemble(
        cfg+"\n"+K.library(base,layout,*G.SCRATCH[base]))
    baseline_start=baseline_labels["seek16_init"]
    K.BLOCKS["seek16_init"]=orig.replace(OLD,NEW)+"\ns16_k1_end:\n"
    try:
     mem,labels,_=Assembler().assemble(cfg+"\n"+K.library(base,layout,*G.SCRATCH[base]))
     new_bytes=labels["s16_k1_end"]-labels["seek16_init"]
     assert labels["seek16_init"]==baseline_start
     # Source-layout candidate cannot go beyond the first pinned neighbor.
     # Even if it fits, isolated 6502 timing and full ABI validation
     # remain mandatory; this screen makes NO speed claim.
     row["source_maps"][kind]={
       "old_start":hex(baseline_start),"candidate_bytes":new_bytes,
       "candidate_growth_bytes":new_bytes-historical_length,
       "fits_existing_island":new_bytes<=available_bytes,
       "candidate_assembled":True}
    finally:K.BLOCKS["seek16_init"]=orig
   result[profile]=row
 finally:
  K.BLOCKS["seek16_init"]=orig
 return result

def main():
 source_status=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
 bench=json.loads((ROOT/"validation/movement/SEEK_PROFILE_BENCHMARK.json").read_text())
 placement=json.loads((ROOT/"validation/movement/SEEK_PLACEMENT.json").read_text())
 slots=json.loads((ROOT/"validation/review/ISSUE39_SEEK_ALL_SLOTS_RESEARCH_2026-10-14.json").read_text())
 native=json.loads((ROOT/"validation/review/ISSUE39_SEEK_ALL_MODES_NATIVE_VICE_2026-10-14.json").read_text())
 mixed=json.loads((ROOT/"validation/review/ISSUE136_SEEK_DIVMOD_MIXED_PROOF.json").read_text())
 assert bench["status"]=="PASS" and placement["status"]=="PASS"
 assert slots["status"]=="PASS_SEEK_ALL_EIGHT_SLOTS"
 assert slots["totals"]=={"init_calls":480,"step_calls":246480,"model_frames":86960}
 assert mixed["totals"]["interleaved_divmod_calls"]==18280
 assert native["status"]=="PASS_NATIVE_SEEK8_16_ALL_STEP_MODES"
 assert native["native_public_step_calls"]==640
 assert native["native_public_init_calls"]==40
 assert not native["native_cycle_timing_measured"]
 assert source_status["issue39_seek16_euclid_scale_2026_10_14"]["issue136_v1v5_division_seek_collision_repaired"]
 assert source_status["issue39_seek_native_all_modes_2026_10_14"]["unchanged_production_binaries"]
 screening=body()
 for profile in PROFILES:
  assert set(bench["profiles"][profile])==set(ROUTINES)
  assert all(bench["profiles"][profile][name]["cases"]>0 for name in ROUTINES)
  assert bench["prg_sha256"][profile]==source_status["reference_prg_sha256"][profile]
  installed=ROOT/profile/"resident"/f"math_{profile}_game_math.prg"
  assert sha(installed)==bench["prg_sha256"][profile],profile
  assert set(screening[profile]["source_maps"])==set(MAPS)
  assert screening[profile]["source_maps"]["reference"]["candidate_growth_bytes"]==screening[profile]["source_maps"]["alternate"]["candidate_growth_bytes"]
  # A proposed fast path which requires moving the occupied V1/V3 islands
  # is NOT promotable as a universal public ABI/resource-neutral change.
 assert not screening["v1_balanced"]["source_maps"]["reference"]["fits_existing_island"]
 assert not screening["v3_reu_512k"]["source_maps"]["reference"]["fits_existing_island"]
 assert not screening["v4_reu_16m"]["source_maps"]["reference"]["fits_existing_island"]
 report={
  "status":"PASS_FAMILY_AUDIT_WITH_NO_NEW_PRODUCTION_CANDIDATE",
  "audit_scope":"all 8 existing SEEK8/16 INIT, STEP, STEP_INT and STEP1 APIs",
  "family_test_evidence":{
     "all_slots":"validation/review/ISSUE39_SEEK_ALL_SLOTS_RESEARCH_2026-10-14.json",
     "native":"validation/review/ISSUE39_SEEK_ALL_MODES_NATIVE_VICE_2026-10-14.json",
     "mixed_divmod":"validation/review/ISSUE136_SEEK_DIVMOD_MIXED_PROOF.json",
     "placement":"validation/movement/SEEK_PLACEMENT.json",
     "public_benchmark":"validation/movement/SEEK_PROFILE_BENCHMARK.json"},
  "public_resident_prg_sha256":bench["prg_sha256"],
  "abi_unchanged":True,"binary_unchanged":True,
  "resource_screening":screening,
  "k1_fastpath_research":{
    "proof_type":"assembled code size and entry-layout resource gate only",
    "k1_equal_deltas_safe_fallback":True,
    "not_claimed_cycle_improvement":True,
    "v1_v3_v4_current_islands_overflow":True,
    "production_promoted":False},
  "optimization_conclusion":"retain qualified existing STEPs and INITs; no universally ABI/resource-compatible new speed winner certified in this screened family",
  "not_a_global_optimality_proof":True,
  "native_cycle_timing_measured":False,
  "private_optisearch_code_published":False,
  "issue39_closeout_status":"PENDING_POSTMERGE_MAIN_CI"
 }
 path=ROOT/"validation/review/ISSUE39_SEEK_FAMILY_FINAL_AUDIT_2026-10-14.json"
 path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 for p,x in screening.items():
  print("K1_FASTPATH_RESOURCE",p,x,flush=True)
 print("SEEK FAMILY FINAL RESOURCE AUDIT PASS, no code promotion",flush=True)

if __name__=="__main__":main()
