#!/usr/bin/env python3
"""Seal Issue39 REU multiplication source-map fix after native x64sc passed.

Do NOT close Issue #39 or mark REU family complete until independent exact-PR
and post-merge main qualification. This is source-only QS16 relocation.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v3_reu_512k","v4_reu_16m")
STAMP="2026-10-14 ISSUE39 REU MULTIPLY NATIVE VICE AND V4 QS16 RELOCATION"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    sf=ROOT/"RELEASE_STATUS.json"
    status=json.loads(sf.read_text())
    row=status["issue39_reu_multiply_modes_2026_10_14"]
    assert row["status"] in ("PASS_REU_CPU_MODEL_SOURCE_MAPS_NATIVE_PENDING",
                            "PASS_NATIVE_VICE_PR_MAIN_CI_PENDING")
    report=json.loads((ROOT/row["evidence"]).read_text())
    native=json.loads((ROOT/"validation/review/ISSUE39_REU_MULTIPLY_NATIVE_2026-10-14.json").read_text())
    assert report["status"]=="PASS_PUBLIC_REU_MULTIPLY_MODES"
    assert report["total_public_product_calls"]==57759
    assert report["source_kinds"]==["published","reference","alternate"]
    assert native["status"]=="PASS_NATIVE_VICE_REU_MODES"
    assert native["total_public_calls"]==120 and native["native_VICE_reu_flags"] is True
    assert native["native_cycle_timing_measured"] is False
    for p in P:
        assert sha(ROOT/p/"resident"/f"math_{p}_game_math.prg")==status["reference_prg_sha256"][p]
        img=ROOT/p/"reu"/("c64_math_v3_512k_game_math.reu" if p==P[0] else "c64_math_v4_16m_game_math.reu")
        assert sha(img)==status["reference_reu_sha256"][p]
        assert report["profiles"][p]["alternate"]["turbo16"]["batch_vs_normal"]["crossover_calls"]==33
        assert report["profiles"][p]["alternate"]["turbo32"]["batch_vs_normal"]["crossover_calls"]==41
        for mode in native["profiles"][p].values():
            assert mode["correct_products_inputs_carry_stack"] is True
            assert mode["calls"]==24
    assert report["profiles"][P[1]]["alternate"]["v4_qs16"]["mode"]["arithmetic_carry_stack_inputs"]=="PASS"
    assert report["profiles"][P[1]]["alternate"]["v4_qs16"]["batch_vs_normal"]["beneficial"] is False
    assert native["profiles"][P[1]]["MATH_REU_QS16"]["correct_products_inputs_carry_stack"] is True
    row.update(status="PASS_NATIVE_VICE_PR_MAIN_CI_PENDING",family_complete=False,
        native_VICE_calls=120, native_evidence="validation/review/ISSUE39_REU_MULTIPLY_NATIVE_2026-10-14.json",
        native_cycle_timing_measured=False,
        v4_QS16_alternate_relocation_fixed=True,
        byte_identical_reference_QS16_retained=True)
    status["issue39_reu_multiply_modes_2026_10_14"]=row
    sf.write_text(json.dumps(status,indent=2)+"\n")
    doc=ROOT/row["documentation"]
    s=doc.read_text()
    heading="## Native VICE x64sc proof"
    if heading not in s:
        s += ("\n"+heading+"\n\n"
            "The published V3 512-KiB and V4 16-MiB REU images passed **120 real "
            "x64sc public product calls**, each inside the required BEGIN/CALL/END "
            "lifecycle. Turbo16/32 passed in both profiles; V4 QS16 passed in "
            "the installed reference map. The native smoke test checks public "
            "products, carry, input/stack preservation and sentinel output "
            "bytes. Native cycles were **not** measured. The V4 QS16 *alternate* "
            "map is source-built and CPU-model-qualified on all 2,097 same "
            "operands; its relocation fixes symbolic public I/O, ZP scratch "
            "and the REU quarter-square base bank, while the installed "
            "reference-mode PRG/REU images remain byte-for-byte unchanged.\n\n"
            "**Next qualification:** independent exact-head full-library, "
            "comparable unsigned and Turbo32 checks; post-merge main checks "
            "before checking off REU multiply in Issue #39.\n")
        doc.write_text(s)
    comment=(STAMP+"\n- Actual VICE x64sc with 512-KiB/16-MiB REU "
      "images qualified 120 Turbo16/Turbo32/QS16 BEGIN/CALL/END calls. "
      "Carry, products, operands, output sentinels and stack passed; "
      "native cycle timing was NOT measured. V4 QS16 alternate relocation "
      "now uses symbolic MATH_IO, REU_SCRATCH, ZP_MAIN and "
      "REU_QS16_BASE_BANK. Reference PRG/REU bytes unchanged; "
      "same-corpus Turbo16 batch crossover 33 and Turbo32 41, QS16 "
      "no crossover. Exact PR/main CI pending.\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        dest=ROOT/name
        if STAMP not in dest.read_text():
            dest.write_text(comment+dest.read_text())
    subprocess.run(["make","clean"],cwd=ROOT,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(ROOT/"tools/package_audit.py")],
                       cwd=ROOT,check=True)
    print("ISSUE39 REU MODE NATIVE VICE AND V4 RELOCATED QS16 SEALED; CI PENDING",flush=True)
if __name__=="__main__":main()
