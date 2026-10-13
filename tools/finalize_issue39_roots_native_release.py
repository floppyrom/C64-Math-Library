#!/usr/bin/env python3
"""Integrate verified native x64sc integer-root proof into the release manifest.

Must run AFTER successful real x64sc executable old/new comparison. Fail
closed on all hashes, counts, public entries and binary ancestry; never mark
issue #39 as complete. Commit only if package_audit passes with a reseal.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
from issue39_root_historical_parent import ROOT_IMAGES,sha
PATH=ROOT/"validation/review/ISSUE39_ROOTS_NATIVE_VICE_2026-10-13.json"
STATUS=ROOT/"RELEASE_STATUS.json"
DOC=ROOT/"docs/ISSUE39_INTEGER_ROOTS_SOURCE_RELEASE_2026-10-13.md"
MARK="2026-10-13 ISSUE39 INTEGER ROOT NATIVE VICE RELEASE PROOF"
def main():
    proof=json.loads(PATH.read_text())
    assert proof["status"]=="PASS_NATIVE_VICE_SOURCE_INSTALLED_ROOTS"
    assert proof["native_calls"]==768 and proof["native_cycles_measured"] is False
    assert proof["parent_commit"]=="f7164dd07223f2f1761dfe6260293af3420357fa"
    assert set(proof["profiles"])==set(ROOT_IMAGES)
    for profile,values in proof["profiles"].items():
        old,current,_,_=ROOT_IMAGES[profile]
        assert values["original_sha256"]==old
        assert values["candidate_sha256"]==current
        assert set(values["entries"])=={"MATH_ISQRT16","MATH_ISQRT32"}
        for entry,row in values["entries"].items():
            assert row["identical_output"] is True and row["cases_per_image"]==48
            assert len(row["old_dump_sha256"])==64 and len(row["new_dump_sha256"])==64
            assert all(ch in "0123456789abcdef" for ch in row["old_dump_sha256"]+row["new_dump_sha256"])
        image=ROOT/profile/"resident"/f"math_{profile}_game_math.prg"
        assert sha(image.read_bytes())==current,(profile,"source PRG drift")
    state=json.loads(STATUS.read_text())
    x=state["issue39_integer_roots_source_release_2026_10_13"]
    assert x["status"] in ("PASS_STAGED_NATIVE_VICE_PENDING","PASS_NATIVE_VICE_SOURCE_INSTALLED_PR_CI_PENDING")
    assert state["reference_prg_sha256"]==x["reference_sha256"]
    assert state["reference_prg_sha256"]["v4_reu_16m"]=="3e2b745e9cd81512f6c3aa4e5cc029528981bb7f6d56abd117e663994685f913"
    x.update(status="PASS_NATIVE_VICE_SOURCE_INSTALLED_PR_CI_PENDING",
       native_vice_calls=768,native_vice_evidence=str(PATH.relative_to(ROOT)),
       native_cycles_measured=False)
    STATUS.write_text(json.dumps(state,indent=2)+"\n")

    p=DOC.read_text()
    p=p.replace(
       "Production staging, native VICE and PR/main CI not yet qualified.",
       "Source installed and native VICE old/new checked (768 full-resident calls); PR/main CI not yet qualified.")
    p=p.replace(
       "**Pending before release:** native VICE on installed source-built resident images, independent PR tests, post-merge main CI.",
       "**Native VICE PASS:** 768 full-resident old/new public calls, including both ISQRT16 and ISQRT32, verified on V1/V2/V3/V5; source-built PRG and exact historical baseline pinned by SHA-256. This test does not claim measured hardware cycle times. **Pending:** independent PR tests and post-merge main CI.")
    DOC.write_text(p)
    marker=" (native VICE and independent PR/main CI pending)."
    new=" (native VICE: 768 old/new full-resident calls PASS; independent PR/main CI pending)."
    for name in ("README.md","USER_MANUAL.md"):
        f=ROOT/name
        s=f.read_text()
        assert marker in s or new in s
        f.write_text(s.replace(marker,new))
    note=(MARK+"\n"
      "- Native x64sc old/new full-resident ISQRT16 and ISQRT32 validation:"
      " 768 calls across V1/V2/V3/V5, exact public output, input, carry,"
      " return-path sentinels and stack invariants. Full root proof: "
      +str(PATH.relative_to(ROOT))+". V4 unchanged; cycle counts from the"
      " independent mini6502 proof only. Issue #39 remains OPEN.\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        p=ROOT/name
        if MARK not in p.read_text():p.write_text(note+p.read_text())
    # Prior proof was SHA sealed before the new native validator was added.
    # The updated 30-point package audit is the mandatory publication gate.
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(ROOT/"tools/package_audit.py")],cwd=ROOT,check=True)
    print("ISQRT16/32 NATIVE VICE SOURCE RELEASE SEALED 768 CALLS; ISSUE39 OPEN")
if __name__=="__main__":main()
