#!/usr/bin/env python3
"""Publish Issue #39 REU multiply family after merged-main green checks.

No deployed PRG/REU change. Only evidence, release status and checksum updates.
Native x64sc result correctness is independently recorded; no native timing.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
PROFILES=("v3_reu_512k","v4_reu_16m")
DOC="docs/ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md"
CERT="validation/review/ISSUE39_REU_MULTIPLY_FAMILY_COMPLETION_2026-10-14.json"
STAMP="2026-10-14 ISSUE39 REU MULTIPLY FAMILY FINAL PUBLICATION"
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--main-sha",required=True)
    ap.add_argument("--full-ci",type=int,required=True)
    ap.add_argument("--comparable-ci",type=int,required=True)
    ap.add_argument("--turbo-ci",type=int,required=True)
    ap.add_argument("--fixed-ci",type=int,required=True)
    args=ap.parse_args()
    assert len(args.main_sha)==40 and all(x in "0123456789abcdef" for x in args.main_sha)
    stfile=ROOT/"RELEASE_STATUS.json"
    st=json.loads(stfile.read_text())
    row=st["issue39_reu_multiply_modes_2026_10_14"]
    assert row["status"]=="PASS_NATIVE_VICE_PR_MAIN_CI_PENDING"
    assert not row["family_complete"]
    proof=json.loads((ROOT/row["evidence"]).read_text())
    native=json.loads((ROOT/row["native_evidence"]).read_text())
    assert proof["status"]=="PASS_PUBLIC_REU_MULTIPLY_MODES"
    assert proof["total_public_product_calls"]==57759
    assert proof["source_kinds"]==["published","reference","alternate"]
    assert native["status"]=="PASS_NATIVE_VICE_REU_MODES" and native["total_public_calls"]==120
    assert native["native_cycle_timing_measured"] is False
    for profile in PROFILES:
        assert sha(ROOT/profile/"resident"/f"math_{profile}_game_math.prg")==row["published_prg_sha256"][profile]==st["reference_prg_sha256"][profile]
        image="c64_math_v3_512k_game_math.reu" if profile==PROFILES[0] else "c64_math_v4_16m_game_math.reu"
        assert sha(ROOT/profile/"reu"/image)==row["published_reu_sha256"][profile]==st["reference_reu_sha256"][profile]
        for kind in ("published","reference","alternate"):
            for mode,expected in (("turbo16",33),("turbo32",41)):
                r=proof["profiles"][profile][kind][mode]
                assert r["batch_vs_normal"]["crossover_calls"]==expected
                assert r["mode"]["arithmetic_carry_stack_inputs"]=="PASS"
                assert r["mode"]["saved_ZP_exactly_restored"]
                assert r["mode"]["second_batch_valid"]
            if profile==PROFILES[1]:
                q=proof["profiles"][profile][kind]["v4_qs16"]
                assert q["mode"]["arithmetic_carry_stack_inputs"]=="PASS"
                assert not q["batch_vs_normal"]["beneficial"]
        entries=("MATH_REU_UMUL16","MATH_REU_UMUL32") if profile==PROFILES[0] else ("MATH_REU_UMUL16","MATH_REU_UMUL32","MATH_REU_QS16")
        for e in entries:
            assert native["profiles"][profile][e]["correct_products_inputs_carry_stack"]
            assert native["profiles"][profile][e]["calls"]==24
    module=(ROOT/"relocatable_source/v4_reu_16m/v4_qs16_relocatable.asm").read_text()
    v4src=(ROOT/"relocatable_source/v4_reu_16m/math_relocatable.asm").read_text()
    assert "ora #REU_QS16_BASE_BANK" in module
    assert "!source \"v4_qs16_relocatable.asm\"" in v4src
    assert row["v4_QS16_alternate_relocation_fixed"]
    assert row["byte_identical_reference_QS16_retained"]
    summary={"status":"PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
      "family_complete":True,"issue39_complete":False,"operations":row["modes"],
      "profiles":list(PROFILES),"matched_public_products":57759,
      "native_installed_x64sc_calls":120,"native_cycle_timing_measured":False,
      "turbo16_profit_batch_from":33,"turbo32_profit_batch_from":41,
      "v4_qs16_has_speed_crossover":False,
      "both_source_maps_qualified":True,"source_reference_images_unchanged":True,
      "public_abi_code_span_normal_ZP_growth":0,
      "private_optisearch_source_published":False,
      "main_sha":args.main_sha,
      "checks":{"main_full_library":args.full_ci,
         "main_comparable_unsigned":args.comparable_ci,
         "main_turbo_relocation":args.turbo_ci,
         "main_fixed_multiply":args.fixed_ci},
      "evidence":{"cpu":row["evidence"],"native":row["native_evidence"],
                  "documentation":DOC},
      "remaining_issue39_families":["Trig / angle","Distance / normalization","Seek movement"]}
    path=ROOT/CERT
    path.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    row.update(status="PASS_COMPLETED_POSTMERGE_MAIN_GREEN",
      family_complete=True,postmerge_main_sha=args.main_sha,
      postmerge_full_ci_run=args.full_ci,
      postmerge_comparable_ci_run=args.comparable_ci,
      postmerge_turbo_ci_run=args.turbo_ci,
      postmerge_fixed_ci_run=args.fixed_ci,
      completion_evidence=CERT)
    st["issue39_reu_multiply_modes_2026_10_14"]=row
    stfile.write_text(json.dumps(st,indent=2)+"\n")
    doc=ROOT/DOC
    old=doc.read_text()
    old=old.replace("**Next qualification:** independent exact-head full-library, comparable unsigned and Turbo32 checks; post-merge main checks before checking off REU multiply in Issue #39.",
        "**Final certification:** Native x64sc, all 57,759 source-level public product calls, and independent post-merge main full-library, comparable unsigned, Turbo32 and fixed-multiply checks are PASS. REU multiply modes are complete; Issue #39 remains open for trigonometric, distance and seeking families.")
    doc.write_text(old)
    entry=(STAMP+"\n- REU Turbo16/32 and V4 QS16 family complete with "
      "source/public matched 57,759 product calls, 120 native x64sc REU "
      "calls, and V4 QS16 alternate REU-bank/I/O/ZP relocation correction. "
      "Turbo16 same-corpus 33-call and Turbo32 41-call crossover; QS16 "
      "has no speed crossover. Installed binaries, interface and resource "
      "allocation unchanged. CPU model timing only; no native raster timing.\n"
      "- Postmerge main "+args.main_sha+
      ": full "+str(args.full_ci)+", comparable "+str(args.comparable_ci)+
      ", Turbo32 "+str(args.turbo_ci)+", fixed-output "+str(args.fixed_ci)+
      ". Issue #39 stays open for trig/distance/seek.\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        p=ROOT/name
        if STAMP not in p.read_text():p.write_text(entry+p.read_text())
    subprocess.run(["make","clean"],cwd=ROOT,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(ROOT/"tools/package_audit.py")],cwd=ROOT,check=True)
    print("ISSUE39 REU MULTIPLY FAMILY FINAL COMPLETION SEALED; ISSUE39 OPEN")
if __name__=="__main__":main()
