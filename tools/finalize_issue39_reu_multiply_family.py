#!/usr/bin/env python3
"""Issue #39: certify the complete REU multiply family after main CI passes.

Finalization only. NEVER edits binaries, REU images, source generators or
private OptiSearch. Hardware correctness was separately tested by native VICE.
Model timings include deterministic REU costs; they are not VICE measurements.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from stage_issue39_v1_3216_ool_release import reseal

PROFILES=("v3_reu_512k","v4_reu_16m")
PROOF="validation/review/ISSUE39_REU_MULTIPLY_MATCHED_CORPUS_2026-10-14.json"
NATIVE="validation/review/ISSUE39_REU_MULTIPLY_NATIVE_2026-10-14.json"
DOC="docs/ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md"
CERT="validation/review/ISSUE39_REU_MULTIPLY_FAMILY_COMPLETION_2026-10-14.json"
KEY="issue39_reu_multiply_modes_2026_10_14"
STAMP="2026-10-14 ISSUE39 REU MULTIPLY FAMILY FINAL CERTIFICATION"

def sha(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--main-sha",required=True)
    parser.add_argument("--full-ci",type=int,required=True)
    parser.add_argument("--comparable-ci",type=int,required=True)
    parser.add_argument("--native-ci",type=int,required=True)
    a=parser.parse_args()
    assert len(a.main_sha)==40 and all(c in "0123456789abcdef" for c in a.main_sha)
    manifest_path=ROOT/"RELEASE_STATUS.json"
    manifest=json.loads(manifest_path.read_text())
    row=manifest[KEY]
    assert row["status"] in ("PASS_NATIVE_VICE_PR_MAIN_CI_PENDING",
                              "PASS_COMPLETED_POSTMERGE_MAIN_GREEN")
    assert row["native_VICE_calls"]==120 and row["v4_QS16_alternate_relocation_fixed"]
    assert not row["family_complete"] or row["status"]=="PASS_COMPLETED_POSTMERGE_MAIN_GREEN"
    assert row["source_maps"]==["published","reference","alternate"]
    assert row["ABI_or_ZP_growth"]==0 and row["resident_or_reu_image_modified"] is False
    model=json.loads((ROOT/PROOF).read_text())
    native=json.loads((ROOT/NATIVE).read_text())
    assert model["status"]=="PASS_PUBLIC_REU_MULTIPLY_MODES"
    assert model["total_public_product_calls"]==57759
    assert model["source_kinds"]==["published","reference","alternate"]
    assert model["reproducible_turbo_relocation_prior_calls"]==17196
    assert model["reproducible_turbo_boundary_prior_calls"]==3556
    assert native["status"]=="PASS_NATIVE_VICE_REU_MODES"
    assert native["total_public_calls"]==120 and native["native_cycle_timing_measured"] is False
    prgs={}
    reus={}
    for p in PROFILES:
        prgs[p]=sha(p+"/resident/math_"+p+"_game_math.prg")
        reu_file=("c64_math_v3_512k_game_math.reu" if p==PROFILES[0]
                  else "c64_math_v4_16m_game_math.reu")
        reus[p]=sha(p+"/reu/"+reu_file)
        assert prgs[p]==manifest["reference_prg_sha256"][p]==row["published_prg_sha256"][p]
        assert reus[p]==manifest["reference_reu_sha256"][p]==row["published_reu_sha256"][p]
        assert native["profiles"][p]["MATH_REU_UMUL16"]["calls"]==24
        assert native["profiles"][p]["MATH_REU_UMUL32"]["calls"]==24
        for mode,expected in (("turbo16",33),("turbo32",41)):
            q=model["profiles"][p]["published"][mode]
            assert q["batch_vs_normal"]["crossover_calls"]==expected
            assert q["mode"]["saved_ZP_exactly_restored"] and q["mode"]["second_batch_valid"]
            for k in ("reference","alternate"):
                alt=model["profiles"][p][k][mode]
                assert alt["mode"]["cycle_vector_sha256"]==q["mode"]["cycle_vector_sha256"]
                assert alt["mode"]["begin_cycles"]==q["mode"]["begin_cycles"]
                assert alt["mode"]["end_cycles"]==q["mode"]["end_cycles"]
    q=model["profiles"]["v4_reu_16m"]
    assert native["profiles"]["v4_reu_16m"]["MATH_REU_QS16"]["calls"]==24
    assert q["published"]["v4_qs16"]["batch_vs_normal"]["crossover_calls"] is None
    for mode in ("reference","alternate"):
        assert q[mode]["v4_qs16"]["mode"]["arithmetic_carry_stack_inputs"]=="PASS"
        assert q[mode]["v4_qs16"]["mode"]["cycle_vector_sha256"]==q["published"]["v4_qs16"]["mode"]["cycle_vector_sha256"]
    symbolic=(ROOT/"relocatable_source/v4_reu_16m/v4_qs16_relocatable.asm").read_text()
    for token in ("REU_QS16_BASE_BANK","MATH_IO","REU_SCRATCH","ZP_MAIN"):
        assert token in symbolic
    row.update(status="PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
               family_complete=True,
               completion_main_sha=a.main_sha,
               completion_full_library_ci_run=a.full_ci,
               completion_comparable_ci_run=a.comparable_ci,
               premerge_native_vice_run=a.native_ci,
               issue39_remains_open=True)
    manifest_path.write_text(json.dumps(manifest,indent=2)+"\n")
    certificate={
        "status":"PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
        "family_complete":True,
        "issue39_complete":False,
        "modes":["MATH_REU_UMUL16","MATH_REU_UMUL32","MATH_REU_QS16"],
        "profile_names":list(PROFILES),
        "source_maps":["published","reference","alternate"],
        "model_public_product_calls":57759,
        "prior_relocation_api_calls":17196,
        "prior_boundary_product_calls":3556,
        "native_VICE_installed_public_calls":120,
        "native_cycle_timing_measured":False,
        "turbo16_amortized_crossover_calls":33,
        "turbo32_amortized_crossover_calls":41,
        "v4_qs16_speed_crossover":None,
        "v4_qs16_alternate_bank_relocation_fixed":True,
        "normal_and_turbo_return_inputs_carry_stack_qualified":True,
        "turbo_begin_end_zp_restored":True,
        "public_abi_or_zp_or_binary_growth":0,
        "private_optisearch_source_published":False,
        "published_prgs_sha256":prgs,"published_reu_sha256":reus,
        "main_sha":a.main_sha,
        "main_full_library_ci_run":a.full_ci,
        "main_comparable_unsigned_ci_run":a.comparable_ci,
        "premerge_native_reu_vice_run":a.native_ci,
        "remaining_issue39_steps":["Trig / angle","Distance / normalization","Seek movement"],
    }
    (ROOT/CERT).write_text(json.dumps(certificate,indent=2,sort_keys=True)+"\n")
    doc=ROOT/DOC
    prefix=("**Final certification (14 October 2026):** The REU multiply "
        "family (Turbo16, Turbo32, and V4 QS16) is complete after real "
        "VICE REU-image validation, reference/alternate relocation tests "
        "and post-merge full-library and comparable checks. The V4 QS16 "
        "alternate-bank defect is corrected in the source generator, "
        "with reference binaries unchanged. Issue #39 remains open.\n\n")
    contents=doc.read_text()
    if prefix not in contents:
        doc.write_text(contents.replace("## Identical-input public-entry results",
                                        prefix+"## Identical-input public-entry results"))
    closing=(f"## {STAMP}\n\n"
        f"**Completed:** Turbo16, Turbo32 and V4 QS16; merged source and "
        f"relocation fix PR #124. Published reference PRGs and REU images "
        f"unchanged. CPU-model comparison uses the same operands and includes "
        f"deterministic REU transfer costs: Turbo16 197.046 versus normal "
        f"216.734, batch crossover 33; Turbo32 676.185 versus normal 693.453, "
        f"batch crossover 41. V4 QS16 281.727 versus 216.734, no speed "
        f"crossover. Exact 57,759 public model products, earlier 17,196 "
        f"relocation API calls/3,556 boundary products, and 120 native VICE "
        f"calls with real 512 KiB/16 MiB REU images passed. Native cycle timing "
        f"**not measured**. Alternate V4 QS16 REU bank $30 is corrected.\n\n"
        f"**Final validated main:** `{a.main_sha}`; full-library "
        f"[#{a.full_ci}](https://github.com/floppyrom/C64-Math-Library/actions/runs/{a.full_ci}), "
        f"comparable unsigned [#{a.comparable_ci}](https://github.com/floppyrom/C64-Math-Library/actions/runs/{a.comparable_ci}), "
        f"native [#{a.native_ci}](https://github.com/floppyrom/C64-Math-Library/actions/runs/{a.native_ci}). "
        f"Reproducible certificate: `{CERT}`. Issue #39 remains open "
        f"for trig, distance and seek.\n\n---\n\n")
    for filename in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        p=ROOT/filename
        current=p.read_text()
        if STAMP not in current:
            p.write_text(closing+current)
    subprocess.run(["make","clean"],cwd=ROOT,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(ROOT/"tools/package_audit.py")],cwd=ROOT,check=True)
    assert all(prgs[p]==sha(p+"/resident/math_"+p+"_game_math.prg") for p in PROFILES)
    print("ISSUE39 REU MULTIPLY FAMILY FINAL CERTIFICATION PASS; ISSUE39 OPEN",flush=True)
if __name__=="__main__":main()
