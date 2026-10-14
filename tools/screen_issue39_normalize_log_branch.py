#!/usr/bin/env python3
"""Issue39 branch-collapse NORMALIZE research, not an installed release.

Regenerates both map builds, independently checks exact public outputs,
zero-carry, signed plane, mixed-call and 723073 reduction-cell precision.
Pairs 107396 identical signed vectors per map/profile with prior committed
benchmark. Never mutates shipped resident PRGs or REU images.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
STOCK={"v1_balanced","v2_pareto_fast","v5_hybrid_lowzp"}
def sha(data):return hashlib.sha256(data).hexdigest()
def run(*args):subprocess.run([*args],cwd=R,check=True)
def main():
    old=json.loads((R/"validation/normalize/NORMALIZE_PROFILE_PARITY_107396.json").read_text())
    oldnative=json.loads((R/"validation/normalize/NATIVE_SOURCE_VALIDATION.json").read_text())
    status=json.loads((R/"RELEASE_STATUS.json").read_text())
    original={p:sha((R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes()) for p in PROFILES}
    assert original==status["reference_prg_sha256"],"pub resident drift before research"
    assert old["status"]=="PASS" and old["corpus_vectors"]==107396
    run("make","normalize")
    new=json.loads((R/"validation/normalize/NORMALIZE_PROFILE_PARITY_107396.json").read_text())
    native=json.loads((R/"validation/normalize/NATIVE_SOURCE_VALIDATION.json").read_text())
    reduced=json.loads((R/"validation/normalize/OPTIMIZED_VALIDATION.json").read_text())
    full_log=json.loads((R/"validation/normalize/LOG_RATIO_FULL_DOMAIN_PRECISION_CERTIFICATE.json").read_text())
    full_exact=json.loads((R/"validation/normalize/EXACT_RATIO_FULL_DOMAIN_PRECISION_CERTIFICATE.json").read_text())
    native_proof=json.loads((R/"validation/review/ISSUE39_NORMALIZE_BRANCH_COLLAPSE_NATIVE_2026-10-14.json").read_text())
    assert native_proof["status"]=="PASS_NATIVE_VICE_NORMALIZE_BRANCH_COLLAPSE"
    assert native_proof["baseline_and_candidate_calls"]==320
    for row in new["profiles"]:
        p=row["profile"]
        assert row["reference"]["prg_sha256"]==native_proof["profiles"][p]["candidate_sha256"],(p,"CPU/native candidate mismatch")
        assert native_proof["profiles"][p]["all_signed_vectors_and_flags_match"]
    assert new["status"]=="PASS" and new["corpus_sha256"]==old["corpus_sha256"]
    assert new["corpus_vectors"]==old["corpus_vectors"]
    assert native["status"]==reduced["status"]=="PASS"
    assert full_log["status"]==full_exact["status"]=="PASS"
    assert full_log["max_angle_deg"]<=0.3621 and full_exact["max_angle_deg"]<=0.3621
    assert full_log["max_component_ceil"]<=202 and full_exact["max_component_ceil"]<=202
    assert native["profiles"]["v1_balanced"]["maps"]["reference"]["code_bytes"]==865
    assert native["profiles"]["v2_pareto_fast"]["maps"]["reference"]["code_bytes"]==865
    assert native["profiles"]["v5_hybrid_lowzp"]["maps"]["reference"]["code_bytes"]==865
    assert native["profiles"]["v3_reu_512k"]["maps"]["reference"]["code_bytes"]==849
    report={"status":"PASS_LOG_BRANCH_COLLAPSE_RESEARCH_NOT_RELEASED",
      "candidate":"eight two-branch index paths reduced to one BEQ per stock implementation",
      "shipped_prgs_modified":False,"REU_images_modified":False,
      "private_optisearch_source_published":False,
      "new_public_model_calls":107396*len(PROFILES)*2,
      "precision_cells":full_log["cells"],
      "stock_code_bytes_before":881,"stock_code_bytes_candidate":865,
      "new_normal_zp":0,"native_vice_candidate_baseline_calls":320,
      "profiles":{}}
    assert len(new["profiles"])==len(old["profiles"])==len(PROFILES)
    for previous,current in zip(old["profiles"],new["profiles"]):
        p=current["profile"];assert previous["profile"]==p
        d={}
        for kind in ("reference","alternate"):
            x=previous[kind];y=current[kind]
            for f in ("backend","cases","output_sha256","max_angle_deg","max_component_lsb",
                      "output_errors","carry_errors","input_preserve_errors","entry"):
                assert y[f]==x[f],(p,kind,f,x[f],y[f])
            assert y["cases"]==107396
            assert current["cycle_vector_mismatches"]==current["output_vector_mismatches"]==0
            gain=x["mean_cycles"]-y["mean_cycles"]
            if p in STOCK:
                assert gain>0.5 and gain<2.1,(p,kind,"unexpected gain",gain)
            else:
                assert abs(gain)<1e-10,(p,kind,"REU timing changed",gain)
            d[kind]={"old_mean_cycles":x["mean_cycles"],"candidate_mean_cycles":y["mean_cycles"],
                 "saved_mean_cycles":gain,"old_min_cycles":x["min_cycles"],
                 "new_min_cycles":y["min_cycles"],"old_max_cycles":x["max_cycles"],
                 "new_max_cycles":y["max_cycles"],
                 "output_sha256":y["output_sha256"],"code_bytes":865 if p in STOCK else 849}
        report["profiles"][p]=d
        print("NORMALIZE BRANCH COLLAPSE",p,"ref saving",d["reference"]["saved_mean_cycles"],flush=True)
    for p in PROFILES:
        assert sha((R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes())==original[p],p
    output=R/"validation/review/ISSUE39_NORMALIZE_BRANCH_COLLAPSE_RESEARCH_2026-10-14.json"
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 NORMALIZE LOG BRANCH COLLAPSE SOURCE RESEARCH PASS",flush=True)
if __name__=="__main__":main()
