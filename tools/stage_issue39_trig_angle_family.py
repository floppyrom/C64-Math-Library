#!/usr/bin/env python3
"""Issue39 trig/angle public-table ABI research publication, not final release.

Never touches executable resident files or published REU images; completion is
pending native VICE and full main CI. Records preserved per-profile resource
tiers, full 256-phase SIN/COS/SINCOS proofs and prior exhaustive ATAN2.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
EVID="validation/review/ISSUE39_TRIG_ANGLE_FAMILY_SOURCE_AUDIT_2026-10-14.json"
DOC="docs/ISSUE39_TRIG_ANGLE_FAMILY_REVIEW_2026-10-14.md"
STAMP="2026-10-14 ISSUE39 TRIG ANGLE PUBLIC TABLE AUDIT RESEARCH"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    model=json.loads((R/EVID).read_text())
    assert model["status"]=="PASS_PUBLIC_TRIG_ANGLE_EXHAUSTIVE"
    assert model["new_public_trig_calls"]==7680
    assert model["already_qualified_public_atan2_calls"]==655360
    assert model["source_maps"]==["reference","alternate"]
    previous=json.loads((R/"validation/ATAN2_DISPATCH_VALIDATION.json").read_text())
    assert previous["status"]=="PASS" and previous["machine_calls"]==655360
    stp=R/"RELEASE_STATUS.json"
    st=json.loads(stp.read_text())
    binaries={p:sha(R/p/"resident"/("math_"+p+"_game_math.prg")) for p in P}
    assert binaries==st["reference_prg_sha256"]
    means={}
    for p in P:
        r=model["profiles"][p]
        for kind in ("reference","alternate"):
            row=r[kind]
            for op in ("MATH_SIN8","MATH_COS8","MATH_SINCOS8"):
                assert row[op]["cases"]==256
                assert row[op]["input_or_carry_or_stack_failures"]==0 if "input_or_carry_or_stack_failures" in row[op] else (
                    row[op]["inputs_preserved"] and row[op]["carry_clear"] and row[op]["stack_stable"])
            assert row["paired_combined_vs_two_separate"]["output_identity_all_256_phases"] is True
        ref=r["reference"]
        avg=ref["MATH_SINCOS8"]["mean_cycles"]
        gain=ref["paired_combined_vs_two_separate"]["mean_saving_public_entry_cycles"]
        assert avg==(39 if p==P[0] else 31),(p,avg)
        assert gain==(13 if p==P[0] else 15),(p,gain)
        means[p]={"combined_mean_cycles":avg,"mean_gain_vs_separate_public_calls":gain}
    doc=("# Issue #39 — Trigonometric and angular routine public audit\n\n"
       "**Research stage, not yet a final family release.** Audited MATH_SIN8, "
       "MATH_COS8, MATH_SINCOS8, MATH_ATAN2_8 on all five public profiles "
       "and both source relocations. Private OptiSearch source is not redistributed.\n\n"
       "The new CPU-model test calls SIN8, COS8 and SINCOS8 on every 8-bit "
       "phase in both memory maps: **7,680 new public calls**. All combined "
       "outputs are exactly equal to separate SIN/COS outputs, inputs preserved, "
       "carry clear, and hardware stack stable. Source-reference and alternate "
       "maps have identical outputs and cycle vectors. The existing signed-byte "
       "ATAN2 public dispatch certificate already covers **655,360 calls** "
       "(full 65,536 signed x/y inputs per profile and map), with at most one "
       "phase unit error on V1/V2/V3/V5 and exact rounded-reference phases on V4.\n\n"
       "| Profile | Combined SINCOS public CPU-model cycles | CPU-model cycles "
       "saved vs separate SIN and COS |\n"
       "|---|---:|---:|\n"
       "| V1 | 39 | 13 |\n"
       "| V2 / V3 / V4 / V5 | 31 | 15 |\n\n"
       "No change has been made to the shipped program binaries, ZP layout, "
       "tables, or stable API. V1 uses a single lookup plane plus phase "
       "rotation to conserve memory; V2–V5 use separate indexed sine/cosine "
       "planes for the faster combined path. Moving V1 to the faster "
       "two-table layout changes its code/table resource class and is "
       "**not** automatically a Pareto improvement. Standalone optimized "
       "ATAN2 variants are already in the public catalog.\n\n"
       "Native VICE spot checks and complete independent PR/main qualification "
       "remain required before checking off the trig family in Issue #39. "
       "No hardware-native cycle timing is claimed.\n")
    p=R/DOC
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(doc)
    note=(STAMP+"\n- SIN8/COS8/SINCOS8 qualified on all 256 phases, 7,680 "
      "five-profile/two-map CPU calls; SINCOS outputs equal separate "
      "operations. Existing ATAN2 exhaustive 655,360-call public dispatch "
      "proof retained. V1 SINCOS 39 cycles, 13 saved vs two separate; "
      "V2-V5 31 cycles, 15 saved. No public ABI, resident binary, "
      "table/ZP or private OptiSearch source changes. Native VICE and "
      "final CI pending; Issue39 trig remains OPEN. "+DOC+"\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        p=R/name
        if STAMP not in p.read_text():p.write_text(note+p.read_text())
    # Real x64sc output equivalence is separate from CPU-model timing.
    native_path=R/"validation/review/ISSUE39_TRIG_ANGLE_NATIVE_2026-10-14.json"
    native=json.loads(native_path.read_text())
    assert native["status"]=="PASS_NATIVE_VICE_TRIG_PUBLIC"
    assert native["public_calls"]==480 and native["native_cycle_timing_measured"] is False
    for p in P:
        for op in ("MATH_SIN8","MATH_COS8","MATH_SINCOS8","MATH_ATAN2_8"):
            q=native["profiles"][p][op]
            assert q["cases"]==24 and q["correct_output_and_inputs"] is True
            assert q["carry_clear"] and q["matched_model_public_results"]
    native_note=("2026-10-14 ISSUE39 TRIG ANGLE NATIVE VICE VALIDATION\n"
      "- 480 installed x64sc public calls in all five profiles covering "
      "SIN8/COS8/SINCOS8/ATAN2; compared exact outputs against independent "
      "model, preserved operands, carry clear and stable stack. V3/V4 REU "
      "image tested. No native cycle measurement; source, standalone, "
      "ZP and public ABI unchanged. Final PR/main CI pending.\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        path=R/name
        if "ISSUE39 TRIG ANGLE NATIVE VICE VALIDATION" not in path.read_text():
            path.write_text(native_note+path.read_text())
    st["issue39_trig_angle_family_2026_10_14"]={
      "status":"PASS_NATIVE_VICE_PR_MAIN_CI_PENDING","family_complete":False,
      "native_vice_calls":480,
      "native_validation":"validation/review/ISSUE39_TRIG_ANGLE_NATIVE_2026-10-14.json",
      "routines":["MATH_SIN8","MATH_COS8","MATH_SINCOS8","MATH_ATAN2_8"],
      "five_profiles":list(P),"reference_and_alternate_maps":True,
      "new_sin_cos_sincos_model_calls":7680,
      "prior_atan2_model_calls":655360,
      "combined_sincos_profile_means":means,
      "production_resident_changed":False,"private_optisearch_source_published":False,
      "native_cycle_timing_measured":False,
      "baseline_prg_sha256":binaries,"documentation":DOC,"evidence":EVID,
      "issue39_remains_open":True}
    stp.write_text(json.dumps(st,indent=2)+"\n")
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(R/"tools/package_audit.py")],cwd=R,check=True)
    assert all(sha(R/p/"resident"/("math_"+p+"_game_math.prg"))==binaries[p] for p in P)
    print("ISSUE39 TRIG CPU AND NATIVE VALIDATION SEALED; PR/MAIN CERTIFICATION PENDING")
if __name__=="__main__":main()
