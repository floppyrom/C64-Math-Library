#!/usr/bin/env python3
"""Seal fully native-qualified V2/V3/V4 UMUL24 result into public package."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
EVIDENCE="validation/review/ISSUE39_V2V4_UMUL24_NOCARRY_CLC_NATIVE_2026-10-13.json"
STATUS=R/"RELEASE_STATUS.json"
DOC=R/"docs/ISSUE39_V2V4_UMUL24_NOCARRY_CLC_2026-10-13.md"
STAMP="2026-10-13 ISSUE39 V2V4 UMUL24 NOCARRY CLC NATIVE VALIDATION"
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=R/EVIDENCE;proof=json.loads(p.read_text())
    assert proof["status"]=="PASS_NATIVE_SOURCE_INSTALLED_NOT_YET_MERGED"
    assert proof["native_calls"]==576 and proof["native_cycle_timing_measured"] is False
    names={"v2_pareto_fast","v3_reu_512k","v4_reu_16m"}
    assert set(proof["profiles"])==names
    st=json.loads(STATUS.read_text());row=st["issue39_v2v4_umul24_nocarry_clc_2026_10_13"]
    assert row["status"] in ("PASS_STAGED_NATIVE_VICE_PENDING","PASS_NATIVE_VICE_PR_CI_PENDING")
    for profile,entries in proof["profiles"].items():
        assert set(entries)=={"MATH_UMUL24","MATH_SMUL24"}
        image=R/profile/"resident"/f"math_{profile}_game_math.prg"
        assert sha(image)==row["candidate"][profile]
        for v in entries.values():
            assert v["paired_inputs"]==48
            assert len(v["old_sha256"])==64 and len(v["new_sha256"])==64
            assert v["old_sha256"]==v["new_sha256"],"native output difference"
    row.update(status="PASS_NATIVE_VICE_PR_CI_PENDING",native_vice_calls=576,
               native_vice_evidence=EVIDENCE,
               native_vice_evidence_sha256=sha(p))
    STATUS.write_text(json.dumps(st,indent=2)+"\n")
    s=DOC.read_text()
    s=s.replace("NOT RELEASED until native VICE/PR/main CI.",
                "Native VICE passed: 576 real full resident old/new calls; PR/main CI pending.")
    s+="\nNative VICE validates both unsigned and signed public entries on three resident profiles, original and candidate, with exact products, input preservation, carry and sentinel parity. It does not measure cycles. See "+EVIDENCE+".\n"
    DOC.write_text(s)
    note=(STAMP+"\n- Pinned real x64sc old/new public UMUL24 and SMUL24 verified"
      " on V2/V3/V4: 576 calls, identical products, preserved inputs,"
      " carry and sentinels; unchanged signed private executable."
      " Native cycles were NOT measured. "+EVIDENCE+".\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        f=R/name
        if STAMP not in f.read_text():f.write_text(note+f.read_text())
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(R/"tools/package_audit.py")],
                       cwd=R,check=True)
    print("ISSUE39 UMUL24 V2-V4 NATIVE VICE PROOF SEALED 576; ISSUE39 OPEN")
if __name__=="__main__":main()
