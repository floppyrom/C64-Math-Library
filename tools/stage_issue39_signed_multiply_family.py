#!/usr/bin/env python3
"""Seal signed multiply family no-gain decisions and native x64sc public proof.

Does not edit any program binary, private OptiSearch, or timing/ABI profile.
Called after the deterministic five-profile model and native VICE probes PASS.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
STAMP="2026-10-14 ISSUE39 SIGNED MULTIPLY FAMILY ABI RESOURCE QUALIFICATION"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    status_path=R/"RELEASE_STATUS.json"
    st=json.loads(status_path.read_text())
    actual={p:sha(R/p/"resident"/("math_"+p+"_game_math.prg")) for p in P}
    assert actual==st["reference_prg_sha256"]
    model_path=R/"validation/review/ISSUE39_SIGNED_MULTIPLY_FAMILY_AUDIT_2026-10-14.json"
    native_path=R/"validation/review/ISSUE39_SIGNED_MULTIPLY_NATIVE_2026-10-14.json"
    model=json.loads(model_path.read_text());native=json.loads(native_path.read_text())
    assert model["status"]=="PASS_PUBLIC_ABI_MODEL" and model["reference_prg_sha256"]==actual
    assert model["s8_exhaustive_all_five_profiles"] is True
    assert model["same_input_corpus_sizes"]=={"8":65536,"16":4457,"24":2409,"32":2409}
    assert all(model["ready_same_input_confirmed"][p]==2409 for p in P)
    assert model["previous_264999_signed_calls"]=="PASS"
    assert native["status"]=="PASS_NATIVE_VICE_PUBLIC_SIGNED_FAMILY"
    assert native["captured_public_calls"]==600
    assert native["additional_ready_preparation_calls"]==120
    assert native["native_cycle_timing_measured"] is False
    assert len(native["profiles"])==5
    st["issue39_signed_multiply_family_2026_10_14"]={
      "status":"PASS_NATIVE_VICE_PR_MAIN_CI_PENDING",
      "family_complete":False,
      "issue39_remains_open":True,
      "profiles":list(P),
      "routines":["MATH_SMUL8","MATH_SMUL16","MATH_SMUL24",
                  "MATH_SMUL32","MATH_SMUL32_READY"],
      "signed_public_cpu_model_calls_prior_suite":264999,
      "new_exhaustive_smul8_pairs_per_profile":65536,
      "new_smul16_pairs_per_profile":4457,
      "new_smul24_pairs_per_profile":2409,
      "new_smul32_and_ready_paired_cases_per_profile":2409,
      "native_public_calls":600,
      "native_ready_setup_calls":120,
      "native_cycle_timing_measured":False,
      "normal_public_abi_changed":False,"resident_prg_changed":False,
      "normal_ZP_or_persistent_stack_growth":0,
      "private_optisearch_source_published":False,
      "unqualified_native_candidates_promoted":False,
      "model_validation":"validation/review/ISSUE39_SIGNED_MULTIPLY_FAMILY_AUDIT_2026-10-14.json",
      "native_validation":"validation/review/ISSUE39_SIGNED_MULTIPLY_NATIVE_2026-10-14.json",
      "documentation":"docs/ISSUE39_SIGNED_MULTIPLY_FAMILY_2026-10-14.md",
      "prg_sha256":actual,
      "separate_pending":["Fixed multiply outputs","REU Turbo and QS multiply","Trig","Distance","Seek"]}
    status_path.write_text(json.dumps(st,indent=2)+"\n")
    entry=(STAMP+"\n"
        "- Completed per-implementation audit of five stable SMUL8/16/24/32 "
        "and conditional SMUL32_READY APIs. Exhaustive SMUL8 65,536 each of "
        "V1-V5; 16/24/32 matched corpora 4,457/2,409/2,409; independent "
        "ordinary/READY paired 2,409 per profile, V1/V5 dirty-pointer interleavings. "
        "The existing 264,999-call signed regression and both relocation maps "
        "remain release gates.\n"
        "- 600 installed-resident native x64sc calls plus 120 READY state "
        "preparation calls, exact product/carry/inputs/output sentinels/stack. "
        "Native cycles NOT measured. Private OptiSearch sign-first/probability "
        "layout, conditional carry, centered tables and SMUL32 compact126 "
        "screened; no demonstrable compatible full public ABI gain; no code "
        "or resident/ZP/stack/table growth.\n"
        "- Publication is staged pending independent PR and main CI. "
        "Issue #39 remains OPEN; shifted multiplication and REU Turbo/QS are "
        "independent later steps. docs/ISSUE39_SIGNED_MULTIPLY_FAMILY_2026-10-14.md\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        p=R/name
        if STAMP not in p.read_text():p.write_text(entry+p.read_text())
    p=R/"README.md";old=p.read_text()
    dest="docs/ISSUE39_SIGNED_MULTIPLY_FAMILY_2026-10-14.md"
    if dest not in old:p.write_text(old+"\nFor the signed SMUL8/16/24/32 "
       "and conditional SMUL32_READY profiles see the [Issue #39 signed "
       "multiply ABI/resource and OptiSearch audit]("+dest+").\n")
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(R/"tools/package_audit.py")],cwd=R,check=True)
    print("ISSUE39 SIGNED MULTIPLY NATIVE ABI RESEARCH NO-GAIN STAGE SEALED")
if __name__=="__main__":main()
