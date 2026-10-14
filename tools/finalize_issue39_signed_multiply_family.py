#!/usr/bin/env python3
"""Final completion certification of signed multiplication after three green main checks.

No production binary edits, ABI/resource change or private source publication.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
STAMP="2026-10-14 ISSUE39 SIGNED MULTIPLY FAMILY FINAL MAIN CERTIFICATION"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--main-sha",required=True)
    ap.add_argument("--full-ci",required=True,type=int)
    ap.add_argument("--comparable-ci",required=True,type=int)
    ap.add_argument("--family-ci",required=True,type=int)
    ap.add_argument("--native-ci",required=True,type=int)
    a=ap.parse_args()
    assert len(a.main_sha)==40 and all(x in "0123456789abcdef" for x in a.main_sha)
    status=R/"RELEASE_STATUS.json"
    st=json.loads(status.read_text())
    row=st["issue39_signed_multiply_family_2026_10_14"]
    assert row["status"] in ("PASS_NATIVE_VICE_PR_MAIN_CI_PENDING",
                             "PASS_COMPLETED_POSTMERGE_MAIN_GREEN")
    actual={p:sha(R/p/"resident"/("math_"+p+"_game_math.prg")) for p in P}
    assert actual==st["reference_prg_sha256"]==row["prg_sha256"]
    model=json.loads((R/row["model_validation"]).read_text())
    native=json.loads((R/row["native_validation"]).read_text())
    assert model["status"]=="PASS_PUBLIC_ABI_MODEL" and model["reference_prg_sha256"]==actual
    assert model["previous_264999_signed_calls"]=="PASS"
    assert model["same_input_corpus_sizes"]=={"8":65536,"16":4457,"24":2409,"32":2409}
    assert native["status"]=="PASS_NATIVE_VICE_PUBLIC_SIGNED_FAMILY"
    assert native["captured_public_calls"]==600 and native["additional_ready_preparation_calls"]==120
    assert native["native_cycle_timing_measured"] is False
    for p in P:
        assert model["same_input_per_profile"][p]["MATH_SMUL8"]["pairs"]==65536
        assert model["same_input_per_profile"][p]["MATH_SMUL32_READY"]["pairs"]==2409
        wanted=25 if p in ("v1_balanced","v5_hybrid_lowzp") else -3
        assert model["same_input_per_profile"][p]["MATH_SMUL32_READY"]["delta_histogram"]=={str(wanted):2409}
        assert native["profiles"][p]["MATH_SMUL32_READY"]["pairs"]==24
    for p in ("v1_balanced","v5_hybrid_lowzp"):
        assert model["ready_mixed_lifetime_lowzp"][p]["ordinary_valid"]==360
        assert model["ready_mixed_lifetime_lowzp"][p]["unqualified_ready_wrong"]==180
    row.update(
        status="PASS_COMPLETED_POSTMERGE_MAIN_GREEN",family_complete=True,
        release_main_sha=a.main_sha,postmerge_full_ci_run=a.full_ci,
        postmerge_comparable_ci_run=a.comparable_ci,
        postmerge_signed_family_ci_run=a.family_ci,
        premerge_native_ci_run=a.native_ci)
    st["issue39_signed_multiply_family_2026_10_14"]=row
    status.write_text(json.dumps(st,indent=2)+"\n")
    cert={
      "status":"PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
      "unsigned_family_unchanged":True,"signed_family_complete":True,
      "issue39_complete":False,"private_optisearch_source_published":False,
      "production_binaries_changed":False,
      "full_signed_8bit_cases_all_5_profiles":5*65536,
      "legacy_signed_model_calls":264999,
      "signed16_pairs_per_profile":4457,
      "signed24_pairs_per_profile":2409,
      "signed32_ready_paired_pairs_per_profile":2409,
      "native_public_calls":600,"native_ready_setup_calls":120,
      "native_cycle_timing_measured":False,
      "ready_lowzp_25_cycles_faster_per_pair":True,
      "ready_other_3_cycles_slower_per_pair":True,
      "ready_lowzp_360_ordinary_valid_180_unqualified_wrong_per_profile":True,
      "main_sha":a.main_sha,
      "main_full_library_run":a.full_ci,
      "main_comparable_unsigned_run":a.comparable_ci,
      "main_signed_family_gate_run":a.family_ci,
      "premerge_native_vice_run":a.native_ci,
      "baseline_profile_sha256":actual,
      "pending_campaign":["Fixed multiply outputs","REU Turbo/QS multiply modes",
                          "Trig/angle","Distance/normalization","Seek movement"]
    }
    proof=R/"validation/review/ISSUE39_SIGNED_MULTIPLY_FAMILY_COMPLETION_2026-10-14.json"
    proof.parent.mkdir(parents=True,exist_ok=True)
    proof.write_text(json.dumps(cert,indent=2,sort_keys=True)+"\n")
    doc=R/row["documentation"]
    part=("**Completion certification (14 October 2026):** The signed "
      "multiplication implementation family has completed the public "
      "ABI/resource audit, native installed VICE qualification and "
      "post-merge main CI. The existing implementations are retained "
      "because no screened alternative achieved a compatible full-API gain. "
      "Issue #39 remains open for the other families.\n\n")
    content=doc.read_text()
    if part not in content:
       doc.write_text(content.replace("## Frozen public choices, manual architecture pass",
           part+"## Frozen public choices, manual architecture pass"))
    note=(STAMP+"\n- Five stable SMUL8/16/24/32 + conditional SMUL32_READY "
       "implementations retained after public-ABI manual and private "
       "OptiSearch resource screen. Exhaustive SMUL8 all five profiles "
       "(327,680 calls); SMUL16 4,457 and SMUL24/32 2,409 matched pairs/profile; "
       "READY same-input 2,409 pairs/profile. V1/V5 READY -25 cycles; "
       "V2-V4 READY +3 for stable redirect; normal low-ZP entry "
       "must remain mixed-call safe.\n"
       "- 600 native VICE signed calls and 120 READY preparation calls "
       "qualified, native timing not measured; no PRG, public ABI, "
       "ZP or persistent stack growth.\n"
       "- PR #120 main "+a.main_sha+" full CI "+str(a.full_ci)+
       ", comparable "+str(a.comparable_ci)+
       ", signed family "+str(a.family_ci)+
       ". Issue #39 remains open for fixed outputs, REU, trig, distance and seek.\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
       p=R/name
       if STAMP not in p.read_text():p.write_text(note+p.read_text())
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
       reseal()
       subprocess.run([sys.executable,str(R/"tools/package_audit.py")],
                      cwd=R,check=True)
    subprocess.run([sys.executable,str(R/"tools/issue39_signed_multiply_family_audit.py")],
                   cwd=R,check=True)
    print("ISSUE39 SIGNED MULTIPLY FAMILY CERTIFIED; LEAVE ISSUE39 OPEN",flush=True)
if __name__=="__main__":main()
