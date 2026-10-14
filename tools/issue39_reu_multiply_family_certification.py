#!/usr/bin/env python3
"""Permanent Issue #39 REU multiplier three-mode installed/alternate ABI certificate.

Prepares no code and measures no native cycles. REU physical emulation is
backed by pinned installed-x64sc proof and a source map/CPU-model audit.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
    s=read("RELEASE_STATUS.json")
    row=s["issue39_reu_multiply_modes_2026_10_14"]
    assert row["status"]=="PASS_COMPLETED_POSTMERGE_MAIN_GREEN" and row["family_complete"]
    cert=read(row["completion_evidence"]);assert cert["status"]==row["status"] and cert["family_complete"]
    assert cert["issue39_complete"] is False and cert["native_cycle_timing_measured"] is False
    proof=read(row["evidence"]);native=read(row["native_evidence"])
    assert proof["total_public_product_calls"]==57759 and proof["status"]=="PASS_PUBLIC_REU_MULTIPLY_MODES"
    assert native["total_public_calls"]==120 and native["status"]=="PASS_NATIVE_VICE_REU_MODES"
    assert proof["source_kinds"]==["published","reference","alternate"]
    assert row["turbo16_crossover_calls"]==33 and row["turbo32_crossover_calls"]==41
    assert row["v4_qs16_speed_crossover"] is None
    for profile in ("v3_reu_512k","v4_reu_16m"):
        assert sha(profile+"/resident/math_"+profile+"_game_math.prg")==s["reference_prg_sha256"][profile]
        name=("c64_math_v3_512k_game_math.reu" if profile.startswith("v3") else "c64_math_v4_16m_game_math.reu")
        assert sha(profile+"/reu/"+name)==s["reference_reu_sha256"][profile]
        for k in ("published","reference","alternate"):
            for t,n in (("turbo16",33),("turbo32",41)):
                q=proof["profiles"][profile][k][t]
                assert q["batch_vs_normal"]["crossover_calls"]==n
                assert q["mode"]["arithmetic_carry_stack_inputs"]=="PASS"
                assert q["mode"]["saved_ZP_exactly_restored"]
                assert q["mode"]["second_batch_valid"]
            if profile.startswith("v4"):
                q=proof["profiles"][profile][k]["v4_qs16"]
                assert q["mode"]["arithmetic_carry_stack_inputs"]=="PASS" and q["mode"]["reu_mode_restored"]
                assert not q["batch_vs_normal"]["beneficial"]
    module=(R/"relocatable_source/v4_reu_16m/v4_qs16_relocatable.asm").read_text()
    assert "ora #REU_QS16_BASE_BANK" in module and "REU_SCRATCH" in module
    src=(R/"relocatable_source/v4_reu_16m/math_relocatable.asm").read_text()
    assert '!source "v4_qs16_relocatable.asm"' in src
    assert not row["resident_or_reu_image_modified"] and row["ABI_or_ZP_growth"]==0
    print("ISSUE39 REU MULTIPLY FAMILY PERMANENT CERTIFICATE PASS",
      proof["total_public_product_calls"],"model public cases;",
      native["total_public_calls"],"native calls; exact reference binary and relocation proof")
if __name__=="__main__":main()
